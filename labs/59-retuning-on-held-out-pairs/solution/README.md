# Lab 59 · Reference solution

Complete implementation of [Lab 59](../README.md).

## What this is

- **`make_pairs`** — reflow/edit cosine-labeled pairs with hard cases (paraphrase → low cosine, label 0; negation → high cosine, label 1), so the classes overlap.
- **`optimism_curve`** — in-sample tuned accuracy vs k-fold held-out accuracy, by sample size; the gap is the optimism of in-sample threshold selection.
- **`cv_accuracy`** — held-out estimate via cross-validation.

## Expected results

- Optimism ~+0.03 at n=16, shrinking to ~0 by n=160; in-sample ≥ held-out everywhere.

## Implementation choices

1. **Cross-validate** for the estimate; refit on all pairs for the deploy threshold.
2. **Hard, overlapping cases** so the threshold and its optimism are real.
3. **Deterministic subsampling** (fixed seeds) so the curve reproduces.

## Running

```bash
cd labs/59-retuning-on-held-out-pairs
python retune.py --self-test
python retune.py            # print the optimism curve
```
