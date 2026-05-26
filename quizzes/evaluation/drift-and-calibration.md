---
quiz_id: drift-and-calibration
title: Drift detection and agent-as-judge calibration
path: 06-evaluation-observability
module: 5
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "What are the three flavors of LLM drift that matter in 2026 production?"
    options:
      - "Latency drift, cost drift, and throughput drift"
      - "Prompt drift (your prompt changes cause second-order failures), model drift (the provider silently updates weights without changing the model identifier), and eval-score drift (rolling-mean rubric scores trend down on production traces)"
      - "Data drift, concept drift, and label drift (the classical ML taxonomy applied unchanged)"
      - "Distribution drift, embedding drift, and prediction drift"
    answer: "Prompt drift (your prompt changes cause second-order failures), model drift (the provider silently updates weights without changing the model identifier), and eval-score drift (rolling-mean rubric scores trend down on production traces)"
  - id: q2
    text: "You're monitoring an evaluator score stream. The mean stays at 0.80 week-over-week, but the distribution shape changes — variance halves and the tail collapses. Which test is most likely to catch this?"
    options:
      - "A mean-monitoring alert with a 5% threshold"
      - "Chi-square test on the score histogram"
      - "Kolmogorov-Smirnov (KS) two-sample test — it measures the maximum vertical distance between empirical CDFs and is sensitive to shape changes, not just mean shifts"
      - "Wasserstein distance — it would report 0.0 since the means are equal"
    answer: "Kolmogorov-Smirnov (KS) two-sample test — it measures the maximum vertical distance between empirical CDFs and is sensitive to shape changes, not just mean shifts"
  - id: q3
    text: "You want a single drift-detection number with interpretable thresholds that have been used across financial ML for two decades. Which test do you pick?"
    options:
      - "KS-test (returns p-value)"
      - "Population Stability Index (PSI) — interpreted as <0.1 stable, 0.1-0.25 moderate, >0.25 significant; thresholds widely used and well-understood"
      - "Wasserstein distance"
      - "Chi-square"
    answer: "Population Stability Index (PSI) — interpreted as <0.1 stable, 0.1-0.25 moderate, >0.25 significant; thresholds widely used and well-understood"
  - id: q4
    text: "Which is NOT one of the five named LLM-judge biases that the 2026 production literature consistently documents?"
    options:
      - "Position bias (preferring whichever answer appears first or last in pairwise mode)"
      - "Verbosity bias (preferring longer answers regardless of quality)"
      - "Confidence bias (judges over-rate outputs that include explicit confidence statements)"
      - "Self-preference bias (judges score outputs from their own model family 10-25% higher than equivalent outputs from other families)"
    answer: "Confidence bias (judges over-rate outputs that include explicit confidence statements)"
  - id: q5
    text: "You measure Cohen's kappa between your LLM judge and your human gold set. You get κ = 0.35. What does this tell you?"
    options:
      - "Almost perfect agreement — the judge is ready for production"
      - "Fair agreement — the judge is useful for aggregate trends but not for individual case decisions; don't rely on it for consequential decisions without human review"
      - "Worse than chance — something is broken"
      - "Cohen's kappa values are not interpretable across tasks; the number is meaningless"
    answer: "Fair agreement — the judge is useful for aggregate trends but not for individual case decisions; don't rely on it for consequential decisions without human review"
  - id: q6
    text: "What is the canonical mitigation for position bias in pairwise LLM-as-judge evaluation?"
    options:
      - "Train a separate model specifically for evaluation"
      - "Permutation averaging: present the same pair in both orderings (A,B) and (B,A); average the verdicts. Costs 2x per evaluation but produces a bias-free signal."
      - "Always present the response you want to win in position A"
      - "Increase the judge's temperature to randomize order effects"
    answer: "Permutation averaging: present the same pair in both orderings (A,B) and (B,A); average the verdicts. Costs 2x per evaluation but produces a bias-free signal."
  - id: q7
    text: "What is the 90/10 split in production LLM-as-judge that ~60% of 2026 production AI teams use?"
    options:
      - "Sample 90% of production traffic for evaluation, drop 10%"
      - "90% LLM-as-judge handles the evaluation volume; 10% human review maintains the gold set, reviews flagged edge cases, and recalibrates the judge against ground truth on a cadence. Neither half works alone."
      - "90% of evaluations are pairwise comparisons, 10% are pointwise scoring"
      - "90% of evaluators are offline (against fixtures); 10% are online (against production)"
    answer: "90% LLM-as-judge handles the evaluation volume; 10% human review maintains the gold set, reviews flagged edge cases, and recalibrates the judge against ground truth on a cadence. Neither half works alone."
  - id: q8
    text: "Drift detection on your evaluator score stream is firing alerts regularly, but on-call investigates and finds no actionable changes in the agent's behavior. What is the most likely missing piece?"
    options:
      - "The drift detection thresholds are too sensitive — relax them"
      - "The judge calibration loop is missing. Without periodic calibration against human ground truth, you can't distinguish real quality drift from judge drift. The drift signal needs an anchor; that anchor is Cohen's kappa against a fixed gold set, measured weekly."
      - "Drift detection doesn't work on LLM outputs — disable it"
      - "Add more drift tests in parallel until consensus emerges"
    answer: "The judge calibration loop is missing. Without periodic calibration against human ground truth, you can't distinguish real quality drift from judge drift. The drift signal needs an anchor; that anchor is Cohen's kappa against a fixed gold set, measured weekly."
---

# Drift detection and agent-as-judge calibration · 🧠 Check your understanding

Calibrate against the [drift detection](../../concepts/evaluation/drift-detection.md) and [agent-as-judge calibration](../../concepts/evaluation/agent-as-judge-calibration.md) concept pages plus [Lab 20](../../labs/20-drift-detection-and-calibration/). 8 single-select questions covering the statistical tests, the named biases, and the trust-stack assembly. Passing: 6/8.

---

**1.** What are the three flavors of LLM drift that matter in 2026 production?

- (a) Latency drift, cost drift, and throughput drift
- (b) Prompt drift (your prompt changes cause second-order failures), model drift (the provider silently updates weights without changing the model identifier), and eval-score drift (rolling-mean rubric scores trend down on production traces)
- (c) Data drift, concept drift, and label drift (the classical ML taxonomy applied unchanged)
- (d) Distribution drift, embedding drift, and prediction drift

<details>
<summary>Answer</summary>

**(b)** — These are the three flavors specific to LLM production. **Prompt drift** is the one you cause (you changed an instruction; downstream behavior shifted). **Model drift** is the one that happens to you silently (GPT-4 Turbo had multiple documented silent updates in 2024 with no version bump; the model_id stayed identical, behavior changed). **Eval-score drift** is the detectable signal — rolling-mean rubric scores on production traces — that surfaces both of the above plus input-distribution shift.

(c) is the classical ML taxonomy, which applies but doesn't capture what's specific to LLMs (model-provider silent updates aren't in the classical framework). (d) confuses drift types with detection mechanisms.

See: [drift-detection.md → "Why classical drift detection doesn't quite map"](../../concepts/evaluation/drift-detection.md#why-classical-drift-detection-doesnt-quite-map).
</details>

---

**2.** You're monitoring an evaluator score stream. The mean stays at 0.80 week-over-week, but the distribution shape changes — variance halves and the tail collapses. Which test is most likely to catch this?

- (a) A mean-monitoring alert with a 5% threshold
- (b) Chi-square test on the score histogram
- (c) Kolmogorov-Smirnov (KS) two-sample test — it measures the maximum vertical distance between empirical CDFs and is sensitive to shape changes, not just mean shifts
- (d) Wasserstein distance — it would report 0.0 since the means are equal

<details>
<summary>Answer</summary>

**(c)** — KS is nonparametric and CDF-based; it catches any distribution shift, not just mean shifts. Mean-monitoring with a 5% threshold (a) fails by design because the mean didn't change. Chi-square (b) works on categorical data, not continuous score distributions. Wasserstein (d) is not zero (it's small but not zero), but more importantly, Wasserstein measures the "earth-mover" effort which is dominated by mean shift; it underestimates shape-only drift.

Lab 20's Scenario C demonstrates this concretely: Beta(20,5) has the same mean as Beta(8,2) but a much narrower distribution. KS catches it with p<1e-8; mean-monitoring would not have fired.

See: [drift-detection.md → "Decision: which test, when"](../../concepts/evaluation/drift-detection.md#decision-which-test-when).
</details>

---

**3.** You want a single drift-detection number with interpretable thresholds that have been used across financial ML for two decades. Which test do you pick?

- (a) KS-test (returns p-value)
- (b) Population Stability Index (PSI) — interpreted as <0.1 stable, 0.1-0.25 moderate, >0.25 significant; thresholds widely used and well-understood
- (c) Wasserstein distance
- (d) Chi-square

<details>
<summary>Answer</summary>

**(b)** — PSI's threshold conventions (0.1 stable / 0.25 significant) are widely shared across organizations and don't require statistical training to interpret. The KS-test p-value is also informative but harder to communicate ("p < 0.001" doesn't tell a product manager whether to act). Wasserstein distance is in score units — useful but requires knowing what a "significant" magnitude is for your specific metric.

The production pattern that works combines two tests: PSI for the threshold-based alert (clean trigger that non-statisticians can interpret), KS for the statistical-significance check (catches subtle shape changes PSI's binning hides).

See: [drift-detection.md → "Decision: which test, when"](../../concepts/evaluation/drift-detection.md#decision-which-test-when).
</details>

---

**4.** Which is NOT one of the five named LLM-judge biases that the 2026 production literature consistently documents?

- (a) Position bias (preferring whichever answer appears first or last in pairwise mode)
- (b) Verbosity bias (preferring longer answers regardless of quality)
- (c) Confidence bias (judges over-rate outputs that include explicit confidence statements)
- (d) Self-preference bias (judges score outputs from their own model family 10-25% higher than equivalent outputs from other families)

<details>
<summary>Answer</summary>

**(c)** — "Confidence bias" is not one of the five named biases. The five are: **position bias**, **verbosity bias**, **self-preference bias**, **format/style bias**, and **calibration drift**. Each has documented magnitude and a mitigation pattern that survives production. Confidence bias in the sense given doesn't appear in the standard bias taxonomy (though there is related work on judge over-confidence in pointwise scoring — different concept).

See: [agent-as-judge-calibration.md → "The five biases — measurement and mitigation"](../../concepts/evaluation/agent-as-judge-calibration.md#the-five-biases--measurement-and-mitigation).
</details>

---

**5.** You measure Cohen's kappa between your LLM judge and your human gold set. You get κ = 0.35. What does this tell you?

- (a) Almost perfect agreement — the judge is ready for production
- (b) Fair agreement — the judge is useful for aggregate trends but not for individual case decisions; don't rely on it for consequential decisions without human review
- (c) Worse than chance — something is broken
- (d) Cohen's kappa values are not interpretable across tasks; the number is meaningless

<details>
<summary>Answer</summary>

**(b)** — The Landis & Koch 1977 interpretation: κ ∈ [0.20, 0.40] is "fair agreement." The judge is doing better than random (which would be κ ≈ 0) but not well enough to trust for individual decisions. It's useful for aggregate trend monitoring (where averaging across many cases washes out individual errors) but not for case-level judgments.

Production targets typically require **substantial** agreement (κ ≥ 0.6) before relying on the judge for consequential decisions, and **almost perfect** agreement (κ ≥ 0.8) in regulated or high-stakes domains. At 0.35 you can use the judge for aggregate dashboards but you need human review for anything user-affecting.

See: [agent-as-judge-calibration.md → "Cohen's kappa — the standard agreement metric"](../../concepts/evaluation/agent-as-judge-calibration.md#cohens-kappa--the-standard-agreement-metric).
</details>

---

**6.** What is the canonical mitigation for position bias in pairwise LLM-as-judge evaluation?

- (a) Train a separate model specifically for evaluation
- (b) Permutation averaging: present the same pair in both orderings (A,B) and (B,A); average the verdicts. Costs 2x per evaluation but produces a bias-free signal.
- (c) Always present the response you want to win in position A
- (d) Increase the judge's temperature to randomize order effects

<details>
<summary>Answer</summary>

**(b)** — Permutation averaging is the standard mitigation. Run the same pair in both orderings, average the results. The 2x cost is the trade-off; production teams typically accept it because the alternative is reporting a biased number. Modern instruction-tuned models have smaller position bias (≤0.04 in some benchmarks) than the original Zheng et al. 2023 measurements showed, but mitigation is still standard practice.

(c) would *induce* position bias deliberately, not mitigate it. (d) randomization at inference time doesn't help — you'd need many samples per evaluation, costing more than permutation averaging anyway.

See: [agent-as-judge-calibration.md → "The five biases — measurement and mitigation"](../../concepts/evaluation/agent-as-judge-calibration.md#the-five-biases--measurement-and-mitigation).
</details>

---

**7.** What is the 90/10 split in production LLM-as-judge that ~60% of 2026 production AI teams use?

- (a) Sample 90% of production traffic for evaluation, drop 10%
- (b) 90% LLM-as-judge handles the evaluation volume; 10% human review maintains the gold set, reviews flagged edge cases, and recalibrates the judge against ground truth on a cadence. Neither half works alone.
- (c) 90% of evaluations are pairwise comparisons, 10% are pointwise scoring
- (d) 90% of evaluators are offline (against fixtures); 10% are online (against production)

<details>
<summary>Answer</summary>

**(b)** — The 90/10 split is the production hybrid that ~59.8% of production AI teams use (per Vadim 2026). The point isn't sampling rate; it's the labor split between automated scoring (handles volume) and human review (maintains calibration anchor). Teams that drop the 10% human review entirely typically operate in low-stakes domains or aren't yet aware of their evaluation blind spots.

Pure LLM-as-judge produces scores you can't trust without an anchor. Pure human review doesn't scale. The hybrid is what makes evaluation work at production scale.

See: [agent-as-judge-calibration.md → "The 90/10 split"](../../concepts/evaluation/agent-as-judge-calibration.md#the-9010-split).
</details>

---

**8.** Drift detection on your evaluator score stream is firing alerts regularly, but on-call investigates and finds no actionable changes in the agent's behavior. What is the most likely missing piece?

- (a) The drift detection thresholds are too sensitive — relax them
- (b) The judge calibration loop is missing. Without periodic calibration against human ground truth, you can't distinguish real quality drift from judge drift. The drift signal needs an anchor; that anchor is Cohen's kappa against a fixed gold set, measured weekly.
- (c) Drift detection doesn't work on LLM outputs — disable it
- (d) Add more drift tests in parallel until consensus emerges

<details>
<summary>Answer</summary>

**(b)** — This is the most common Path 06 failure mode. Drift detection alone tells you something is shifting; it doesn't tell you whether the shift reflects real quality changes or judge drift. The kappa-against-gold-set loop is what disambiguates: if kappa stays stable while drift fires, the shift is real (input distribution or agent behavior has changed). If kappa drops along with the drift signal, the judge itself has shifted and you can't trust its scores.

(a) is the wrong first instinct — relaxing thresholds hides the signal you need. (c) abandons monitoring entirely. (d) doesn't help; uncalibrated tests still produce uncalibrated alerts. The fix is to add the calibration layer, not to tune the drift layer.

See: [agent-as-judge-calibration.md → "Putting it together — the trust stack"](../../concepts/evaluation/agent-as-judge-calibration.md#putting-it-together--the-trust-stack).
</details>

---

✓ **Module 5 complete after this quiz.** Modules 6-7 in future batches.
