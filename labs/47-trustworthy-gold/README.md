# Lab 47: Trustworthy gold

> 🔴 Advanced · ⏱ ~75–95 min · 📚 Builds on Lab 45

## 🎯 Goal

[Lab 45](../45-anchoring-the-consensus/) anchored the annotator consensus to a gold label — but treated gold as a single expert's call. A single expert is just another annotator with its own bias, so a single-expert gold can move the circularity rather than remove it. This lab builds gold from **multiple experts** (agreement measured, disagreements adjudicated), shows the annotator consensus was *flattering* the judge, and re-derives the [Lab 40](../40-annotation-quality/) judge ceiling against gold instead of consensus.

By the end you should be able to:

- Measure inter-expert agreement and show experts are a tighter anchor than annotators.
- Demonstrate that a single expert is fallible, so gold needs multiple experts plus adjudication.
- Re-derive the judge ceiling against gold, and explain why a consensus that shares the judge's biases overstates it.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 45: Anchoring the consensus](../45-anchoring-the-consensus/) — this makes the gold it introduced plural and adjudicated.
- 🧪 [Lab 40: Annotation quality and the judge ceiling](../40-annotation-quality/) — the ceiling this re-derives.

**Assumed background:** Fleiss/Cohen κ (Labs 40/43), majority-vote consensus, and correlated error (why two raters that share a bias agree for the wrong reason).

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`. Fleiss κ is implemented inline (no `statsmodels`). No LLM key needed.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | `cohen_kappa_score`, `accuracy_score` |

## What you'll build / what ships

- `expert_gold.jsonl` — 20 items with three annotators, three experts, and the judge label.
- A notebook that compares inter-expert vs inter-annotator agreement, shows single-expert fallibility and an adjudication queue, and re-derives the judge ceiling against gold vs consensus.

## How item 4 works here

Adjudicated gold is the majority of multiple experts, with split items routed to adjudication. Inter-expert Fleiss κ (higher than inter-annotator) shows experts are a tighter anchor; single-expert-vs-gold accuracy (below 1.0) shows even experts err. The judge ceiling, recomputed against gold, comes out lower than against consensus — because the judge shares the annotators' collective errors, so grading it against that consensus measures it against its own mistakes.

## Steps

1. **Setup** (0).
2. **Annotators, experts, judge** (1).
3. **Are experts a tighter anchor?** (2).
4. **Single-expert fallibility + adjudication** (3).
5. **Re-derive the ceiling against gold** (4).
6. **The same lesson as the operations side** (5).

## Design choices and tradeoffs

- **Gold = multiple experts, adjudicated.** One expert is a single point of bias; agreement among several, with splits adjudicated, is a measurable, tighter anchor. Report its own ceiling (inter-expert agreement) — gold isn't truth, it's a better-anchored estimate.
- **Re-derive against gold, keep consensus as the cheap monitor.** Consensus stays the day-to-day signal; gold is the periodic anchor that catches when consensus and judge drift together.
- **Correlated error is the trap.** A judge graded against a consensus that shares its biases looks better than it is. Only an independent anchor (gold) exposes the gap.

## Common gotchas

- **Gold still isn't truth.** Treating multi-expert gold as infallible repeats the single-expert mistake one level up. Report inter-expert agreement alongside it.
- **Adjudicate the splits, don't average them.** Where experts disagree, a senior decision with the guideline beats a silent majority — the disagreement often signals an ambiguous item or a guideline gap.
- **Re-derive everything calibrated against consensus.** The judge ceiling and the Lab 45 annotator weights were anchored to consensus; recompute them against gold or they inherit the consensus's bias.
- **Small samples swing κ.** Treat the gaps as directional; size the expert-labeled set for the decision you're making.

## 🧮 Going deeper

- 🧪 [Lab 45](../45-anchoring-the-consensus/) — single-gold anchoring this extends.
- 🧪 [Lab 40](../40-annotation-quality/) — the ceiling re-derived here.
- 📄 Fleiss (1971); Landis & Koch (1977) — agreement and its bands.

## What comes next

This closes the evaluation-quality thread end to end: Lab 40 set a ceiling, Lab 43 caught annotator drift, Lab 45 anchored the consensus, and this makes the gold itself plural and adjudicated — then re-derives the ceiling against it. The recurring lesson across Labs 46–47: any single point you trusted — one worker's state, one curated sample, one corpus hash, one expert — has to become plural and externally anchored before you can trust it at scale.
