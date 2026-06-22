# IVF and quantization

> Concept note. ~8 min. Builds on [similarity and ANN](./similarity-and-ann.md). Runnable companion: [`labs/03-rag-and-ann/`](../../labs/03-rag-and-ann/) (`ann.py`).

Two more techniques cover the cases graph indexes do not: **IVF** cuts the number of vectors searched, and **quantization** cuts the cost of storing and comparing each one. They combine, and together they are how billion-scale indexes fit in memory.

## IVF: search fewer vectors

The **inverted file (IVF)** index partitions the vectors into cells with k-means: learn a set of centroids, and assign each vector to its nearest one. At query time, find the few centroids nearest the query and search only the vectors in those cells, ignoring the rest. The knob is **nprobe** — how many cells to search. Probe one cell and you scan a small fraction of the data for approximate results; probe every cell and you are back to exact search. The lab builds exactly this and traces the curve: nprobe=1 gives ~0.79 recall scanning 13% of the vectors, and nprobe=nlist recovers recall 1.00 at full scan. IVF is simple, memory-light (it stores the vectors plus a centroid table), and easy to tune, which is why it is a common baseline.

## Quantization: store and compare cheaper

A raw embedding can be hundreds of dimensions of 32-bit floats — large, and slow to compare in bulk. **Product quantization (PQ)** compresses it: split the vector into sub-vectors, replace each with the nearest entry from a small learned codebook, and store the short codes instead of the floats. The result is a fraction of the memory, and distances can be approximated from the codes with table lookups instead of full arithmetic. The cost is accuracy — the codes are lossy — so PQ trades some recall for large memory and speed gains.

## Putting it together, and choosing

IVF and PQ compose: **IVF+PQ** probes a few cells *and* stores compressed vectors, which is how indexes scale to billions of vectors in bounded memory. Choosing among the families is a balance of four quantities:

- **recall** — how exact you need to be,
- **latency** — your query-time budget,
- **memory** — how much RAM the index may use,
- **build and update cost** — how often the corpus changes.

Graph indexes ([HNSW](./hnsw.md)) favor recall and latency at a memory cost; IVF favors simplicity and memory; PQ favors memory and speed at a recall cost; IVF+PQ targets scale. There is no universally best index — only the one that fits your point on those four axes.

## What to remember

- IVF clusters the vectors and searches only the cells near the query; nprobe trades recall for speed.
- Product quantization compresses vectors into codebook codes, cutting memory and comparison cost for some recall.
- The two compose (IVF+PQ) for billion-scale indexes; index choice balances recall, latency, memory, and update cost.

## References

- Jégou, H., Douze, M. & Schmid, C. (2011). *Product Quantization for Nearest Neighbor Search.*
- Johnson, J., et al. (2017). *Billion-scale similarity search with GPUs (FAISS).* arXiv:1702.08734. See [`../../references/references.md`](../../references/references.md).
