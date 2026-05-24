# Reranking

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, retrieval, reranking, cross-encoder

## TL;DR

A bi-encoder (the kind Lab 06 uses) embeds the query and chunk independently and compares them with cosine similarity. It's fast and indexable but it never sees the two together. A **cross-encoder** runs the query and chunk through the model *together*, capturing how they interact — at the cost of being far too slow to run over a whole corpus.

The standard production pipeline pairs them: bi-encoder retrieves a candidate set of 30-50 chunks; cross-encoder reranks within that set. Higher precision at the top of the ranking, modest cost overhead, no architectural complexity beyond an extra model call.

This is consistently one of the highest-impact RAG-quality interventions for an effort that fits in an afternoon. [Lab 07](../../labs/07-retrieval-strategies-and-reranking/) builds the pipeline from scratch.

---

## The bi-encoder limit

Lab 06's `search_corpus` works like this:

1. **At index time:** embed every chunk independently. Save the resulting `(n_chunks, 384)` array.
2. **At query time:** embed the query into a `(384,)` vector. Compute `query @ chunk_embeddings.T` to get similarity scores. Return top-k.

This is the bi-encoder pattern (sometimes called "dual encoder" or "two-tower"). Each side gets one pass through the model, independently. The model never sees query and chunk together.

The bi-encoder's superpower is **precomputation**. Chunks are embedded once, indexed once, and reused for every query. Retrieving from 1M chunks takes a millisecond.

The bi-encoder's blind spot is **fine-grained query-document interaction**. The model can't tell that a chunk contains "the answer to the user's specific question" vs. "general content about the topic". Both get mapped to nearby points in embedding space, and the bi-encoder can't tell them apart.

Symptoms of bi-encoder precision limits:

- The right answer is consistently in the top-10 but rarely the top-3.
- Top-k results are all *about* the topic but only one or two actually *answer* the question.
- Semantically-related-but-wrong chunks rank above semantically-distant-but-correct ones.

## What a cross-encoder does differently

A cross-encoder takes a `(query, passage)` pair as input and outputs a single relevance score. The query and passage are concatenated and run through a transformer together, so the model sees how every query token interacts with every passage token.

```
query + passage → transformer → relevance score
```

vs. bi-encoder:

```
query → transformer → query_emb ──┐
                                   ├─→ cosine(query_emb, passage_emb)
passage → transformer → passage_emb ┘
```

The cross-encoder has **direct access to the interaction terms**. It can tell that the chunk's third sentence directly addresses the query's main noun phrase, that a numeric value in the chunk matches a numeric constraint in the query, that the query's verb is contradicted by the chunk. None of that is recoverable from independent embeddings.

The cost: you can't precompute anything. Every (query, chunk) pair requires a forward pass. For a corpus of N chunks and a single query, you'd need N forward passes — at MiniLM speeds, ~1ms each on CPU, so 1000 chunks is 1 second per query. At 100K chunks, you've left interactive territory entirely.

This is why cross-encoders are used **as rerankers**, not as primary retrievers.

## The retrieve-then-rerank pipeline

```
                              ┌──────────────────┐
   query ──→ bi-encoder ─→ top-30 candidates ──→ │ cross-encoder    │
                                                  │ scores each pair │
                                                  └──────────────────┘
                                                          │
                                                          ▼
                                                  re-sorted top-5
```

Bi-encoder narrows the field from N chunks to 30 candidates (fast, indexable). Cross-encoder rescores those 30 pairs (slow per pair, but only 30 pairs, so total latency is ~30ms-300ms). The reranked top-5 has higher precision than the bi-encoder's top-5 alone.

The math: if your right answer is in the bi-encoder's top-30 but ranked 12th, the reranker often pulls it to position 1-3. If your right answer is *not* in the top-30, no reranker can help.

This is why reranking sits *downstream* of retrieval strategies — the retrieval step has to surface candidates in its top-50 for reranking to matter. Bad retrieval upstream means bad reranking downstream.

## Picking a reranker

For a community-scale lab and most production systems where latency budget allows a small extra model: **`cross-encoder/ms-marco-MiniLM-L-6-v2`** from sentence-transformers.

Specs:
- 6-layer MiniLM, ~22M parameters, ~80 MB on disk.
- Trained on the MS MARCO passage reranking dataset (~530K query-passage pairs).
- CPU-runnable at ~5-50 pairs/second on a modern laptop, much faster on GPU.
- Apache-2.0, no API key.
- Output: raw logits (typically `[-10, +15]` range), with higher = more relevant. Optionally sigmoid-activated to `[0, 1]`.

Alternatives, in roughly increasing operational footprint:

| Model | Size | When to reach |
|---|---|---|
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | ~80 MB | Default for community labs. Fast, decent quality. |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | ~120 MB | ~2 points better on benchmarks. Worth measuring on your corpus. |
| `BAAI/bge-reranker-base` | ~280 MB | Stronger on diverse domains, slower. |
| `BAAI/bge-reranker-large` | ~1.3 GB | Higher quality, much slower. Production-grade. |
| Cohere Rerank API | hosted | Hosted API; ~$2/1K searches; competitive quality without local infra. |
| Voyage AI rerank-2 | hosted | Similar tradeoffs to Cohere. |

Lab 07 uses the MiniLM-L-6 default for the same reason Lab 06 uses MiniLM for embeddings: small, fast, CPU-runnable, no API key, well-documented.

## When reranking helps the most

Real-world workloads where reranking reliably improves quality:

- **Long, nuanced queries** where bi-encoder loses fine-grained signal in compression.
- **Technical Q&A** where multiple chunks discuss the topic and only one answers it.
- **Multi-aspect queries** ("X and how does it relate to Y") — the cross-encoder is much better at scoring both-aspects-present.
- **Domain-specific corpora** where bi-encoder embeddings are off-domain.

Workloads where reranking has smaller marginal effect:

- **Very short, lexical queries** where BM25 already gives a strong top-1.
- **Single-topic corpora** where chunk-level distinctions don't matter much.
- **Latency-critical workloads** where adding 30-300ms per query is unacceptable.

## What changes about the agent loop

Almost nothing. The reranker is internal to `search_corpus` (or its production equivalent). The agent still calls `search_corpus(query, top_k=5)` and gets the same `{chunk_id, doc_id, title, snippet, score}` shape back. The `score` semantic changes (it's now a reranker score, not a cosine), but the agent doesn't care about absolute values — it cares about relative ranking, which is exactly what reranking improves.

If you're integrating reranking into Lab 06's pattern:

```python
def search_corpus(query, top_k=5, candidate_k=30):
    # 1. Bi-encoder retrieves candidates
    query_emb = embedder.encode([query], normalize_embeddings=True)[0]
    scores = embeddings @ query_emb  # all chunks
    candidate_idx = np.argsort(scores)[::-1][:candidate_k]

    # 2. Reranker rescores the candidates
    pairs = [(query, all_chunks[i]["text"]) for i in candidate_idx]
    rerank_scores = reranker.predict(pairs)  # numpy array, higher = better

    # 3. Pick top-k by reranker score
    reranked_idx = candidate_idx[np.argsort(rerank_scores)[::-1][:top_k]]
    return [build_result(all_chunks[i], rerank_scores[j])
            for j, i in enumerate(reranked_idx)]
```

The tool's contract is unchanged. The candidate set widened (5 → 30), then narrowed back (30 → 5) with better choices. Lab 07 implements this pattern end-to-end.

## A common misconception

People sometimes assume "reranking makes retrieval better," full stop. It does — but only within the candidate set. If the right chunk wasn't in the bi-encoder's top-30, the reranker can't pull it in. Reranking is a *precision* improvement on a fixed *recall* set.

The implications:

- Always set `candidate_k` (the bi-encoder's top-k passed to the reranker) *larger* than your final `top_k`. The standard ratio is 5-10x: final `top_k=5` → candidate `top_k=30-50`.
- If you increase candidate_k and the right chunk is found, your bi-encoder's recall is the bottleneck — fix retrieval before reranking.
- If you increase candidate_k and the right chunk *still* isn't in the candidate set, the problem is upstream (chunking, query, or corpus).

## Cost in plain terms

For the Lab 07 pipeline on a modern laptop:

| Step | Wall time (per query, CPU) |
|---|---|
| Bi-encoder query embed | ~10-50ms |
| Index search (numpy dot product, 55 chunks) | ~1ms |
| Cross-encoder rerank (30 pairs) | ~300-1500ms |
| **Total** | ~310ms-1.5s |

For a small interactive lab this is fine. For a production system with strict latency budgets, you'd:
- Use a smaller candidate_k (say 15-20).
- Use a smaller reranker (or run it on GPU).
- Cache reranker outputs for popular queries.

But this is the operational-tuning conversation, not the should-we-add-reranking conversation. The default answer for production is: add it, measure the improvement, only then decide whether to optimize the latency.

## What this page deliberately skips

- **Training your own reranker** on domain data. Possible but rarely needed; off-the-shelf rerankers are surprisingly transferable.
- **Late-interaction models** (ColBERT, PLAID, ColPali). Conceptually between bi- and cross-encoders — token-level interactions instead of one full pass. Operationally complex; production-grade infrastructure required. Reserved for a later batch or noted as a production path.
- **Listwise reranking** with an LLM ("score these 10 chunks for relevance to this query"). Real technique, expensive, and the gains over a dedicated reranker are usually small. Mentioned briefly here, full treatment elsewhere.
- **Reranker fine-tuning** with feedback from production. Useful at scale; out of scope for a lab.

## What comes next in Path 02

Reranking and [hybrid search](./hybrid-search.md) are the two production-grade retrieval-quality interventions covered in this batch. Future Path 02 batches will add:

- **Contextual retrieval** — Anthropic's technique for augmenting each chunk with document-level context *before* embedding, addressing some chunk-boundary failure modes.
- **Query expansion / HyDE** — generating hypothetical answers as the retrieval query.
- **RAG evaluation** — measuring whether your retrieval and answer-generation actually improved. (Note: also covered in Path 06.)
- **The framework bridge** — same RAG agent in LangChain/LangGraph.

After this batch, your Lab 06 + Lab 07 pipeline handles ~80% of what production RAG systems do. The remaining 20% is the items above plus corpus-specific tuning.

## See also

- 📖 [Retrieval strategies](./retrieval-strategies.md) — the top_k / score floor / MMR knobs that bound what reranking can do.
- 📖 [Hybrid search](./hybrid-search.md) — pairs naturally with reranking; production systems use both.
- 📖 [Chunking and indexing](./chunking-and-indexing.md) — the upstream decisions both retrievers depend on.
- 🧪 [Lab 07](../../labs/07-retrieval-strategies-and-reranking/) — implements bi-encoder + BM25 + RRF + cross-encoder reranking against Lab 06's corpus.

## References

- Reimers, N., & Gurevych, I. (2019). [*Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*](https://arxiv.org/abs/1908.10084). EMNLP 2019. Introduces the bi-encoder pattern; the cross-encoder appears as Section 5.3 as a separate architecture for tasks requiring sentence-pair interaction.
- Nogueira, R., & Cho, K. (2019). [*Passage Re-ranking with BERT*](https://arxiv.org/abs/1901.04085). The early demonstration that BERT-based cross-encoders strongly outperform bi-encoders on passage reranking. The lineage of `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Nguyen, T., et al. (2016). [*MS MARCO: A Human Generated MAchine Reading COmprehension Dataset*](https://arxiv.org/abs/1611.09268). The dataset most reranker models are trained on.
- Pradeep, R., Liu, Y., Zhang, X., Li, Y., Yates, A., & Lin, J. (2023). [*Squeezing Water from a Stone: A Bag of Tricks for Further Improving Cross-Encoder Effectiveness for Reranking*](https://arxiv.org/abs/2208.01230). ECIR 2023. Practical engineering paper on getting more from cross-encoders.
- Khattab, O., & Zaharia, M. (2020). [*ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT*](https://arxiv.org/abs/2004.12832). SIGIR 2020. The late-interaction approach mentioned above; reading even just §3 builds intuition for the bi-/cross-/late-interaction spectrum.
