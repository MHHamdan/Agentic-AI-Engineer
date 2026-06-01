# Lab 33 · Reference solution

The complete implementation of [Lab 33: Graph RAG from scratch](../README.md).

## What this is

A GraphRAG pipeline over Lab 06's corpus, using `networkx`:

- **`extract_entities_relations`** — per-document LLM extraction of entities + relationships (JSON).
- **`build_graph`** — networkx graph; entity nodes track source docs, edges carry relation descriptions.
- **`detect_communities`** — greedy modularity (Leiden stand-in).
- **`summarize_community`** — per-community summaries (the substrate for global queries).
- **`graph_rag_global`** — map-reduce over community summaries.
- **`graph_rag_local`** — seed-entity + neighborhood traversal.
- **`graph_rag`** — routes global vs local.

## Implementation choices

1. **`networkx` greedy modularity stands in for Leiden.** Leiden needs `igraph`/`leidenalg`; greedy modularity ships with networkx and is adequate for a lab. Marked as a simplification.
2. **Entity canonicalization by lowercasing.** Same-name entities across docs merge (their `docs` sets union). Real systems do entity resolution; lowercasing is the lab-grade version and the main thing to watch on real corpora.
3. **Global = map-reduce.** Each community summary produces a partial answer (or `NONE`); partials are synthesized. This is how GraphRAG answers corpus-wide questions flat top-k retrieval cannot.
4. **Local = bounded traversal.** Seed entities are those named in the query (or the highest-degree node as fallback), expanded `hops=1`. The subgraph edge list is the context.
5. **Nodes carry doc provenance** (`docs` set), so answers can cite sources and the extraction step is debuggable.

## What's deliberately out of scope

- **Leiden clustering** (see choice 1).
- **Hierarchical/multi-resolution community summaries.** We summarize one level.
- **Entity resolution** beyond lowercasing.
- **Hybrid graph+vector retrieval.** Kept pure-graph to make the mechanism legible.

## Running the solution

```bash
uv add 'networkx>=3.0'
cd labs/33-graph-rag-from-scratch/solution
jupyter notebook lab.ipynb
```

Index-time cost: one LLM call per document for extraction, plus one per community for summarization. On the 8-doc lab corpus this is a handful of calls; on a real corpus it dominates and motivates GraphRAG's "stable corpus" guidance.

## Next

You've built CRAG, Self-RAG, and GraphRAG from scratch. Combine them, or measure them head-to-head with the [RAG evaluation framework](../../../concepts/evaluation/rag-evaluation-framework.md).
