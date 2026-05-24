# Lab 07 · Reference solution

The polished final implementation of [Lab 07: Retrieval strategies and reranking](../README.md).

## What this is

A four-stage retrieval pipeline composed into `search_corpus_v2`:

1. **Dense retrieve** (`MiniLM-L6-v2`, top-30 candidates) — Lab 06's baseline.
2. **BM25 retrieve** (`rank_bm25.BM25Okapi`, top-30 candidates) — sparse lexical, catches proper nouns and exact phrases dense retrieval misses.
3. **Reciprocal Rank Fusion** (`k=60`) — score-free combination of dense + BM25.
4. **Cross-encoder rerank** (`ms-marco-MiniLM-L-6-v2`, top-30 → top-5) — joint query+chunk scoring, the single biggest quality lever.

Plus **MMR** available via `use_mmr=True` for redundancy-prone queries (off by default — most factual queries are hurt, not helped, by diversification).

The whole thing keeps Lab 06's tool contract intact (`status: ok/empty/error`), so the agent loop is unchanged.

## How it differs from `../lab.ipynb`

| Lab notebook (41 cells) | Solution (25 cells) |
|---|---|
| Step-by-step rank-shift comparison: dense alone → +BM25 → +RRF → +MMR → +reranker | Composed pipeline shipped as `search_corpus_v2` |
| Step 7 rebuilds the agent loop inline | Reuses the Lab 06 loop with the new search tool |
| Step 8 stretch on calibration helper for new queries | Out of scope here |
| Discusses scoring incompatibilities and when MMR hurts | The defaults encode the lessons; lab is where the *why* lives |

## ⚠️ Two pinned numbers worth flagging

- **`TARGET_TOKENS=160`, `OVERLAP_TOKENS=32`** — same chunker config as Lab 06. Don't change without re-validating Labs 08-09.
- **`MIN_SIMILARITY=0.0` against cross-encoder logits**, NOT Lab 06's `0.30` against cosines. Different scales. The cross-encoder produces logits that can be negative for non-matches; the `0.0` floor is the natural calibration point. The lab's "Step 5" walks through this scale issue explicitly.

## Implementation choices

1. **Two indexes, two retrievers, one fusion.** Dense and BM25 are *complementary*, not redundant. Dense catches paraphrase + synonyms; BM25 catches proper nouns + rare terms + exact phrases. RRF combines them at the rank level without needing score calibration.
2. **`k=60` in RRF.** Cormack et al. 2009's recommended value. The intuition: at rank 60+ the contribution `1/(60+r)` is tiny enough that doc presence matters more than precise rank. Worth changing if you find one retriever consistently outranks the other (you'd lower k); rarely worth it in practice.
3. **Rerank `candidate_k=30` → `top_k=5`.** The cross-encoder is ~50× slower per pair than the bi-encoder, so it can only score a small candidate set. The trade-off is recall@30 of the hybrid stage — that's what determines the ceiling on rerank's gains.
4. **MMR off by default.** The lab's eval set showed MMR helping on 1 of 8 queries (a deliberately broad query) and hurting or being neutral on the other 7. Diversification is a tool for specific query shapes, not a default.
5. **`retrieval_signals` in the result envelope.** Each result carries `{"dense": ..., "bm25": ..., "rerank": ...}` for debuggability. When the agent produces a strange answer, you can read off which signal *would* have surfaced the right chunk — that tells you which intervention to invest in next.

## What's deliberately out of scope

- **ANN-backed dense index.** Numpy at 55 chunks is fine; at 50K+ you want HNSW/IVF (Chroma, Qdrant, pgvector).
- **Reranker batching with `batch_size=` tuning.** The default behavior is fine for top-30 reranking; large candidate sets need batching for throughput.
- **Caching reranker outputs.** Production systems cache on `(query_hash, chunk_id)`. Out of scope here.
- **LLM-as-judge eval of pipelines.** That's Lab 09.
- **Contextual augmentation + query rewriting** for the cases hybrid+rerank still misses. That's Lab 08.

## Running the solution

```bash
cd labs/07-retrieval-strategies-and-reranking/solution
jupyter notebook lab.ipynb
```

First run downloads two models (`all-MiniLM-L6-v2` ~80 MB, `ms-marco-MiniLM-L-6-v2` ~80 MB) to your HuggingFace cache; subsequent runs are instant.

## Next

- Take the [retrieval strategies quiz](../../../quizzes/agentic-rag/retrieval-strategies.md) if you haven't already.
- Continue to [Lab 08: Contextual retrieval and query rewriting](../../08-contextual-retrieval-and-query-rewriting/) — the layer above this one, for when hybrid + reranking still misses.
- Or jump to [Lab 09: Evaluating agentic RAG](../../09-evaluating-agentic-rag/) — the systematic evaluation.
