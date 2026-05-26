# Agent-as-judge calibration against human ground truth

> ⏱ ~13 min · 🔴 Advanced · Prerequisites: [Drift detection](./drift-detection.md) (this is the trust-the-scores complement), [Online evaluator registration](./online-evaluator-registration.md) (the LLM-as-judge mechanism this page calibrates).

Lab 19's online evaluator scored production traces. Module 5's drift-detection page monitors those scores for distribution shifts. Both presuppose that the scores actually correlate with what humans care about. This page covers what happens when they don't — when the judge itself is biased, drifts over time, or measures something subtly different from what you think it measures.

LLM-as-judge isn't a replacement for human judgment. It's a way to *scale* human judgment by anchoring the LLM to a human baseline through periodic calibration. Without the calibration loop, the judge's scores are confident-looking numbers that may or may not mean what their label says.

## The Zheng et al. 2023 problem statement, three years later

The original paper (Zheng et al., NeurIPS 2023) established LLM-as-judge as a viable scalable evaluation paradigm. It also documented several systematic biases that mean the scores aren't a faithful proxy for human preference without explicit mitigation.

The 2026 picture is more refined. Five named biases now appear consistently in the production literature, each with documented magnitude:

- **Position bias** (in pairwise judging) — favoring whichever response appears first or last. Documented at 10-15 percentage-point preference for slot A in pairwise MT-Bench comparisons (Wang et al. 2024; Zheng et al. 2024). Recent instruction-tuned models show smaller position bias (≤0.04 in some benchmarks); mitigation is still standard practice.
- **Verbosity bias** — preferring longer responses, even when length doesn't correlate with quality (Saito et al. 2023; Wu & Aji 2024). Observed in both pairwise and pointwise settings.
- **Self-preference bias** — judges score outputs from their own model family 10-25% higher than equivalent outputs from other families (Panickssery et al. 2024).
- **Format / style bias** — judges prefer specific output formats (bulleted lists over prose, markdown over plaintext) independent of content quality (Wu & Aji 2024).
- **Calibration drift** — the judge's scoring distribution shifts over time as the underlying judge model updates. The score "0.91 means helpful" can stop meaning that after a silent model bump.

Each has a measurement (is this happening?) and a mitigation (how to reduce it). Below.

## The five biases — measurement and mitigation

**Position bias** (pairwise mode only):
- **Measurement**: present the same pair (A, B) in both orderings; count how often the verdict matches. If A wins 60% in (A, B) order but only 40% in (B, A) order, position bias is responsible for 20 percentage points of the gap.
- **Mitigation**: permutation averaging. Run both orderings; average the scores. Costs 2x per evaluation. Most production teams accept the cost; the alternative is reporting a biased number.

**Verbosity bias** (pairwise or pointwise):
- **Measurement**: control for length. Construct paired examples where the correct answer is short and incorrect answer is long, and vice versa. Compare judge agreement with ground truth on long-correct/short-wrong vs short-correct/long-wrong subsets.
- **Mitigation**: explicit length-controlled rubric in the prompt ("score independently of length; do not reward longer answers for being longer"). Post-hoc length-controlled win rates (Dubois et al. 2024) — adjust scores by regressing out length effect.

**Self-preference bias**:
- **Measurement**: judge a set of outputs from your own model family (e.g., GPT-4 judging GPT-4 outputs) against the same outputs judged by a different family (Claude judging GPT-4 outputs). Compare mean scores.
- **Mitigation**: cross-family judging — use a different model family as the judge than the one producing the outputs you're judging. Ensemble across 3+ judges from different families when stakes are high.

**Format bias**:
- **Measurement**: re-format the same content into different presentations (bulleted vs prose, markdown vs plain). Score each; compare.
- **Mitigation**: format-normalize the input before scoring — strip markdown, normalize whitespace, expand bullets to prose. Or measure across format permutations and average.

**Calibration drift**:
- **Measurement**: this is what the rest of this page is about. Maintain a fixed human-labeled gold set; re-run the judge against it periodically; track agreement.
- **Mitigation**: the calibration loop, covered below.

The first four biases are static — once you build a debiasing pattern into your evaluator, it tends to hold. Calibration drift is dynamic — it can show up even after a debiased evaluator has been working fine for months.

## Cohen's kappa — the standard agreement metric

When you have judge scores and human scores on the same set of examples, you need a metric for how well they agree. Cohen's kappa is the standard:

```python
from sklearn.metrics import cohen_kappa_score

human_labels = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1]   # 10 examples, binary
judge_labels = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1]
kappa = cohen_kappa_score(human_labels, judge_labels)
# kappa ∈ [-1, 1]; > 0 means agreement above chance
```

Kappa corrects for chance agreement, which raw accuracy doesn't. Two judges who flip coins independently will agree 50% of the time on binary labels by chance alone; kappa subtracts that off so you measure agreement *above chance*.

Interpretation ranges (Landis & Koch 1977, the canonical thresholds the field uses):

| Kappa range | Interpretation | What this means for your judge |
|---|---|---|
| < 0 | Worse than chance | Something is broken; judge is anti-correlated with human |
| 0 - 0.20 | Slight agreement | Judge scores carry almost no signal; don't trust them for decisions |
| 0.20 - 0.40 | Fair agreement | Judge is useful for aggregate trends; not for individual case decisions |
| 0.40 - 0.60 | Moderate agreement | Judge is usable for most production cases; flag low-confidence cases for human review |
| 0.60 - 0.80 | Substantial agreement | Judge is trustworthy for routine cases; reserve human review for stakes |
| 0.80 - 1.00 | Almost perfect agreement | Judge can substitute for human review on routine cases |

For ordinal scores (1-5 rubric, 0-1 continuous binned into quintiles), use **weighted kappa** — penalizes large disagreements more than small ones. `sklearn.metrics.cohen_kappa_score(..., weights='quadratic')`. For more than two raters, use **Krippendorff's alpha**.

Production targets: aim for substantial agreement (κ ≥ 0.6) before relying on the judge for any consequential decision. If you can't reach 0.6 on your specific task, the judge is too biased for that task — adjust the rubric, switch judge models, or accept that human review can't be replaced for this metric.

## The calibration loop

The pattern that closes the trust gap on LLM-as-judge:

1. **Build a small gold set.** 50-200 examples. Carefully curated, manually labeled by 2+ human raters, with disagreements resolved through discussion. This is your ground truth. Invest in this; everything else depends on its quality.
2. **Run the judge against the gold set on a cadence.** Daily, weekly, or per-release — depends on how fast your judge model and prompt move. Weekly is a common default.
3. **Compute kappa.** Against the gold set human labels.
4. **Plot kappa over time.** A trend is what you're watching for. Single-week dips can be noise; sustained drops are signal.
5. **When kappa drops below threshold**, the judge needs recalibration. Investigation order: did the judge model update? Did the rubric/prompt change? Has the input distribution shifted so much that your gold set no longer represents production?
6. **Recalibrate.** Update the judge prompt, switch judge model, expand the gold set, or accept that this metric needs human-in-the-loop for the current quarter.

The cadence matters. Too infrequent (quarterly) and you miss the drift window. Too frequent (every trace) and the labeling cost defeats the purpose of using LLM-as-judge. Weekly is the production default; per-release for CI gates.

## The 90/10 split

The production consensus in 2026 (per Vadim 2026; ~60% of production AI teams) is a hybrid model:

- **90% LLM-as-judge** — handles the volume. Thousands of evaluations per day across CI gates, production monitoring, regression suites.
- **10% human review** — handles the calibration. Maintains the gold set, reviews flagged edge cases, makes high-stakes decisions, recalibrates the judge on a cadence.

Neither half works alone. Pure LLM-as-judge sounds like full automation but produces scores you can't trust without an anchor. Pure human review doesn't scale past small evaluation sets. The hybrid is what makes evaluation at production scale work.

Teams that have dropped human review entirely typically operate in low-stakes domains, or aren't yet aware of their evaluation blind spots. The teams reporting high LLM-as-judge agreement on regulated tasks (medical, legal, financial) without periodic human calibration are the ones to watch carefully — that's not a sign of a great judge; it's typically a sign that the calibration check isn't being run.

## When NOT to use LLM-as-judge

The unvarnished reality: LLM-as-judge isn't right for every task. Specific cases where it's the wrong tool:

- **High-stakes, low-volume decisions.** Medical diagnoses, legal opinions, financial recommendations. The volume doesn't justify automation; the stakes don't survive judge bias.
- **Regulated domains requiring defensible audit trails.** "The LLM judge scored this 0.87" isn't a defensible record. Human review is required for compliance.
- **Novel tasks with no calibration history.** A judge that hasn't been calibrated against humans on the specific task type produces unanchored scores. Build the calibration set first; the judge follows.
- **Subjective tasks where the rubric itself is contested.** If humans disagree among themselves on the rubric, LLM-as-judge will produce confident scores on whichever side of the disagreement its training data happened to favor.
- **Adversarial inputs.** Prompt-injection-resistant evaluation requires different machinery; LLM-as-judge is vulnerable to inputs that manipulate the judge prompt.

Use LLM-as-judge where it earns its place: high-volume routine evaluation tasks with well-defined rubrics, where periodic calibration against humans is feasible and tracked.

## Putting it together — the trust stack

The Path 06 trust stack reads bottom-up:

1. **Instrumentation** (Modules 2-3) emits traces.
2. **Online evaluators** (Module 4) score traces.
3. **Drift detection** (Module 5, previous page) monitors scores for distribution shifts.
4. **Judge calibration** (this page) verifies scores correlate with human judgment.

Each layer fails silently if a lower layer is broken. Drift detection on uncalibrated judge scores tells you the scores are shifting; it doesn't tell you whether the shift reflects real quality changes or judge drift. The calibration loop is what disambiguates.

A production-trustworthy evaluation pipeline runs all four. Skipping the calibration loop is the most common failure mode — drift detection looks like it's working, alerts fire periodically, on-call investigates and finds nothing actionable. Without the kappa anchor, the team can't tell whether the drift is real or whether the judge has just shifted under them.

## What this misses

Deferred to later modules or out of scope:

- **Cost attribution on the calibration loop itself.** When the gold set grows, when judges run frequently, costs add up. Module 6 covers OTel-baggage propagation that makes the cost attributable to specific cost centers.
- **Multi-turn (threaded) calibration.** Calibrating a judge that scores conversations rather than single turns introduces additional complexity. Module 7.
- **Active learning for gold-set curation.** Which examples should humans label next to maximize calibration value? Out of scope; a research-frontier topic.
- **RLAIF — using the calibrated judge for model training.** Different operational discipline; this page covers monitoring, not training.

## Related concepts

- [Drift detection](./drift-detection.md) — the score-stream-monitoring complement.
- [Online evaluator registration](./online-evaluator-registration.md) — the evaluator-running mechanism this page calibrates.
- [Lab 20 — drift detection and calibration](../../labs/20-drift-detection-and-calibration/) — applies these patterns end-to-end.

## References

- Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — the foundational paper establishing LLM-as-judge and the original bias taxonomy. [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
- FutureAGI (May 2026), *LLM-Judge Bias Mitigation (2026): Detect, Measure, Fix* — the five-named-biases framing this page uses, with documented magnitudes and the recalibration-loop pattern. [futureagi.com/blog](https://futureagi.com/blog/evaluating-llm-judge-bias-mitigation-2026/).
- Adaline (May 2026), *LLM-as-a-Judge: Why Frontier Models Fail 50%+ Bias Tests* — the JudgeBiasBench finding (Zhou et al.); RAND analysis confirming no judge is uniformly reliable across benchmarks. [adaline.ai/blog](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias).
- Vadim's blog (March 2026), *LLM as Judge: What AI Engineers Get Wrong About Automated Evaluation* — the 90/10 production split; the "59.8% of production AI teams use human review alongside LLM-as-judge" statistic. [vadim.blog](https://vadim.blog/llm-as-judge).
- Evidently AI documentation, *LLM-as-a-judge: a complete guide* — practical patterns for managing position, verbosity, and self-enhancement biases; pairwise-vs-pointwise trade-offs. [evidentlyai.com](https://www.evidentlyai.com/llm-guide/llm-as-a-judge).
- Dubois et al. 2024, *Length-Controlled AlpacaEval* — the post-hoc length-controlled win rate methodology for the verbosity-bias mitigation. [arxiv.org/abs/2404.04475](https://arxiv.org/abs/2404.04475).
- Landis & Koch 1977, *The Measurement of Observer Agreement for Categorical Data*, Biometrics — the original kappa interpretation thresholds the field still uses.
