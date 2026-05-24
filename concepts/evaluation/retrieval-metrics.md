# Retrieval metrics

> 🟢 Stable · ⏱ ~11 min read · 🏷 rag, evaluation, retrieval, metrics

## TL;DR

Retrieval metrics measure "did the right chunks make it into the top-k?" — a ranking question, well-studied in classical information retrieval since the 1960s. Six metrics matter for RAG work, each with different sensitivities:

- **Hits@k** — did *any* relevant chunk make the top-k? Binary; easiest to interpret.
- **Recall@k** — what fraction of relevant chunks made the top-k? Penalizes missing relevant chunks.
- **Precision@k** — what fraction of the top-k is relevant? Penalizes returning irrelevant chunks.
- **MRR** (Mean Reciprocal Rank) — how high up was the *first* relevant chunk? Captures "how fast did we find it?"
- **nDCG@k** — graded relevance with position discount. The IR community's standard but often overrated for RAG.
- **Mean rank of expected chunk** — average rank of the expected chunk across queries. Distribution-friendly; great for debugging.

This page covers each: the formula in plain Python, what it reveals, what it hides. [Lab 09](../../labs/09-evaluating-agentic-rag/) implements all of them from scratch.

---

## Setup — what these metrics consume

Every retrieval metric takes the same inputs:

- A **ranked list** of chunks from your retriever for one query (the top-k or top-50).
- A set of **relevant chunks** from your eval set (`expected_chunks` or any chunk in `expected_doc`).

The metric collapses these into a single number per query. You then average across queries to get an aggregate.

```python
# What every metric looks like in shape
def metric(
    ranked_results: list[str],  # chunk_ids in rank order from retriever
    relevant: set[str],         # chunk_ids known to be relevant from eval set
    k: int = 10,                # cutoff
) -> float:
    ...
```

## Hits@k — the simplest metric

Did *any* relevant chunk make the top-k?

```python
def hits_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(c in relevant for c in ranked[:k]) else 0.0
```

Averaged across queries, this gives you the **hit rate** — fraction of queries where retrieval surfaced at least one relevant chunk.

**Reveals:** Coverage. If hits@10 is 0.7, retrieval is missing 30% of queries entirely — those queries can never be answered correctly downstream.

**Hides:** Quality within the top-k. A query with one relevant chunk at rank 10 counts the same as a query with three relevant chunks at ranks 1, 2, 3.

**When it's the right metric:** Early debugging. If hits@k is 0.5, no other metric matters until you fix this. Anthropic's contextual retrieval paper uses Pass@k (= 1 - hits failure rate) as its headline number for exactly this reason — at large k it's the cleanest signal that retrieval is or isn't finding the right doc.

## Recall@k — fraction of relevant chunks retrieved

Of the chunks that *should* have been retrieved, what fraction were?

```python
def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0  # undefined; convention varies
    retrieved_relevant = set(ranked[:k]) & relevant
    return len(retrieved_relevant) / len(relevant)
```

**Reveals:** Completeness. Useful when queries have multiple relevant chunks and you need to surface all of them (multi-chunk synthesis, comparative questions).

**Hides:** Rank. A query with 3 relevant chunks at ranks 1, 8, 10 has the same recall@10 as one with them at ranks 1, 2, 3. From the LLM's perspective the second is much better — the relevant chunks come first.

**Gotcha:** When most queries have only one relevant chunk, recall@k and hits@k are the same metric, just renamed. The distinction only matters for multi-relevant queries.

**When it's the right metric:** Multi-chunk queries; benchmarking against published retrieval results (which usually report recall).

## Precision@k — fraction of top-k that's relevant

Of the chunks you *did* retrieve, what fraction are relevant?

```python
def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if k == 0:
        return 0.0
    retrieved_relevant = set(ranked[:k]) & relevant
    return len(retrieved_relevant) / k
```

**Reveals:** Density of relevant content in the top-k. If precision@5 is 0.2 (one relevant chunk out of five), the LLM is reading mostly noise.

**Hides:** Whether you got the relevant chunks at all. Precision@5 can be 0.2 with the *one* relevant chunk at rank 1 (good) or rank 5 (the model has to read past 4 irrelevant chunks first; bad).

**Gotcha:** Precision@k has a hard ceiling when there are fewer than k relevant chunks in the corpus. If only 2 chunks are relevant and you ask for precision@10, the maximum is 0.2. This makes per-query precision values not directly comparable when relevance counts differ.

**When it's the right metric:** When you care about noise in the top-k — important for token budget reasons (each irrelevant chunk wastes context window) and for [failure mode 5 (redundant top-k)](../rag/retrieval-failure-modes.md#failure-mode-5-the-top-k-are-redundant).

## MRR — Mean Reciprocal Rank

How fast did we find the *first* relevant chunk?

For one query: find the rank of the first relevant chunk in the ranked list; reciprocal rank is `1/rank`. If no relevant chunk appears in the top-k, reciprocal rank is 0.

```python
def reciprocal_rank(ranked: list[str], relevant: set[str], k: int) -> float:
    for i, chunk_id in enumerate(ranked[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / i
    return 0.0


def mrr(rrs: list[float]) -> float:
    return sum(rrs) / len(rrs) if rrs else 0.0
```

A query with the first relevant chunk at rank 1 contributes 1.0; rank 2 contributes 0.5; rank 5 contributes 0.2; rank 10 contributes 0.1.

**Reveals:** How buried the first relevant chunk is. Sensitive to small rank improvements at the top — a chunk moving from rank 3 to rank 1 contributes meaningfully to MRR.

**Hides:** Whether there are *more* relevant chunks below the first one. MRR only cares about the topmost relevant chunk.

**When it's the right metric:** When the user/agent reads chunks top-down and stops as soon as it has the answer (Lab 06's pattern). The agent's experience is dominated by the first useful chunk; MRR aligns with that.

**Caveat:** MRR is sensitive but interpreted awkwardly. "MRR of 0.5" means *on average* the first relevant chunk is at rank 2, but mean-of-reciprocals doesn't actually correspond to a clean "average rank" interpretation. Use it relatively (did MRR go up after my change?) rather than absolutely.

## nDCG@k — graded relevance with position discount

The classical IR community's preferred metric. **N**ormalized **D**iscounted **C**umulative **G**ain at cutoff k.

The intuition: each chunk has a *relevance grade* (binary 0/1, or graded 0/1/2/3 for irrelevant/partial/relevant/highly relevant). Chunks earlier in the ranking count more, with a logarithmic discount. The result is normalized against the best possible ranking so it falls in [0, 1].

```python
import math


def dcg_at_k(ranked: list[str], relevance: dict[str, float], k: int) -> float:
    """ranked: chunk_ids in rank order; relevance: chunk_id → grade."""
    total = 0.0
    for i, chunk_id in enumerate(ranked[:k], start=1):
        rel = relevance.get(chunk_id, 0.0)
        # Position discount: log2(rank + 1). Rank 1 → divide by log2(2) = 1.
        total += rel / math.log2(i + 1)
    return total


def ndcg_at_k(ranked: list[str], relevance: dict[str, float], k: int) -> float:
    actual = dcg_at_k(ranked, relevance, k)
    # Ideal DCG: same chunks sorted by relevance grade descending
    ideal_ranking = sorted(relevance.keys(), key=lambda c: -relevance[c])
    ideal = dcg_at_k(ideal_ranking, relevance, k)
    return actual / ideal if ideal > 0 else 0.0
```

**Reveals:** Position-aware quality. A chunk moving from rank 5 to rank 1 lifts nDCG more than a chunk moving from rank 50 to rank 45.

**Hides:** Coverage. Like MRR, nDCG mostly cares about the top of the ranking.

**Gotcha:** nDCG@k is overrated for RAG. It was designed for *search engines* where the user sees the entire ranked list and clicks results from anywhere on the page. In RAG, the LLM reads the top-k as a batch — position within the top-k matters less than which chunks are *in* the top-k. For RAG, recall@k and hits@k often tell you more about what'll happen downstream than nDCG.

**When it's the right metric:** Comparing against published retrieval benchmarks (BEIR uses nDCG@10) or when you have graded relevance labels (most RAG eval sets have only binary labels).

## Mean rank of expected chunk

For each query with a known expected_chunk, the rank at which the retriever returned it. Average across queries.

```python
def rank_of_expected(ranked: list[str], expected: str) -> int | None:
    for i, chunk_id in enumerate(ranked, start=1):
        if chunk_id == expected:
            return i
    return None  # not found in top-k


def mean_rank(ranks: list[int | None], missing_penalty: int = 100) -> float:
    """missing_penalty: what to count when expected chunk wasn't retrieved."""
    return sum(r if r is not None else missing_penalty for r in ranks) / len(ranks)
```

This isn't a textbook metric, but it's the one Labs 06-08 already use informally and it's the most useful for **debugging**.

**Reveals:** Rank distribution. Where, exactly, is the right chunk landing? If mean rank is 8.3 with most queries at rank 1-3 and a few at rank 50, you have a long-tail problem that aggregate metrics hide.

**Hides:** Less than you'd think — but it requires you to look at the distribution, not just the mean. Always plot the per-query ranks; the histogram is more informative than the mean.

**When it's the right metric:** Debugging. When you ask "did retrieval get *worse* on which specific queries?", per-query rank is what you compare. Aggregate hits@k can stay flat while ranks within the top-k shift dramatically.

## Which metrics to compute when

A pragmatic decision tree:

```text
Are you debugging a specific failure?
   YES → Look at per-query rank of expected chunk.
         Compute aggregate hits@k as a sanity check.
         Skip everything else.

Are you A/B testing a retrieval change?
   YES → Compute recall@5, recall@10, MRR, mean rank.
         Slice by query category.
         Don't trust a single aggregate.

Are you benchmarking against published baselines?
   YES → Compute nDCG@10 (BEIR's convention) and recall@100.
         Use the exact same formula the baseline uses.

Are you in CI catching regressions?
   YES → Track hits@5, MRR. Alert on absolute change > 0.05 from
         baseline; warn on > 0.02. Slice by category.
```

For Path 02 / Lab 09, you'll see recall@5, recall@10, MRR, and mean rank. These cover the most common needs without the overhead of full graded-relevance annotations that nDCG requires.

## What none of these metrics tell you

Three categories of failure that retrieval metrics miss entirely:

### Retrieved the right chunk, but it's incomplete

The chunker split a fact across two chunks. Your retriever returns one of them at rank 1 — recall@1 = 1.0, MRR = 1.0, everything looks great. But the LLM reading that chunk only sees half the fact. Retrieval metrics call this a win; the downstream generation will fail.

The fix isn't a different metric. It's [chunking quality](../rag/chunking-and-indexing.md). Retrieval metrics can't detect chunker problems; only end-to-end evaluation can.

### Retrieved a *similar* chunk, not the *right* chunk

You annotated `expected_chunks: ["02-tool-design.md:1"]`. Retrieval returns `02-tool-design.md:2` at rank 1. Strict recall@1 = 0.0 (chunk:2 isn't the expected one). Loose recall@1 (any chunk from the right *doc*) = 1.0.

Which is the truth? Probably between them — chunk:2 is *nearby* the right answer, may contain it, may not. This is why eval sets often store *both* `expected_doc` and `expected_chunks` and compute metrics both ways. The discrepancy is informative.

### Retrieved a chunk that's irrelevant but *looks* relevant

The user asks about iOS; retrieval returns a chunk about Android that uses the same vocabulary. To the metric, it scores by whether the chunk is in `expected_chunks` — if not, irrelevant, miss. But the metric can't tell whether the chunk was a *plausible mistake* (close but wrong) or a *random miss* (completely off-topic). The downstream impact is different; the metric is the same.

Slicing by `category` and `failure_label` partially compensates. Reading the actual ranked output for failed queries is the rest.

## The discipline of looking at the distribution

The single most important habit for working with retrieval metrics: **look at the histogram, not the mean**.

A pipeline with mean rank = 5.0 could be:
- Every query at rank 5 (uniform mediocrity).
- Half the queries at rank 1, half at rank 9 (bimodal).
- Most queries at rank 1, a handful at rank 50 (long tail).

These three distributions need different interventions. The mean tells you nothing about which one you're in. Always pair aggregate metrics with the per-query distribution — even a quick `sorted(ranks)` printout is enough.

This is also why slicing by category matters more than expanding the metric set. A single per-category mean rank table tells you more than ten aggregate metrics.

## See also

- 📖 [What is RAG evaluation?](./what-is-rag-evaluation.md) — the retrieval/generation split this page assumes.
- 📖 [Eval set construction](./eval-set-construction.md) — where the `relevant` set comes from.
- 📖 [Answer quality metrics](./answer-quality-metrics.md) — what to measure on the generation side.
- 📖 [Retrieval failure modes](../rag/retrieval-failure-modes.md) — the qualitative version; failure modes 1-6 are what these metrics quantify.
- 🧪 [Lab 09](../../labs/09-evaluating-agentic-rag/) — implements all of these from scratch.

## References

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). [*Introduction to Information Retrieval*, Chapter 8: Evaluation in Information Retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html). Cambridge University Press. The textbook source; covers precision, recall, F-measure, MAP, and nDCG with worked examples.
- Järvelin, K., & Kekäläinen, J. (2002). [*Cumulated gain-based evaluation of IR techniques*](https://dl.acm.org/doi/10.1145/582415.582418). ACM Transactions on Information Systems. The original DCG/nDCG paper.
- Craswell, N. (2009). [*Mean Reciprocal Rank*](https://link.springer.com/referenceworkentry/10.1007/978-0-387-39940-9_488). Encyclopedia of Database Systems. The formal definition of MRR; short and clear.
- Thakur, N. et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS 2021. Establishes nDCG@10 + recall@100 as the standard for cross-corpus retrieval evaluation.
- Bajaj, P. et al. (2018). [*MS MARCO: A Human Generated MAchine Reading COmprehension Dataset*](https://arxiv.org/abs/1611.09268). The reference benchmark whose MRR@10 became the default retrieval metric in much of the dense-retrieval literature.
- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). Uses `1 - recall@20` (re-named "retrieval failure rate") as its headline metric — a real-world example of metric choice mattering.
