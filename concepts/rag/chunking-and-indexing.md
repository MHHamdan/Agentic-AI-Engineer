# Chunking and indexing

> 🟢 Stable · ⏱ ~12 min read · 🏷 rag, chunking, embeddings

## TL;DR

Chunking is the single decision that has the largest effect on retrieval quality. Get it badly wrong and no amount of fancier retrievers, re-rankers, or larger models will rescue your RAG system. Get it adequately right and most other RAG decisions become forgiving.

This page covers the stable patterns: what a chunk is, how to size them, how to handle overlap and metadata, why the embedding model's token limit matters, and what a "vector index" actually is mechanically. The page deliberately stops short of optimization techniques (hybrid search, re-ranking, contextual retrieval) — those are later batches.

---

## A chunk, defined

A **chunk** is a sub-section of a document that gets embedded and indexed independently. The corpus is a set of documents; each document is split into chunks; each chunk gets one embedding vector.

This is mechanically necessary for two reasons:

1. **Embedding models have a maximum input length.** `all-MiniLM-L6-v2` truncates inputs to 256 wordpieces. `text-embedding-3-small` accepts up to 8,191 tokens but it's still finite. A document longer than this can't be embedded as one piece.
2. **A single embedding for a whole document is a bad representation anyway.** Document-level embeddings smear specific facts together; they're useful for "find documents similar to this one" but terrible for "find the passage that answers this question."

The chunk is the *retrieval unit*. When you query, you get back chunks. When the LLM synthesizes, it reads chunks. Picking the chunking strategy means picking the granularity at which your system can be helpful.

## Why this is harder than it sounds

The chunking-strategy literature is unusually noisy because chunking is doing two jobs at once that are in tension:

- **Each chunk should be small enough** that its embedding captures one coherent topic, so similarity ranking can be discriminative.
- **Each chunk should be large enough** that it contains enough context to be self-contained when the LLM reads it.

"Small enough to be discriminative, large enough to be useful." Those pull in opposite directions.

The other constraint hovering over both: **chunk boundaries are where information is lost**. Whatever falls across a boundary is invisible to retrieval, because no single chunk contains the full statement.

So: chunk size + overlap + how you pick the boundaries — these are the three knobs, and they all matter.

## Chunk size: a practical recommendation

Most of the literature converges on **200–800 tokens per chunk** for general-purpose RAG, with two stable defaults:

- **~512 tokens** for question-answering over knowledge bases, technical docs, articles. Enough context for one idea, small enough that the embedding focuses.
- **~256 tokens** for short-answer retrieval, FAQs, very precise queries. More chunks, higher specificity.

When the headlines about "the optimal chunk size" surface, they're usually narrow studies on specific corpora. The practical advice from production teams: **start at 512 tokens with ~20% overlap, measure on your corpus, adjust if needed**. Don't pre-optimize.

A note on the `all-MiniLM-L6-v2` default in Lab 06: the model truncates at 256 wordpieces. **Wordpieces ≈ ~75% of tokens** for English text, so a 256-wordpiece limit corresponds to roughly 200 LLM-tokens. Your chunks must stay under this or the embedding silently loses information. Lab 06 chunks at 200 tokens deliberately to stay under the limit. The chunking-token-limit relationship is the single most common foot-gun in MiniLM-based RAG systems.

If you're using a larger embedding model (`text-embedding-3-small` at 8,191 tokens, or BGE-large at 512 tokens), you have more room. But "the chunks can be bigger" is not the same as "the chunks *should* be bigger" — the discriminativeness argument still applies.

## Overlap

When you split a document into 512-token chunks with no overlap, you create one boundary every 512 tokens. Any fact straddling that boundary is invisible to retrieval.

**Overlap** is the practice of letting adjacent chunks share their boundary region — typically 10–20% of the chunk size. A 512-token chunk with 20% overlap means each chunk overlaps 102 tokens with the previous and next chunks.

The cost: ~20% more storage and embedding compute, because the same text gets embedded twice in adjacent chunks.

The benefit: information at chunk boundaries is recoverable. A fact whose statement straddles a boundary will appear (in full) in at least one of the two adjacent chunks.

Lab 06 uses 200-token chunks with ~20% overlap. Most production systems pick a similar ratio.

## How to pick boundaries

Three strategies, in increasing order of how much they care about the document's structure:

### 1. Fixed-window splitting

Split every N tokens. Simplest possible approach. Boundaries fall wherever they fall — mid-sentence, mid-paragraph, mid-list.

**Pros:** trivial to implement, deterministic, fast.
**Cons:** boundaries break natural units. A sentence cut in half loses meaning.

Acceptable for prototypes. Almost always worth upgrading to recursive splitting before production.

### 2. Recursive splitting on document structure

Try to split at natural boundaries first (double newlines, paragraph breaks), fall back to sentence breaks, fall back to fixed-window only as a last resort. LangChain's `RecursiveCharacterTextSplitter` is the popular implementation; the algorithm is straightforward enough to write yourself.

**Pros:** chunks respect paragraph and sentence boundaries. Better embeddings.
**Cons:** chunk sizes become non-uniform. Some chunks are 300 tokens, some are 700.

This is what Lab 06 uses (implemented from scratch — it's ~20 lines).

### 3. Semantic splitting

Use a separate model pass to detect topic boundaries and split there. A statement-similarity test between adjacent sentences, splitting where similarity drops.

**Pros:** chunks are topically coherent.
**Cons:** expensive at index time; not always meaningfully better than recursive splitting in practice; more moving parts.

Reasonable for production systems on stable corpora where re-indexing is rare. Overkill for most use cases. Reserved for a later Path 02 batch as an optimization technique.

## Metadata: the underused lever

Every chunk should carry metadata. At minimum:

- `doc_id` — which document this chunk is from.
- `chunk_id` — a stable identifier for this specific chunk.
- `title` — the document title (for display and as a triage cue).
- `source` — the URL, file path, or other origin pointer.

Optional and often very useful:

- `section` — the heading the chunk falls under.
- `position` — 0-indexed position within the document.
- `created_at` / `updated_at` — for freshness-aware retrieval.
- `category`, `tags` — for filtered retrieval ("retrieve only chunks tagged 'policy'").

Metadata is free at storage time and lets you do *filtered retrieval*: similarity search within a subset of the corpus. This is one of the most under-used features of vector stores and one of the most powerful: filtering by `category="legal"` before similarity-ranking dramatically improves precision for many real-world use cases.

Lab 06 keeps metadata minimal (`doc_id`, `chunk_id`, `title`) because the corpus is small. Real systems should plan their metadata schema before indexing.

## What "the index" actually is

This part is worth getting concrete because vector-store marketing tends to obscure it.

An index, mechanically, is:

1. A 2D array of shape `(num_chunks, embedding_dim)` — every chunk's embedding stacked.
2. A parallel array of chunk metadata, same length, so you can look up the actual chunk by row index.
3. A similarity function (almost always cosine similarity, or dot product on normalized vectors).
4. A search algorithm:
   - **Brute-force**: for each query, compute similarity against every chunk's embedding, return top-k. O(n) per query. Fine up to ~10K chunks on a laptop.
   - **Approximate Nearest Neighbor (ANN)**: pre-build a structure (HNSW, IVF, ScaNN, etc.) that lets you find approximate top-k without comparing against every chunk. O(log n) or better. Required at million-chunk scale.

That's it. Everything else — the database server, the persistence layer, the metadata filtering, the hybrid search, the management UI — is plumbing around those four things.

Lab 06 implements the brute-force version in ~5 lines of numpy:

```python
import numpy as np

# Normalized embeddings + dot product = cosine similarity
def search(query_emb: np.ndarray, embeddings: np.ndarray, top_k: int = 5):
    scores = embeddings @ query_emb          # (num_chunks,)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return top_indices, scores[top_indices]
```

That's a real, working vector index. Production stores wrap algorithms like this with persistence, network APIs, sharding, and operational tooling — but the core math is identical. Knowing this changes how you read the marketing.

## The retrieval-quality knobs, ranked by impact

A rough ordering by how much each tends to affect retrieval quality on production RAG systems. Spend your time accordingly:

1. **Chunking strategy.** Bad chunking dominates everything else.
2. **The corpus.** Garbage in, garbage out. If your docs are stale, contradictory, or low-quality, retrieval will be too.
3. **The embedding model.** MiniLM works; BGE-large works better at the cost of higher operational footprint. Bigger isn't always meaningfully better.
4. **Metadata and filtering.** Pre-filtering by category, date, or domain shrinks the relevant search space and improves precision more than people expect.
5. **`top_k` value.** More chunks → more recall, more noise. 5–10 is the usual range.
6. **Re-ranking** (a later Path 02 topic). A cross-encoder re-ranks the top 30–50 results from dense retrieval. High gain, modest cost.
7. **Hybrid search** (also a later batch). Fusing BM25 keyword search with dense vector search. Helps for queries with proper nouns, codes, statute numbers, etc.
8. **The similarity function.** Cosine vs dot product is almost always cosine (or dot product on normalized vectors, which is the same thing). L2 distance is occasionally useful. Don't agonize over this.
9. **Index parameters** (HNSW `m`, `ef_construction`, etc.). At <10K chunks, irrelevant. At >1M chunks, worth careful tuning.

If you're trying to improve a RAG system and you haven't audited the corpus and the chunking, do those before anything else.

## The chunking failure modes you'll actually see

The patterns to recognize when debugging a RAG system that "isn't working":

| Symptom | Likely chunking issue |
|---|---|
| Retrieval returns chunks that are *close* to the question but never quite contain the answer | Chunks too small; answer spans a boundary |
| Retrieval scores are uniformly low | Chunks too large; embeddings are smearing multiple topics |
| The same chunk keeps coming back regardless of query | Duplicate or near-duplicate content in the corpus; dedupe before indexing |
| Top-1 chunk is wrong but top-5 contains the right one | Embedding model is choosing badly; re-ranking would help (later batch) |
| Question is about a specific code/ID and retrieval misses it | Dense embeddings miss exact tokens; hybrid search would help (later batch) |
| Recently-updated info isn't retrieved | Stale index; re-index periodically |

Lab 06 demonstrates the first two explicitly — the bundled corpus has chunks deliberately sized to surface the boundary issue, and the lab walks through what it looks like.

## The 256-wordpiece foot-gun (worth repeating)

If you're using `all-MiniLM-L6-v2` (Lab 06's default, and the most common community-tutorial embedding model), the model truncates inputs at 256 wordpieces. About 200 LLM-tokens.

This means: **if you encode a chunk longer than ~200 tokens, the embedding represents only the first ~200 tokens.** The rest is silently invisible. The encoding call won't warn you, won't fail, won't give you any indication.

Symptoms of this happening:

- Chunks containing important content in their last third don't get retrieved when queried for that content.
- Recall drops sharply as you increase chunk size past 200 tokens — the opposite of the expected pattern.
- Two semantically different chunks have suspiciously similar embeddings because their first 200 tokens overlap.

The fix is simple: chunk under the limit. Lab 06 chunks at 200 tokens. If you switch to a larger embedding model, you can chunk larger, but check the model's actual limit before relying on it.

The lesson generalizes: **every embedding model has a token limit, and exceeding it is silent failure**. Knowing the limit for your chosen model is non-optional.

## See also

- 📖 [What is RAG?](./what-is-rag.md) — the conceptual frame this page operates inside.
- 📖 [Retrieval as a tool](./retrieval-as-a-tool.md) — how the chunks get used by the agent loop.
- ⚙️ [Embedding models snapshot](../../tools/embeddings/snapshot-v1.0.md) — the model the lab uses, with the 256-wordpiece limit called out.
- ⚙️ [Vector stores snapshot](../../tools/vector-stores/snapshot-v1.0.md) — what production indexing looks like when you outgrow numpy.
- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — implements all of this against a bundled corpus.

## References

- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The original paper used 100-word passages from Wikipedia as their retrieval units; the 200–800-token convention came later as embedding models grew.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). §3 covers chunking strategies in detail with citations to empirical studies.
- Karpukhin, V. et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP 2020. DPR's passage-size choices set the convention much of the field follows.
- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). Treated in detail in a later Path 02 batch; the technique addresses some of the chunking-boundary failure modes by augmenting each chunk with document-level context before embedding.
- Malkov, Y. A., & Yashunin, D. A. (2018). [*Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*](https://arxiv.org/abs/1603.09320). The HNSW paper. Worth skimming for the geometric intuition behind ANN search.
