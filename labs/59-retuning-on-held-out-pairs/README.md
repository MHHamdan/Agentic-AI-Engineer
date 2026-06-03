# Lab 59: Re-tuning the threshold on held-out pairs

> 🔴 Advanced · ⏱ ~70–85 min · 📚 Builds on Lab 55 · Module 27

## 🎯 Goal

When you swap in a real sentence-transformer ([Lab 55](../55-calibrated-detection-judgment/) `embedders.py`) and re-tune the change-detection threshold, the question is how to tune *out-of-sample* and how many labeled pairs you need. In-sample tuning — pick the threshold that maximizes accuracy on a set of pairs, then report that accuracy — is optimistically biased. This lab measures that optimism as a function of sample size and shows the held-out (cross-validation) fix.

By the end you should be able to:

- Explain why in-sample threshold selection inflates the reported accuracy.
- Use k-fold cross-validation to get an held-out estimate and a stable threshold.
- Read the optimism curve to decide how many reflow/edit pairs to label.

## 📋 Prerequisites

- 🧪 [Lab 55](../55-calibrated-detection-judgment/) (the threshold and the swappable embedder).
- 📐 [math-foundations/16](../../math-foundations/16-threshold-selection-under-shift.md) — in-sample optimism and held-out validation.
- **Assumed background:** ROC/Youden's J, cross-validation, the bias–variance idea.

**Setup:** Python 3.11+, standard library. `--real-embedder` uses a sentence-transformer when installed; the char-trigram stand-in is the offline default.

## 🛠 Module

| Component | Notes |
|---|---|
| `retune.py` | `make_pairs` (overlapping hard cases), `tune_threshold`, `cv_accuracy`, `optimism_curve` (`--self-test`) |

## What the numbers say

| n (pairs) | in-sample acc | held-out acc | optimism |
|---|---|---|---|
| 16 | 0.881 | 0.850 | +0.031 |
| 40 | 0.841 | 0.823 | +0.019 |
| 80 | 0.811 | 0.809 | +0.002 |
| 160 | 0.823 | 0.823 | +0.000 |

## Design choices and tradeoffs

- **A threshold is a fitted parameter.** It earns the same train/validation discipline as any model. Tuning and reporting on the same pairs is data leakage; the inflation is real and one-sided.
- **Optimism shrinks with n.** The bias is large when the sample is small relative to the threshold's freedom to chase noise, and vanishes as n grows — so the curve is a label-budget tool, not just a warning.
- **Cross-validate for the estimate, refit on all data for the deploy threshold.** Use CV to estimate unbiased accuracy and threshold stability; fit the threshold you actually ship on all your labeled pairs.

## Common gotchas

- **Don't report in-sample accuracy.** If you tuned the threshold on a set, that set's accuracy is optimistic — quote the held-out number.
- **Hard cases matter.** Paraphrases (meaning preserved, low cosine) and negations (meaning changed, high cosine) are where the threshold actually lives; a clean, separable sample hides the problem and the optimism.
- **Re-tune on change.** A threshold fit for the char-trigram embedder doesn't transfer to a sentence-transformer — re-run the whole procedure when the embedder or data distribution changes.

## 🧮 Going deeper

- 📐 [math-foundations/16](../../math-foundations/16-threshold-selection-under-shift.md) — the bias of in-sample selection and how it scales with n.
- 🧪 [Lab 55](../55-calibrated-detection-judgment/) — the threshold and the swappable embedder.

## What comes next

- 🧪 [Lab 60: Multimodal RAG, runnable](../60-multimodal-rag-runnable/) — the other retrieval-science gap: retrieval over images and tables.
