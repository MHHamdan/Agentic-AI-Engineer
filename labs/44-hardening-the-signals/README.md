# Lab 44: Hardening the signals for real traffic

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 42

## 🎯 Goal

[Lab 42](../42-hardening-operations/) built three signals — a notifier, a drift baseline, a canary set. They work on a quiet repo; this lab hardens them for the conditions live traffic actually creates. The notifier gains retries, rate limiting, and dedup/cooldown so it neither drops a page on a transient blip nor floods on-call. The drift baseline moves off the circular prototype set onto a held-out clean reference. The canary suite grows to cover named failure modes and learns to flag itself for review when the corpus changes.

By the end you should be able to:

- Make an alert path resilient: retry transient failures, rate-limit a burst, suppress a re-fire within a cooldown.
- Explain why a baseline measured on training data is optimistic, and replace it with a held-out reference.
- Grow a canary suite around the failure modes you've actually seen, and revalidate it on corpus change.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 42: Hardening the operations loop](../42-hardening-operations/) — this lab hardens its `notify.py`, `record_baseline.py`, and `canary.py`/`canary_queries.jsonl`, and adds `reference_sample.jsonl`.

**Assumed background:** retry/backoff and rate-limiting basics, the idea of train/test leakage (why measuring on training data flatters you), and GitHub Actions caching.

**Setup:** Python 3.11+ with the repo environment. Logic runs via `--self-test` (no LLM key, no webhook). Live baseline/canary runs need `sentence-transformers`.

## 🛠 Tools and versions

| Component | Notes |
|---|---|
| `notify.py` | `send_with_retry`, `rate_limited`, `in_cooldown`/`record_send`, `deliver` (`--self-test`, `--state-file`) |
| `record_baseline.py` | measures on `reference_sample.jsonl` (held-out); `--reference` override |
| `canary.py` + `canary_queries.jsonl` | failure-mode tags; `corpus_fingerprint`/`review_status` (`--review`) |
| GitHub Actions | the three Lab 42 workflows, updated in place |

## What you'll build / what ships (in the operating-the-loop toolkit)

- `notify.py` — retry-with-backoff, fixed-window rate limit, dedup/cooldown (state persisted across runs via `--state-file`).
- `record_baseline.py` — measures the band on a held-out clean reference; falls back to the trainset with a loud warning.
- `reference_sample.jsonl` — 16 held-out clean queries (realistic phrasings, none verbatim in the trainset).
- `canary.py` + grown `canary_queries.jsonl` — 16 failure-mode-tagged canaries; corpus-fingerprint review.

## How the three requested items map here

1. **Retries + rate limiting + dedup/cooldown** → `notify.py` (`send_with_retry`, `rate_limited`, `in_cooldown`, `deliver`); the nightly workflow persists state via `actions/cache` + `--state-file` (Step 1).
2. **Held-out reference baseline** → `record_baseline.py` + `reference_sample.jsonl` (Step 2).
3. **Grow the canary suite + review on corpus change** → `canary.py` failure-mode tags + `corpus_fingerprint`/`review_status` + the drift workflow's review step (Step 3).

## Steps

1. **Setup** (0).
2. **Notifier resilience** (1): retry, rate limit, cooldown.
3. **Held-out baseline** (2): stop measuring against training data.
4. **Failure-mode canaries + corpus review** (3).
5. **Hardened cadence** (4).

## Design choices and tradeoffs

- **Dedup key = (metric, severity).** A value change at the same severity is the same incident, not a new page. Keying on the raw value would re-fire on every nightly run.
- **Fixed-window rate limit, not a token bucket.** Simpler to reason about for a per-run CI job; a high-throughput service would want a token bucket and a shared store.
- **Held-out reference, not the trainset.** A classifier is over-confident on its training data, so a prototype-set band sits too high and the drift check under-fires. The held-out sample is the same leakage discipline you already apply to model evaluation.
- **Corpus fingerprint gates canary review.** A content hash is cheap and catches any corpus change; `corpus_refs` on each canary tells you which ones to revalidate (the corpus-free parametric/refusal canaries are unaffected).

## Common gotchas

- **Cooldown state needs to persist.** A local `alert_state.json` resets every CI run unless you cache it (or use an external store) — without persistence, cooldown only works within a run. The nightly workflow caches it; note the cache-key immutability caveat.
- **Rate limit hides real incidents.** If you cap too low, a genuine multi-metric regression gets one alert and the rest are swallowed. Cap for your on-call appetite, and let `page` bypass softer limits if you split tiers.
- **Held-out reference can rot.** It must stay "clean" — revisit it when the corpus or the routes change, or it stops representing healthy traffic.
- **Canary fingerprint is coarse.** A whole-corpus hash flags *all* corpus-dependent canaries on any change; a per-doc map would scope the review more tightly.

## 🧮 Going deeper

- 🧪 [Lab 42](../42-hardening-operations/) — the signals this hardens.
- 🧪 [Lab 38](../38-calibrating-the-eval-gate/) — where the alert threshold comes from.

## What comes next

- 🧪 [Lab 45: Anchoring the consensus](../45-anchoring-the-consensus/) — the same "don't measure against yourself" move, on the evaluation side.
