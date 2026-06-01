# Lab 45: Anchoring the consensus

> 🔴 Advanced · ⏱ ~75–95 min · 📚 Builds on Lab 43

## 🎯 Goal

[Lab 43](../43-annotator-drift/) ranked annotators by how well they agreed with the majority **consensus**. But the consensus is built from those same annotators — so ranking them against it is circular, and a confidently wrong majority looks like truth. This lab adds a **gold** label (expert / adjudicated ground truth), shows the majority can be collectively wrong, re-ranks annotators against gold, and spends adjudication where it changes the answer. It's the evaluation-side twin of [Lab 44](../44-hardening-the-signals/)'s held-out baseline: don't measure against yourself.

By the end you should be able to:

- Measure consensus against gold and find the items where the majority is collectively wrong.
- See how consensus-only ranking can misrank an annotator that a gold anchor rescues.
- Anchor reliability weights to gold rather than to the consensus derived from the annotators.
- Decide where to spend scarce gold labels (adjudicate disagreements; spot-check agreements).

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 43: Tracking annotator drift](../43-annotator-drift/) — this replaces its consensus-anchored ranking with a gold-anchored one.
- 🧪 [Lab 40: Annotation quality and the judge ceiling](../40-annotation-quality/) — the ceiling that should also be re-checked against gold.

**Assumed background:** Cohen's κ, majority-vote consensus, and the idea of circular evaluation (measuring against a reference derived from the thing under test).

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`. No LLM key needed.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | `cohen_kappa_score`, `accuracy_score` |

## What you'll build / what ships

- `annotations_with_gold.jsonl` — 20 items with three annotator labels plus a gold label, designed so the majority is collectively wrong on a couple.
- A notebook that scores consensus against gold, compares per-annotator agreement vs-consensus and vs-gold, anchors reliability weights to gold, and lays out an adjudication strategy.

## How item 4 works here

Each item carries a gold label alongside the three annotator labels. Scoring the majority consensus against gold surfaces the items where annotators are collectively wrong (so consensus ≠ truth). Scoring each annotator against gold rather than consensus can change the ranking — an annotator that disagreed with the (wrong) majority looks bad by consensus and good by gold. Reliability weights then anchor to gold, and adjudication is spent on the disagreements plus a sample of agreements.

## Steps

1. **Setup** (0).
2. **Annotations + gold** (1).
3. **Consensus vs gold** (2): is the majority right?
4. **Per-annotator vs gold vs consensus** (3).
5. **Gold-anchored weights** (4).
6. **Adjudication strategy** (5).
7. **The parallel to the held-out baseline** (6).

## Design choices and tradeoffs

- **Gold on a subset, not everything.** Expert labels are expensive. Spend them on the adjudication queue (where annotators disagree) plus a sample of unanimous items (where a confident, wrong consensus hides) — not uniformly.
- **Re-rank by gold, but keep consensus as a cheap monitor.** Consensus-agreement is still the day-to-day signal (Lab 43); gold is the periodic anchor that catches when the cheap signal has gone circular.
- **Weights from gold break the circularity.** Weighting annotators by agreement-with-consensus rewards conformity; weighting by agreement-with-gold rewards correctness.

## Common gotchas

- **Gold isn't infallible.** A single expert is just another annotator. Use multiple experts or adjudication for the gold itself, or you've moved the circularity, not removed it.
- **Small samples swing κ.** Treat the ranking shift as directional, not precise; size the gold set for the decision you're making.
- **Re-check the ceiling against gold.** The [Lab 40](../40-annotation-quality/) judge ceiling was measured against consensus; recompute it against gold, since a wrong consensus inflates or deflates it.
- **Don't gold-label only the easy items.** If you adjudicate only where annotators already agree, you'll never find the collective errors — sample the agreements deliberately.

## 🧮 Going deeper

- 🧪 [Lab 43](../43-annotator-drift/) — the consensus-anchored ranking this corrects.
- 🧪 [Lab 44](../44-hardening-the-signals/) — the same move on the operations side (held-out baseline).
- 📄 Cohen's κ; Landis & Koch (1977) — agreement bands.

## What comes next

This closes the evaluation-quality thread: Lab 40 gave you the ceiling, Lab 43 caught annotators drifting, and this anchors the consensus they vote on. The recurring lesson across Labs 44–45 — anchor every reference to something you did not derive from the thing being judged.
