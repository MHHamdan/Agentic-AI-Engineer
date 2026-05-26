# Drift detection on agent traces

> ⏱ ~14 min · 🔴 Advanced · Prerequisites: [Online evaluator registration](./online-evaluator-registration.md) (the score stream this page operates on), familiarity with at least Lab 19. Helpful: any prior exposure to classical ML drift detection.

Module 4 produced a continuous stream of online-evaluator scores. This page is what you do with that stream — detect when the distribution of scores is changing, before the change becomes a user-facing regression. The patterns extend classical ML drift detection but the signals are different, the failure modes are different, and the alerting trade-offs are different.

Three flavors of LLM drift matter in 2026, in order of how often you'll see them:

1. **Prompt drift** — your prompt updates cause second-order failures. You changed one instruction; the agent's downstream behavior shifted in ways you didn't predict. CI catches the obvious cases; production catches the subtle ones.
2. **Model drift** — the provider updates weights without changing the model identifier. Documented for GPT-4 Turbo in 2024 (multiple silent updates with no version bump). The model_id field is identical; the behavior isn't. Latency dashboards don't catch this; eval-score-attached span monitoring does.
3. **Eval-score drift** — rolling-mean rubric scores trend down on production traces. Could be caused by either of the above, or by input-distribution shift (new user segments asking different questions), or by the judge itself drifting (Module 5's calibration topic).

This page covers the mechanisms for detecting all three on the score stream. Calibration of the judge against ground truth — required to trust the scores in the first place — is the [next page](./agent-as-judge-calibration.md).

## Why classical drift detection doesn't quite map

Classical ML drift detection compares feature distributions: today's `user_age` distribution vs last quarter's, today's `transaction_amount` vs the training set. The math is well-developed (KS-test, PSI, Wasserstein) and the tools are mature (Evidently, NannyML, whylogs).

LLM evaluator scores aren't features. They're already aggregations — the output of a Lab 19-style evaluator that has condensed many trace attributes into a single number. Two consequences:

- **The score stream itself is what you monitor.** Not the input features (though embedding-space input drift is a separate complementary signal — out of scope for this page, mentioned in `what-is-rag-evaluation.md`). Not the raw model outputs. The aggregated scores.
- **Score drift can be caused by many things.** Input distribution shift, model behavior shift, judge bias drift, prompt change effects, even seasonal user-behavior patterns. The detection mechanism tells you something is changing; the diagnosis requires the full trace + the calibration loop from the next page.

The math from classical ML drift detection still applies. The interpretation is different.

## The four canonical statistical tests

When you have a baseline distribution (last week's eval scores) and a current distribution (this week's), four tests answer "are these the same distribution":

**Kolmogorov-Smirnov (KS) two-sample test**: nonparametric; measures the maximum vertical distance between two empirical CDFs. Returns a test statistic D and a p-value. Strong on distribution shape changes (variance shifts, tail collapse), not just mean shifts. The default for continuous-valued eval scores.

```python
from scipy.stats import ks_2samp
statistic, p_value = ks_2samp(baseline_scores, current_scores)
# Reject null (same distribution) if p_value < 0.05
```

**Population Stability Index (PSI)**: bins both distributions, computes a weighted log-ratio. Interpretation-friendly thresholds: PSI < 0.1 = stable, 0.1-0.25 = moderate drift, > 0.25 = significant drift. Standard in financial-ML monitoring; well-understood across teams.

```python
import numpy as np

def psi(baseline, current, bins=10):
    breakpoints = np.linspace(0, 1, bins + 1)
    baseline_pct = np.histogram(baseline, bins=breakpoints)[0] / len(baseline)
    current_pct = np.histogram(current, bins=breakpoints)[0] / len(current)
    # Avoid log(0); add small epsilon
    baseline_pct = np.where(baseline_pct == 0, 1e-6, baseline_pct)
    current_pct = np.where(current_pct == 0, 1e-6, current_pct)
    return np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
```

**Wasserstein distance (Earth Mover's Distance)**: how much "work" to transform one distribution into the other. Scale-aware — the value's magnitude has meaning in score units, not just a yes/no signal. Useful when you want to alert on "the mean shifted by more than 0.1 in absolute terms," not just on statistical significance.

```python
from scipy.stats import wasserstein_distance
distance = wasserstein_distance(baseline_scores, current_scores)
# distance is in score-units; alert when distance > threshold
```

**Chi-square (categorical)**: for binned categorical features — error_kind counts, tool_choice frequencies, retrieval_source distributions. Not the test for continuous eval scores; the test for the categorical dimensions you might also monitor alongside.

```python
from scipy.stats import chisquare
chi2, p_value = chisquare(observed_counts, expected_counts)
```

## Decision: which test, when

| Question you're answering | Test | Why |
|---|---|---|
| "Has the distribution of eval scores shifted at all (mean, variance, shape)?" | **KS-test** | Nonparametric; catches shape changes mean-monitoring misses |
| "How much has the distribution shifted, in interpretable terms?" | **PSI** | Threshold-friendly: 0.1 / 0.25 lines work across organizations |
| "How much has the mean shifted, in score units?" | **Wasserstein** | Scale-aware; output is in the units of the metric |
| "Has the distribution of categorical labels shifted?" | **Chi-square** | The right test for categorical data; wrong for continuous |
| "Did this drift happen recently or has it been building?" | **Rolling-window KS** | Slide a window across the score stream; plot p-value over time |

The default production pattern uses two tests in parallel: PSI for the threshold-based alert (clean trigger), KS for the statistical significance check (catches subtle shape changes PSI's binning hides).

## The rolling-window pattern

A point-in-time KS-test gives you a snapshot. Production needs a stream. The rolling-window pattern: keep a fixed baseline (last month's distribution, frozen), slide a window of recent scores (last 24 hours, last 1000 samples), compute KS at every interval, plot the p-value over time.

```
Time:    Day 1     Day 5     Day 10    Day 15    Day 20    Day 25    Day 30
KS p:    0.78      0.65      0.71      0.42      0.08      0.001     0.0001
                                        ↑warning  ↑alert    ↑critical
```

The shape of the p-value curve tells you whether the drift is abrupt (cliff) or gradual (slope). Abrupt cliffs typically indicate model-provider weight updates or prompt changes. Gradual slopes typically indicate input-distribution shift (your user base is changing).

Three windows to keep in mind:
- **Baseline window** — frozen historical reference, typically last month or last release. Updated infrequently.
- **Reference window** — sliding recent baseline (last 7 days). Lets you detect "this week vs last week" drift independent of the long-term baseline.
- **Current window** — latest data (last 24 hours). The one being tested.

## The alerting problem

Drift detection is famously noisy. Naive thresholds fire on every minor variation; lax thresholds miss the silent degradations the whole point of monitoring catches.

The pattern that works in production:

1. **Two-tier thresholds.** A warning level (PSI > 0.1) and a critical level (PSI > 0.25). Warning goes to a dashboard; critical goes to on-call.
2. **Persistence requirements.** Drift must persist for N consecutive windows before alerting. Single-window spikes are usually noise.
3. **Slice the dashboards.** Drift on the overall score distribution can hide drift on a single user cohort. Per-locale, per-device, per-user-tier slices catch tier-specific regressions.
4. **Confirm with proxy signals.** A drift alert from PSI on `citation_preservation` scores correlates with abstain rate, average output length, retrieval-result count. If all three move together, the signal is real; if only PSI moves, suspect a measurement artifact.
5. **The runbook.** Drift alerts route to a documented investigation flow: check model_id, check prompt history, check input distribution slice. Diagnosis ordering matters because some checks are cheap (model_id query) and some are expensive (judge recalibration).

## Monitoring without labels

The hard production reality: most of your traces don't ship with ground truth. There's no "correct answer" attached to last Tuesday's user query about subscription cancellation. You can't compute accuracy because there's nothing to compare against.

Three proxy signals carry useful drift information even without labels:

- **Confidence distributions.** Models that emit calibrated confidence scores (or proxies like log-probabilities) give you a distribution to drift-detect. A confidence-distribution shift toward lower confidence is an early signal even when scores stay stable.
- **Abstain / fallback rates.** Agents that route to "I don't know" or escalate to humans encode an explicit signal. Rising abstain rates signal degradation before downstream scores catch it.
- **Output structural properties.** Average output length, citation count per output, tool-call count per trace, retry rate. None is ground truth; all carry drift signal cheaply.

Combine these with the **delayed-label backfill** pattern: when ground truth eventually arrives (user clicks "this answer was helpful" three hours later, or a support ticket resolves, or a downstream metric stabilizes), retroactively join the label to the trace and compute drift metrics on the labeled subset. The delayed window matters less than the consistency of the delay.

## The tool landscape (2026)

Open-source libraries for drift detection on agent traces:

- **Evidently** — Python OSS, Apache 2.0. CI-friendly: produces HTML reports, supports both numeric and categorical drift, 100+ metrics. Best for "drift report on a fixture comparison" workflows. The lab uses this.
- **NannyML** — focuses on performance estimation without ground truth (the proxy-signals pattern above). Apache 2.0; strong fit when you have lots of unlabeled production data.
- **whylogs** (WhyLabs) — profile-based architecture; summarizes data locally before sending profiles to a central service. Privacy-preserving — useful when raw prompts/responses can't leave the network.
- **Arize Phoenix** — OTel-native; the OSS counterpart to Arize AX. Embedding drift visualization is a strength; ingests OTel traces directly.
- **FutureAGI** — full agent stack including drift, evaluation, simulation. OSS; pick when you want one platform for the entire Path 06 surface.

Commercial-grade alternatives extend these (Arize, Fiddler, Aporia/Coralogix, Datadog) — same statistical underpinnings, productized dashboards and integration. The math is the same; the operational fit varies.

## The "silent provider weight update" failure mode

The pattern that motivates this entire page, with a concrete example: a team scored helpfulness at 0.91 all quarter. Their judge model bumped a minor version in March without a public announcement. The mean shifted four points; the score distribution narrowed. The CI gate kept passing because it was checking aggregate score, not distribution shape. In May, the agent quoted a refund off by an order of magnitude. The eval suite never flagged it.

The drift detection that would have caught this: KS-test rolling-window on the judge's score distribution. The mean shifted only 4 points (under most warning thresholds), but the distribution shape changed (KS would have fired with low p-value). The distribution-shape signal precedes the score-shift signal by weeks. PSI on the binned distribution would have crossed 0.25 around March 15.

The lesson is that monitoring the mean of eval scores is necessary but not sufficient. Distribution shape carries the early signal. The lab makes this concrete with three drift scenarios.

## What this misses

Out of scope; covered elsewhere or later:

- **Embedding-space drift on RAG inputs.** Path 02 v2 territory. The retrieval-side complement to score-side drift. Could be added as a Lab 09 extension.
- **Concept drift in the strict ML sense** (input-label relationship changing). When the relationship between what users ask and what counts as a good answer shifts. Mostly a human-judgment problem; addressed by the calibration loop in the next page.
- **Drift-triggered retraining / RLAIF.** This page covers detection. Triggering retraining decisions is a separate operational topic with its own runbooks.
- **The agent-as-judge calibration loop** that decides whether drift in judge scores reflects real quality changes vs judge drift. [Next page](./agent-as-judge-calibration.md).

## Related concepts

- [Agent-as-judge calibration](./agent-as-judge-calibration.md) — the calibration loop that lets you trust the scores drift detection is monitoring.
- [Online evaluator registration](./online-evaluator-registration.md) — produces the score stream this page operates on.
- [Lab 20 — drift detection and calibration](../../labs/20-drift-detection-and-calibration/) — applies these patterns end-to-end against simulated drift scenarios.

## References

- All Days Tech (January 2026), *Model Drift in Production* — the production-first runbook covering PSI/KS/Wasserstein/JS-KL/chi-square choices, warning-vs-critical alerting, the slice-dashboards pattern. [alldaystech.com](https://alldaystech.com/guides/artificial-intelligence/model-drift-detection-monitoring-response).
- Galileo (March 2026), *Best LLM Drift Monitoring Platforms in 2026* — comparison of 9 platforms by drift methods (PSI / KL / Hellinger / Jensen-Shannon / Isolation Forest / autoencoder reconstruction). [galileo.ai/blog](https://galileo.ai/blog/best-llm-output-drift-monitoring-platforms).
- FutureAGI (May 2026), *What is LLM Drift? Prompt, Model, and Eval-Score Drift in 2026* — the three-flavor taxonomy this page uses; the GPT-4 Turbo silent-update story; rolling-mean-on-spans approach. [futureagi.com/blog](https://futureagi.com/blog/what-is-llm-drift-2026).
- Galtea (May 2026), *The complete guide for LLM evaluations in 2026* — production-monitoring patterns at 5-10% sampling rate; the "changes that happen to you" framing for online evaluation. [galtea.ai/blog](https://galtea.ai/blog/llm-evaluation-complete-guide).
- Evidently AI documentation — the OSS Python library this page uses as a primary tool reference. [evidentlyai.com](https://www.evidentlyai.com/).
- DevOpsRoles (April 2026), *MLOps Model Drift Detection* — concrete KS-test implementation with scipy; the alpha = 0.05 significance pattern. [devopsroles.com](https://www.devopsroles.com/ultimate-strategies-master-mlops-model-drift).
