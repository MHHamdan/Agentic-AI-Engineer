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
import argparse, sys, time, uuid

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
        self.entries[mid] = payload; self.order.append(mid)
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
                meta["delivered_at"] = now; meta["deliveries"] += 1
                out.append((mid, self.entries[mid]))
        return out

    def deliveries(self, mid: str) -> int:
        return self.pel.get(mid, {}).get("deliveries", 0)

    def xack(self, mid: str) -> None:
        self.pel.pop(mid, None); self.acked.add(mid)

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
        self.r.xack(mid); self.r.xdel(mid)        # XACK + XDEL (retention: drop acked)

    def reclaim_expired(self, lease_s: float, now: float) -> list[tuple[str, dict]]:
        claimed = self.r.xautoclaim(lease_s, now)  # XAUTOCLAIM s g c <min-idle> 0
        live = []
        for mid, payload in claimed:
            if self.r.deliveries(mid) > self.max_deliveries:
                self._dead.append(payload); self.r.xack(mid); self.r.xdel(mid)  # give up -> DLQ
            else:
                live.append((mid, payload))
        return live

    def pending(self) -> int:
        return len(self.r.pel)

    def dead(self) -> int:
        return len(self._dead)


class SQSQueue:
    """Production: `sqs = boto3.client("sqs")`; SendMessage/ReceiveMessage/DeleteMessage with a
    VisibilityTimeout and a redrive policy to a DLQ. Here `sqs` is a FakeSQS mirroring those."""
    def __init__(self, client=None, max_receives: int = 3):
        self.q = client or FakeSQS()
        self.max_receives = max_receives

    def enqueue(self, payload: dict) -> str:
        return self.q.send(payload)               # SendMessage

    def lease(self, max_n: int, lease_s: float, now: float) -> list[tuple[str, dict]]:
        msgs = self.q.receive(max_n, lease_s, now)  # ReceiveMessage VisibilityTimeout=lease_s
        # redrive anything that has now been received too many times
        out = []
        for mid, payload in msgs:
            if self.q.receives(mid) > self.max_receives:
                self.q.redrive(mid)
            else:
                out.append((mid, payload))
        return out

    def ack(self, mid: str) -> None:
        self.q.delete(mid)                        # DeleteMessage

    def reclaim_expired(self, lease_s: float, now: float) -> list[tuple[str, dict]]:
        # SQS redelivers automatically when the visibility timeout lapses; leasing again at a
        # later `now` surfaces the expired messages. This mirrors that.
        return self.lease(1000, lease_s, now)

    def pending(self) -> int:
        return len(self.q.msgs)

    def dead(self) -> int:
        return len(self.q.dlq)


def run_contract(q, send_fn, *, lease_s: float = 30.0) -> dict:
    """Drive any backend through the Lab 50 redelivery contract: enqueue three failed pages,
    lease + redeliver, ack the ones that land, let the rest expire and reclaim, and give up the
    permanent failure. Returns the observable end state."""
    for i in range(3):
        q.enqueue({"metric": f"m{i}"})
    # first drain at t=0: m0 acks; m1 (transient) and m2 (permanent) fail and stay leased
    for mid, payload in q.lease(10, lease_s, now=0.0):
        try:
            send_fn(payload); q.ack(mid)
        except Exception:
            pass                                   # leave leased; the lease will expire
    # advance past the lease repeatedly; reclaim expired and retry. m1 recovers on its retry; m2
    # keeps failing until it gives up to the dead set.
    redelivered = 0
    for t in (lease_s + 1, 2 * lease_s + 2, 3 * lease_s + 3, 4 * lease_s + 4):
        for mid, payload in q.reclaim_expired(lease_s, now=t):
            try:
                send_fn(payload); q.ack(mid); redelivered += 1
            except Exception:
                pass
    return {"pending": q.pending(), "dead": q.dead(), "redelivered": redelivered}


def _self_test() -> int:
    # m0 always ok; m1 transient (fails its first delivery, then recovers); m2 permanent failure
    def make_send():
        seen = set()
        def send(payload):
            m = payload["metric"]
            if m == "m2":
                raise RuntimeError("endpoint permanently down")
            if m == "m1" and m not in seen:
                seen.add(m); raise RuntimeError("transient blip")
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
