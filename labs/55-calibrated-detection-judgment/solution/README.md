# Lab 55 · Reference solution

The complete implementation of [Lab 55: Calibrated detection and judgment](../README.md).

## What this is

- **Part A** — `tune_threshold` selects the cosine cutoff that maximizes Youden's J on labeled reflow/edit pairs (char-trigram embedder stand-in). Fixed 0.98: acc 0.83 / FPR 0.33; tuned ~0.94: acc 0.96 / FPR 0.08.
- **Part B** — `isotonic_fit`/`isotonic_predict` (PAVA) calibrate a monotone, non-additive judge bias; completeness QWK on held-out goes 0.70 (raw) → 0.88 (additive) → 0.92 (isotonic). `weighted_gate` replaces all-dimensions-pass; the two rules diverge on a faithfulness-strong / completeness-weak release.

## Implementation choices

1. **Fit the threshold by an objective** (Youden's J) on held-out pairs, not a guess.
2. **Isotonic over additive** — a monotone fit corrects the shape of a compressing bias.
3. **Weighted over conjunctive** — the weights encode the product's risk posture.

## What's out of scope

- A real sentence-transformer embedder (char-trigram stand-in; procedure identical).
- `sklearn.isotonic.IsotonicRegression` (PAVA is implemented inline to show the algorithm).
- Cost-weighted / $F_\beta$ objectives (Youden's J shown; the page covers the alternatives).

## Running

```bash
cd labs/55-calibrated-detection-judgment
python calibrate.py --self-test
```

## Next

[Lab 56: Production traces and routing](../../56-production-traces-routing/).
