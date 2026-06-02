# Lab 48: Distributed backends and failure handling

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 46

## 🎯 Goal

[Lab 46](../46-scaling-the-signals/) scaled the three signals but left three stand-ins that only hold under lab conditions: the `FileLockStore` needs a shared filesystem (serverless and multi-region workers don't have one), the claim is taken *before* delivery so a failed page silently keeps its cooldown slot, and the per-document corpus map hashes raw bytes so a cosmetic reformat looks like a content change. This lab makes each one production-shaped.

By the end you should be able to:

- Implement the atomic claim on a real distributed store (Redis) behind the same `StateStore` interface, and select the backend by config.
- Free a claimed slot when delivery fails after retries, and capture the failed page in a dead-letter queue instead of dropping it.
- Hash normalized content so corpus change detection fires on content, not whitespace.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 46: Scaling the signals across workers and traffic](../46-scaling-the-signals/) — this hardens its `store.py`, `notify.py`, and `canary.py`.

**Assumed background:** Redis basics (`SET NX PX`, sorted sets, `EVAL`/Lua atomicity), append-only queues / dead-lettering, and content vs byte equality.

**Setup:** Python 3.11+ with the repo environment. Logic runs via `--self-test` against a `FakeRedis` test double — no Redis server, no network, no key needed. For real use, `pip install redis` and pass `--store redis://...`.

## 🛠 Tools and versions

| Component | Notes |
|---|---|
| `store.py` | `RedisStore` (atomic Lua claim), `release`, `make_store`, `FakeRedis` (tests/demo) |
| `notify.py` | `DeadLetter`; `deliver` release-on-failure; `--store` / `--dead-letter` |
| `canary.py` | `normalize_corpus_text`; `per_doc_fingerprint(normalize=True)` |
| `redis` (prod only) | any recent `redis-py`; not needed for `--self-test` |

## How the three requested items map here

1. **Real distributed store (Redis/DB)** → `RedisStore` + `make_store('redis://...')`; the claim is one atomic Lua round-trip (cooldown + global sliding window). A SQL backend is the same shape (`SELECT … FOR UPDATE` then conditional insert in one transaction).
2. **Release-on-failure / dead-letter** → `StateStore.release` on every backend + `notify.DeadLetter`; `deliver` frees the slot and records the payload when retries are exhausted. The nightly workflow passes `--dead-letter` and caches the queue.
3. **Normalized corpus hashing** → `canary.normalize_corpus_text`; `per_doc_fingerprint` normalizes by default, so a reformat does not trigger review.

## Steps

1. **Setup** (0).
2. **Distributed store** (1).
3. **Release-on-failure + dead-letter** (2).
4. **Normalized hashing** (3).
5. **Cadence** (4).

## Design choices and tradeoffs

- **One atomic Lua claim, not several commands.** Doing cooldown + window check + record in separate round-trips reopens the race between them. A single `EVAL` runs server-side, single-threaded — atomic across every worker regardless of region. The cooldown is a per-key value; the rate limit is a global sliding-window sorted set, so "max N alerts per window" counts across all alert keys.
- **Release-on-failure changes Lab 46's deliberate choice.** Lab 46 kept the slot on failure to avoid retry-storms. With a dead-letter queue you can do better: free the slot so the *next scheduled* run retries (not an immediate storm — `send_with_retry` already backed off), and record the payload so on-call sees the miss. Net: no silent drops, no storm.
- **Normalized, not semantic.** Stripping whitespace/CRLF/blank runs catches the common "no-op reformat" without an embedding model. It is deliberately *not* meaning-aware — a prose reflow that rewraps lines still changes the hash. Semantic hashing is a separate, noisier tool.
- **Same interface throughout.** `InMemoryStore`, `FileLockStore`, `RedisStore` all satisfy `StateStore`, so the backend is a config choice (`make_store`) and the call sites never change.

## Common gotchas

- **`FakeRedis` is for tests/demo only.** It mirrors Redis's single-threaded atomicity in-process; production needs a real client and a real server. The Lua is identical.
- **The dead-letter queue here is a file.** Append-only JSONL is enough to teach the pattern; a real DLQ is a durable queue with redelivery, inspection, and retention.
- **Releasing a slot is not free retrying.** Release lets the *next* run try; it does not re-send immediately. If you need stronger delivery guarantees, add redelivery off the DLQ.
- **Normalization can mask intent.** If you ever care about exact bytes (a signed manifest, a checksum file), use `normalize=False`.

## 🧮 Going deeper

- 🧪 [Lab 46](../46-scaling-the-signals/) — the stand-ins this replaces.
- 🧪 [Lab 41](../41-operating-the-loop/) — the loop the toolkit serves.
- 📄 Redis docs — `SET … NX PX`, sorted sets, `EVAL`/Lua atomicity.

## What comes next

- 🧪 [Lab 49: Graded gold](../49-graded-gold/) — the evaluation-side twin: move the rubric from binary to ordinal, adjudicate with a real protocol, and re-derive the Lab 45 annotator weights against gold.
