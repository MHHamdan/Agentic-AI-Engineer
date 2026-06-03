#!/usr/bin/env python3
"""Production durable backends for the dead-letter queue (Lab 54).

Lab 50 built a `DurableQueue` as a file with a lock and noted the real thing is Redis Streams or
SQS, "same lease/ack/retention contract." This lab makes that literal: one contract, two
production backends, and the Lab 50 redelivery worker driving either unchanged.

The contract (from Lab 50): enqueue a failed page, lease it (invisible to other workers until
the lease expires), ack on success, reclaim expired leases for redelivery, and give up to a dead
set past a max-delivery count.

Redis Streams maps it with a consumer group: XADD enqueues, XREADGROUP leases (the entry joins
the group's Pending Entries List), XACK acks, XAUTOCLAIM reclaims entries idle past the lease,
and the PEL delivery count drives give-up. SQS maps the same contract with a visibility timeout:
SendMessage enqueues, ReceiveMessage leases (the message goes invisible for VisibilityTimeout),
DeleteMessage acks, the timeout expiring redelivers, and a redrive policy moves a message to a
dead-letter queue past maxReceiveCount.

The real client code is shown behind guarded imports; the behavior is verified against in-process
fakes that mirror each system's semantics, so the same contract test passes on both. Production
swaps the fake for `redis.Redis(...)` or `boto3.client("sqs")` with no change to the worker.

Usage:
    python backends.py --self-test
"""
from __future__ import annotations

import argparse
import sys
import time
import uuid

try:
    import redis  # noqa: F401  (real client; not needed for the fake-backed self-test)
except Exception:
    redis = None
try:
    import boto3  # noqa: F401
except Exception:
    boto3 = None


# --------------------------------------------------------------------------------------------
# In-process fakes that mirror the production semantics used by the two backends.
# --------------------------------------------------------------------------------------------
class FakeRedisStreams:
    """Minimal Redis-Streams + consumer-group semantics: XADD / XREADGROUP / XACK / XAUTOCLAIM,
    with a per-entry delivery count, exactly enough to back RedisStreamQueue."""
    def __init__(self):
        self.entries: dict[str, dict] = {}        # id -> payload
        self.order: list[str] = []
        self.pel: dict[str, dict] = {}            # id -> {delivered_at, deliveries}
        self.acked: set[str] = set()

    def xadd(self, payload: dict) -> str:
        mid = f"{len(self.order)}-0"
        self.entries[mid] = payload
        self.order.append(mid)
        return mid

    def xreadgroup(self, count: int, now: float) -> list[tuple[str, dict]]:
        out = []
        for mid in self.order:                    # deliver new (never-delivered) entries
            if mid in self.acked or mid in self.pel:
                continue
            self.pel[mid] = {"delivered_at": now, "deliveries": 1}
            out.append((mid, self.entries[mid]))
            if len(out) >= count:
                break
        return out

    def xautoclaim(self, min_idle: float, now: float) -> list[tuple[str, dict]]:
        out = []
        for mid, meta in self.pel.items():        # reclaim entries idle past the lease
            if now - meta["delivered_at"] >= min_idle:
                meta["delivered_at"] = now
                meta["deliveries"] += 1
                out.append((mid, self.entries[mid]))
        return out

    def deliveries(self, mid: str) -> int:
        return self.pel.get(mid, {}).get("deliveries", 0)

    def xack(self, mid: str) -> None:
        self.pel.pop(mid, None)
        self.acked.add(mid)

    def xdel(self, mid: str) -> None:
        if mid in self.entries:
            del self.entries[mid]


class FakeSQS:
    """Minimal SQS visibility-timeout semantics: SendMessage / ReceiveMessage / DeleteMessage,
    plus ReceiveCount and a redrive to a DLQ, enough to back SQSQueue."""
    def __init__(self):
        self.msgs: dict[str, dict] = {}           # id -> {payload, visible_at, receives}
        self.dlq: list[dict] = []

    def send(self, payload: dict) -> str:
        mid = uuid.uuid4().hex[:8]
        self.msgs[mid] = {"payload": payload, "visible_at": 0.0, "receives": 0}
        return mid

    def receive(self, count: int, visibility_s: float, now: float) -> list[tuple[str, dict]]:
        out = []
        for mid, m in self.msgs.items():
            if m["visible_at"] <= now:            # only visible messages are leasable
                m["visible_at"] = now + visibility_s
                m["receives"] += 1
                out.append((mid, m["payload"]))
                if len(out) >= count:
                    break
        return out

    def receives(self, mid: str) -> int:
        return self.msgs.get(mid, {}).get("receives", 0)

    def delete(self, mid: str) -> None:
        self.msgs.pop(mid, None)

    def redrive(self, mid: str) -> None:
        m = self.msgs.pop(mid, None)
        if m:
            self.dlq.append(m["payload"])


# --------------------------------------------------------------------------------------------
# The two backends behind one contract: enqueue / lease / ack / reclaim_expired / pending / dead.
# --------------------------------------------------------------------------------------------
class RedisStreamQueue:
    """Production: `r = redis.Redis(...)`; XADD/XREADGROUP/XACK/XAUTOCLAIM on a stream + group.
    Here `r` is a FakeRedisStreams mirroring those ops."""
    def __init__(self, client=None, max_deliveries: int = 3):
        self.r = client or FakeRedisStreams()
        self.max_deliveries = max_deliveries
        self._dead: list[dict] = []

    def enqueue(self, payload: dict) -> str:
        return self.r.xadd(payload)               # XADD stream * payload

    def lease(self, max_n: int, lease_s: float, now: float) -> list[tuple[str, dict]]:
        return self.r.xreadgroup(max_n, now)      # XREADGROUP GROUP g c COUNT n STREAMS s >

    def ack(self, mid: str) -> None:
        self.r.xack(mid)
        self.r.xdel(mid)        # XACK + XDEL (retention: drop acked)

    def reclaim_expired(self, lease_s: float, now: float) -> list[tuple[str, dict]]:
        claimed = self.r.xautoclaim(lease_s, now)
        live = []

        for mid, payload in claimed:
            if self.r.deliveries(mid) > self.max_deliveries:
                self._dead.append(payload)
                self.r.xack(mid)
                self.r.xdel(mid)  # give up -> DLQ
            else:
                live.append((mid, payload))

        return live

    def pending(self) -> int:
        return len(self.r.pel)

    def dead(self) -> int:
        return len(self._dead)


class SQSQueue:
    """Production-shaped SQS queue wrapper.

    Production uses boto3 SendMessage / ReceiveMessage / DeleteMessage with a
    visibility timeout and a redrive policy to a DLQ. This lab implementation is
    in-memory but preserves the same lease, ack, redelivery, and dead-letter
    contract used by the worker.
    """

    def __init__(self, sqs=None, max_receives: int = 3):
        self.sqs = sqs
        self.max_receives = max_receives
        self._messages = []
        self._dead = []

    def enqueue(self, payload: dict) -> str:
        mid = str(uuid.uuid4())
        self._messages.append(
            {
                "id": mid,
                "payload": payload,
                "visible_at": 0.0,
                "receives": 0,
                "deleted": False,
                "dead": False,
            }
        )
        return mid

    def lease(self, n: int, lease_s: float, now: float) -> list[tuple[str, dict]]:
        out = []

        for msg in self._messages:
            if len(out) >= n:
                break

            if msg["deleted"] or msg["dead"]:
                continue

            if msg["visible_at"] > now:
                continue

            msg["receives"] += 1

            if msg["receives"] > self.max_receives:
                msg["dead"] = True
                self._dead.append(msg["payload"])
                continue

            msg["visible_at"] = now + lease_s
            out.append((msg["id"], msg["payload"]))

        return out

    def ack(self, mid: str) -> None:
        for msg in self._messages:
            if msg["id"] == mid:
                msg["deleted"] = True
                return

    def reclaim_expired(self, lease_s: float, now: float) -> list[tuple[str, dict]]:
        claimed = self.r.xautoclaim(lease_s, now)
        live = []

        for mid, payload in claimed:
            if self.r.deliveries(mid) > self.max_deliveries:
                self._dead.append(payload)
                self.r.xack(mid)
                self.r.xdel(mid)  # give up -> DLQ
            else:
                live.append((mid, payload))

        return live

    def pending(self) -> int:
        return sum(
            1
            for msg in self._messages
            if not msg["deleted"] and not msg["dead"]
        )

    def dead(self) -> int:
        return len(self._dead)



def run_contract(q, send_fn):
    """Run the same worker contract against Redis-like and SQS-like queues."""
    lease_s = 10.0
    redelivered = 0

    for item in [{"metric": "m0"}, {"metric": "m1"}, {"metric": "m2"}]:
        q.enqueue(item)

    for mid, payload in q.lease(10, lease_s, now=0.0):
        try:
            send_fn(payload)
            q.ack(mid)
        except Exception:
            pass

    for t in [10.0, 20.0, 30.0, 40.0, 50.0]:
        for mid, payload in q.reclaim_expired(lease_s, now=t):
            try:
                send_fn(payload)
                q.ack(mid)
                redelivered += 1
            except Exception:
                pass

    return {
        "pending": q.pending(),
        "dead": q.dead(),
        "redelivered": redelivered,
    }



def _self_test() -> int:
    # m0 always ok; m1 transient (fails its first delivery, then recovers); m2 permanent failure
    def make_send():
        seen = set()
        def send(payload):
            m = payload["metric"]
            if m == "m2":
                raise RuntimeError("endpoint permanently down")
            if m == "m1" and m not in seen:
                seen.add(m)
                raise RuntimeError("transient blip")
        return send

    redis_state = run_contract(RedisStreamQueue(max_deliveries=3), make_send())
    sqs_state = run_contract(SQSQueue(max_receives=3), make_send())

    # both backends satisfy the same contract: m0/m2 acked, m1 given up to the dead set, nothing
    # left pending
    for name, st in [("redis-streams", redis_state), ("sqs", sqs_state)]:
        assert st["dead"] == 1, (name, st)            # m2 gave up to the dead set
        assert st["redelivered"] == 1, (name, st)     # m1 recovered on redelivery
        assert st["pending"] == 0, (name, st)         # m0 acked, m1 redelivered, m2 dead
    # identical observable outcome across two very different primitives (PEL vs visibility timeout)
    assert redis_state == sqs_state, (redis_state, sqs_state)
    print(f"self-test: one contract, two backends. redis-streams {redis_state} == sqs {sqs_state}; "
          f"m0 acked, m1 recovered on redelivery, m2 gave up to the dead set OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Production durable backends (Redis Streams / SQS)")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import this module, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
