# Lab 38: Calibrating the eval gate

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 37

## 🎯 Goal

The [Lab 37](../37-rag-eval-gates/) gate produces numbers. This lab makes those numbers trustworthy. Measure how well the LLM judge agrees with human labels before you report a judged metric; derive gate thresholds from a baseline run instead of picking round numbers; and operate judged faithfulness as a nightly monitor rather than a PR gate.

By the end you should be able to:

- Measure judge-vs-human agreement with Cohen's κ and decide whether a judge is trustworthy enough to track.
- Read a confusion matrix and a disagreement list to find a judge's blind spots.
- Derive thresholds from a baseline: a tolerance band for deterministic metrics, mean − k·σ for noisy ones.
- Separate what blocks a PR (cheap, deterministic) from what gets monitored nightly (expensive, noisy).

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 37: Evaluation gates for RAG](../37-rag-eval-gates/) — this lab calibrates that gate and extends its `eval_gate.py`.
- 🧪 [Lab 36: Training the router](../36-training-the-router/) — the baseline routing accuracy comes from the trained router.

**Assumed background:** Cohen's κ and chance-corrected agreement, basic sampling variance (mean/std), and CI concepts (scheduled vs PR-triggered jobs).

**Setup:** Python 3.11+ with the repo environment, `scikit-learn` (for `cohen_kappa_score`), your LLM provider key (a strong judge model). `PyYAML` if you want to lint the workflow locally.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | `cohen_kappa_score`, `confusion_matrix` |
| `openai` *or* `anthropic` | from prior labs | The judge under validation |
| GitHub Actions | — | `.github/workflows/rag-faithfulness-nightly.yml` |

## What you'll build / what ships

- `judge_validation.jsonl` — 24 human-labeled `(query, candidate, correct, faithful)` triples covering paraphrase, evasion, fabrication, and abstention.
- A notebook that runs the judge over them and reports agreement (accuracy, Cohen's κ, confusion, disagreements) with a trust rule.
- `derive_thresholds.py` — writes `gate_thresholds.json` from a baseline (tolerance band for routing accuracy, mean − k·σ for faithfulness).
- An extended `eval_gate.py` (Lab 37) that reads `--thresholds gate_thresholds.json`.
- `nightly_faithfulness.py` + `.github/workflows/rag-faithfulness-nightly.yml` — the non-blocking nightly monitor.

## How the three requested items map here

1. **Judge-vs-human agreement** → the validation set + the κ/confusion/trust-rule notebook (Steps 1–3).
2. **Nightly judged-faithfulness workflow** → `nightly_faithfulness.py` + the scheduled workflow (Step 5).
3. **Thresholds from a baseline + tolerance band** → `derive_thresholds.py` → `gate_thresholds.json`, read by `eval_gate.py` (Step 4).

## Steps

1. **Setup + judge** (0).
2. **Validation set** (1): the cases that separate good judges from bad.
3. **Agreement** (2): accuracy, κ, confusion, disagreements.
4. **Trust rule** (3): promote judged metrics only above the κ bar.
5. **Thresholds** (4): derive from baseline.
6. **Block vs monitor** (5): wire the gate and the nightly job.

## Design choices and tradeoffs

- **Why Cohen's κ, not raw accuracy.** Raw agreement is inflated when one label dominates (here, "correct" is 15/24). κ corrects for chance agreement, so it is the number to trust for an imbalanced label set. Landis-Koch reads 0.61–0.80 as "substantial."
- **Why a tolerance band for routing but mean − k·σ for faithfulness.** Routing accuracy is deterministic — one baseline measurement plus a band for benign drift is enough. Faithfulness varies run to run even at temperature 0, so its threshold must come from the *distribution* of repeated runs, not a single point.
- **Why faithfulness is nightly, not a PR gate.** It needs judge calls (cost) and is noisy (flaky as a blocker). A scheduled job reports a trend and alerts on drift without ever holding up a merge.

## Common gotchas

- **A judge is not ground truth.** Even a "substantial" κ means ~10–15% disagreement with humans. Report κ alongside any judged metric, and re-validate whenever you change the judge model, the rubric, or the domain — each invalidates the old agreement number.
- **Inter-annotator agreement is the ceiling.** If two humans only agree at κ = 0.7, no judge can meaningfully exceed that. A single-annotator validation set (like this one) can't reveal that ceiling — use multiple annotators in practice.
- **Thresholds drift with the model.** Re-derive the baseline after the router changes (e.g. after [Lab 39](../39-router-data-lifecycle/) retrains it), or the gate is measuring against a stale reference.
- **Don't gate on the noisy metric "just to be safe."** That's how you get a flaky red build everyone learns to ignore. Keep the blocking gate deterministic.

## 🧮 Going deeper

- 📄 Zheng et al. 2023, *Judging LLM-as-a-judge* ([arXiv:2306.05685](https://arxiv.org/abs/2306.05685)) — the MT-Bench judge-vs-human methodology.
- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — where these gates sit.

## What comes next

- 🧪 [Lab 39: The router's query-data lifecycle](../39-router-data-lifecycle/) — collect real queries to retrain the router, then re-derive this lab's baseline.
