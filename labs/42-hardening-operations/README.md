# Lab 42: Hardening the operations loop

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 41

## 🎯 Goal

[Lab 41](../41-operating-the-loop/) built the maintenance loop; this lab hardens it for real operation — closing the three gaps that bite once it's actually running. The notifier becomes severity-aware and routed to a real on-call channel (Slack/PagerDuty/issue) instead of a generic webhook; the drift baseline re-records itself on every promote so it can't go stale against a retrained model; and a fixed **canary** set gives the drift check and nightly job a heartbeat that survives a quiet traffic day.

By the end you should be able to:

- Add severity (warn vs page) to an alert and shape it for Slack, PagerDuty, or a GitHub issue.
- Re-record a drift baseline as part of a promote so the check tracks the current model.
- Use a canary set so volume-based signals don't go dark when traffic is low.
- Reason about which failures each mechanism catches that the others miss.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 41: Operating the maintenance loop](../41-operating-the-loop/) — this lab hardens its `notify.py`, `drift_check.py`, and `run_loop.py`, and adds `record_baseline.py`, `canary.py`, and `canary_queries.jsonl` to its toolkit.

**Assumed background:** GitHub Actions secrets/env, webhook/Events-API shapes (Slack incoming webhooks, PagerDuty Events API v2), and the on-call concepts of severity and alert fatigue.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`, `sentence-transformers`, `numpy`. No LLM key needed (logic runs via `--self-test`). No webhook needed — the notifier no-ops safely without one.

## 🛠 Tools and versions

| Component | Notes |
|---|---|
| `notify.py` | severity tiers + `to_slack` / `to_pagerduty` / `to_github_issue` (`--self-test`) |
| `record_baseline.py` | recompute + persist `confidence_baseline.json` (`--self-test`) |
| `canary.py` + `canary_queries.jsonl` | fixed heartbeat set; routing-failure check (`--self-test`) |
| `drift_check.py` | now reads the recorded baseline + `--canaries` |
| GitHub Actions | the three Lab 41 workflows, updated in place |

## What you'll build / what ships (in the operating-the-loop toolkit)

- `notify.py` — `severity()`, `to_slack`/`to_pagerduty`/`to_github_issue`, `route_alert`; safe no-op without an endpoint.
- `record_baseline.py` — `compute_baseline()` → `confidence_baseline.json`, called by the promote phase.
- `canary.py` + `canary_queries.jsonl` — `augment_window()`, `canary_routing_failures()`, and a CLI that exits non-zero on a flipped canary route.
- Updated `drift_check.py` (reads the baseline, `--canaries`), `run_loop.py` (promote re-records), and the three workflows.

## How the three requested items map here

1. **Map the notifier to a real on-call tool + tune the threshold** → `notify.py` severity tiers + provider adapters; `PAGE_FRACTION` is the tuning knob (Step 1).
2. **Re-record the drift baseline on promote** → `record_baseline.py` + `drift_check.load_baseline()` + the promote phase calling it (Step 2).
3. **Canary set the drift check and nightly always include** → `canary.py` + `canary_queries.jsonl`, wired into `drift_check.py --canaries` and `nightly_faithfulness.scoring_items()` (Step 3).

## Steps

1. **Setup** (0).
2. **Real notifier** (1): severity + adapters.
3. **Self-updating baseline** (2): promote re-records; check reads current.
4. **Canaries** (3): heartbeat + hard routing check.
5. **Hardened cadence** (4): how the workflows change.

## Design choices and tradeoffs

- **Severity as a fraction of the threshold.** A dip just below threshold is a warn; a gap beyond `PAGE_FRACTION` of the threshold is a page. One knob, easy to reason about and tune to your tolerance — the whole point of "tune the alert threshold."
- **Re-record on promote, not on a timer.** The baseline only becomes wrong when the model changes, and the model only changes on promote — so that's exactly when to refresh it. A timer would either lag or thrash.
- **Canaries are threshold-free for routing.** A flipped canary route is a hard failure regardless of any band, because it's a known-answer query — the cleanest possible regression signal.
- **No-op-by-default notifier.** Ships green before you wire Slack/PagerDuty; you opt in by setting a secret.

## Common gotchas

- **Alert fatigue.** If everything pages, nothing does. Keep `page` for real regressions (the baseline-derived threshold from Lab 38 is what makes the line meaningful) and let smaller dips warn.
- **Stale baseline if promote skips the re-record.** The whole point is that promote and re-record are atomic — don't ship a model without refreshing the baseline, or the drift check silently compares against the old distribution.
- **Canary rot.** Canaries encode answers that can legitimately change as the corpus evolves; review them when you change the corpus, or they'll false-alarm.
- **Provider payload drift.** Slack/PagerDuty shapes change over time; the adapters here are minimal and unversioned — pin to the API version you target.

## 🧮 Going deeper

- 🧪 [Lab 41](../41-operating-the-loop/) — the loop this hardens.
- 🧪 [Lab 38](../38-calibrating-the-eval-gate/) — where the alert threshold comes from.

## What comes next

- 🧪 [Lab 43: Tracking annotator drift](../43-annotator-drift/) — harden the evaluation side: catch drift in the annotators, not just the model.
