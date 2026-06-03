"""Integration tests for the real durable backends (Lab 57).

These run the SAME backends as the self-test against live infrastructure:

    REDIS_URL=redis://localhost:6379 pytest test_integration.py -v
    AWS_ENDPOINT_URL=http://localhost:4566 pytest test_integration.py -v   # LocalStack

Each test skips cleanly when its service is not configured, so the suite is safe to run anywhere.
The point is that nothing in the backend code changes between the in-process self-test and a live
server - only the client the test injects.
"""
import json
import os
import time
import uuid

import pytest
from backends import RedisStreamsBackend, SQSBackend, _make_send, run_contract


@pytest.fixture
def redis_backend():
    url = os.environ.get("REDIS_URL")
    if not url:
        pytest.skip("set REDIS_URL to run the live Redis integration test")
    import redis
    client = redis.Redis.from_url(url, decode_responses=True)
    # unique stream/group per run so repeated runs don't collide
    tag = uuid.uuid4().hex[:8]
    backend = RedisStreamsBackend(client, stream=f"dlq:test:{tag}", group="workers",
                                  dead_stream=f"dlq:test:{tag}:dead")
    yield backend
    client.delete(backend.stream, backend.dead_stream)


@pytest.fixture
def sqs_backend():
    endpoint = os.environ.get("AWS_ENDPOINT_URL")
    if not endpoint:
        pytest.skip("set AWS_ENDPOINT_URL (e.g. LocalStack) to run the live SQS integration test")
    import boto3
    sqs = boto3.client("sqs", endpoint_url=endpoint, region_name="us-east-1",
                       aws_access_key_id="test", aws_secret_access_key="test")
    # a live visibility timeout cannot be 0, so use a short one and let it lapse between reclaims
    backend = SQSBackend.create(sqs, name=f"metrics-{uuid.uuid4().hex[:8]}", visibility_timeout=1)
    yield backend
    sqs.delete_queue(QueueUrl=backend.q)
    sqs.delete_queue(QueueUrl=backend.dlq)


def test_redis_contract(redis_backend):
    state = run_contract(redis_backend, _make_send())
    assert state == {"pending": 0, "dead": 1, "redelivered": 1}


def test_sqs_contract(sqs_backend):
    # with a real visibility timeout we wait for it to lapse before each reclaim round
    def run_with_waits(backend, send):
        for i in range(3):
            backend.enqueue({"metric": f"m{i}"})
        for handle, payload in backend.lease(10):
            try:
                send(payload)
                backend.ack(handle)
            except Exception:
                pass
        redelivered = 0
        for _ in range(8):
            time.sleep(backend.lease_s + 0.5)        # let the visibility timeout lapse
            for handle, payload in backend.reclaim_expired():
                try:
                    send(payload)
                    backend.ack(handle)
                    if payload["metric"] == "m1":
                        redelivered += 1
                except Exception:
                    pass
        return {"pending": backend.pending(), "dead": backend.dead(), "redelivered": redelivered}

    state = run_with_waits(sqs_backend, _make_send())
    assert state["dead"] == 1 and state["redelivered"] == 1
