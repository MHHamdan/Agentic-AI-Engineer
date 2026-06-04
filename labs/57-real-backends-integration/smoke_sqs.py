#!/usr/bin/env python3
"""LocalStack-backed SQS smoke test (Lab 57, Batch 84).

A fast liveness check for the nightly CI job: create a queue, round-trip one message, tear it down.
It is not the full contract test (that is `test_integration.py`) - it answers "is SQS reachable and
behaving" in a second, so a broken LocalStack/AWS surfaces before the heavier suite runs.

Against a live endpoint it uses AWS_ENDPOINT_URL; with `--self-test` it runs offline through moto.

Usage:
    AWS_ENDPOINT_URL=http://localhost:4566 python smoke_sqs.py
    python smoke_sqs.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid


def smoke(sqs) -> dict:
    name = f"smoke-{uuid.uuid4().hex[:8]}"
    url = sqs.create_queue(QueueName=name)["QueueUrl"]
    try:
        body = json.dumps({"ping": name})
        sqs.send_message(QueueUrl=url, MessageBody=body)
        msgs = sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=1, WaitTimeSeconds=1).get("Messages", [])
        assert len(msgs) == 1 and msgs[0]["Body"] == body, "round-trip mismatch"
        sqs.delete_message(QueueUrl=url, ReceiptHandle=msgs[0]["ReceiptHandle"])
        return {"queue": name, "round_trip": "ok"}
    finally:
        sqs.delete_queue(QueueUrl=url)


def _live_client():
    import boto3
    endpoint = os.environ.get("AWS_ENDPOINT_URL")
    return boto3.client("sqs", endpoint_url=endpoint, region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
                        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
                        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"))


def _self_test() -> int:
    import boto3
    from moto import mock_aws
    with mock_aws():
        result = smoke(boto3.client("sqs", region_name="us-east-1"))
    assert result["round_trip"] == "ok", result
    print(f"self-test: SQS smoke via moto - created {result['queue']}, sent/received/deleted one "
          f"message, queue torn down OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="SQS smoke test")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    if not os.environ.get("AWS_ENDPOINT_URL"):
        print("set AWS_ENDPOINT_URL (LocalStack/AWS) or run --self-test")
        return 0
    print("SQS smoke:", smoke(_live_client()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
