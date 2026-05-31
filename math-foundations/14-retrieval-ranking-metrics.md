# Retrieval and ranking metrics

> Mathematical foundation. About 11 minutes to read. Anchor: [`concepts/evaluation/rag-evaluation-framework.md`](../concepts/evaluation/rag-evaluation-framework.md).

## Why this matters for agentic AI

Retrieval quality sets the ceiling on RAG answer quality: the generator cannot synthesize a correct answer from chunks that were never retrieved. These metrics let you measure retrieval in isolation, so when an answer is wrong you can tell whether the retriever missed the evidence or the generator misused it. Picking the wrong metric (accuracy on a ranking problem, say) hides real failures.

## The equations

Let a query have a set of relevant documents, and let the retriever return a ranked list of $k$ documents. Define an indicator $\text{rel}(i) = 1$ if the document at rank $i$ is relevant, else $0$.

**Precision@k** - fraction of the top-$k$ that are relevant:

$$
P@k = \frac{1}{k} \sum_{i=1}^{k} \text{rel}(i).
$$

**Recall@k** - fraction of all relevant documents that appear in the top-$k$:

$$
R@k = \frac{\sum_{i=1}^{k} \text{rel}(i)}{|\text{relevant}|}.
$$

**Reciprocal Rank** - one over the rank of the first relevant document. **MRR** averages it over a set of $Q$ queries:

$$
\text{MRR} = \frac{1}{Q} \sum_{q=1}^{Q} \frac{1}{\text{rank}_q},
$$

where $\text{rank}_q$ is the position of the first relevant document for query $q$ (and $1/\text{rank}_q = 0$ if none is found).

**Average Precision (AP)** - precision averaged at every rank where a relevant document appears. **MAP** averages AP over queries:

$$
\text{AP} = \frac{1}{|\text{relevant}|} \sum_{i=1}^{k} P@i \cdot \text{rel}(i), \qquad \text{MAP} = \frac{1}{Q} \sum_{q=1}^{Q} \text{AP}_q.
$$

**Discounted Cumulative Gain (DCG@k)** and its normalized form **NDCG@k**, which support graded relevance $\text{gain}(i)$ (not just binary):

$$
DCG@k = \sum_{i=1}^{k} \frac{\text{gain}(i)}{\log_2(i + 1)}, \qquad NDCG@k = \frac{DCG@k}{IDCG@k},
$$

where $IDCG@k$ is the DCG of the ideal ranking (relevant documents sorted by descending gain).

**Symbols:**

- $k$ - the cutoff rank (top-$k$).
- $\text{rel}(i)$ - binary relevance of the document at rank $i$.
- $\text{gain}(i)$ - graded relevance of the document at rank $i$ (for example, 0/1/2/3).
- $|\text{relevant}|$ - total number of relevant documents for the query.
- $\text{rank}_q$ - rank of the first relevant document for query $q$.
- $Q$ - number of queries.
- $IDCG@k$ - the best possible DCG@k for this query.

## How to read these equations

**Precision@k** asks: of what I showed, how much was good? **Recall@k** asks: of what was good, how much did I show? They trade off: raising $k$ usually raises recall and lowers precision.

**MRR** cares only about the first relevant result. It is the right metric when there is essentially one right answer and you care how high it ranks (navigational search, single-fact lookup).

**MAP** rewards getting all relevant documents ranked high, averaging precision at each relevant hit. It is the metric when there are several relevant documents and the full ordering matters.

**NDCG** is the most general: it supports graded relevance (a document can be "perfectly relevant," "somewhat relevant," or "irrelevant") and discounts gains logarithmically by rank, so a relevant document at rank 1 counts more than the same document at rank 5. Normalizing by the ideal DCG puts the score in $[0, 1]$ and makes it comparable across queries with different numbers of relevant documents. This is why retrieval benchmarks like BEIR report NDCG@10.

## Mathematical intuition

Three things to internalize.

**Rank-unaware metrics hide ranking failures.** Precision@k and recall@k treat all $k$ positions equally: a relevant document at rank 1 and at rank 10 contribute the same. For RAG this matters because of the lost-in-the-middle effect (page 13): a relevant chunk buried at rank 8 of 10 may as well not have been retrieved. Rank-aware metrics (MRR, MAP, NDCG) capture this; rank-unaware ones do not.

**The log discount in NDCG encodes a model of attention.** The $1/\log_2(i+1)$ term says the value of a result decays with rank, but slowly. The choice of logarithm is conventional, not derived; it roughly matches how much less likely a user (or a generator) is to attend to lower-ranked items. The exact discount matters less than the fact that there is one.

**Context precision and context recall are these metrics, reframed for RAG.** The Ragas-style "context precision" is precision computed over the retrieved context chunks for a single query; "context recall" is recall of the information needed to answer. The math is the classical IR math above; the framing is per-query over the generator's actual context window. Knowing the underlying equations means you are not learning two separate things.

## Where this appears in agentic systems

- **Choosing $k$.** Recall@k rises and precision@k falls as $k$ grows. The right $k$ balances "did we get the evidence" against "did we flood the context with distractors." Measure both curves on your eval set rather than guessing.
- **Comparing retrieval strategies.** Dense vs BM25 vs hybrid vs reranked is an NDCG@10 (or recall@k) comparison on a labeled set. The [RAG evaluation framework](../concepts/evaluation/rag-evaluation-framework.md) Layer 2 is exactly this.
- **Detecting ranking regressions in CI.** A change that improves recall@10 but tanks MRR has moved relevant chunks down the ranking. Only rank-aware metrics catch this; it is a common silent regression.
- **Reranker evaluation.** A reranker should improve NDCG and MRR (it reorders) without necessarily changing recall@k (it works on already-retrieved candidates). Measuring the right metric tells you whether the reranker is doing its job.

## Code example

Compute all of these from a ranked list of relevance labels. No external dependencies.

```python
import math

def precision_at_k(rels: list[int], k: int) -> float:
    """rels: relevance (0/1) in rank order. Returns P@k."""
    topk = rels[:k]
    return sum(topk) / k if k else 0.0

def recall_at_k(rels: list[int], k: int, total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    return sum(rels[:k]) / total_relevant

def reciprocal_rank(rels: list[int]) -> float:
    for i, r in enumerate(rels, start=1):
        if r:
            return 1.0 / i
    return 0.0

def average_precision(rels: list[int], total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    hits, score = 0, 0.0
    for i, r in enumerate(rels, start=1):
        if r:
            hits += 1
            score += hits / i          # precision@i at this relevant hit
    return score / total_relevant

def dcg_at_k(gains: list[float], k: int) -> float:
    return sum(g / math.log2(i + 1) for i, g in enumerate(gains[:k], start=1))

def ndcg_at_k(gains: list[float], k: int) -> float:
    ideal = sorted(gains, reverse=True)
    idcg = dcg_at_k(ideal, k)
    return dcg_at_k(gains, k) / idcg if idcg else 0.0

# Worked example: one query, 5 retrieved docs.
# Binary relevance for P/R/MRR/MAP; graded gains for NDCG.
rels  = [0, 1, 0, 1, 0]      # relevant docs at ranks 2 and 4
gains = [0, 2, 0, 3, 1]      # graded relevance (0..3)
total_relevant = 2           # this query has 2 relevant docs in the corpus

print(f"P@3   = {precision_at_k(rels, 3):.3f}")        # 1/3 = 0.333
print(f"R@5   = {recall_at_k(rels, 5, total_relevant):.3f}")  # 2/2 = 1.000
print(f"RR    = {reciprocal_rank(rels):.3f}")          # first hit at rank 2 -> 0.500
print(f"AP    = {average_precision(rels, total_relevant):.3f}")  # (1/2 + 2/4)/2 = 0.500
print(f"NDCG@5 = {ndcg_at_k(gains, 5):.3f}")           # DCG / IDCG -> 0.618
```

Expected output:

```
P@3   = 0.333
R@5   = 1.000
RR    = 0.500
AP    = 0.500
NDCG@5 = 0.618
```

Walk the NDCG by hand to check the code (the code uses the rank-starts-at-1, denominator $\log_2(i+1)$ convention):

- $DCG@5 = \frac{2}{\log_2 3} + \frac{3}{\log_2 5} + \frac{1}{\log_2 6} = 1.262 + 1.292 + 0.387 = 2.941$ (gains at ranks 2, 4, 5).
- Ideal ordering of the gains is $[3, 2, 1, 0, 0]$, so $IDCG@5 = \frac{3}{\log_2 2} + \frac{2}{\log_2 3} + \frac{1}{\log_2 4} = 3.000 + 1.262 + 0.500 = 4.762$.
- $NDCG@5 = 2.941 / 4.762 = 0.618$.

If your by-hand number disagrees with the code, recheck the denominator convention first; the $\log_2(i+1)$ form (rather than $\log_2 i$, which divides by zero at rank 1) is the common one and what the code above uses. Treat the code as the source of truth.

## Common mistakes

- **Using accuracy on a ranking problem.** "The right doc was in the results" (accuracy/hit-rate) ignores where it ranked. For RAG, rank matters because of context-window position effects. Use MRR or NDCG.
- **Reporting a single $k$.** Recall@1 and recall@20 tell different stories. Report a small and a large $k$, or the full curve, so the precision-recall tradeoff is visible.
- **Mixing binary and graded relevance.** P/R/MRR/MAP use binary relevance; NDCG uses graded. Do not feed graded gains into MAP or binary labels into NDCG and expect meaningful numbers.
- **Forgetting the denominator in recall.** Recall needs the total count of relevant documents in the corpus, not just those retrieved. If you only count retrieved relevant docs you are computing precision, not recall.
- **Comparing NDCG across queries without normalization.** Raw DCG is not comparable across queries with different numbers of relevant docs. Always normalize (the N in NDCG) before averaging.

## Repo cross-references

- [`concepts/evaluation/rag-evaluation-framework.md`](../concepts/evaluation/rag-evaluation-framework.md) - Layer 2 (component metrics) uses these directly.
- [`concepts/evaluation/retrieval-metrics.md`](../concepts/evaluation/retrieval-metrics.md) - the engineering treatment with production examples.
- [`concepts/rag/reranking.md`](../concepts/rag/reranking.md) - what a reranker changes (NDCG and MRR up; recall flat).
- [Lab 07 - Retrieval strategies and reranking](../labs/07-retrieval-strategies-and-reranking/) and [Lab 09 - Evaluating agentic RAG](../labs/09-evaluating-agentic-rag/) - implementations.

## Related pages

- [02 - Embeddings and vector similarity](./02-embeddings-vector-similarity.md) - how the ranking these metrics score is produced.
- [03 - RAG formulation](./03-rag-formulation.md) - where retrieval quality enters the RAG equation.
- [11 - Evaluation metrics](./11-evaluation-metrics.md) - precision, recall, F1, and faithfulness for the generation side.
- [13 - Context-window optimization](./13-context-window-optimization.md) - why rank position matters (lost in the middle).
- [Glossary: NDCG, MRR, MAP, BM25, Reranking](../glossary/terms.md) - short definitions.

## References

- Manning, C., Raghavan, P., and Schutze, H. (2008). [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/), Ch. 8. Cambridge University Press. The canonical treatment of precision, recall, MAP, and NDCG.
- Jarvelin, K., and Kekalainen, J. (2002). [*Cumulated Gain-based Evaluation of IR Techniques*](https://dl.acm.org/doi/10.1145/582415.582418). ACM TOIS. The original DCG and NDCG definitions.
- Thakur, N., et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS. Why NDCG@10 is the standard retrieval-benchmark metric.
- Es, S., et al. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). Defines context precision and context recall as RAG-specific framings of these metrics.
- Robertson, S., and Zaragoza, H. (2009). [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.nowpublishers.com/article/Details/INR-019). Foundations and Trends in IR. The sparse-retrieval scoring function these metrics are often used to evaluate.
