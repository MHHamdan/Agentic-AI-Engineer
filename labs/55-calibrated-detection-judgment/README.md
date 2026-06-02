# Lab 55: Calibrated detection and judgment

> 🔴 Advanced · ⏱ ~95–115 min · 📚 Builds on Labs 50, 51 · Module 25

## 🎯 Goal

Two stand-ins from earlier labs, both replaced by calibration on held-out data:

- **Part A (item 2)** — [Lab 50](../50-closing-the-failure-loop/)'s semantic fingerprint used a fixed cosine threshold of 0.98. Real embeddings put reflows and meaning-changes on overlapping cosine ranges, so a fixed cutoff cries wolf on reflows. Tune it on labeled reflow/edit pairs by maximizing Youden's J.
- **Part B (item 3)** — [Lab 51](../51-calibrated-multidimensional/) corrected the judge with a single additive shift and gated on all-dimensions-pass. A real judge bias is monotone but not a constant offset; isotonic regression (PAVA) fits a monotone map and recovers more agreement, and a weighted gate replaces the conjunctive one.

The math is in [math-foundations/15](../../math-foundations/15-calibration-threshold-selection.md).

By the end you should be able to:

- Select a detector threshold from labeled data by an explicit objective (Youden's J / $F_\beta$).
- Fit an isotonic calibration with PAVA and explain why it beats a constant shift on a non-additive bias.
- Build a weighted multi-dimensional gate and reason about conjunctive vs weighted decisions as a product choice.

## 📋 Prerequisites

- 🧪 [Lab 50](../50-closing-the-failure-loop/) (the fixed threshold) and 🧪 [Lab 51](../51-calibrated-multidimensional/) (the additive shift, the gate).
- 📐 [math-foundations/15](../../math-foundations/15-calibration-threshold-selection.md) — ROC/Youden and isotonic regression.
- **Assumed background:** ROC curves, quadratic-weighted κ, monotone regression, train/test discipline.

**Setup:** Python 3.11+; no model or network. The embedder is a deterministic char-trigram stand-in; production uses a sentence-transformer.

## 🛠 Module

| Component | Notes |
|---|---|
| `calibrate.py` | `embed`/`cosine`/`tune_threshold` (Part A); `isotonic_fit`/`isotonic_predict`/`additive_shift`/`weighted_gate`/`qwk` (Part B) (`--self-test`) |

## What the numbers say

| | Result |
|---|---|
| Fixed 0.98 threshold | acc 0.83, FPR 0.33 (flags a third of reflows) |
| Tuned threshold (~0.94, Youden J) | acc 0.96, FPR 0.08 |
| Completeness QWK (held-out) | raw 0.70 → additive 0.88 → **isotonic 0.92** |
| Weighted gate vs all-dims | differ on a faithfulness-strong / completeness-weak release |

## Design choices and tradeoffs

- **A threshold is fitted, not guessed.** Under overlapping score distributions a guessed cutoff sits in the overlap and trades misses for false alarms. Youden's J picks the prior-free separating point; switch to a cost-weighted objective or $F_\beta$ when a missed change and a false alarm cost differently.
- **Monotone, not arbitrary, calibration.** Isotonic regression bends to fit a compressing bias that an additive shift can't, but the monotonicity constraint stops it from overfitting the calibration sample (an unconstrained lookup can invert the ordering — worse than the original bias).
- **Conjunctive vs weighted is a policy.** All-dimensions-pass treats every dimension as a hard floor; a weighted gate lets a strong dimension offset a weak one. Neither is "correct" — the weights belong to whoever owns the release. A common hybrid keeps a hard floor on a safety dimension and weights the rest.

## Common gotchas

- **Refit on change.** A threshold or calibration fit for one embedder/judge doesn't transfer to another — refit when the model changes, the same as retraining.
- **Hold out.** Fit the threshold and the isotonic map on a calibration split and measure on a test split, or the improvement is partly memorization.
- **Char-trigram ≠ semantic.** The offline embedder captures surface overlap; a real sentence-transformer captures meaning, which changes the cosine distributions (and the tuned threshold) but not the procedure.

## 🧮 Going deeper

- 📐 [math-foundations/15](../../math-foundations/15-calibration-threshold-selection.md) — every equation here, derived.
- 🧪 [Lab 50](../50-closing-the-failure-loop/), [Lab 51](../51-calibrated-multidimensional/) — the stand-ins this replaces.

## What comes next

- 🧪 [Lab 56: Production traces and routing](../56-production-traces-routing/) — run the eval and cost loops over real OpenTelemetry spans, and learn the routing decision instead of hand-flagging it.
