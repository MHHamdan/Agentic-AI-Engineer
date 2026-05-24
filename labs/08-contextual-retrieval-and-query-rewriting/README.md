# Lab 08: Contextual retrieval and query rewriting

> 🟡 Intermediate · ⏱ ~110–140 min · 📚 Same corpus as Labs 06 + 07; corpus-side and query-side interventions

## 🎯 Goal

Extend Lab 07's hybrid + rerank pipeline with two new categories of quality intervention:

- **Contextual retrieval** (Anthropic's technique) — augment each chunk with an LLM-generated context summary *before* indexing. The augmented chunks feed both BM25 and the dense embedder. Cache the summaries to disk so re-runs don't re-pay the LLM cost.
- **Query rewriting** — generate alternative queries before retrieval runs. Three patterns from scratch: HyDE (hypothetical answer), multi-query expansion, and query decomposition.

You'll see, query-by-query, which intervention helps which failure mode. The lab is honest about scale: on Lab 06's 55-chunk corpus the gains are modest (most queries already hit rank 1), but the *mechanism* is visible and the *production-scale* benchmarks (Anthropic's 35-67% retrieval-failure-rate reduction) carry forward.

By the end you should be able to:

- Implement contextual chunk augmentation with an LLM call per chunk.
- Cache context summaries to JSON so re-runs are free.
- Build BM25 + dense indexes over augmented chunks (Anthropic's "Contextual BM25" + "Contextual Embeddings").
- Implement HyDE in ~30 lines: generate hypothetical answer, embed it, retrieve against it.
- Implement multi-query expansion: generate 3 rephrasings, retrieve each, fuse with RRF.
- Implement query decomposition: split compound queries into sub-queries.
- Reason about which intervention to reach for given a specific failure mode (the [retrieval-failure-modes](../../concepts/rag/retrieval-failure-modes.md) decision tree).
- Decide when query rewriting is *not* worth the LLM-call latency.

## 📋 Prerequisites

**Read first:**

- 📖 [Contextual retrieval](../../concepts/rag/contextual-retrieval.md)
- 📖 [Query rewriting](../../concepts/rag/query-rewriting.md)
- 📖 [Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md)

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — bi-encoder retrieval, agent loop, citations.
- 🧪 [Lab 07: Retrieval strategies and reranking](../../labs/07-retrieval-strategies-and-reranking/) — BM25, RRF, MMR, cross-encoder rerank. Lab 08 builds on this pipeline directly.

**Setup:**

Python 3.11+ with the repo's environment. **No new dependencies on top of Lab 07.** This lab uses the same LLM client, embedder, BM25, and reranker:

- `rank-bm25 >= 0.2.2` (from Lab 07)
- `sentence-transformers >= 5.0` (from Lab 06)
- `openai` or `anthropic` (from Lab 01)
- `numpy` (already a dep)

The LLM that powers your agent loop in Labs 06/07 is the same LLM that generates context summaries here. **Be aware of the cost** — at index time, the lab makes one LLM call per chunk (55 chunks for the lab corpus, ~$0.01-0.05 total). Production corpora are larger; see the [contextual-retrieval.md cost section](../../concepts/rag/contextual-retrieval.md#the-cost-question).

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `rank-bm25` | `>=0.2.2,<0.3` (latest: `0.2.2`) | 2026-05-24 (from Lab 07) |
| `sentence-transformers` | `>=5.0,<6.0` (latest: `5.5.1`) | 2026-05-24 (from Lab 06) |
| `openai` SDK | `>=2.0` (latest: `2.38.0`) | 2026-05-24 (from Lab 01) |
| `anthropic` SDK | `>=0.34` | 2026-05-24 (from Lab 01) |

No new pins introduced by this lab.

## What you'll build

A retrieval pipeline that adds two upstream stages to Lab 07's hybrid + rerank stack:

```text
─── INDEX TIME (once, cached to disk) ───
   for each chunk:
       LLM(document, chunk) → context summary
       cache to context_cache.json
   build BM25 + dense indexes over (context + chunk)


─── QUERY TIME (per query) ───

   user query
       │
       ▼
  ┌─────────────────────────────────┐
  │ Query rewriting (optional)      │
  │   HyDE / multi-query / decompose│
  └─────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────┐
  │ Lab 07 pipeline                 │
  │   dense + BM25 → RRF → MMR      │
  │   → cross-encoder rerank        │
  │   → top-k                       │
  └─────────────────────────────────┘
       │
       ▼
  agent reads chunks (originals, not augmented)
```

Same `search_corpus` envelope contract as Labs 06 + 07. The agent loop is unchanged.

## Steps

The notebook covers these in order:

**0. Setup.** Imports, LLM client, load Lab 06 corpus. Same provider-agnostic chat client as Lab 06.

**1. Recreate Lab 07's pipeline.** Bi-encoder index, BM25 index, RRF fusion, cross-encoder reranker — all from Lab 07. This is the baseline every later upgrade is measured against.

**2. Build the context summaries.** One LLM call per chunk. Pass the full document + the chunk; ask the LLM for 1-2 sentences of context. Cache to `context_cache.json` keyed by `(doc_id, chunk_index)` so re-runs are free. Print three summaries to show the output shape.

**3. Build the contextual indexes.** BM25 over augmented chunks ("Contextual BM25"). Dense embeddings over augmented chunks ("Contextual Embeddings"). Side-by-side comparison with Lab 07's baseline indexes on the same EVAL_QUERIES.

**4. Implement HyDE.** Generate a hypothetical answer with the LLM, embed *that*, retrieve against it. Demonstrate on a paraphrased query where the baseline missed.

**5. Implement multi-query expansion.** Ask the LLM for 3 rephrasings of the query. Retrieve each. Fuse with RRF (k=60, same as Lab 07). Demonstrate on a vocabulary-shifted query.

**6. Implement query decomposition.** Detect compound queries (multiple sub-questions joined by "and", or naturally complex). Ask the LLM to break them into atomic sub-queries. Retrieve each.

**7. The full pipeline.** `search_corpus_v3` combines everything: optional query rewriting, dense + BM25 over contextual chunks, RRF, optional MMR, cross-encoder rerank, top-k. The envelope contract is unchanged from Labs 06/07.

**8. Wire into the agent loop.** Same agent as Lab 06/07. Same `read_chunk`. Only the body of `search_corpus` differs. Run the three Lab 06 queries through the new pipeline.

**9. (Stretch) Failure-mode walkthrough.** Pick 2-3 queries that Lab 07 still got wrong (or got at rank > 1). Show which intervention from this lab fixes each. The pattern: diagnose → match to the failure-modes taxonomy → apply the matching intervention.

## What we don't do in this lab

Anti-scope, kept explicit:

- **No RAG evaluation framework** (Ragas, TruLens, custom eval frameworks). Same as Labs 06/07 — Path 06.
- **No production vector stores** as default. Numpy + `rank-bm25` stays.
- **No LangChain `MultiQueryRetriever` or LlamaIndex equivalents.** Same pedagogical reason — Lab 08's whole point is showing what those abstractions wrap. Framework bridge is a future batch.
- **No prompt caching against the Anthropic API.** The lab notes that prompt caching would reduce index-time cost ~80% on long documents, but the corpus is small enough here that caching adds noise without showing the benefit. Production work *should* enable it; the linked [docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) cover the mechanics.
- **No fine-tuning.** Not the rewriter, not the embedder, not the reranker. Off-the-shelf throughout.
- **No conversational query rewriting** (multi-turn rewriting against chat history). Out of scope; future framework-bridge lab.
- **No multi-agent retrieval.** Path 03.

## Common gotchas

- **Cost discipline.** If you re-run step 2 without checking the cache, you re-pay for 55 LLM calls. The cache key `(doc_id, chunk_index)` lets you re-run only the chunks that changed; trust the cache by default.
- **Lab corpus undersells the benefit.** On a 55-chunk well-aligned corpus, most queries already hit rank 1 at Lab 07's baseline — contextual retrieval can't improve a perfect score. The lab uses *referential* test queries (e.g. "what does the document on tool design say about errors") that need doc context to retrieve well. Production corpora typically have the harder failure modes; treat the lab's gains as a *demonstration of mechanism*, not a *benchmark of magnitude*. Anthropic's 35-67% headline numbers came from real-world codebase/fiction/arXiv/science-paper corpora.
- **HyDE in unfamiliar domains is risky.** If the LLM has no relevant knowledge, the hypothetical answer is invented and the embedding goes to a random place in semantic space. Retrieval gets *worse*, not better. For the Lab 06 corpus (about agentic AI engineering), the LLM has strong priors and HyDE works well. Your mileage may vary.
- **Multi-query latency stacks.** 3 LLM-generated rephrasings + each one's retrieval call = ~4 LLM calls + 3 retrievals before the agent even sees a result. For interactive UIs, this latency matters. Lab 08 doesn't dwell on it; production code should.
- **Score scale shifts again.** Lab 07's rerank logits are in `[-15, +15]`. RRF over augmented retrievers is still `[0, ~0.033]`. The `MIN_SIMILARITY` floor needs to be calibrated for whichever score the pipeline returns. Lab 08 keeps `MIN_SIMILARITY = 0.0` on rerank logits, same as Lab 07.
- **The agent reads the *original* chunk, not the augmented one.** The context summary is a retrieval aid only. Lab 08's `read_chunk` returns the original chunk text (Lab 06's behavior is preserved). Passing the augmented chunk to the LLM at answer-generation time is a separate tunable.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 26 cells vs the lab's 46 — three rewrite modes (`hyde`, `multi`, `decompose`) composed in `search_corpus_v3` with the cache-or-generate pattern from Anthropic's verbatim `CONTEXT_PROMPT`. Two design choices worth flagging:

- **The lab uses an LLM call per chunk** without prompt caching. Caching would reduce index-time cost ~80% on long documents but adds complexity that distracts from the core mechanism. Real production builds *should* use caching; the [contextual-retrieval.md](../../concepts/rag/contextual-retrieval.md#the-cost-question) cost section explains how.
- **The lab uses the same LLM as the agent loop** for context generation. Production systems often use a *cheaper* model for context generation (e.g., Haiku for context, Sonnet for answers). Same provider, two model strings — trivial substitution. The lab uses one model for clarity.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — same policy framing; the action space is unchanged from Labs 06/07.
- 📖 [Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md) — the debug decision tree this lab gives you the interventions for.
- ⚙️ [Embedding models snapshot](../../tools/embeddings/snapshot-v1.0.md) — what's under the embedder Lab 08 indexes against.

## ✅ Check your understanding

- 🧠 [`quizzes/agentic-rag/contextual-retrieval-and-query-rewriting.md`](../../quizzes/agentic-rag/contextual-retrieval-and-query-rewriting.md) — 8 single-select questions covering Anthropic's technique, HyDE mechanics, when to decompose vs let-the-agent-decompose, the cost question, and the failure-modes decision tree.

If you score below 6/8, re-read the three concept pages and walk through step 9 of the notebook.

## What comes next

You've now built every standard retrieval intervention covered in mainstream RAG literature:

- Lab 06: bi-encoder + chunking + agent loop with citations.
- Lab 07: BM25 + RRF + MMR + cross-encoder rerank.
- Lab 08: contextual retrieval + HyDE + multi-query + decomposition.

The remaining Path 02 directions:

- **RAG evaluation primer** — measuring faithfulness, groundedness, citation accuracy on your own corpus. Lightweight before Path 06 in earnest. (Future batch.)
- **Framework bridge** — the same Lab 06–08 agent in LangChain/LangGraph. (Future batch.)
- **Conversational RAG** — multi-turn retrieval with chat history, query rewriting against context. (Future batch.)

Or pivot to:

- **Path 03 — Multi-Agent Systems.** The Lab 06–08 patterns transfer cleanly; multi-agent RAG is just two of these agents talking to each other.
- **Path 06 — Evaluation & Observability.** The proper home for the "is this actually good?" question. The Lab 08 quiz hints at why you can't fully answer this without dedicated evaluation tooling.
