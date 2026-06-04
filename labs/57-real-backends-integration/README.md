# Lab 57: Real durable backends, integration-tested

> 🔴 Advanced · ⏱ ~75–95 min · 📚 Builds on Lab 54 · Module 26

## 🎯 Goal

[Lab 54](../54-production-durable-backends/) showed the durable-queue contract on hand-written fakes. This lab uses the *actual* client libraries — `redis-py` Streams and `boto3` SQS — so the lab code is the code you ship. The self-test exercises it through `fakeredis` and `moto` (which run the real commands in-process), and `test_integration.py` runs the same backends against a live Redis or LocalStack, skipping when neither is configured.

By the end you should be able to:

- Implement the lease/ack/reclaim/give-up contract with real `redis-py` consumer-group and `boto3` SQS calls.
- Use `fakeredis` / `moto` for fast, offline tests of real client code, and a live integration test for the gap they don't cover.
- Explain why the give-up path is server-side in SQS (redrive policy) and library-side in Redis (PEL delivery count).

## 📋 Prerequisites

- 🧪 [Lab 54](../54-production-durable-backends/) — the contract this makes real.
- **Assumed background:** `redis-py` Streams (`XREADGROUP`/`XACK`/`XAUTOCLAIM`), `boto3` SQS, and pytest fixtures/skips.

**Setup:** Python 3.11+ with `redis`, `fakeredis`, `boto3`, `moto[sqs]`, `pytest`. No server needed for the self-test.

## 🛠 Module

| Component | Notes |
|---|---|
| `backends.py` | `RedisStreamsBackend` (real redis-py), `SQSBackend` (real boto3), `run_contract` (`--self-test` via fakeredis/moto) |
| `test_integration.py` | live Redis (`REDIS_URL`) / LocalStack (`AWS_ENDPOINT_URL`) tests; skip otherwise |

## Running

```bash
python backends.py --self-test                                   # offline, via fakeredis + moto
REDIS_URL=redis://localhost:6379 pytest test_integration.py      # live Redis
AWS_ENDPOINT_URL=http://localhost:4566 pytest test_integration.py  # LocalStack
```

## Design choices and tradeoffs

- **Real client code, fast tests.** `fakeredis` and `moto` execute the actual `redis-py` / `boto3` commands, so the self-test covers the same code path a live server would — without standing up infrastructure in CI.
- **An integration test for the gap.** Mocks mirror documented semantics, not every server edge case (consumer-group lag, SQS in-flight limits, partial visibility). The skip-unless-live integration test is what closes that gap, so it ships with the lab rather than as an afterthought.
- **Give-up where it belongs.** SQS enforces `maxReceiveCount` → DLQ server-side via the redrive policy; Redis tracks delivery in the consumer group's Pending Entries List and the lab moves over-limit entries to a dead stream. Same contract, two enforcement points.

## Common gotchas

- **Deterministic vs real timing.** The self-test uses `min_idle_time=0` / `VisibilityTimeout=0` for immediate, deterministic reclaim; the live test uses a real timeout and waits for it to lapse. Don't ship a zero visibility timeout.
- **At-least-once → idempotent consumer.** Both backends can redeliver; dedupe on the alert key.
- **Clean up test resources.** The fixtures use unique stream/queue names per run and delete them on teardown so repeated runs don't collide.

## 🧮 Going deeper

- 🧪 [Lab 54](../54-production-durable-backends/) — the contract and the hand-written fakes.
- 📖 [From stand-ins to production](../../concepts/observability/from-stand-ins-to-production.md).

## Nightly SQS smoke test (`smoke_sqs.py`, Batch 84)

`smoke_sqs.py` is a one-second liveness check for the nightly CI job: create a queue, round-trip one message, tear it down. It is not the full contract test (`test_integration.py`) - it answers "is SQS reachable and behaving" so a broken LocalStack/AWS surfaces before the heavier suite. Offline it runs through moto (`--self-test`); in CI it runs against a LocalStack service container (`.github/workflows/nightly-smoke.yml`).

```bash
python smoke_sqs.py --self-test                              # offline (moto)
AWS_ENDPOINT_URL=http://localhost:4566 python smoke_sqs.py   # live LocalStack
```

## What comes next

- 🧪 [Lab 58: Measuring lost-in-the-middle](../58-measuring-lost-in-the-middle/) — a retrieval-science gap the path skipped: how context position changes answer accuracy, and how to measure it.
