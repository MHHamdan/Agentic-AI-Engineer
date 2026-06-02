# Lab 48 · Reference solution

The complete implementation of [Lab 48: Distributed backends and failure handling](../README.md).

## What this is

Lab 46's three stand-ins, made production-shaped, in the operating-the-loop toolkit:

- **`store.py`** — `RedisStore` whose `try_claim` is a single atomic Lua call: cooldown via a per-key value, rate limit via a global sliding-window sorted set. `release` on every backend (`InMemoryStore`, `FileLockStore`, `RedisStore`) frees a claimed slot. `make_store(spec)` selects the backend from `memory` / `file:/path` / `redis://…`. `FakeRedis` is an in-process double for tests and the notebook.
- **`notify.py`** — `DeadLetter` (append-only JSONL); `deliver` now releases the slot and records the payload when a send exhausts its retries, returning a `failed; dead-lettered and slot released` status. New `--store` and `--dead-letter` flags.
- **`canary.py`** — `normalize_corpus_text` (line endings, trailing whitespace, blank-line runs); `per_doc_fingerprint(normalize=True)` by default, so a reformat does not trigger review.

## Expected results

- `RedisStore(FakeRedis())`: a second worker is suppressed for the same incident; rate limit blocks the 6th send in a 5/window; `release` frees a slot so the next claim succeeds.
- A delivery that always fails returns `failed; dead-lettered…`, writes one DLQ entry, and frees the slot.
- `normalize_corpus_text(base) == normalize_corpus_text(reformat)` but `!= normalize_corpus_text(content_edit)`.

## Implementation choices

1. **Atomic Lua claim** for cross-region correctness; global window key for "max N total".
2. **Release-on-failure + DLQ** replaces Lab 46's keep-the-slot choice — no silent drops, no storm.
3. **Normalized (not semantic) hashing** — format-insensitive without an embedding model.
4. **One interface** (`StateStore`) so the backend is a config choice.

## What's out of scope

- A real Redis/SQL server (use `FakeRedis` here; swap a real client in production).
- Durable DLQ with redelivery/retention (file is a teaching stand-in).
- Semantic corpus hashing (normalized ≠ meaning-aware).

## Running

```bash
cd labs/41-operating-the-loop
python store.py --self-test
python notify.py --self-test
python canary.py --self-test
# real distributed backend + dead-letter:
python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 \
  --channel pagerduty --store redis://localhost:6379/0 \
  --dead-letter dead_letter.jsonl
```

## Next

[Lab 49: Graded gold](../../49-graded-gold/) — the evaluation-side twin.
