# Lab 06 · Reference solution

The polished final implementation of [Lab 06: Agentic RAG from scratch](../README.md).

## What this is

A complete agentic RAG stack in pure Python:

- **Chunker** — recursive paragraph→sentence split, `TARGET_TOKENS=160`, `OVERLAP_TOKENS=32`. 55 chunks across 8 documents.
- **Embedding index** — `sentence-transformers/all-MiniLM-L6-v2` on CPU, `normalize_embeddings=True` so cosine = dot product.
- **`search_corpus`** — top-k retrieval with `MIN_SIMILARITY=0.30` floor; `status: empty` when no chunk crosses.
- **`read_chunk`** — full text by ID; structured `not_found` error on bad IDs.
- **Agent loop** — `MAX_STEPS=8`, action-hash dedup, citations recorded structurally on successful `read_chunk` (not on snippet view).

## How it differs from `../lab.ipynb`

| Lab notebook (38 cells) | Solution (19 cells) |
|---|---|
| Steps 6+7 run 3 test queries + 3 failure-mode walks | Single demo query |
| Step 9 stretch swaps to OpenAI embeddings | Out of scope here |
| Discusses chunker tuning trade-offs across multiple cells | Chunker config pinned with a brief note about why |

## 🔒 Critical: chunker config is pinned

`TARGET_TOKENS=160` and `OVERLAP_TOKENS=32` produce a specific chunking of the 8-document corpus → 55 chunks with specific IDs like `02-tool-design.md:3`. Labs 07-09 annotate their eval sets and tests against these IDs. **Changing the chunker config invalidates downstream labs.**

If you want to experiment with different chunker settings:

1. Make the change in this solution only.
2. Re-run Labs 07, 08, 09 end-to-end against the new chunk IDs.
3. Update the eval_set.jsonl annotations in Lab 09 if you used strict (chunk-level) annotations.

The lab notebook explains *why* 160/32 was chosen — short version: stays comfortably under MiniLM's 256-wordpiece truncation limit even with overlap prepended, and produces ~50-60 chunks for the 8-document corpus which is enough to demonstrate the patterns without making the lab corpus unwieldy.

## Implementation choices

1. **The corpus path is `../corpus/`**, not `./corpus/`. The solution lives at `labs/06-…/solution/lab.ipynb`, one directory deeper than the lab notebook, so the relative path moves up one level.
2. **`normalize_embeddings=True` is non-optional.** Without it, the `embeddings @ query_emb` matmul returns dot products that aren't cosine similarities, and `MIN_SIMILARITY=0.30` stops being meaningful. The lab's chunking-and-indexing concept page makes the case in detail.
3. **`MIN_SIMILARITY=0.30` is calibrated for MiniLM.** Different embedding models have different cosine distributions; you'd recalibrate the floor empirically (run on-corpus and off-corpus queries; pick a value that separates them cleanly). The cross-encoder reranker in Lab 07 uses a different scale entirely (logits, not cosines).
4. **Citations are tracked structurally**, just like Lab 03's URL citations. The agent loop appends `(chunk_id, doc_id, title)` on every successful `read_chunk` — the LLM can't fabricate citations. This is the agentic-RAG version of the search-citations pattern.
5. **Tool results are capped at 4000 chars** when appended to state. Long chunks would otherwise dominate the context window across multi-step trajectories.

## What's deliberately out of scope

- **A real vector store.** Numpy is fine at 55 chunks; at 50K+ you'd want Chroma, Qdrant, pgvector, or similar for ANN + persistence + metadata filtering. See [`tools/vector-stores/snapshot-v1.0.md`](../../../tools/vector-stores/snapshot-v1.0.md) for the current landscape.
- **OpenAI/Cohere embeddings.** MiniLM is free and CPU-friendly; production often swaps to `text-embedding-3-small` for quality. The swap is a one-function change — see lab Step 9.
- **Hybrid retrieval** (BM25 + dense). That's Lab 07.
- **Contextual augmentation** + query rewriting. That's Lab 08.
- **Evaluation harness.** That's Lab 09.

## Running the solution

```bash
cd labs/06-agentic-rag-from-scratch/solution
jupyter notebook lab.ipynb
```

First run downloads `all-MiniLM-L6-v2` (~80 MB to your HuggingFace cache); subsequent runs are instant.

## Next

- Take the [RAG fundamentals quiz](../../../quizzes/agentic-rag/rag-fundamentals.md) if you haven't already.
- Continue to [Lab 07: Retrieval strategies and reranking](../../07-retrieval-strategies-and-reranking/).
