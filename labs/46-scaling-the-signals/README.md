# Lab 46: Scaling the signals across workers and traffic

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 44

## 🎯 Goal

The three [Lab 44](../44-hardening-the-signals/) signals work on one box. Production runs many, and the assumptions break: per-process alert state means each worker pages for the same incident; a 16-query curated reference carries a wide confidence band; a single whole-corpus hash flags every corpus-dependent canary on any edit. This lab fixes all three — a shared **StateStore** with an atomic claim, a larger clean **held-out reference** distilled from real traffic, and a **per-document** corpus map.

By the end you should be able to:

- Spot the check-then-record race that makes two workers double-page, and fix it with an atomic claim.
- Distill a clean, stratified, held-out reference from messy traffic, and reason about its confidence band.
- Localize a corpus change to specific documents so only the affected canaries are revalidated.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 44: Hardening the signals for real traffic](../44-hardening-the-signals/) — this scales its `notify.py`, `record_baseline.py`'s reference, and `canary.py`'s corpus review.

**Assumed background:** read-modify-write races and atomic compare-and-set (Redis `SETNX`, DB row locks), the standard error of a mean (`SE = σ/√n`), and content hashing.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`. Logic runs via `--self-test` (no LLM key, no webhook, no shared infra — `FileLockStore` uses a local file lock).

## 🛠 Tools and versions

| Component | Notes |
|---|---|
| `store.py` | `StateStore`, `InMemoryStore`, `FileLockStore`, atomic `try_claim` (`--self-test`) |
| `notify.py` | `deliver` accepts a `StateStore` (shared) or a dict (legacy); `--shared-store` |
| `build_reference.py` | `clean_candidates` / `stratify` / `band_ci` (`--self-test`) |
| `canary.py` | `per_doc_fingerprint` / `changed_docs` / `review_status_per_doc` |

## What you'll build / what ships (in the operating-the-loop toolkit)

- `store.py` — a `StateStore` with an atomic claim; in-memory and file-lock backends; a `naive_claim` kept to demonstrate the race.
- `build_reference.py` + `captured_traffic.jsonl` — distill a clean, stratified, held-out reference; the grown `reference_sample.jsonl` replaces the curated 16.
- Hardened `notify.py` (shared-store `deliver`) and `canary.py` (per-document map).

## How the three requested items map here

1. **Shared/distributed rate-limit + cooldown** → `store.py` + `notify.deliver(store=...)` + `--shared-store`; the nightly workflow uses it (Step 1).
2. **Larger clean reference from real traffic** → `build_reference.py` + `captured_traffic.jsonl`; the maintenance loop refreshes it before re-baselining (Step 2).
3. **Per-document corpus map** → `canary.py` `per_doc_fingerprint`/`review_status_per_doc`; the drift workflow caches the map (Step 3).

## Steps

1. **Setup** (0).
2. **Shared store + atomic claim** (1).
3. **Larger reference from traffic** (2).
4. **Per-document corpus map** (3).
5. **Scaled cadence** (4).

## Design choices and tradeoffs

- **Atomic claim, not check-then-record.** The race is structural: any gap between "is it in cooldown?" and "mark it sent" lets a second worker slip through. One operation under a lock closes it. `FileLockStore` stands in for the Redis/DB you'd use across a fleet.
- **Claim before delivery.** A send that fails after retries still consumed the cooldown slot — deliberate, so a broken webhook can't retry-storm every worker. Release-on-failure is a possible refinement.
- **Backward-compatible `deliver`.** It still accepts a plain dict (Lab 44's single-process behavior), so nothing downstream breaks; pass a `StateStore` to go shared.
- **Stratified, verified reference.** Balancing across routes keeps the band from being dominated by one route; the clean filter (length, dedup, trainset-leak) only *proposes* candidates — they still need verification.
- **Per-document map over whole-corpus hash.** Localizing change cuts revalidation noise sharply (here, 12 → the few that depend on the changed doc) without losing safety.

## Common gotchas

- **A shared filesystem is not a database.** `FileLockStore` needs the workers to share a filesystem; serverless or multi-region workers need a real shared store (Redis/DB) — the interface is the same, swap the backend.
- **The cooldown slot is consumed on failure.** Know that a failing delivery still cools down; if you need guaranteed delivery, add release-on-failure or a dead-letter path.
- **Clean filters are heuristic.** Length/dedup/trainset-leak filters catch obvious junk, not subtle off-distribution queries — verification is still a human (or model) step.
- **Content hashes flag no-op edits.** A reformat with no semantic change still changes the per-document hash; if that's noisy, hash normalized content.

## 🧮 Going deeper

- 🧪 [Lab 44](../44-hardening-the-signals/) — the single-process signals this scales.
- 🧪 [Lab 41](../41-operating-the-loop/) — the loop the toolkit serves.

## What comes next

- 🧪 [Lab 47: Trustworthy gold](../47-trustworthy-gold/) — the same "one point becomes plural" move on the evaluation anchor: gold from multiple experts, ceiling re-derived against it.
