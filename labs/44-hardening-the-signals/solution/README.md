# Lab 44 · Reference solution

The complete implementation of [Lab 44: Hardening the signals for real traffic](../README.md).

## What this is

The three Lab 42 signals, hardened in the operating-the-loop toolkit:

- **`notify.py`** (item 1) — `send_with_retry` (exponential backoff on `URLError`/`OSError`/`TimeoutError`), `rate_limited` (fixed-window count), `in_cooldown`/`record_send` (suppress a re-fire of the same `(metric, severity)` within a window), and `deliver` which composes cooldown → rate-limit → retry around `post`. State persists across runs via `--state-file`.
- **`record_baseline.py`** (item 2) — `measure_reference_confidences()` now reads `reference_sample.jsonl` (held-out), with a `--reference` override and a loud warning if it falls back to the trainset. The held-out band is lower and realistic.
- **`canary.py` + `canary_queries.jsonl`** (item 3) — 16 canaries tagged with a `failure_mode` and `corpus_refs`; `corpus_fingerprint` hashes the corpus, `review_status` lists the corpus-dependent canaries to revalidate when the fingerprint changes (`--review`).

Each script keeps its `--self-test`. The three Lab 42 workflows are updated in place.

## Implementation choices

1. **Dedup on `(metric, severity)`** — a value change at the same severity is the same incident.
2. **Compose cooldown → rate-limit → retry in `deliver`** — control-flow suppression never raises; only a true post failure after retries propagates.
3. **Held-out reference** — the same leakage discipline as model evaluation; measuring on the trainset flatters the band.
4. **Whole-corpus fingerprint** — cheap and complete; `corpus_refs` scopes *which* canaries to review.
5. **No-op default preserved** — without an endpoint, `deliver` records the send (so cooldown still applies) and sends nothing.

## What's out of scope

- A shared/distributed rate-limiter and cooldown store (single-process here).
- A larger, real-traffic-collected reference sample.
- A per-document corpus map for finer canary review scoping.

## Running

```bash
cd labs/41-operating-the-loop      # the hardened toolkit lives here
python notify.py --self-test
python record_baseline.py --self-test
python canary.py --self-test
python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 --channel pagerduty --state-file alert_state.json
python canary.py --review
jupyter notebook ../44-hardening-the-signals/solution/lab.ipynb
```

## Next

[Lab 45: Anchoring the consensus](../../45-anchoring-the-consensus/) — the evaluation-side twin.
