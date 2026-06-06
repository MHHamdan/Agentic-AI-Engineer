# Nugget coverage metrics

> Mathematical foundation. About 10 minutes to read. Anchor: [`labs/64-nugget-based-evaluation/`](../labs/64-nugget-based-evaluation/). Builds on [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) and [`17-multimodal-eval-metrics.md`](./17-multimodal-eval-metrics.md).

## Why this matters for agentic AI

Long-form and report-generation RAG cannot be scored against a single gold string. The 2026 standard, nugget-based evaluation, instead scores two things: how completely the report covers the facts it should (coverage) and how well its sentences are supported by the evidence they cite (citation). This page makes both precise, shows that one is a recall measure and the other a precision measure, and explains why you summarize them with a harmonic combination rather than an average - because a plain mean hides exactly the axis that is failing.

## Coverage as weighted recall

Let the information need decompose into nuggets $\{1, \dots, M\}$, each with a weight $w_i$ (vital nuggets weigh more than okay nuggets) and a support score $s_i \in \{0, \tfrac{1}{2}, 1\}$ assigned by the judge for No / Partial / Full support. Coverage is the weighted fraction of supportable nugget mass the report actually supports:

$$
\text{Coverage} = \frac{\sum_{i=1}^{M} s_i\, w_i}{\sum_{i=1}^{M} w_i}.
$$

This is a **recall** measure: the denominator is fixed by the reference nugget set (everything that *should* appear), and the numerator credits how much of it the report covers, with partial credit for partial support. Restricting the sum to vital nuggets ($w_i$ for vital only) gives the strict vital-coverage; including okay nuggets at a lower weight gives the fuller score. Either way, the report cannot raise coverage by writing more - only by supporting more of the required facts.

## Citation as precision

Citation is scored on what the report *emitted*. Let the report have sentences $\{1, \dots, N\}$, each carrying citations, and let $c_j \in \{0, 1\}$ indicate whether sentence $j$'s cited evidence supports it. The Sentence-Support Rate is

$$
\text{SSR} = \frac{1}{N} \sum_{j=1}^{N} c_j.
$$

This is a **precision** measure: the denominator is the number of sentences the system chose to write, and the numerator is how many are backed by their citations. Unlike coverage, SSR *can* be raised by writing less - a report that emits only the one sentence it is sure of scores SSR $= 1$. That asymmetry is the whole reason the two are reported together.

## Why they are orthogonal, and why you do not average

Coverage and SSR move independently because they are normalized by different sets - the reference nuggets and the emitted sentences. A report can sit at any corner:

| | high coverage | low coverage |
|---|---|---|
| **high SSR** | good report | terse: cites well, omits facts |
| **low SSR** | verbose: covers facts, cites wrong | bad report |

The off-diagonal corners are the interesting ones, and a single summary must not let a report hide in them. The arithmetic mean does exactly that: the "covers everything, cites nothing" report ($\text{Coverage} = 1$, $\text{SSR} = 0$) averages to $0.5$, which reads as half-good. The harmonic mean (an $F$-score over the two axes) does not:

$$
F_\beta = (1 + \beta^2)\,\frac{\text{Coverage}\cdot \text{SSR}}{\beta^2\,\text{Coverage} + \text{SSR}}, \qquad F_1 = \frac{2\,\text{Coverage}\cdot \text{SSR}}{\text{Coverage} + \text{SSR}}.
$$

For that report $F_1 = 0$: a zero on either axis drives the summary to zero, which is the behavior you want. For the "cites well, omits facts" report ($\text{Coverage} = 0.5$, $\text{SSR} = 1$), $F_1 = 0.67$ versus an arithmetic $0.75$ - the harmonic mean penalizes the imbalance. Use $\beta > 1$ to weight coverage over citation (the 2026 emphasis, since coverage is the harder axis) and $\beta < 1$ for the reverse. But the safest report is still both numbers plus the attribution - which nuggets are missing, which sentences are unsupported - because the $F$-score, like any scalar, throws away the diagnosis.

## The metric is only as good as the nuggets

Coverage is defined against the nugget set, so a bad nuggetization makes it meaningless: nuggets that are redundant, off-topic, or wrongly marked vital corrupt the denominator. This is why the AutoNuggetizer line of work calibrates LLM-generated nuggets against human-edited ones and reports the agreement; treat the nuggetizer as a measured component, not an oracle. The same caution applies to the support and citation judges - they are models, with their own precision and recall against human labels, and a coverage number is only interpretable alongside that calibration.

## What to remember

- Coverage is weighted recall over the reference nuggets (with partial credit and vital/okay weights); it cannot be gamed by writing more.
- Sentence-support rate is precision over emitted sentences; it *can* be gamed by writing less, which is why it never travels alone.
- The two are orthogonal; summarize with a harmonic ($F_\beta$) combination, never a plain mean, and prefer reporting both axes plus the attribution.
- Coverage is only as trustworthy as the nuggetization; calibrate the nuggetizer and the judges against human labels.

## See also

- [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) - precision, recall, and $F$-scores in general.
- [`17-multimodal-eval-metrics.md`](./17-multimodal-eval-metrics.md) - the same report-both-axes, attribute-the-failure discipline for multimodal RAG.
- [`labs/64-nugget-based-evaluation/`](../labs/64-nugget-based-evaluation/) - coverage and citation, measured.
