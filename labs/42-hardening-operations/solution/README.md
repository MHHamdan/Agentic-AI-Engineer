# Lab 42 · Reference solution

The complete implementation of [Lab 42: Hardening the operations loop](../README.md).

## What this is

Three gaps in the Lab 41 loop, closed in the operating-the-loop toolkit:

- **`notify.py`** (item 1) — `severity(value, threshold, page_fraction)` returns ok/warn/page; `to_slack`/`to_pagerduty`/`to_github_issue` shape the payload per channel; `route_alert` dispatches; `post` no-ops without an endpoint. A `warn` maps PagerDuty to `acknowledge`, only a `page` to `trigger`.
- **`record_baseline.py`** (item 2) — `compute_baseline(confidences)` → `{mean, std, n}`; `write_baseline` persists `confidence_baseline.json` with a recorded date. The promote phase calls it; `drift_check.load_baseline()` reads it (falling back to the constant before the first record).
- **`canary.py` + `canary_queries.jsonl`** (item 4) — `augment_window` prepends canaries to the drift window; `canary_routing_failures` returns canaries whose predicted route ≠ gold; the CLI exits non-zero on any failure. `nightly_faithfulness.scoring_items()` appends canaries to the eval set.

Each script has a `--self-test`. The three Lab 41 workflows are updated in place.

## Implementation choices

1. **Severity from one fraction.** `PAGE_FRACTION` is the single tuning knob for "how far below threshold pages" — easy to reason about and to set to your tolerance.
2. **Re-record on promote.** The baseline goes stale exactly when the model changes; promote is the only time that happens, so promote re-records — atomically.
3. **Threshold-free canary routing.** A known-answer query whose route flips is a hard regression with no band to argue about.
4. **No-op-by-default notifier.** Ships green; you opt into real alerting by setting a secret.
5. **Updated in place, not duplicated.** The hardened scripts replace the Lab 41 versions at their original paths, so the workflows and imports keep working.

## What's out of scope

- Retries, rate limiting, and alert dedup/cooldown in the notifier.
- A held-out clean reference for the baseline (uses the prototype set).
- A large canary suite (ten queries; grow to cover the failures you fear).

## Running

```bash
cd labs/41-operating-the-loop   # the hardened toolkit lives here
python notify.py --self-test
python record_baseline.py --self-test
python canary.py --self-test
python drift_check.py --self-test
python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 --channel pagerduty
jupyter notebook ../42-hardening-operations/solution/lab.ipynb
```

## Next

[Lab 43: Tracking annotator drift](../../43-annotator-drift/) — harden the evaluation side.
