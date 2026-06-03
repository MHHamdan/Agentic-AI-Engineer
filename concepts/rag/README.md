# 📖 Concepts · RAG

> 🟢 Stable explainers · concepts/rag/ is the conceptual spine of Path 02 (Agentic RAG).

The pages here cover the *stable* conceptual material for retrieval-augmented generation: what RAG is, how it relates to the agent loop, the decisions that govern how a corpus gets chunked and indexed, the strategies that improve retrieval quality, and the corpus-side and query-side interventions for the harder failure modes. Fast-changing tools (embedding models, vector stores) have their own versioned snapshots in [`tools/embeddings/`](../../tools/embeddings/) and [`tools/vector-stores/`](../../tools/vector-stores/).

## Current pages

### Foundations (read these first)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [what-is-rag.md](./what-is-rag.md) | ~10 min | The pattern, naive vs agentic, what RAG does and doesn't fix. |
| 📖 [retrieval-as-a-tool.md](./retrieval-as-a-tool.md) | ~9 min | The agentic framing: how retrieval becomes a tool inside the Lab 01/03 loop. |
| 📖 [chunking-and-indexing.md](./chunking-and-indexing.md) | ~12 min | Stable patterns: chunk size, overlap, boundaries, metadata, what an index actually is. |

These three are prerequisites for [Lab 06](../../labs/06-agentic-rag-from-scratch/).

### Retrieval quality

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [retrieval-strategies.md](./retrieval-strategies.md) | ~11 min | The four knobs that drive retrieval quality: top_k, score floors, MMR, query construction. |
| 📖 [hybrid-search.md](./hybrid-search.md) | ~10 min | BM25 + dense fusion via reciprocal rank fusion (RRF). When hybrid beats dense alone. |
| 📖 [reranking.md](./reranking.md) | ~10 min | Cross-encoder reranking, the retrieve-then-rerank pipeline, what changes vs bi-encoders. |
| 📖 [lost-in-the-middle.md](./lost-in-the-middle.md) | ~8 min | Why a perfect retriever can still answer wrong: U-shaped accuracy by context position, and how to measure it (Lab 58). |
| 📖 [multimodal-rag.md](./multimodal-rag.md) | ~10 min | Retrieval over images/tables/charts: shared-space vs caption-then-embed, mixed-content chunking, and grounding/OCR eval. |

These three are prerequisites for [Lab 07](../../labs/07-retrieval-strategies-and-reranking/).

### Quality interventions

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [contextual-retrieval.md](./contextual-retrieval.md) | ~11 min | Anthropic's chunk-augmentation technique. Indexing with LLM-generated doc context. |
| 📖 [query-rewriting.md](./query-rewriting.md) | ~10 min | HyDE, multi-query expansion, decomposition. The query-side counterpart. |
| 📖 [retrieval-failure-modes.md](./retrieval-failure-modes.md) | ~11 min | The synthesis: 8 RAG failure modes, how to diagnose each, which intervention to reach for. |

These three are prerequisites for [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/), and the failure-modes page is the debugging mental model the whole Path 02 curriculum builds toward.

### SOTA patterns (2024-2026)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [sota-rag-patterns.md](./sota-rag-patterns.md) | ~15 min | Self-RAG, Corrective RAG (CRAG), Adaptive RAG, Agentic RAG, Graph RAG, long-context and multimodal RAG. When each pattern earns its cost, with citations. |

This page is the map of the modern RAG landscape. Read it after the foundations and failure-modes pages; it assumes you know the canonical pipeline and want to know what to add and when.

## Pending pages (future Path 02 batches)

The following concept pages are forward-referenced from this curriculum but not yet authored:

- `conversational-rag.md` — multi-turn query rewriting, chat history handling, when to recompute retrieval.
- `framework-bridge-rag.md` — same Lab 06–08 agent in LangChain/LangGraph.

> RAG evaluation (faithfulness, groundedness, citation accuracy) is covered in [`concepts/evaluation/rag-evaluation-framework.md`](../evaluation/rag-evaluation-framework.md), the consolidated A-Z evaluation hub, cross-referenced from here.

## Where this is used

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — built on the foundations pages.
- 🧪 [Lab 07: Retrieval strategies and reranking](../../labs/07-retrieval-strategies-and-reranking/) — built on the retrieval-quality pages, extends Lab 06.
- 🧪 [Lab 08: Contextual retrieval and query rewriting](../../labs/08-contextual-retrieval-and-query-rewriting/) — built on the quality-interventions pages, extends Lab 07.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — curated reading list using these pages.
