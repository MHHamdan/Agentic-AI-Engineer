# Lab 38 · Reference solution

The complete implementation of [Lab 38: Calibrating the eval gate](../README.md).

## What this is

The calibration layer for the Lab 37 gate, in three parts plus the shipped scripts:

- **Judge-vs-human agreement** — runs the judge over `judge_validation.jsonl` (24 human-labeled triples) and reports accuracy, Cohen's κ, a confusion matrix, and the disagreement list, with a trust rule (κ ≥ 0.60 → track the judge's scores as a trend).
- **`derive_thresholds.py`** — writes `gate_thresholds.json` from a baseline: `routing_accuracy = baseline − tolerance`, `judged_faithfulness = mean − k·σ` over repeated runs.
- **`eval_gate.py --thresholds`** — Lab 37's gate, extended to read the derived config (additive `load_thresholds`; `_meta` keys ignored; only metrics this run computed are enforced).
- **`nightly_faithfulness.py` + `rag-faithfulness-nightly.yml`** — judged faithfulness as a scheduled, non-blocking monitor that writes a 🔴/🟢 trend line to the run summary.

## Implementation choices

1. **Cohen's κ over raw accuracy.** The label set is imbalanced (15/24 correct), so chance-corrected agreement is the number to trust.
2. **The disagreement list is the deliverable, not the κ value alone.** It shows *where* the judge fails (paraphrase accepted-or-not, evasive-but-true, vague) so you can fix the rubric.
3. **Two derivation rules.** Deterministic metric → tolerance band; noisy metric → mean − k·σ. Using one rule for both either over- or under-tightens.
4. **`eval_gate.py` enforces only computed metrics.** A judged-faithfulness threshold can live in the config without the blocking gate trying to compute it — the nightly job owns that one.
5. **The nightly job exits 0.** Non-blocking by design; drift shows in the summary and via the scheduled run, never as a failed PR.

## Expected shape of the result

With a strong judge, agreement is high (accuracy ~0.85–0.90) and κ lands "substantial" (~0.7), with disagreements concentrated on the borderline items. The derived routing threshold sits a tolerance band below the baseline; the faithfulness threshold sits ~2σ below its sample mean.

## What's out of scope

- A large, multi-annotator validation set (this one is 24 single-annotator items; multi-annotator sets also reveal the inter-annotator ceiling).
- Many faithfulness samples (five here; use more for a stable σ).
- Alerting integrations (the nightly job writes a summary; wire your own notifier).

## Running

```bash
cd labs/38-calibrating-the-eval-gate
python derive_thresholds.py --self-test        # derivation math, offline
python derive_thresholds.py                    # writes gate_thresholds.json
python nightly_faithfulness.py --self-test      # monitor logic, offline
jupyter notebook solution/lab.ipynb             # judge-vs-human agreement
# the gate, with derived thresholds:
python ../37-rag-eval-gates/eval_gate.py --thresholds gate_thresholds.json
```

## Next

[Lab 39: The router's query-data lifecycle](../../39-router-data-lifecycle/) — retrain the router, then re-derive these thresholds.
