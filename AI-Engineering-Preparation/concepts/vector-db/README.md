# Vector databases

The storage and search layer under retrieval: how embeddings are indexed for approximate nearest-neighbor search, and the accuracy/latency/memory tradeoffs that drive index choice.

> Batch 03: notes delivered. Runnable companion: [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/) (`ann.py`).

## Notes

1. [Similarity and approximate nearest neighbors](./similarity-and-ann.md) — why exact search stalls; recall@k; the index families.
2. [HNSW: graph-based ANN](./hnsw.md) — navigable small-world graphs, layers, the efSearch dial.
3. [IVF and quantization](./ivf-and-quantization.md) — cluster-and-probe; product quantization; choosing an index.

## Key references

- HNSW — arXiv:1603.09320.
- Billion-scale similarity search (FAISS) — arXiv:1702.08734.
- Product Quantization for Nearest Neighbor Search (2011).

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
