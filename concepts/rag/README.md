# 📖 Concepts · RAG

> 🟢 Stable explainers · concepts/rag/ is the conceptual spine of Path 02 (Agentic RAG).

The pages here cover the *stable* conceptual material for retrieval-augmented generation: what it is, how it relates to the agent loop, and the decisions that govern how a corpus gets chunked and indexed. Fast-changing tools (embedding models, vector stores) have their own versioned snapshots in [`tools/embeddings/`](../../tools/embeddings/) and [`tools/vector-stores/`](../../tools/vector-stores/).

## Current pages

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [what-is-rag.md](./what-is-rag.md) | ~10 min | The pattern, naive vs agentic, what RAG does and doesn't fix. |
| 📖 [retrieval-as-a-tool.md](./retrieval-as-a-tool.md) | ~9 min | The agentic framing: how retrieval becomes a tool inside the Lab 01/03 loop. |
| 📖 [chunking-and-indexing.md](./chunking-and-indexing.md) | ~12 min | Stable patterns: chunk size, overlap, boundaries, metadata, what an index actually is. |

## Pending pages (future Path 02 batches)

The following concept pages are forward-referenced from this batch but not yet authored. They'll land in subsequent Path 02 batches:

- `retrieval-strategies.md` — top-k tuning, MMR, re-ranking strategies.
- `hybrid-search.md` — BM25 + dense retrieval fusion.
- `contextual-retrieval.md` — Anthropic's contextual retrieval technique.
- `rag-evaluation.md` — faithfulness, groundedness, citation accuracy. (Likely lives in `concepts/evaluation/` cross-referenced from here.)

## Where this is used

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — primary consumer; all three pages are prerequisites.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — curated reading list using these pages.
