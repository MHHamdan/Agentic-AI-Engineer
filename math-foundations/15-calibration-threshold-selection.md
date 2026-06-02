# Calibration and threshold selection

> Mathematical foundation. About 12 minutes to read. Anchor: [`labs/55-calibrated-detection-judgment/`](../labs/55-calibrated-detection-judgment/) and [`concepts/observability/`](../concepts/observability/from-stand-ins-to-production.md).

## Why this matters for agentic AI

Two recurring jobs in an agent's observability loop are the same problem in disguise: turning a continuous or coarse score into a decision. A change detector turns a cosine similarity into "changed / not changed." A judge turns an ordinal rating into "ship / block." Both need a cutoff, and both fail when the cutoff is guessed instead of fit. This page covers picking a threshold from labeled data (ROC and Youden's $J$) and correcting a monotone-but-nonlinear bias (isotonic regression), which together replace the fixed-0.98 cosine cutoff and the constant judge shift used as stand-ins earlier in the path.

## Threshold selection

Let a detector produce a score $s \in \mathbb{R}$ for each item, with a label $y \in \{0, 1\}$ (here $y = 1$ means "meaning changed"). A threshold $\tau$ turns the score into a prediction $\hat{y} = \mathbb{1}[s < \tau]$. Sweeping $\tau$ traces out the true-positive and false-positive rates:

$$
\text{TPR}(\tau) = \frac{\#\{s < \tau,\, y = 1\}}{\#\{y = 1\}}, \qquad
\text{FPR}(\tau) = \frac{\#\{s < \tau,\, y = 0\}}{\#\{y = 0\}}.
$$

The curve $\big(\text{FPR}(\tau), \text{TPR}(\tau)\big)$ over all $\tau$ is the **ROC curve**. A single operating point is chosen by an objective. A common, prior-free choice is **Youden's $J$**:

$$
J(\tau) = \text{TPR}(\tau) - \text{FPR}(\tau), \qquad \tau^\star = \arg\max_\tau J(\tau).
$$

$J$ is the vertical distance from the ROC curve to the diagonal; maximizing it picks the threshold that best separates the two classes without assuming their relative cost. When the classes have different costs (a missed meaning-change versus a false alarm that wakes on-call), replace $J$ with a cost-weighted objective, or maximize $F_\beta$:

$$
F_\beta = (1 + \beta^2)\,\frac{\text{precision} \cdot \text{recall}}{\beta^2\,\text{precision} + \text{recall}}.
$$

**Why a fixed cutoff fails.** A guessed threshold like $\tau = 0.98$ is only optimal if the score distributions of the two classes happen to separate there. With real embeddings, reflows (same meaning, reformatted) and small meaning-changes produce overlapping cosine ranges, so $0.98$ sits inside the overlap: it flags many reflows as changes (high FPR) while still missing some edits. Fitting $\tau^\star$ on a labeled held-out set of reflow/edit pairs moves the cutoff into the gap between the class modes, cutting the false-alarm rate at equal or better recall. The cost of being wrong here is a noisy alert channel, which is its own failure mode.

## Isotonic regression (monotone calibration)

A judge (or any scorer) can be biased in a way that a constant offset cannot fix. Suppose the judge's score $j$ relates to the gold score $g$ by a function that is monotone non-decreasing but not affine, for example one that compresses the low end:

$$
g = 0,1,2,3 \;\longmapsto\; j = 0,0,1,2.
$$

An additive correction $j \mapsto j + c$ uses one parameter and cannot bend: choosing $c$ to fix the high end overshoots the low end and vice versa. **Isotonic regression** fits a free monotone function instead. Given calibration pairs $(j_i, g_i)$, it solves

$$
\min_{f \text{ non-decreasing}} \sum_i w_i \big(f(j_i) - g_i\big)^2,
$$

the least-squares fit subject only to $f$ being non-decreasing. The solution is a step function, and the standard algorithm is **pool adjacent violators (PAVA)**:

1. Sort the pairs by $j$ and average duplicates, giving an initial sequence of block values.
2. Scan left to right. Whenever a block value exceeds the next block's value (a monotonicity violation), merge the two blocks and replace both with their weighted mean.
3. A merge can create a new violation with the previous block, so step back one and repeat until the sequence is non-decreasing.

PAVA runs in $O(n)$ after the sort and returns the unique monotone least-squares fit. Applied to the example above it recovers a map close to $j = 0 \mapsto 0.5,\ 1 \mapsto 2,\ 2 \mapsto 3$, which the additive shift cannot represent. On held-out data this raises the quadratic-weighted agreement (see [page 11](./11-evaluation-metrics.md)) above what the shift achieves, because it corrects the shape of the bias, not just its average.

**Why monotone and not arbitrary.** Constraining $f$ to be non-decreasing encodes a real assumption: a higher judge score should never map to a lower gold estimate. Dropping the constraint (fitting an arbitrary lookup) overfits the calibration sample and can invert the ordering, which is worse than the original bias. Monotonicity is the minimum structure that lets the fit bend without memorizing. In production, `sklearn.isotonic.IsotonicRegression` is the same fit; PAVA is what it runs.

## Conjunctive versus weighted decisions

A multi-dimensional gate combines per-dimension scores $x_d$ into one decision. Two rules:

$$
\text{conjunctive:} \quad \text{pass} \iff \forall d,\ x_d \ge \tau_d, \qquad
\text{weighted:} \quad \text{pass} \iff \sum_d w_d\, x_d \ge \Theta.
$$

The conjunctive (all-dimensions-pass) rule treats every dimension as a hard floor; a release that is excellent on faithfulness and relevance but one level low on completeness is blocked. The weighted rule lets one strong dimension compensate for a weaker one, with the weights $w_d$ encoding which dimensions the product owner values. Neither is "correct" - they encode different risk postures, and the choice is a product decision, not a statistical one. A common hybrid keeps a hard floor on a safety-critical dimension and weights the rest:

$$
\text{pass} \iff \big(x_{\text{safety}} \ge \tau_{\text{safety}}\big) \;\wedge\; \Big(\sum_{d \ne \text{safety}} w_d\, x_d \ge \Theta\Big).
$$

## What to remember

- A threshold is a fitted quantity, not a guess: choose it on labeled held-out data by an explicit objective ($J$ for prior-free separation, $F_\beta$ or a cost-weighted rule when errors differ in cost).
- A monotone-but-nonlinear bias needs a monotone fit (isotonic / PAVA), not a constant shift; the monotonicity constraint is what keeps the fit from overfitting.
- Combining dimensions is a policy choice: conjunctive floors versus weighted trade-offs encode different risk postures, and the weights belong to whoever owns the release.

## See also

- [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) - quadratic-weighted kappa, the ordinal agreement isotonic calibration improves.
- [`14-retrieval-ranking-metrics.md`](./14-retrieval-ranking-metrics.md) - precision/recall, the ingredients of $F_\beta$.
- [`labs/55-calibrated-detection-judgment/`](../labs/55-calibrated-detection-judgment/) - the runnable version of every equation here.
