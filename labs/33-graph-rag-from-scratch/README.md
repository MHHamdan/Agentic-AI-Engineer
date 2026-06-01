# Lab 33: Graph RAG from scratch

> 🔴 Advanced · ⏱ ~110–140 min · 📚 Builds on Lab 06's corpus

## 🎯 Goal

Replace the flat vector index with a knowledge graph. Extract entities and relationships from the corpus, build a graph, detect communities of related entities, summarize each community, and answer two query types: GLOBAL questions ("what are the themes?") by map-reduce over community summaries, and LOCAL questions (about a specific entity) by traversing its neighborhood.

By the end you should be able to:

- Extract entities and relationships from documents into a graph with `networkx`.
- Detect communities and summarize them as the substrate for global queries.
- Implement the global (map-reduce) and local (traversal) query paths and route between them.
- Show a global question that flat chunk-retrieval handles poorly and GraphRAG handles well.
- Articulate GraphRAG's defining tradeoff: high index-time cost for global/multi-hop capability.

## 📋 Prerequisites

**Read first:**

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Pattern 5 (Graph RAG)
- 🖼 [RAG diagram bundle](../../diagrams/rag-bundle.md) — diagram 6 (Graph RAG workflow)

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../06-agentic-rag-from-scratch/) — reuses its corpus (the contrast: flat retrieval vs graph).

**Setup:** Python 3.11+ with the repo environment, plus one new dependency:

```bash
uv add 'networkx>=3.0'
```

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `networkx` | `>=3.0` | Graph construction + greedy-modularity community detection |
| `openai` *or* `anthropic` | from prior labs | LLM for extraction, summarization, routing, synthesis |

No embedding model is strictly required for the graph paths, though a hybrid GraphRAG would combine both. This lab keeps the graph paths pure to make the mechanism legible.

## What you'll build

A `graph_rag(query)` pipeline: `extract_entities_relations` (per-doc LLM extraction), `build_graph` (networkx), `detect_communities` + `summarize_community` (index-time), and the two query paths `graph_rag_global` (map-reduce over community summaries) and `graph_rag_local` (subgraph traversal), with a router that picks between them.

## Steps

1. **Setup + load documents** (Steps 0–1). Whole docs, not fine chunks.
2. **Extract entities and relationships** (Step 2). One LLM call per doc — the expensive part.
3. **Build the graph** (Step 3). networkx nodes/edges with doc provenance.
4. **Detect communities** (Step 4). Greedy modularity (Leiden stand-in).
5. **Summarize communities** (Step 5). The substrate for global queries.
6. **Query paths** (Step 6). Global map-reduce; local traversal.
7. **Route and answer** (Step 7).
8. **See the global-question win** (Step 8). A themes question flat RAG misses.

## What we don't do in this lab

- **We don't use Leiden clustering.** The paper uses Leiden; we use networkx greedy modularity (no extra dependency). Faithful to the control flow; simplified in the clustering algorithm.
- **Summarization is flat, not hierarchical.** The paper builds a hierarchy of community summaries at multiple resolutions. We summarize one level.
- **Entity resolution is best-effort.** We canonicalize by lowercasing names; real systems do entity resolution (coreference, aliasing). Same-name merge is the lab-grade version.

## Common gotchas

- **Index-time cost is the headline.** Entity extraction is one LLM call per document, plus a summarization call per community. On a large corpus this is the dominant cost, and re-indexing on every corpus change is expensive — which is why GraphRAG suits relatively stable corpora.
- **Entity-name drift fragments the graph.** If "the agent loop" and "agent loop" become separate nodes, the graph splinters. The lowercasing canonicalization mitigates this; watch for it on real corpora.
- **Global vs local routing matters.** Sending a specific-entity question down the global path wastes a map-reduce over every community; sending a themes question down the local path misses the cross-corpus synthesis. The router is load-bearing.

## Solution discussion

- **Why global uses map-reduce.** A themes question has no single answer chunk; the answer is distributed across the corpus. Mapping over community summaries then reducing is how GraphRAG synthesizes corpus-wide, which flat top-k retrieval structurally cannot do.
- **Why nodes track their source docs.** Provenance (`docs` set per node) lets answers cite where an entity came from, and supports debugging the extraction step.

## 🧮 Going deeper

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — global-question quality needs different eval than chunk retrieval.
- 🧮 [Multi-agent coordination graphs](../../math-foundations/10-multi-agent-coordination.md) — the graph-theoretic view, reused here for knowledge rather than agents.

## ✅ Check your understanding

- 🧠 [SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md) — question 5 covers Graph RAG.

## What comes next

You've now built the three self-corrective / restructured RAG patterns from scratch (CRAG, Self-RAG, GraphRAG). Natural continuations: combine them (an agentic loop that routes to graph or flat retrieval), or measure them head-to-head on a shared eval set using the [evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md).
