# Threshold selection under distribution shift

> Mathematical foundation. About 11 minutes to read. Anchor: [`labs/59-retuning-on-held-out-pairs/`](../labs/59-retuning-on-held-out-pairs/). Builds on [`15-calibration-threshold-selection.md`](./15-calibration-threshold-selection.md).

## Why this matters for agentic AI

Page 15 showed how to pick a threshold by an objective (Youden's $J$). This page is about a trap that appears the moment you *report* how good that threshold is, and about what happens when the data you tuned on stops matching the data you deploy on. Both bite when you swap a stand-in embedder for a real one and re-tune: the re-tuned threshold looks better than it is, and the gain may not transfer. The fix is the same discipline you already apply to a model - hold out, cross-validate, and re-fit when the distribution moves.

## The optimism of in-sample selection

Let a threshold $\tau$ be chosen from a finite candidate set $\{\tau_1, \dots, \tau_m\}$ (the midpoints between sorted scores) to maximize an empirical accuracy $\hat{A}_n(\tau)$ measured on $n$ labeled pairs. Define

$$
\hat{\tau} = \arg\max_{j} \hat{A}_n(\tau_j), \qquad \hat{A}_n(\hat{\tau}) = \max_j \hat{A}_n(\tau_j).
$$

Each $\hat{A}_n(\tau_j)$ is an unbiased estimate of the true accuracy $A(\tau_j)$, with sampling noise of order $1/\sqrt{n}$. The problem is the maximization. The expectation of a maximum of noisy estimates exceeds the maximum of their expectations:

$$
\mathbb{E}\big[\max_j \hat{A}_n(\tau_j)\big] \;\ge\; \max_j \mathbb{E}\big[\hat{A}_n(\tau_j)\big] = \max_j A(\tau_j) = A(\tau^\star),
$$

by Jensen's inequality applied to the convex $\max$ function. So the reported in-sample accuracy is **biased upward**: selection lets $\hat{\tau}$ chase the favorable noise in this particular sample. The gap

$$
\text{optimism} = \mathbb{E}\big[\hat{A}_n(\hat{\tau})\big] - A(\hat{\tau})
$$

is the amount by which tuning-and-reporting-on-the-same-data flatters the threshold.

**How it scales.** Two things drive the optimism: the noise per estimate, which shrinks like $1/\sqrt{n}$, and the number of candidates $m$ you maximize over, which inflates the maximum by roughly $\sqrt{2 \log m}$ standard deviations (the expected maximum of $m$ roughly-Gaussian variables). Combining, the optimism scales on the order of

$$
\text{optimism} \;\sim\; \sqrt{\frac{2 \log m}{n}} \cdot \sigma,
$$

so it is large when $n$ is small or you sweep many thresholds, and vanishes as $n$ grows. This is exactly the curve [Lab 59](../labs/59-retuning-on-held-out-pairs/) measures: a clear gap at $n = 16$ that is gone by $n = 160$. It is also why a threshold sweep over a fine grid on a tiny calibration set is the worst case - many candidates, little data.

## The held-out fix

The unbiased estimate of $A(\hat{\tau})$ separates selection from evaluation. Split the pairs into a tuning set and a disjoint test set; choose $\hat{\tau}$ on the first and measure on the second:

$$
\hat{A}^{\text{held-out}} = \hat{A}_{\text{test}}(\hat{\tau}), \qquad \hat{\tau} = \arg\max_j \hat{A}_{\text{tune}}(\tau_j).
$$

Because $\hat{\tau}$ is fixed before the test set is seen, $\hat{A}^{\text{held-out}}$ is unbiased for $A(\hat{\tau})$. **$k$-fold cross-validation** reuses the data: partition into $k$ folds, and for each fold tune on the other $k-1$ and evaluate on the held-out fold, then average. It trades a little bias for much lower variance than a single split, which matters when labeled pairs are scarce. A useful by-product is the spread of the selected $\hat{\tau}$ across folds: a wide spread means the threshold is poorly determined and you need more pairs before trusting any single value.

The operational rule: **cross-validate to estimate the accuracy; refit the deployed threshold on all the data.** The CV estimate describes the threshold you will ship; the ship threshold itself uses every pair you have.

## Distribution shift

In-sample optimism assumes the tuning and test pairs are drawn from the same distribution. They often are not. When you re-tune after swapping the embedder, the cosine distribution itself changes - a sentence-transformer separates reflows from edits differently than a char-trigram bag, so the old threshold is simply wrong, not merely optimistic. More subtly, the *deployment* distribution of edits drifts: a calibration set built from last quarter's reflow/edit pairs may under-represent the kinds of edits your documents now see (covariate shift on the inputs, or a changed base rate of real edits).

Two consequences. First, a threshold and its CV estimate are valid only for the distribution they were fit on; treat "the embedder changed" or "the document mix changed" as a trigger to re-tune, the same way you retrain a model on drift. Second, if the base rate of true changes in deployment differs from the calibration set, an accuracy-tuned threshold is miscalibrated for the operating point you care about - tune on a cost-weighted objective (page 15) using the deployment base rate, or re-balance the calibration set to match it.

## What to remember

- Tuning a threshold and reporting its accuracy on the same data is optimistically biased; the bias grows with the number of candidate thresholds and shrinks like $1/\sqrt{n}$.
- Estimate out-of-sample with a held-out set or cross-validation; refit the shipped threshold on all the data, and watch the cross-fold spread of $\hat{\tau}$ as a signal of whether you have enough pairs.
- A threshold is valid only for the distribution it was fit on - re-tune when the embedder or the data distribution changes, and match the calibration base rate to deployment.

## See also

- [`15-calibration-threshold-selection.md`](./15-calibration-threshold-selection.md) - ROC / Youden's $J$ and isotonic calibration, the selection this page evaluates out-of-sample.
- [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) - the estimators whose sampling noise drives the optimism.
- [`labs/59-retuning-on-held-out-pairs/`](../labs/59-retuning-on-held-out-pairs/) - the optimism curve, measured.
