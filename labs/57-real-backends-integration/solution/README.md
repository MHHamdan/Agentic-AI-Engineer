# Lab 57 · Reference solution

The complete implementation of [Lab 57: Real durable backends, integration-tested](../README.md).

## What this is

- **`RedisStreamsBackend`** — real `redis-py`: `XGROUP_CREATE`, `XADD`, `XREADGROUP`, `XACK`+`XDEL`, `XAUTOCLAIM`, `XPENDING` for delivery count; over-limit entries → dead stream.
- **`SQSBackend`** — real `boto3`: `SendMessage` / `ReceiveMessage` (VisibilityTimeout) / `DeleteMessage`; give-up enforced by the queue's `RedrivePolicy` → DLQ.
- **`run_contract`** drives the m0/m1/m2 scenario against either.
- **`test_integration.py`** — same backends against live Redis / LocalStack; skip-unless-configured.

## Expected results

- `python backends.py --self-test`: both backends end at `{pending: 0, dead: 1, redelivered: 1}`, identical.
- `pytest test_integration.py`: 2 skipped with no servers; both pass against live infrastructure.

## Implementation choices

1. **Real client libraries** exercised by `fakeredis` / `moto`, not hand-written fakes.
2. **Server-side give-up for SQS** (redrive policy), PEL-driven for Redis — same contract.
3. **Live integration test** ships with the lab to cover what mocks don't.

## What's out of scope

- A running Redis / LocalStack in CI (tests skip without one).
- Stream `MAXLEN`, consumer-group lag alarms, SQS in-flight limits (production concerns, noted).

## Running

```bash
cd labs/57-real-backends-integration
python backends.py --self-test
pytest test_integration.py            # 2 skipped without REDIS_URL / AWS_ENDPOINT_URL
```
