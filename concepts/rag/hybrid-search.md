# Hybrid search

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, retrieval, bm25, dense

## TL;DR

Dense retrievers (the kind Lab 06 uses) are good at *semantic* matches — "what's the four-phase agent loop?" finds chunks about perceive/reason/act/observe even if those words don't appear in the query. They're worse at *lexical* matches — queries with proper nouns, error codes, API names, or rare technical terms get embedded into a fuzzy semantic neighborhood and the exact match gets ranked alongside merely-related chunks.

BM25 (a 1990s keyword-scoring algorithm that still dominates traditional search) is the opposite: razor-sharp on lexical matches, blind to semantics.

**Hybrid search** is what you get when you run both retrievers and combine their results. The combination consistently beats either alone on real-world workloads. This page explains how, why, and when not to bother.

If you finished [`retrieval-strategies.md`](./retrieval-strategies.md), this is the next concept page. [Lab 07](../../labs/07-retrieval-strategies-and-reranking/) implements hybrid search against the Lab 06 corpus.

---

## What BM25 actually does

BM25 — Best Matching 25, Stephen Robertson's reformulation of probabilistic IR from 1994 — scores documents against queries based on **term frequency and document length normalization**. The simplified intuition:

A document is more relevant if:
- It contains the query's terms (frequency).
- The query's terms are *rare* across the corpus (inverse document frequency).
- The document is short relative to the corpus average (length normalization).

There's no semantic understanding. "Car" and "automobile" are different terms; "ReAct" and "thought-action-observation" are unrelated; "deploy" and "ship" don't match. BM25 sees tokens, not meaning.

What it does well:

- **Exact-match queries** with proper nouns, technical terms, codes, API names.
- **Rare-term retrieval** — a single distinctive term in the query can dominate the score.
- **Length-balanced retrieval** — long chunks aren't unfairly favored just because they have more terms.

What it does poorly:

- **Paraphrased queries.** "How do I send messages between agents?" finds documents that contain the words "send messages between agents" but misses ones about A2A protocols, inter-agent communication, or shared state.
- **Semantic similarity.** "Vector index" and "embedding store" don't match unless those exact words appear.
- **Anything requiring synonymy or polysemy disambiguation.**

This is the *exact* opposite of dense retrieval's failure modes — which is why combining them works.

## Why combine BM25 and dense?

Run both, see what each finds:

| Query | Dense retrieval (MiniLM) | BM25 |
|---|---|---|
| "what's the ReAct pattern" | Top 3 are React-pattern chunks ✓ | Top 1 is React-pattern (proper noun wins) ✓ |
| "agent loop four phases" | Top 1 is the right doc ✓ | Top 1 is the right doc (heading contains exact phrase) ✓ |
| "wrong-but-confident retrieval failure" | Top 1 is the right chunk ✓ | Top 1 is *wrong* — "duplicates/dedupe" doc | 
| "thought trace observation visible" | Decent, ~ rank 2-3 | Strong (these are exact ReAct paper terms) ✓ |
| "what truncates silently" | Top 1 is the embeddings-truncation chunk ✓ | Misses — none of "truncates" or "silently" are corpus tokens |

Each retriever has a non-empty set of queries the other one handles better. The combination has access to both winners' answers.

This is a measured property — empirical studies (Sciavolino et al. 2021, Kamalloo et al. 2023, the BEIR benchmark broadly) consistently find that hybrid retrieval beats dense-alone by 3-15% on retrieval metrics, depending on corpus and query distribution. The gain is biggest for **domain-specific or technical corpora** where proper nouns and codes appear often.

## How to combine them

You have two ranked lists from two retrievers. You need one ranked list out. Three common ways to combine:

### 1. Reciprocal Rank Fusion (RRF) — the safe default

Cormack, Clarke & Büttcher (2009). The idea: ignore the raw scores entirely (they're on incomparable scales) and combine ranks.

For each chunk that appears in either list:

```
RRF_score = sum over each retriever of: 1 / (k + rank_in_that_retriever)
```

where `k` is typically `60` (the paper's constant, which is robust across many settings) and `rank_in_that_retriever` is 1-indexed. Chunks that appear in only one list get a contribution only from that list.

```python
# 10 lines of numpy + dict
def rrf(rankings: dict[str, list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for retriever_name, ranked_ids in rankings.items():
        for rank, chunk_id in enumerate(ranked_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
```

Why RRF is the safe default:

- **Score-scale agnostic.** Dense cosines are `[-1, 1]`, BM25 scores are unbounded. Ranks are integers; comparable directly.
- **Robust to outliers.** A single chunk with an absurd score doesn't dominate.
- **No tuning required.** `k=60` works across many corpora; that's why the paper named the constant.

What it doesn't do: weight one retriever more than the other. If your BM25 is consistently better, RRF won't notice.

### 2. Weighted score combination — when you've measured

If you've measured that one retriever is meaningfully better on your corpus and you want to weight it:

```python
final_score = α * normalize(dense_score) + (1 - α) * normalize(bm25_score)
```

`normalize()` rescales each retriever's scores into `[0, 1]` so they're comparable. `α` is the weight on dense retrieval (so `α=0.7` means "trust dense more").

This works *only* if you've actually measured `α` on a validation set. The default-`α=0.5` version is similar to RRF without the rank-fusion robustness; it's not obviously better unless you tune.

### 3. Cascade — BM25 to filter, dense to rank

Some production systems use BM25 as a first-stage filter (return top-100 by lexical match) and dense retrieval to rerank within that. This works for very large corpora where dense retrieval over everything is expensive, but at the lab-scale corpora most learners work with (thousands or tens of thousands of chunks), it's overkill.

### Which to use

For a tutorial lab and most prototypes: **RRF**. It's simple, robust, and a defensible default.

For production after measurement: weighted combination if you've shown one retriever is reliably better.

For very large corpora (10M+ chunks) where dense retrieval is the cost bottleneck: cascade.

Lab 07 implements RRF from scratch (~10 lines), demonstrates the lift on the Lab 06 corpus, and notes where weighted fusion would be appropriate.

## What hybrid search doesn't fix

This is worth being explicit about, because hybrid is sometimes pitched as "just turn it on for free quality":

- **Bad chunks stay bad.** Hybrid retrieval over a poorly chunked corpus retrieves bad chunks more reliably. The chunking concerns from [`chunking-and-indexing.md`](./chunking-and-indexing.md) are still the first thing to fix.
- **Missing content stays missing.** If the right answer isn't in any chunk, neither retriever finds it.
- **Bad queries stay bad.** Hybrid amplifies *what the query reaches for*. Vague queries get vague results from both retrievers.
- **The latency cost is real.** Two retrieval passes per query, plus fusion. For lab-scale corpora it's negligible; for high-QPS production systems it adds 5-50ms.
- **The infrastructure cost is real.** You need an inverted index for BM25 alongside the vector index. Some vector stores (Weaviate, Qdrant, OpenSearch) handle both natively; others (Chroma, basic pgvector) need a separate BM25 service.

## When hybrid search isn't worth it

Cases where pure dense retrieval is the right call:

- **Your queries are uniformly conversational.** No proper nouns, no technical terms, no codes. Hybrid won't help.
- **Your corpus is uniformly conceptual.** No identifiers, no API names. Hybrid won't help.
- **You're optimizing for latency.** A single retrieval pass is faster than two.

For most knowledge-base RAG systems — internal docs, technical wikis, codebases, customer-support corpora — hybrid is worth the small operational cost. For pure conversational-AI use cases (chat history retrieval, generic FAQ), it often isn't.

## Production vector stores and hybrid

Brief note: most modern dedicated vector stores have added native hybrid search in the last 2-3 years:

- **Weaviate** has had hybrid since v1.18 (2023). API: `collection.query.hybrid(query=text, vector=emb, alpha=0.5)`.
- **Qdrant** added hybrid (named-vector / multi-vector) in v1.9 (2024).
- **Pinecone** added hybrid via sparse-dense indexes in 2023.
- **pgvector + Postgres** can do hybrid via SQL — combine `<=>` (dense distance) with `tsvector` full-text search.
- **Chroma** does *not* yet have native hybrid (as of mid-2026); you'd run BM25 alongside and combine outside.

For specifics see [`tools/vector-stores/snapshot-v1.0.md`](../../tools/vector-stores/snapshot-v1.0.md). Lab 07 doesn't use any of these — it runs RRF over Lab 06's numpy index and an in-memory `rank-bm25` index, because the math is identical and the mechanics are clearer when visible.

## Where this leads

Hybrid search and [reranking](./reranking.md) are the two RAG-quality interventions that pay off most reliably in production. They're independent — you can apply either without the other — but they're complementary. Hybrid widens the candidate set; reranking sharpens the order within it. Production systems often run both: BM25 + dense → top-30 by RRF → cross-encoder rerank → top-5.

Lab 07 walks through that full pipeline against the same corpus you used in Lab 06.

## See also

- 📖 [Retrieval strategies](./retrieval-strategies.md) — the prerequisite knobs (top_k, score floors, MMR).
- 📖 [Reranking](./reranking.md) — cross-encoder rescoring of the candidate set.
- 📖 [Chunking and indexing](./chunking-and-indexing.md) — the upstream decisions both retrievers depend on.
- ⚙️ [Vector stores snapshot](../../tools/vector-stores/snapshot-v1.0.md) — which production stores have native hybrid support.
- 🧪 [Lab 07](../../labs/07-retrieval-strategies-and-reranking/) — implements RRF + BM25 + dense + rerank in one notebook.

## References

- Robertson, S., & Walker, S. (1994). *Some simple effective approximations to the 2-Poisson model for probabilistic weighted retrieval*. SIGIR 1994. The BM25 paper.
- Robertson, S., & Zaragoza, H. (2009). [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.staff.city.ac.uk/~sb317/papers/foundations_bm25_review.pdf). The definitive review.
- Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). [*Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*](https://dl.acm.org/doi/10.1145/1571941.1572114). SIGIR 2009. The RRF paper; introduces the `k=60` constant.
- Sciavolino, C., Zhong, Z., Lee, J., & Chen, D. (2021). [*Simple Entity-Centric Questions Challenge Dense Retrievers*](https://arxiv.org/abs/2109.08535). EMNLP 2021. Empirical demonstration of dense retrieval's weakness on proper-noun queries; motivating evidence for hybrid.
- Kamalloo, E., Thakur, N., Lassance, C., Ma, X., Yang, J.-H., & Lin, J. (2023). [*Resources for Brewing BEIR: Reproducible Reference Models and an Official Leaderboard*](https://arxiv.org/abs/2306.07471). Establishes hybrid retrieval as a robust baseline on BEIR.
- Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., & Gurevych, I. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS 2021. The standard reference benchmark; consistently shows BM25 is competitive with neural retrieval on many domains.
