# Lab 45 · Reference solution

The complete implementation of [Lab 45: Anchoring the consensus](../README.md).

## What this is

The gold-anchored correction to Lab 43's consensus-only ranking:

- **`annotations_with_gold.jsonl`** — 20 items, three annotator labels + a gold label, built so the majority is collectively wrong on two items.
- **Consensus vs gold** — `accuracy_score(gold, consensus)` = 0.90; the majority is wrong on `g17`/`g18`. Consensus is not ground truth.
- **Per-annotator vs gold vs consensus** — `a3` reads 0.50 against consensus but 0.70 against gold (beating `a2`'s 0.60), because on the items the majority got wrong, `a3` was right.
- **Gold-anchored weights** — re-ranking by agreement-with-gold can reorder who you trust.
- **Adjudication** — gold-label the disagreement queue in full; spot-check unanimous items to catch collective error.

## The lesson

The consensus is built from the annotators, so ranking them against it is circular — exactly like measuring a drift baseline on the model's own training data (Lab 44). Both are fixed by an external anchor: a held-out clean sample there, a gold set here.

## Implementation choices

1. **Gold on a subset** — adjudicate disagreements; sample agreements (where confident-wrong hides).
2. **Keep consensus as the cheap monitor** — gold is the periodic anchor, not the daily signal.
3. **Weights from gold reward correctness, not conformity.**

## What's out of scope

- Multiple experts / adjudicated gold (a single expert is just another annotator).
- Larger sample (20 items is a teaching size; κ swings on small n — ranking shift is directional).
- Re-deriving the Lab 40 ceiling against gold (named as the follow-on).

## Running

```bash
cd labs/45-anchoring-the-consensus
jupyter notebook solution/lab.ipynb
```

## Next

Recompute the Lab 40 judge ceiling against gold; use multiple experts for the gold itself.
