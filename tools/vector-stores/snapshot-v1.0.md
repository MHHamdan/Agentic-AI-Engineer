# Vector stores — tool snapshot

> 🔴 **Tool snapshot — vector store landscape, verified 2026-05-24**
> Primary sources: each tool's official documentation, linked per row. This is a survey, not a how-to.

This page is a *decision aid*, not a tutorial. The Path 02 headline lab (Lab 06) uses a numpy in-memory index because it's the right pedagogical choice. When you outgrow that — or when you start a non-tutorial project — you'll pick a real vector store. This page tells you which ones to consider and why.

## Where Path 02 stands

Lab 06 doesn't use any of these. It uses `numpy` + cosine similarity. That's fine up to a few thousand chunks; the math is the same.

When a future Path 02 lab needs production-grade infrastructure (re-ranking with a real corpus, hybrid search benchmarks, etc.) it'll add a per-tool snapshot under `tools/<tool>/snapshot-v*.md` with the verified API and current pinned version. Until then this page is the only place these tools are documented.

## The 2026 vector store landscape, briefly

Five names dominate community discussion as of mid-2026: **Chroma, pgvector, Qdrant, Weaviate, Pinecone**. There are others — Milvus, LanceDB, Turbopuffer, OpenSearch k-NN, Redis with RediSearch, FAISS — but if you're starting out, the five above are where the documentation and Stack Overflow answers live.

The decisions matrix that drives "which one":

| If your situation is... | Lean toward |
|---|---|
| Prototyping locally, want zero infrastructure | **Chroma** (embedded mode) |
| Already running Postgres in production | **pgvector** |
| Self-hosting and want best price-performance | **Qdrant** |
| Want managed and willing to pay the premium | **Pinecone** |
| Need built-in hybrid search and/or schema | **Weaviate** |
| Need pure ANN with maximum raw performance | **FAISS** as a library inside your own service |
| Already have OpenSearch / Elasticsearch | **OpenSearch k-NN** (extend existing infra) |

The cost of getting the choice wrong is real but bounded: chunks have stable embeddings, your code talks to the store through ~10 lines of API, and migrating between stores is a one-time data shuffle. Don't agonize over this for a prototype.

---

## Chroma

- **Open-source**, embedded-or-server, simple Python API, very low operational footprint.
- **Production-ready for many use cases** in 2026 (the "just a dev tool" reputation lags reality). Single-VPS deployments handle low millions of embeddings comfortably.
- **No native hybrid search (BM25 + dense)** — this is the most-commonly-cited gap.
- **API**:
  ```python
  import chromadb
  client = chromadb.PersistentClient(path="./chroma_db")
  collection = client.get_or_create_collection("docs")
  collection.add(ids=["1"], embeddings=[emb], documents=["text"], metadatas=[{"source": "x"}])
  results = collection.query(query_embeddings=[query_emb], n_results=5)
  ```
- **License**: Apache 2.0.
- **When to use**: prototyping, single-node production, anything where operational simplicity matters more than raw throughput. The most defensible default if "build a RAG in a day" is the constraint.
- **Watch for**: lock-in to Chroma's collection-level abstractions; awkward to mix retrievers across the same store.
- **Official docs**: [docs.trychroma.com](https://docs.trychroma.com/).

## pgvector

- **Postgres extension** adding the `vector` type and `<->` / `<=>` distance operators. Index types include IVFFlat and HNSW.
- **Current 0.7+ series** (mid-2026) includes parallel index builds and improved HNSW performance. Production-grade.
- **Production ceiling** is single-node Postgres scale — roughly 50M vectors on a well-provisioned instance, more with `pgvectorscale` (an open-source extension that adds StreamingDiskANN and partitioned indexes for the "billions of vectors" regime).
- **API**:
  ```sql
  CREATE EXTENSION vector;
  CREATE TABLE docs (id bigserial, embedding vector(384), text text);
  CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops);
  SELECT * FROM docs ORDER BY embedding <=> $1 LIMIT 5;
  ```
- **License**: PostgreSQL License (permissive).
- **When to use**: you already run Postgres and want vector search in the same DB without adding infra. Companies including Supabase, Neon, and Instacart run this in production.
- **Watch for**: large vector workloads can degrade performance on the rest of your Postgres workload; consider a dedicated DB instance.
- **Official docs**: [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector).

## Qdrant

- **Open-source dedicated vector database**, written in Rust. Strong on price-performance — self-hosted on a small VPS handles 10M+ vectors comfortably.
- **Rich metadata filtering** is a real strength; useful for "embeddings + structured filters" workloads (legal, financial, etc.).
- **Native hybrid search** since v1.9 (named-vector / multi-vector model).
- **API**:
  ```python
  from qdrant_client import QdrantClient
  from qdrant_client.models import PointStruct, VectorParams, Distance
  client = QdrantClient(":memory:")  # or url=...
  client.create_collection(
      collection_name="docs",
      vectors_config=VectorParams(size=384, distance=Distance.COSINE),
  )
  client.upsert(collection_name="docs", points=[PointStruct(id=1, vector=emb, payload={...})])
  hits = client.search(collection_name="docs", query_vector=q, limit=5)
  ```
- **License**: Apache 2.0.
- **When to use**: self-hosted production with metadata filtering, hybrid search, or horizontal scaling. Best price-performance ratio of the dedicated vector DBs.
- **Watch for**: operational footprint is heavier than embedded options. Run-it-yourself or pay for Qdrant Cloud.
- **Official docs**: [qdrant.tech/documentation](https://qdrant.tech/documentation/).

## Weaviate

- **Open-source vector database with built-in modules** for generating embeddings (insert text, the DB calls the embedding model). Schema-rich and module-rich, with native hybrid search (BlockMax WAND + RSF fusion).
- **Heaviest of the open-source options** in terms of operational complexity, but pays off when you need its features.
- **API**:
  ```python
  import weaviate
  client = weaviate.connect_to_local()
  collection = client.collections.get("Docs")
  collection.data.insert({"text": "...", "source": "..."}, vector=emb)
  resp = collection.query.near_vector(near_vector=q, limit=5)
  # Or for hybrid search:
  resp = collection.query.hybrid(query="text query", vector=q, alpha=0.5, limit=5)
  ```
- **License**: BSD-3-Clause.
- **When to use**: hybrid search and/or multi-modal retrieval are first-class requirements *and* you're willing to invest in the system's vocabulary. Overbuilt for simple semantic-search workloads.
- **Watch for**: vocabulary surface (modules, vectorizers, schema classes) is steep to learn relative to Chroma or Qdrant.
- **Official docs**: [weaviate.io/developers/weaviate](https://weaviate.io/developers/weaviate).

## Pinecone

- **Managed-only, proprietary.** No self-hosted option. The dominant managed vector database in 2026 production AI.
- **Serverless architecture** (introduced 2024) replaced the older pod-based pricing. Scales to zero cost when idle; pay per query and storage.
- **Native hybrid search** via proprietary sparse encoding.
- **API**:
  ```python
  from pinecone import Pinecone, ServerlessSpec
  pc = Pinecone(api_key=...)
  index = pc.Index("docs")
  index.upsert(vectors=[("1", emb, {"text": "..."})])
  res = index.query(vector=q, top_k=5, include_metadata=True)
  ```
- **License**: proprietary; service-only.
- **When to use**: no infrastructure team, want managed everything, willing to pay the premium. Variable RAG workloads (serverless scales to zero) get particularly good economics.
- **Watch for**: vendor lock-in by definition; pricing predictability changed when the serverless model rolled out, so check current rates.
- **Official docs**: [docs.pinecone.io](https://docs.pinecone.io/).

## FAISS (honorable mention)

- **A library, not a database.** No persistence layer, no API server, no metadata storage. Pure C++ ANN index with Python bindings.
- **Used inside** many of the databases above — Qdrant, Weaviate, and others incorporate FAISS-derived algorithms.
- **API**:
  ```python
  import faiss
  index = faiss.IndexFlatIP(384)        # inner product on normalized vectors
  index.add(embeddings_array)
  D, I = index.search(query_emb_array, k=5)
  ```
- **License**: MIT.
- **When to use**: you're building your own service and want the fastest possible ANN with no overhead. You'll wrap it with your own persistence and metadata.
- **Watch for**: needs significant engineering to be production-usable as a service.
- **Official docs**: [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss).

---

## What we deliberately don't cover (and why)

- **OpenSearch / Elasticsearch k-NN** — solid choice if you're already running OpenSearch. If you're not, the operational cost of adopting it for vector search alone is too high; pick one of the dedicated stores.
- **Milvus** — strong technology, dominant in some Chinese-language ecosystems, less mind-share in Anglophone communities. Reasonable production choice; just less likely to be where a new learner starts.
- **LanceDB** — relatively new (2023+), columnar/embedded model, growing fast. Likely to be a serious contender by 2027; for a 2026 snapshot it's still niche enough that we're not making it a first-class recommendation here.
- **Turbopuffer** — managed, performant, less mind-share. Watch as the market shakes out.
- **Redis with RediSearch / RedisVL** — fine if you're already running Redis. Not a starting point.

This list is intentionally short. The five primary tools above plus FAISS cover ≥95% of the production decisions a Path 02 learner will face.

## Common pitfalls regardless of which store you pick

1. **Dimension mismatch.** Your embedding model emits 384-dim vectors and your collection is configured for 1536. Most errors with vector stores come from this. Always set the collection's dimension explicitly from the model's `get_sentence_embedding_dimension()`.
2. **Distance metric mismatch.** Cosine vs dot product vs L2. If your embeddings are normalized (recommended), use inner product. Most stores default to cosine but allow overrides; pick deliberately.
3. **Metadata schema drift.** Stores let you attach arbitrary metadata to vectors. Without a schema, you'll end up with inconsistent fields. Decide your metadata shape *before* indexing; treating "metadata is free" is how you get unfilterable corpora.
4. **Index parameters chosen badly.** HNSW's `m` and `ef_construction`, IVFFlat's `nlist` — these matter at scale. At <10K vectors they don't. Don't over-tune until you've measured.

## Freshness check

This page is a survey, so the bar for "still current" is lower than a snapshot-of-a-specific-API. Trigger an update when:

- Any of the five tools above changes hosted-vs-self-hosted status or pricing model.
- A genuinely new player emerges with significant production traction (e.g., LanceDB graduating from niche to mainstream).
- Hybrid search becomes uniformly supported (it's currently the main differentiator).

Per-tool snapshot pages (when future labs need them) carry their own verified APIs and pinned versions.

## Primary sources

| Tool | Source |
|---|---|
| Chroma | [docs.trychroma.com](https://docs.trychroma.com/) |
| pgvector | [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) |
| Qdrant | [qdrant.tech/documentation](https://qdrant.tech/documentation/) |
| Weaviate | [weaviate.io/developers/weaviate](https://weaviate.io/developers/weaviate) |
| Pinecone | [docs.pinecone.io](https://docs.pinecone.io/) |
| FAISS | [github.com/facebookresearch/faiss/wiki](https://github.com/facebookresearch/faiss/wiki) |

The numbers in this page (vector-count regimes, MTEB scores, etc.) come from independent comparative writeups verified May 2026 — they're directional, not authoritative. For decisions, benchmark on your own data.
