# Nearest-neighbor search

> Mathematical foundation. ~8 min. Anchor: [`labs/03-rag-and-ann/`](../labs/03-rag-and-ann/) (`ann.py`). Supports [similarity and ANN](../concepts/vector-db/similarity-and-ann.md).

## Why this matters

Retrieval is nearest-neighbor search. This page states the problem, shows why the exact version does not scale, defines the metric used to judge approximations, and analyzes the IVF tradeoff the lab measures.

## The problem

Given a set of vectors $X = \{x_1, \dots, x_n\} \subset \mathbb{R}^d$ and a query $q$, the **k-nearest-neighbor** problem returns the $k$ indices minimizing a distance (or maximizing a similarity). With cosine similarity the target is

$$
\text{top-}k\;=\;\operatorname*{arg\,max}_{i}^{(k)} \; \cos(q, x_i),
$$

the $k$ vectors whose direction is closest to the query's (see [embeddings and similarity](./01-embeddings-and-similarity.md)).

## Exact search and why it stalls

Exact search evaluates the similarity for every stored vector and keeps the best $k$. Each comparison is $O(d)$, so a query is

$$
O(n \, d),
$$

linear in the corpus size $n$. Doubling the corpus doubles the work per query; at $n$ in the tens of millions and a millisecond budget, this is infeasible. The cost is structural — there is no corpus size you "grow into."

## Recall@k: scoring an approximation

An approximate index returns a set $\hat{N}$ of $k$ candidates that may not equal the true neighbor set $N$. Quality is **recall@k**:

$$
\text{recall@}k \;=\; \frac{|\,\hat{N} \cap N\,|}{k} \;\in\; [0, 1].
$$

It is $1$ when the index returned exactly the true neighbors and degrades as it misses them. Averaged over a query set, it is the y-axis of every ANN tradeoff curve.

## The IVF tradeoff, analyzed

IVF partitions the $n$ vectors into $\text{nlist}$ cells via k-means. If vectors split evenly, each cell holds about $n / \text{nlist}$ of them, so probing $\text{nprobe}$ cells scans roughly

$$
\text{scanned} \;\approx\; \frac{n \cdot \text{nprobe}}{\text{nlist}}
$$

vectors instead of $n$ — a speedup of about $\text{nlist} / \text{nprobe}$. Recall rises with $\text{nprobe}$ because the true neighbor is more likely to fall in one of the probed cells; at $\text{nprobe} = \text{nlist}$ every cell is searched and the method reduces to exact search (recall $1$, full scan). The lab reproduces this: at $\text{nprobe}=1$ of $12$, recall $\approx 0.79$ scanning $\approx n/8$; at $\text{nprobe}=12$, recall $1.0$ scanning all $n$. The misses at low $\text{nprobe}$ are the true neighbors that sit just across a cell boundary — the price of not looking everywhere.

## Quantization, briefly

Product quantization replaces each vector with short codes from learned codebooks, so a distance becomes a sum of table lookups rather than $d$ multiply-adds. Memory drops by the compression ratio and comparisons get cheaper, at the cost of approximating the true distance — another point on the same recall-vs-resources tradeoff.

## What to remember

- k-NN search returns the $k$ closest vectors; exact search is $O(nd)$ per query and does not scale.
- Recall@k measures how many true neighbors an approximate index returned; it is the quality axis of ANN.
- IVF scans about $n\cdot\text{nprobe}/\text{nlist}$ vectors; recall rises with nprobe to exact at nprobe = nlist.

## See also

- [`labs/03-rag-and-ann/`](../labs/03-rag-and-ann/) — the IVF tradeoff in code.
- [`concepts/vector-db/`](../concepts/vector-db/) — the same ideas in prose.
