# Vector Indexes: From Numpy to Production

A vector index is a data structure that, given a query embedding, returns the top-k most similar embeddings from a collection. That's the entire specification. Everything else — persistence, network APIs, metadata filtering, hybrid search, management UIs — is plumbing around that core capability.

## The brute-force baseline

The simplest possible vector index is a numpy array.

```python
import numpy as np

# embeddings: shape (num_chunks, embedding_dim), all unit-normalized
# query_emb: shape (embedding_dim,), unit-normalized
scores = embeddings @ query_emb              # shape (num_chunks,)
top_indices = np.argsort(scores)[::-1][:k]   # indices of top-k
```

This is brute-force search: every query computes similarity against every stored vector. The cost is O(n) per query, where n is the number of vectors. On a laptop, this handles up to roughly 10,000 vectors with sub-100-millisecond latency. For a tutorial corpus, it's the right choice.

This is also the math every production vector store implements, just wrapped in more sophisticated algorithms for scale.

## Approximate Nearest Neighbor

At larger scale, brute-force becomes impractical. The standard mitigation is Approximate Nearest Neighbor (ANN) search: instead of computing similarity against every vector, build a pre-computed structure that lets queries find approximate top-k in sublinear time.

The most common ANN algorithm in 2026 is HNSW — Hierarchical Navigable Small World graphs. HNSW maintains a multi-layer graph where each node connects to a curated set of similar nodes. Queries start at the top layer and navigate down, refining the candidate set at each level. The result is approximate — the true top-k may not be the returned top-k — but for well-tuned indexes the recall stays above 95% at orders of magnitude lower latency than brute-force.

Other ANN algorithms include IVF (Inverted File index, used in FAISS), ScaNN (Google's optimized variant), and DiskANN (designed for indexes that don't fit in memory). The trade-offs are between recall, latency, memory footprint, index-build time, and update characteristics. Most production systems use HNSW or a variant.

## What "production-grade" actually means

Beyond the indexing algorithm, production vector stores provide several capabilities that a numpy array does not.

**Persistence**: the index survives restarts. Brute-force-on-numpy means re-embedding the corpus every time you restart. Production stores save the index to disk.

**Metadata storage and filtering**: each vector has associated metadata (document ID, chunk ID, timestamps, tags). Queries can filter by metadata before similarity search — "find similar chunks from documents tagged 'policy'" — which is more efficient than retrieving similar chunks and then filtering.

**Updates**: vectors can be added and removed without rebuilding the whole index. HNSW handles this gracefully; IVF and some other algorithms require periodic re-indexing.

**Concurrent access**: multiple processes can query simultaneously without locking.

**Network APIs**: the store runs as a service that your application talks to over HTTP or gRPC. This decouples the index from the application lifecycle.

**Operational tooling**: backups, monitoring, schema migration. The boring infrastructure work that any production data store needs.

## Choosing a store

Five names dominate community discussion in 2026:

**Chroma** is open-source, runs embedded or as a server, has a simple Python API. Production-ready for many use cases despite its early reputation as a dev tool. The natural default for prototyping.

**pgvector** is a PostgreSQL extension. If you already run Postgres, it adds vector search without new infrastructure. The 0.7+ series is production-grade up to roughly 50 million vectors per Postgres instance.

**Qdrant** is an open-source dedicated vector database written in Rust. Strong on price-performance for self-hosted deployments, with rich metadata filtering and native hybrid search.

**Weaviate** is open-source with built-in modules for generating embeddings inline. The most feature-rich option but the heaviest to learn.

**Pinecone** is managed-only and proprietary. The dominant managed offering, with a serverless tier that scales to zero. The premium price buys operational simplicity.

There are others — Milvus, LanceDB, Turbopuffer, OpenSearch k-NN — but the five above cover most decisions. The right choice depends on scale, infrastructure preferences, and feature requirements rather than philosophical preferences.

## When to upgrade from brute-force

Three rough signals:

The corpus has crossed roughly 10,000-50,000 chunks and queries are getting slower than you'd like.

You need persistence — restart-without-re-indexing — and you're tired of managing it manually.

You need metadata filtering on a non-trivial schema, and your current approach (filter then search, or search then filter) is producing wrong results.

If none of these apply, brute-force-on-numpy is genuinely fine. Many production systems run this way for years before outgrowing it. Don't reach for vector store infrastructure prematurely.
