# Retrieval-augmented generation (RAG)

Giving a frozen model fresh, grounded knowledge by retrieving relevant context at query time. Covers chunking, embeddings, retrieval and reranking, generation, and citation.

> Batch 03: notes delivered. Runnable companion: [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/).

## Notes

1. [RAG end-to-end](./rag-end-to-end.md) — the retrieve-then-generate pattern; why RAG over fine-tuning; what goes wrong.
2. [Chunking and retrieval](./chunking-and-retrieval.md) — chunk sizing; lexical, dense, and hybrid retrieval; top-k.
3. [Reranking and citation](./reranking-and-citation.md) — two-stage retrieval with a cross-encoder; verifiable citation; coverage.

## Key references

- Retrieval-Augmented Generation — arXiv:2005.11401.
- Dense Passage Retrieval — arXiv:2004.04906.
- BM25 / the probabilistic relevance framework.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
