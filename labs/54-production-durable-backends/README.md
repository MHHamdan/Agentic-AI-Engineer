# Lab 54: Production durable backends

> 🔴 Advanced · ⏱ ~80–100 min · 📚 Builds on Lab 50 · Module 25

## 🎯 Goal

[Lab 50](../50-closing-the-failure-loop/) built the dead-letter queue as a file with a lock and noted the real thing is Redis Streams or SQS, *same lease/ack/retention contract*. This lab makes that literal: one contract, two production backends, and the Lab 50 redelivery worker driving either unchanged.

By the end you should be able to:

- Map the lease/ack/reclaim/give-up contract onto Redis Streams (consumer group + PEL) and SQS (visibility timeout + redrive).
- See the *same* observable behavior emerge from two systems with nothing in common at the primitive level.
- Swap a real client for the fake without touching the worker.

## 📋 Prerequisites

- 🧪 [Lab 50: Closing the failure loop](../50-closing-the-failure-loop/) — the contract this implements.
- **Assumed background:** Redis Streams consumer groups (XREADGROUP/XACK/XAUTOCLAIM) and SQS visibility timeout / redrive policy at a conceptual level.

**Setup:** Python 3.11+; no server needed. `backends.py` verifies against in-process fakes; production uses `redis-py` or `boto3`.

## 🛠 Module

| Component | Notes |
|---|---|
| `backends.py` | `RedisStreamQueue`, `SQSQueue`, `run_contract`, `FakeRedisStreams`, `FakeSQS` (`--self-test`) |

## The mapping

| Contract op | Redis Streams | SQS |
|---|---|---|
| enqueue | `XADD` | `SendMessage` |
| lease | `XREADGROUP` → PEL | `ReceiveMessage` (VisibilityTimeout) |
| ack | `XACK` + `XDEL` | `DeleteMessage` |
| reclaim expired | `XAUTOCLAIM` (min-idle) | timeout lapses → visible again |
| give up | PEL deliveries > max → DLQ | ReceiveCount > max → redrive to DLQ |

## Design choices and tradeoffs

- **Code to the contract, not the backend.** The redelivery worker calls `enqueue`/`lease`/`ack`/`reclaim_expired` and never learns which system it's on, so you can start on Redis and move to SQS (or back) without touching the worker.
- **Lease semantics differ in mechanism, not in contract.** Redis tracks delivery in the consumer group's Pending Entries List; SQS makes a message invisible for the visibility timeout. Both give at-least-once delivery with a reclaim path — which is why the consumer must be idempotent (an ack can race a reclaim).
- **Give-up is built in.** PEL delivery count (Redis) and ReceiveCount + redrive policy (SQS) both move a permanently failing message to a dead set instead of looping forever.

## Common gotchas

- **At-least-once means duplicates.** Both backends can redeliver a message whose ack was lost. Make the send idempotent (dedupe on the alert key).
- **Configure the give-up path explicitly.** A Redis stream needs a consumer group created and a DLQ stream; SQS needs a redrive policy with a DLQ ARN and `maxReceiveCount`. Without it, a poison message loops.
- **Retention is separate from ack.** Acking drops the message; a time-based retention floor (stream `MAXLEN`, SQS retention period) bounds the rest.

## 🧮 Going deeper

- 🧪 [Lab 50](../50-closing-the-failure-loop/) — the file-backed contract this productionizes.
- 📖 [From stand-ins to production](../../concepts/observability/from-stand-ins-to-production.md) — where this sits in the arc.

## What comes next

- 🧪 [Lab 55: Calibrated detection and judgment](../55-calibrated-detection-judgment/) — real embeddings and isotonic calibration replacing the bag-of-words and additive-shift stand-ins.
