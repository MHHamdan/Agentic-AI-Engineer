# Lab 47 · Reference solution

The complete implementation of [Lab 47: Trustworthy gold](../README.md).

## What this is

Multi-expert gold and a re-derived judge ceiling:

- **`expert_gold.jsonl`** — 20 items with three annotators (a1–a3), three experts (e1–e3), and the judge label.
- **Inter-rater agreement** — inter-expert Fleiss κ (~0.73) above inter-annotator (~0.53): experts are a tighter anchor.
- **Single-expert fallibility** — each expert vs adjudicated gold ~0.90–0.95 (below 1.0), so gold needs multiple experts plus an adjudication queue for splits.
- **Re-derived ceiling** — judge vs consensus ~0.80, judge vs gold ~0.60. The consensus shares the judge's collective errors, so it overstates the judge; gold reveals the real (lower) ceiling. Expert gold also recovers truth where consensus failed (1.00 vs 0.80).

Fleiss κ is implemented inline (no `statsmodels`).

## The lesson

A single expert is just another annotator; one gold label moves the circularity rather than removing it. Multiple experts, agreement measured and splits adjudicated, are a tighter anchor — and every metric calibrated against consensus (the judge ceiling, the Lab 45 weights) must be re-derived against gold.

## Implementation choices

1. **Gold = adjudicated majority of multiple experts**, with inter-expert agreement reported as its own ceiling.
2. **Re-derive against gold; keep consensus as the cheap monitor.**
3. **Correlated error is the trap** — only an independent anchor exposes a judge that agrees with annotators for the wrong reason.

## What's out of scope

- More experts/items (3 experts, 20 items is a teaching size).
- Graded/multi-class rubrics (labels are binary here).
- A real adjudication protocol (majority-of-experts stands in for a senior adjudicator).

## Running

```bash
cd labs/47-trustworthy-gold
jupyter notebook solution/lab.ipynb
```

## Next

Re-derive the Lab 45 annotator weights against gold; report inter-expert agreement alongside every gold-anchored metric.
