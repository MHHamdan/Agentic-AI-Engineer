# Lab 49 · Reference solution

The complete implementation of [Lab 49: Graded gold](../README.md).

## What this is

The graded, adjudicated version of the evaluation anchor:

- **`graded_gold.jsonl`** — 24 items on a 0-3 faithfulness scale: three annotators (a1–a3), three experts (e1–e3), a `senior` adjudicator label on the items experts split on, and the judge.
- **Ordinal agreement** — inter-expert α (~0.90) above inter-annotator α (~0.86), via Krippendorff's α with the ordinal metric. Experts are a tighter anchor even graded.
- **Two gold protocols** — majority/median-of-experts vs senior-adjudicated. They agree on the easy items and diverge on the three wide splits (`g07`, `g15`, `g21`) — exactly the items worth a human decision.
- **Graded judge** — QWK ~0.67 vs gold, MAE ~0.54, off-by-one ~46%: the judge is systematically one level low on high-faithfulness answers. Binary would hide this; graded lets you calibrate the threshold instead of discarding the judge.
- **Re-derived weights** — against the biased consensus the ranking is `a2, a3, a1` (a1 last); against gold it is `a1, a2, a3` (a1 first). The flip: a1 diverged from the consensus because the consensus was biased low, not because a1 was wrong.

Measures (Krippendorff ordinal α, quadratic-weighted κ) are inline — no `statsmodels`.

## The lesson

A binary label discards the distance between answers; a majority vote hides the disagreements that most need a human. Grade the rubric, adjudicate the splits with a senior protocol, and re-derive every weight (and ceiling) against the graded gold rather than the consensus.

## Implementation choices

1. **Ordinal measures** (α + quadratic-weighted κ) score disagreements by distance.
2. **Senior adjudication on wide splits**, median elsewhere — humans where it matters.
3. **Re-derive weights against gold**; the flip exposes consensus bias.
4. **Graded judge** → calibrate, don't discard.

## What's out of scope

- Multi-dimensional rubrics (faithfulness × relevance × completeness).
- A documented multi-adjudicator protocol (single senior here).
- Justifying equal spacing of the 0-3 steps (assumed).

## Running

```bash
cd labs/49-graded-gold
jupyter notebook solution/lab.ipynb
```

## Next

Re-derive the Lab 40 judge ceiling on the ordinal scale; calibrate the judge's one-level bias and re-threshold the eval gate; extend to multi-dimensional rubrics.
