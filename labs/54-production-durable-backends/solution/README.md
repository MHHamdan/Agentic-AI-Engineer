# Lab 54 · Reference solution

The complete implementation of [Lab 54: Production durable backends](../README.md).

## What this is

One contract, two production backends:

- **`RedisStreamQueue`** — `XADD` / `XREADGROUP` (→ Pending Entries List) / `XACK` + `XDEL` / `XAUTOCLAIM`; PEL delivery count drives give-up to a dead set.
- **`SQSQueue`** — `SendMessage` / `ReceiveMessage` (VisibilityTimeout) / `DeleteMessage`; ReceiveCount + redrive policy moves a poison message to a DLQ.
- **`run_contract`** drives the Lab 50 redelivery scenario against either.

## Expected results

- Scenario: m0 succeeds, m1 fails once then recovers, m2 fails permanently.
- Both backends end at `{pending: 0, dead: 1, redelivered: 1}` — identical.

## Implementation choices

1. **Code to the contract**, not the backend — the worker is backend-agnostic.
2. **At-least-once + reclaim** — idempotent consumer required.
3. **Give-up built in** — PEL count / ReceiveCount → dead set.

## What's out of scope

- Real client wiring (guarded `redis` / `boto3` imports; verified on fakes).
- Stream `MAXLEN` / consumer-group creation, SQS redrive ARNs, time-based retention floors.
- Exactly-once (neither system offers it; dedupe on the alert key).

## Running

```bash
cd labs/54-production-durable-backends
python backends.py --self-test
```

## Next

[Lab 55: Calibrated detection and judgment](../../55-calibrated-detection-judgment/).
