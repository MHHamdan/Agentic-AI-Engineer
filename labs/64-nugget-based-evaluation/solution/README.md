# Lab 64 · Reference solution

Complete implementation of [Lab 64](../README.md).

## What this is

- **`coverage(answer, vital_only)`** — weighted nugget recall (Full/Partial/No → partial credit; vital/okay weights).
- **`sentence_support_rate(answer)`** — fraction of answer sentences supported by their cited evidence.
- **`evaluate(...)`** — both axes plus an attribution (missing vital nuggets, unsupported sentences).
- **`assign_with_judge`** — guarded seam for an AutoNuggetizer-style LLM support assignment.

## Expected results

- Cite-good/miss: vital coverage 0.50, SSR 1.00.
- Cover/cite-bad: vital coverage 1.00, SSR 0.00.
- Balanced: 1.00 / 1.00.

## Implementation choices

1. **Coverage = recall, citation = precision** — orthogonal, reported separately.
2. **Vital/okay weighting + partial credit**, following the TREC nugget tradition.
3. **Deterministic stand-ins** for the support and citation judges, with an LLM seam.

## Running

```bash
cd labs/64-nugget-based-evaluation
python nugget_eval.py --self-test
python nugget_eval.py            # the three-answer table
```
