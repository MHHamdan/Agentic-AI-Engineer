# Lab 49: Graded gold

> 🔴 Advanced · ⏱ ~80–100 min · 📚 Builds on Lab 47

## 🎯 Goal

[Lab 47](../47-trustworthy-gold/) built gold from multiple experts but kept labels **binary**. A faithfulness judgment is really ordinal — fully supported, a minor unsupported detail, partially supported, contradicted — and a binary gate collapses a 2-vs-3 near-miss and a 0-vs-3 blunder into the same "wrong". Worse, a majority vote silently resolves the very expert disagreements that most deserve a human. This lab moves the rubric to a 0-3 scale, adds a real adjudication protocol, grades the judge, and re-derives the [Lab 45](../45-anchoring-the-consensus/) annotator weights against graded gold.

By the end you should be able to:

- Measure multi-rater agreement on an ordinal scale (Krippendorff's α) and pairwise graded agreement (quadratic-weighted κ).
- Build gold with a senior-adjudicator protocol and show where it diverges from majority-of-experts.
- Grade the judge to expose a near-miss bias the binary gate hides, and re-derive annotator weights against graded gold — where the ranking can flip.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 47: Trustworthy gold](../47-trustworthy-gold/) — this makes its multi-expert gold graded and adjudicated.
- 🧪 [Lab 45: Anchoring the consensus](../45-anchoring-the-consensus/) — the annotator weights re-derived here.

**Assumed background:** ordinal vs nominal data, Cohen/Fleiss κ (Labs 40/43/47), and why a weighted κ (penalizing big disagreements more than small ones) fits ordinal labels.

**Setup:** Python 3.11+ with the repo environment. Krippendorff's α and quadratic-weighted κ are implemented inline (no `statsmodels`). No LLM key needed.

## 🛠 Tools and versions

Pure-Python ordinal measures, inline in the notebook. No external stats dependency.

## What you'll build / what ships

- `graded_gold.jsonl` — 24 items on a 0-3 faithfulness scale: three annotators, three experts, a `senior` adjudicator label on the items experts split, and the judge.
- A notebook computing ordinal inter-rater α, the two gold protocols, the graded judge metrics, and the re-derived annotator weights.

## How item 4 works here

The rubric is ordinal 0-3. Multi-rater agreement uses Krippendorff's α with the ordinal metric; pairwise graded agreement uses quadratic-weighted κ. Gold is the majority/median of experts, except where they split widely (range ≥ 2), which routes to a **senior adjudicator** whose call is gold — and that differs from the silent median on those items. The judge, graded, shows a systematic one-level-low bias (high off-by-one rate) that a binary gate would hide. Finally, the annotator weights are re-derived against graded gold: because the consensus here is biased low (two annotators share that bias), the ranking flips — the annotator that looks worst against the consensus is best against gold.

## Steps

1. **Setup** (inline measures) (0).
2. **The graded set** (1).
3. **Experts tighter, graded?** (2).
4. **Majority vs senior adjudicator** (3).
5. **Grade the judge** (4).
6. **Re-derive the weights** (5).

## Design choices and tradeoffs

- **Ordinal, not binary.** A binary gate throws away the distance between answers; the ordinal scale keeps it, so a near-miss judge can be *calibrated* (shift the threshold) instead of discarded.
- **The right agreement measure.** Plain κ/accuracy treats a 2-vs-3 disagreement like a 0-vs-3 one. Krippendorff's α (ordinal) and quadratic-weighted κ penalize by distance — the only defensible way to score ordinal raters.
- **Adjudicate splits, don't average them.** A median silently picks the middle of a wide split; a senior adjudicator makes a reasoned call with the guideline. The protocols agree on the easy items and diverge exactly where a human is worth it.
- **Re-derive against gold, not consensus.** A consensus that shares a bias rewards the annotators that share it. Graded gold re-ranks them — and the flip is the whole point.

## Common gotchas

- **Even spacing is an assumption.** The ordinal metric treats 0→1 and 2→3 as equal steps; a real rubric should justify that (or use explicit category distances).
- **Gold is still an anchor, not truth.** Report inter-expert α alongside it; a graded gold can be precise and still biased.
- **One dimension is a simplification.** Faithfulness alone misses relevance and completeness; real rubrics are multi-dimensional, and a judge can be calibrated per dimension.
- **Small samples swing α and κ.** Treat the gaps as directional; size the expert-labeled set for the decision.

## 🧮 Going deeper

- 🧪 [Lab 47](../47-trustworthy-gold/) — multi-expert (binary) gold this grades.
- 🧪 [Lab 45](../45-anchoring-the-consensus/) — the weights re-derived here.
- 📄 Krippendorff (1980) — α and its ordinal metric; Cohen — quadratic-weighted κ.

## What comes next

This is the graded close of the evaluation-quality thread: Lab 40 set a ceiling, Lab 45 anchored the consensus, Lab 47 made gold multi-expert, and this makes it graded and adjudicated — then re-derives the weights against it. Batch 78's through-line, across Labs 48–49: the stand-ins become the things you run, and binary becomes graded — the anchor gets as production-shaped as the backend.
