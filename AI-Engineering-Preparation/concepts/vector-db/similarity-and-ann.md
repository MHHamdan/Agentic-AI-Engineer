# Similarity and approximate nearest neighbors

> Concept note. ~9 min. Runnable companion: [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/) (`ann.py`). Math: [`math-foundations/03`](../../math-foundations/03-nearest-neighbor-search.md).

A vector database does one thing well: given a query vector, find the stored vectors closest to it, fast, over millions or billions of them. Everything else — retrieval, "find similar," recommendations — is that one operation. This note is why it is hard and how it is made fast.

## Similarity is the easy part

Closeness between [embeddings](../llm/tokens-and-embeddings.md) is usually [cosine similarity](../../math-foundations/01-embeddings-and-similarity.md) — the dot product of length-normalized vectors — or plain dot product when vectors are already normalized. That is a handful of multiply-adds per comparison. The problem is not one comparison; it is doing it against every stored vector.

## Exact search does not scale

To return the true nearest neighbors, exact search compares the query against all *n* vectors of dimension *d*: cost on the order of *n·d* per query. At a few thousand vectors that is fine. At tens of millions, with many queries per second and a latency budget in milliseconds, it is hopeless — the work grows linearly with the corpus and there is no corpus-size you can grow into. This is the wall every retrieval system hits.

## ANN: trade a little recall for a lot of speed

The escape is to stop insisting on the *exact* nearest neighbors and accept *almost* the nearest, much faster. An **approximate nearest neighbor (ANN)** index organizes the vectors so a query only has to look at a small, promising fraction of them. The quality of that approximation is **recall@k** — of the true top-k neighbors, how many the index actually returned. Every ANN index rides the same curve: look at more of the data for higher recall and higher latency, or less for the reverse. The lab measures exactly this curve on an IVF index — at one cluster, ~0.79 recall scanning 13% of the data; at all clusters, exact.

## The index families

- **Graph-based ([HNSW](./hnsw.md))** — connect vectors into a navigable graph and walk it toward the query. High recall at low latency; higher memory.
- **Cluster-based ([IVF](./ivf-and-quantization.md))** — partition vectors into cells and search only the cells near the query. Simple and tunable via how many cells you probe.
- **Quantization ([PQ](./ivf-and-quantization.md))** — compress vectors so more fit in memory and distances are cheaper, at some accuracy cost; usually combined with the above.

## What to remember

- A vector DB finds nearest neighbors under cosine/dot similarity; the measure is cheap, doing it over everything is not.
- Exact search is linear in corpus size and does not scale; ANN trades a little recall for large speedups.
- Recall@k quantifies the approximation; HNSW, IVF, and PQ are the families that buy speed, each with its own tradeoff.

## References

- Malkov, Yu. & Yashunin, D. (2016). *HNSW.* arXiv:1603.09320.
- Johnson, J., et al. (2017). *Billion-scale similarity search with GPUs (FAISS).* arXiv:1702.08734. See [`../../references/references.md`](../../references/references.md).
