# 🗄️ Tools · Vector stores

> 🔴 Fast-changing. The vector-database market is consolidating but still evolving. Pricing models, hybrid-search support, and managed-vs-self-hosted offerings shift continuously.

This folder is a *survey* of the vector-store landscape, not a usage tutorial. The Path 02 headline lab (Lab 06) uses an in-memory numpy index because the cosine math is identical and the pedagogy is clearer. When a future lab needs production-grade infrastructure, it'll add a per-tool snapshot page with the verified API and current pinned version.

## Current pages

| Page | What it covers | Verified |
|------|----------------|----------|
| 📌 [snapshot-v1.0.md](./snapshot-v1.0.md) | The 2026 vector-store landscape: Chroma, pgvector, Qdrant, Weaviate, Pinecone, plus FAISS as honorable mention. A decision aid, not a how-to. | 2026-05-24 |

## Where this is used in the curriculum

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — uses numpy, mentions this snapshot for production paths.
- 📖 [Chunking and indexing](../../concepts/rag/chunking-and-indexing.md) — references this for "what production vector stores add on top of numpy."

## What's not here (and why)

We don't pin specific versions of each vector store in the survey — they each have their own release cadence, and forcing a single verification date across all of them would be misleading. When a lab requires a specific store, it'll get a dedicated `tools/<tool>/snapshot-v*.md` with that store's pinned version and primary-source URL.
