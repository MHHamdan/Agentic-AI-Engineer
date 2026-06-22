# Path 03: Retrieval & memory

How systems give a frozen model fresh, grounded knowledge — and how agents keep track of what they are doing across long tasks. This path covers retrieval-augmented generation, the vector databases under it, and the separation of agent state from memory.

> Status: **delivered** (Batches 03–04). All nine modules, two runnable labs, a math page, and two diagrams are in place.

## Learning objectives

- Build a RAG pipeline: chunk, embed, retrieve, rerank, generate, and cite.
- Explain approximate nearest-neighbor indexes and their accuracy/latency/memory tradeoffs.
- Separate agent state (the current task) from memory (what carries across tasks).
- Design a memory lifecycle and a context budget that does not overflow the window.

## Modules

### Retrieval (Batch 03)

| # | Note | Topic |
|---|---|---|
| 1 | [RAG end-to-end](../../concepts/rag/rag-end-to-end.md) | retrieve-then-generate; grounding; abstention |
| 2 | [Chunking and retrieval](../../concepts/rag/chunking-and-retrieval.md) | chunk sizing; lexical/dense/hybrid; top-k |
| 3 | [Reranking and citation](../../concepts/rag/reranking-and-citation.md) | cross-encoder rerank; verifiable citation; coverage |
| 4 | [Similarity and approximate nearest neighbors](../../concepts/vector-db/similarity-and-ann.md) | why exact stalls; recall@k; index families |
| 5 | [HNSW](../../concepts/vector-db/hnsw.md) | navigable graphs; layers; efSearch |
| 6 | [IVF and quantization](../../concepts/vector-db/ivf-and-quantization.md) | cluster-and-probe; PQ; choosing an index |

### Memory & context (Batch 04)

| # | Note | Topic |
|---|---|---|
| 7 | [State vs. memory](../../concepts/memory/state-vs-memory.md) | rewindable state vs. durable memory |
| 8 | [Short-term, long-term, and external memory](../../concepts/memory/memory-types.md) | the three tiers; RAM/disk |
| 9 | [The memory lifecycle](../../concepts/memory/memory-lifecycle.md) | create/read/update/delete; consolidation; consistency |
| 10 | [Context engineering](../../concepts/context/context-engineering.md) | write/select/compress/isolate |
| 11 | [Context strategies](../../concepts/context/context-strategies.md) | just-in-time retrieval; compaction; note-taking; isolation |
| 12 | [Context rot and failure modes](../../concepts/context/context-rot-and-failure-modes.md) | why long contexts degrade |

## Labs

- [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/) — a minimal RAG pipeline and an exact-vs-IVF nearest-neighbor tradeoff study.
- [`labs/04-memory-and-context/`](../../labs/04-memory-and-context/) — a checkpointed state-vs-memory agent and a context-budget assembler.

## Math

- [`math-foundations/03-nearest-neighbor-search.md`](../../math-foundations/03-nearest-neighbor-search.md) — the k-NN problem, exact cost, recall@k, and the IVF tradeoff.

## Diagrams

- [`diagrams/rag-pipeline.md`](../../diagrams/rag-pipeline.md) — the indexing and query phases of RAG.
- [`diagrams/agent-state-and-memory.md`](../../diagrams/agent-state-and-memory.md) — state, memory, and the assembled context window.

## Concept areas in this path

- [`concepts/rag`](../../concepts/rag/) · [`concepts/vector-db`](../../concepts/vector-db/) · [`concepts/memory`](../../concepts/memory/) · [`concepts/context`](../../concepts/context/)

## References

Canonical sources for this path are collected in [`references/references.md`](../../references/references.md). Curriculum sequencing only; all explanations are original. See [`STYLE.md`](../../STYLE.md).
