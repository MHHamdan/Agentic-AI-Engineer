#!/usr/bin/env python3
"""Real durable backends, integration-tested (Lab 57).

Lab 54 implemented the durable-queue contract against hand-written fakes to show the shape. This
lab uses the *actual* client libraries - `redis-py` Streams and `boto3` SQS - so the lab code is
the code you would ship. The self-test exercises that code against `fakeredis` and `moto`, which
run the real client commands in-process and mirror server semantics; `test_integration.py` runs
the same backends against a live Redis (`REDIS_URL`) or LocalStack / AWS (`AWS_ENDPOINT_URL`) and
is skipped when neither is configured.

The contract is unchanged from Lab 54: enqueue / lease / ack / reclaim_expired / pending / dead.
What changes is that `RedisStreamsBackend` issues real `XADD` / `XREADGROUP` / `XACK` / `XAUTOCLAIM`
and `SQSBackend` issues real `SendMessage` / `ReceiveMessage` / `DeleteMessage` with a server-side
redrive policy - so the give-up path is enforced by SQS itself, not by lab code.

Usage:
    python backends.py --self-test
    REDIS_URL=redis://localhost:6379 pytest test_integration.py
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys


# ============================ Redis Streams backend (real redis-py) ============================
class RedisStreamsBackend:
    """The durable-queue contract on a Redis Streams consumer group. `client` is any redis-py
    client (a live `redis.Redis`, or `fakeredis` in the self-test)."""
    def __init__(self, client, stream="dlq:metrics", group="workers", dead_stream="dlq:dead",
                 consumer="c1", max_deliveries=3):
        self.r = client
        self.stream = stream
        self.group = group
        self.dead_stream = dead_stream
        self.consumer = consumer
        self.max_deliveries = max_deliveries
        with contextlib.suppress(Exception):
            self.r.xgroup_create(stream, group, id="0", mkstream=True)

    def enqueue(self, payload: dict) -> str:
        return self.r.xadd(self.stream, payload)

    def lease(self, max_n: int):
        resp = self.r.xreadgroup(self.group, self.consumer, {self.stream: ">"}, count=max_n)
        return [(mid, fields) for _, entries in (resp or []) for mid, fields in entries]

    def ack(self, mid) -> None:
        self.r.xack(self.stream, self.group, mid)
        self.r.xdel(self.stream, mid)

    def _deliveries(self, mid) -> int:
        info = self.r.xpending_range(self.stream, self.group, min="-", max="+", count=1000)
        return next((x["times_delivered"] for x in info if x["message_id"] == mid), 1)

    def reclaim_expired(self, min_idle_ms: int = 0):
        # XAUTOCLAIM reclaims entries idle past min_idle (0 = all pending, for a deterministic test;
        # in production set it to the lease duration). Entries past the delivery cap give up to the
        # dead stream.
        cursor, entries, _ = self.r.xautoclaim(self.stream, self.group, self.consumer,
                                               min_idle_time=min_idle_ms, start_id="0")
        live = []
        for mid, fields in entries:
            if self._deliveries(mid) > self.max_deliveries:
                self.r.xadd(self.dead_stream, fields)
                self.ack(mid)  # give up -> dead stream
            else:
                live.append((mid, fields))
        return live

    def pending(self) -> int:
        return self.r.xpending(self.stream, self.group)["pending"]

    def dead(self) -> int:
        return self.r.xlen(self.dead_stream)


# ============================ SQS backend (real boto3) ============================
class SQSBackend:
    """The same contract on SQS. `sqs` is a boto3 SQS client (live, LocalStack, or moto). The
    give-up path is the queue's own redrive policy to a dead-letter queue - SQS moves a message
    past `maxReceiveCount`, no lab code required."""
    def __init__(self, sqs, queue_url, dlq_url, lease_s=0):
        self.sqs = sqs
        self.q = queue_url
        self.dlq = dlq_url
        self.lease_s = lease_s

    @staticmethod
    def create(sqs, name="metrics", max_receives=3, visibility_timeout=0):
        dlq = sqs.create_queue(QueueName=f"{name}-dead")["QueueUrl"]
        arn = sqs.get_queue_attributes(QueueUrl=dlq, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
        q = sqs.create_queue(QueueName=name, Attributes={
            "VisibilityTimeout": str(visibility_timeout),
            "RedrivePolicy": json.dumps({"deadLetterTargetArn": arn, "maxReceiveCount": str(max_receives)}),
        })["QueueUrl"]
        return SQSBackend(sqs, q, dlq, lease_s=visibility_timeout)

    def enqueue(self, payload: dict) -> str:
        return self.sqs.send_message(QueueUrl=self.q, MessageBody=json.dumps(payload))["MessageId"]

    def lease(self, max_n: int):
        resp = self.sqs.receive_message(QueueUrl=self.q, MaxNumberOfMessages=min(max_n, 10),
                                       VisibilityTimeout=self.lease_s)
        return [(m["ReceiptHandle"], json.loads(m["Body"])) for m in resp.get("Messages", [])]

    def ack(self, receipt) -> None:
        self.sqs.delete_message(QueueUrl=self.q, ReceiptHandle=receipt)

    def reclaim_expired(self, min_idle_ms: int = 0):
        # SQS makes a message visible again when its visibility timeout lapses, and redrives it to
        # the DLQ past maxReceiveCount on its own. Reclaiming is just receiving again.
        return self.lease(10)

    def _count(self, url, attr) -> int:
        return int(self.sqs.get_queue_attributes(QueueUrl=url, AttributeNames=[attr])["Attributes"][attr])

    def pending(self) -> int:
        return self._count(self.q, "ApproximateNumberOfMessages")

    def dead(self) -> int:
        return self._count(self.dlq, "ApproximateNumberOfMessages")


# ============================ shared contract driver ============================
def run_contract(backend, send_fn, rounds: int = 6) -> dict:
    """Drive any backend through the Lab 50 redelivery scenario: m0 succeeds, m1 fails once then
    recovers on redelivery, m2 fails permanently and gives up to the dead set."""
    for i in range(3):
        backend.enqueue({"metric": f"m{i}"})

    def drain(items, count_redeliver):
        n = 0
        for handle, payload in items:
            try:
                send_fn(payload)
                backend.ack(handle)
                if count_redeliver:
                    n += 1
            except Exception:
                pass  # leave unacked; it will be reclaimed
        return n

    drain(backend.lease(10), count_redeliver=False)   # first delivery
    redelivered = 0
    for _ in range(rounds):                            # reclaim + retry
        redelivered += drain(backend.reclaim_expired(), count_redeliver=True)
    return {"pending": backend.pending(), "dead": backend.dead(), "redelivered": redelivered}


def _make_send():
    seen = set()
    def send(payload):
        m = payload["metric"]
        if m == "m2":
            raise RuntimeError("endpoint permanently down")
        if m == "m1" and m not in seen:
            seen.add(m)
            raise RuntimeError("transient blip")
    return send


def _self_test() -> int:
    import boto3
    import fakeredis
    from moto import mock_aws

    redis_state = run_contract(RedisStreamsBackend(fakeredis.FakeStrictRedis(decode_responses=True)),
                               _make_send())
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        sqs_state = run_contract(SQSBackend.create(sqs), _make_send())

    for name, st in [("redis-streams", redis_state), ("sqs", sqs_state)]:
        assert st["dead"] == 1, (name, st)         # m2 gave up to the dead set
        assert st["redelivered"] == 1, (name, st)  # m1 recovered on redelivery
        assert st["pending"] == 0, (name, st)
    assert redis_state == sqs_state, (redis_state, sqs_state)
    print(f"self-test: real redis-py (via fakeredis) {redis_state} == real boto3 SQS (via moto) "
          f"{sqs_state}; m0 acked, m1 recovered on redelivery, m2 gave up to the dead set OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Real durable backends (redis-py Streams / boto3 SQS)")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("run --self-test, or point test_integration.py at a live Redis / LocalStack")
    return 0


if __name__ == "__main__":
    sys.exit(main())
