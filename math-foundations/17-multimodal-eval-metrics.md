# Multimodal evaluation metrics

> Mathematical foundation. About 12 minutes to read. Anchors: [`labs/61-grading-multimodal-rag/`](../labs/61-grading-multimodal-rag/), [`labs/62-ocr-reading-quality/`](../labs/62-ocr-reading-quality/). Builds on [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) and [`14-retrieval-ranking-metrics.md`](./14-retrieval-ranking-metrics.md).

## Why this matters for agentic AI

When a RAG answer depends on text inside an image, correctness is the product of three things going right - the right element retrieved, its text read correctly, and the answer grounded in that text. This page makes that decomposition precise, defines the OCR-reading metrics (edit distance, CER, WER) and their failure on numeric answers, and shows why a single end-to-end accuracy is not invertible to the stage that broke - so you must attribute, not average.

## Edit distance, CER, and WER

The Levenshtein distance $d(a, b)$ between strings $a$ and $b$ is the minimum number of single-character insertions, deletions, and substitutions to turn one into the other. It satisfies the recurrence

$$
d_{i,j} = \begin{cases}
\max(i, j) & \min(i, j) = 0 \\
\min\big(d_{i-1,j} + 1,\; d_{i,j-1} + 1,\; d_{i-1,j-1} + \mathbb{1}[a_i \ne b_j]\big) & \text{otherwise,}
\end{cases}
$$

computed in $O(|a|\,|b|)$ time by dynamic programming. The **Character Error Rate** normalizes it by the reference length,

$$
\text{CER}(r, h) = \frac{d(r, h)}{|r|},
$$

and the **Word Error Rate** is the same edit distance over token sequences instead of characters,

$$
\text{WER}(r, h) = \frac{d_{\text{word}}(r, h)}{N_r},
$$

where $N_r$ is the number of reference words. CER is finer (a one-character typo costs $1/|r|$); WER is coarser but matches how a reader perceives errors. Both are unbounded above when $h$ is much longer than $r$, which is why a verbose hallucination can score CER $> 1$.

**Normalization.** Before scoring, map both strings through a normalizer $\nu$ that removes formatting - lowercasing, whitespace collapse - and report $\text{CER}(\nu(r), \nu(h))$. The requirement on $\nu$ is that it changes only presentation, never content: $\nu$ must not round numbers, strip units, or correct spelling, or the metric stops measuring what you need.

## Why CER is the wrong score for numbers

CER weights every character equally, but the information in a numeric answer is not uniformly distributed over its characters. Two failure modes follow.

*Too lenient.* Misreading $4.2$ as $42$ deletes one character: with reference "4.2 million" ($|r| = 11$), $\text{CER} = 1/11 \approx 0.09$, a near-perfect score for a $10\times$ error. The deleted character carried an order of magnitude; CER cannot see that.

*Too harsh.* "\$4.2M" against "4.2 million" shares almost no characters, so CER is large, yet the value is identical. CER penalizes a correct answer for its format.

The fix is a second, value-aware metric on the answer span. Parse each side to a number $x = \phi(\cdot)$ (handling magnitude words, suffixes, percent) and accept within a relative tolerance:

$$
\text{numeric-match}(r, h) = \mathbb{1}\!\left[\,|\phi(r) - \phi(h)| \le \varepsilon \cdot \max(|\phi(r)|, \delta)\,\right].
$$

Report CER/WER for the read text overall (legibility) and numeric-match (or structured-cell equality) for the answer span (correctness). Neither alone is sufficient: legibility without value-awareness passes the $10\times$ misread; value-awareness without legibility tells you nothing about a table you must read in full.

## Grounding as conditional accuracy

Let $E$ be the retrieved-and-read evidence and $\hat{y}$ the generated answer. Grounding is the event that $\hat{y}$ is derived from $E$ rather than the model's parameters. Operationally, with an entailment or containment test $\text{supp}(\hat{y}, E) \in \{0, 1\}$, the **grounding rate** is

$$
\text{GR} = \mathbb{E}\big[\text{supp}(\hat{y}, E)\big].
$$

Grounding is distinct from correctness. Write $C$ for the event that $\hat{y}$ matches the truth. Then a grounded answer is wrong exactly when the evidence was wrong: $\text{supp}(\hat{y}, E) = 1$ and $C = 0$ implies the error entered before generation - the read text was already incorrect. This is the "grounded but wrong" case, and it is why a faithfully reported misread is charged to OCR-reading, not to grounding.

## The end-to-end decomposition

Define stage-success indicators with their natural conditioning: $R$ (the answer-bearing element is retrieved), $O$ (its text is read correctly, given $R$), $G$ (the answer is grounded in and uses that text, given $O$). If a correct end-to-end answer requires all three,

$$
\Pr[C] = \Pr[R] \cdot \Pr[O \mid R] \cdot \Pr[G \mid O].
$$

End-to-end accuracy is a **product** of stage rates. Two consequences. First, it is not invertible: an accuracy of $0.75$ is consistent with $(\Pr[R], \Pr[O\mid R], \Pr[G\mid O]) = (1, 0.75, 1)$ or $(1, 1, 0.75)$ or many others - the number alone cannot say which stage is leaking. Second, the error mass telescopes into a sum of first-failure contributions:

$$
\Pr[\neg C] = \underbrace{\Pr[\neg R]}_{\text{retrieval}} + \underbrace{\Pr[R]\Pr[\neg O \mid R]}_{\text{OCR-reading}} + \underbrace{\Pr[R]\Pr[O\mid R]\Pr[\neg G \mid O]}_{\text{grounding}}.
$$

Each term is the share of failures whose *first* failing stage is that stage, and the three add up to $1 - \Pr[C]$. This is the attribution [Lab 61](../labs/61-grading-multimodal-rag/) computes empirically: charge each wrong answer to its first failing stage, and the per-stage counts partition the errors. The product form is why you measure the conditional rates $\Pr[O \mid R]$ and $\Pr[G \mid O]$ on the *subset that reached each stage*, not marginally - a high marginal CER on retrieval-missed queries is meaningless.

## What to remember

- CER/WER are edit distances; normalize away formatting first, but never let normalization touch content.
- For numeric and structured answers, add a value-aware match - CER is too lenient on a misread digit and too harsh on a reformat.
- Grounding (derived from evidence) is distinct from correctness; a grounded answer is wrong only when its evidence was wrong, so that failure belongs to reading, not grounding.
- End-to-end accuracy is a product of conditional stage rates and is not invertible; attribute each error to its first failing stage and the per-stage error shares sum to the total.

## See also

- [`14-retrieval-ranking-metrics.md`](./14-retrieval-ranking-metrics.md) - recall@k, the retrieval term in the decomposition.
- [`11-evaluation-metrics.md`](./11-evaluation-metrics.md) - the precision/recall and faithfulness metrics this extends to the multimodal setting.
- [`labs/61-grading-multimodal-rag/`](../labs/61-grading-multimodal-rag/), [`labs/62-ocr-reading-quality/`](../labs/62-ocr-reading-quality/) - the decomposition and the OCR metric, measured.
