# HNSW: graph-based ANN

> Concept note. ~8 min. Builds on [similarity and ANN](./similarity-and-ann.md).

**Hierarchical Navigable Small World (HNSW)** is the graph index behind many vector databases. It earns that place by hitting high recall at low latency, which is what most online retrieval needs. The intuition is worth having even without the implementation.

## The idea: walk a graph toward the query

Connect each vector to a handful of its near neighbors, forming a graph. To search, start at some node and repeatedly step to whichever neighbor is closer to the query, until no neighbor improves — a greedy walk downhill toward the nearest vectors. Because the graph is built so that near vectors are linked, this walk reaches the neighborhood of the answer after visiting only a tiny fraction of the nodes, not all of them.

The catch with a plain neighbor graph is that the walk can take many small steps across the space. HNSW fixes this with **layers**, like a skip list for geometry: sparse upper layers with long-range links let the search cross the space in a few big hops, then denser lower layers refine locally. Enter at the top, traverse coarse-to-fine, and arrive near the answer quickly.

## The knobs

- **M** — how many neighbors each node keeps. Higher M means a richer graph: better recall, more memory, slower build.
- **efConstruction** — how hard the build works to find good neighbors; higher gives a better graph at higher build cost.
- **efSearch** — how many candidates the search keeps in play at query time. This is the live recall/latency dial: raise it for higher recall and higher latency, lower it for the reverse — the same tradeoff `nprobe` controls for [IVF](./ivf-and-quantization.md).

## Where it fits

HNSW's strength is excellent recall at low latency, which makes it a default for latency-sensitive retrieval. Its costs are memory (the graph of links is held in addition to the vectors) and updates — deleting and re-inserting nodes while keeping the graph healthy is more involved than appending to a list. When memory is tight or the corpus is enormous, HNSW is often combined with [quantization](./ivf-and-quantization.md) to shrink the vectors it stores.

## What to remember

- HNSW links vectors into a navigable graph and greedily walks toward the query, visiting few nodes.
- Layers give long-range hops first, local refinement second — fast convergence across the space.
- efSearch is the recall/latency dial; the costs are memory and harder updates, often offset with quantization.

## References

- Malkov, Yu. A. & Yashunin, D. A. (2016). *Efficient and Robust Approximate Nearest Neighbor Search Using HNSW Graphs.* arXiv:1603.09320. See [`../../references/references.md`](../../references/references.md).
