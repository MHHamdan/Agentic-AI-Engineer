# Path 03: Retrieval & memory

How systems give a frozen model fresh, grounded knowledge — and how agents keep track of what they are doing across long tasks. This path covers retrieval-augmented generation, the vector databases under it, and the separation of agent state from memory.

## Learning objectives

- Build a RAG pipeline: chunk, embed, retrieve, rerank, generate, and cite.
- Explain approximate nearest-neighbor indexes and their accuracy/latency/memory tradeoffs.
- Separate agent state (the current task) from memory (what carries across tasks).
- Design a memory lifecycle and a context budget that does not overflow the window.

## Planned modules

1. RAG end-to-end: the retrieve-then-generate pattern.
2. Chunking, embeddings, and hybrid retrieval.
3. Reranking and citation/attribution.
4. Vector databases and ANN indexes (HNSW, IVF, product quantization).
5. Agent state vs. memory: short-term, long-term, external.
6. The memory lifecycle and consistency under change.
7. Context engineering: budgeting the window.

## Concept areas in this path

- [`concepts/rag`](../../concepts/rag/)
- [`concepts/vector-db`](../../concepts/vector-db/)
- [`concepts/memory`](../../concepts/memory/)
- [`concepts/context`](../../concepts/context/)

## Capstone

- [`projects/rag-with-evals`](../../projects/rag-with-evals/)

## References

Canonical sources for this path are collected in [`references/references.md`](../../references/references.md). Curriculum sequencing only; all explanations are original. See [`STYLE.md`](../../STYLE.md).
