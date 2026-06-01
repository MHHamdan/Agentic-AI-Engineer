# Lab 46 · Reference solution

The complete implementation of [Lab 46: Scaling the signals across workers and traffic](../README.md).

## What this is

The three Lab 44 signals, scaled across workers and real traffic, in the operating-the-loop toolkit:

- **`store.py`** (item 1) — a `StateStore` with an atomic `try_claim(key, now, cooldown, max, window)` that checks cooldown + rate limit AND records under one lock. `InMemoryStore` (single process) and `FileLockStore` (shared filesystem, `fcntl.flock`; stands in for Redis/DB). `naive_claim` is kept to demonstrate the check-then-record race. `notify.deliver` accepts a store (shared) or a dict (legacy Lab 44 behavior).
- **`build_reference.py` + `captured_traffic.jsonl`** (item 2) — `clean_candidates` (drop garbage, near-dupes, trainset-leak), `stratify` (balance routes), `band_ci` (the CI narrows as `n` grows). The distilled `reference_sample.jsonl` replaces the curated 16.
- **`canary.py`** (item 3) — `per_doc_fingerprint`, `changed_docs`, `review_status_per_doc`; `--review` now diffs a per-document map (`canary_corpus.map.json`) and flags only canaries that depend on a changed doc.

Each script keeps its `--self-test`. The three workflows are updated in place.

## Expected results

- `naive_claim` under contention: 2 workers win (the bug). `FileLockStore.try_claim`: 1 winner (the fix).
- captured 43 → cleaned 31 → stratified reference; band CI at n=80 is roughly half the width of n=16.
- One changed doc: per-document review flags ~5 canaries vs 12 for the whole-corpus review.

## Implementation choices

1. **Atomic claim under a lock** closes the race; `FileLockStore` is the portable stand-in for a real shared store.
2. **Claim before delivery** (a failed send still cools down) prevents retry-storms; release-on-failure is a noted refinement.
3. **Backward-compatible `deliver`** (dict or store) so Lab 44 keeps working.
4. **Stratified + verified reference**, not raw traffic; the clean filter only proposes.
5. **Per-document map** localizes change to cut revalidation noise.

## What's out of scope

- A real distributed store (Redis/DB) — `FileLockStore` needs a shared filesystem.
- Release-on-failure / dead-letter for the cooldown slot.
- Semantic (normalized) corpus hashing — content hashes flag no-op reformats.

## Running

```bash
cd labs/41-operating-the-loop      # the toolkit lives here
python store.py --self-test
python build_reference.py --self-test && python build_reference.py
python canary.py --self-test
python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 --channel pagerduty --shared-store alert_store.json
jupyter notebook ../46-scaling-the-signals/solution/lab.ipynb
```

## Next

[Lab 47: Trustworthy gold](../../47-trustworthy-gold/) — the evaluation-side twin.
