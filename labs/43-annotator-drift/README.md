# Lab 43: Tracking annotator drift

> 🔴 Advanced · ⏱ ~70–90 min · 📚 Builds on Lab 40

## 🎯 Goal

[Lab 40](../40-annotation-quality/) measured inter-annotator agreement once and used it as the ceiling on judge quality. But annotators drift too: a rater's internal rubric slips over time, and the labels everything downstream is measured against quietly degrade. This lab tracks each annotator's agreement-with-consensus across rounds, flags a drifting rater by trajectory, down-weights them, and recomputes the ceiling among the calibrated annotators — because annotator drift and model drift look identical in a single judge-vs-consensus number.

By the end you should be able to:

- Track per-annotator agreement-with-consensus (Cohen's κ) over annotation rounds.
- Flag a drifting annotator by trajectory rather than a single noisy round.
- Build a reliability-weighted consensus that down-weights a drifter.
- Explain why annotator drift is invisible in model-level metrics and what to do about it.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 40: Annotation quality and the judge ceiling](../40-annotation-quality/) — this lab extends its single-round agreement into a tracked-over-time signal.

**Assumed background:** Cohen's κ (Lab 40), the idea of consensus from majority vote, and the distinction between sampling noise and a genuine trend.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn` (`cohen_kappa_score`). No LLM key needed.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | `cohen_kappa_score` |

## What you'll build / what ships

- `annotation_rounds.jsonl` — three rounds of three-annotator labels, with one annotator drifting.
- A notebook that computes per-round, per-annotator agreement-with-consensus; flags the drifter by trajectory; builds a reliability-weighted consensus; and recomputes the ceiling among the calibrated raters.

## How item 3 works here

Each round has its own majority consensus. Scoring each annotator against that consensus per round gives three trajectories; the drifting annotator's trajectory falls monotonically while the others hold. The flag is on the trajectory (a drop beyond a tolerance), not a single round — small rounds wobble. The reaction is to down-weight the drifter and recompute the ceiling from the calibrated pair, since the drifter's labels are noise until re-calibrated.

## Steps

1. **Setup** (0).
2. **Multiple rounds** (1).
3. **Per-round agreement** (2).
4. **Detect drift** (3): trajectory, not one round.
5. **React** (4): down-weight + re-ceiling.
6. **Why it matters for the judge** (5).

## Design choices and tradeoffs

- **Agreement-with-consensus, not pairwise, as the per-annotator signal.** Consensus is the working ground truth; an annotator's distance from it is what corrupts downstream metrics. Pairwise κ (Lab 40) is the diagnostic; consensus-agreement-over-time is the monitor.
- **Trajectory over a tolerance, not a single round.** Small rounds are noisy; a one-round dip isn't drift. A monotone fall beyond a tolerance band is.
- **Reliability weighting down-weights, doesn't delete.** A drifting annotator is a re-calibration problem (shared examples, guideline review), not necessarily a bad rater — keep their signal at reduced weight while you fix the rubric.

## Common gotchas

- **Confusing annotator drift with model drift.** A single judge-vs-consensus number can't tell them apart — if your judge "got worse," check whether an annotator drifted and dragged the consensus first. This is the central reason to track annotators over time.
- **Too few items per round.** κ swings hard on small samples; a couple of flips can look like drift. Size rounds for the precision you need before you act.
- **The ceiling moves with the annotators.** Re-measure inter-annotator agreement among the calibrated raters after a drift event; the old ceiling no longer applies.
- **Self-fulfilling consensus.** If a drifter is heavily weighted, the consensus follows them and their agreement looks fine. Reliability weighting from prior rounds guards against this.

## 🧮 Going deeper

- 🧪 [Lab 40](../40-annotation-quality/) — the one-time agreement this extends over time.
- 📄 Cohen's κ; Landis & Koch (1977) — the agreement bands.

## What comes next

This closes the evaluation-quality thread: Lab 40 gave you the ceiling; this keeps it current as the annotators themselves change. Beyond the labs, the loop is continuous — re-measure agreement every round, watch each trajectory, re-calibrate drifters, and recompute the ceiling before trusting any judged metric again.
