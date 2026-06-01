# Lab 34 · Reference solution

The complete implementation of [Lab 34: Head-to-head RAG pattern evaluation](../README.md).

## What this is

A comparison harness over four condensed pipelines and one shared corpus + eval set:

- **`pipe_static` / `pipe_crag` / `pipe_self_rag`** — three flat pipelines, common interface `{answer, retrieved_docs, retrieved}`.
- **`pipe_graph`** — Graph RAG; builds the knowledge graph once at setup, routes global (map-reduce over community summaries) vs local (subgraph traversal).
- **Scoring** — `doc_recall` (generation-side retrieval recall), `answer_correct` (expected-token presence, with abstention handling), `abstained` (off-corpus refusal).
- **`run_harness` + comparison table** — answer correctness by pattern × category, plus retrieval recall and off-corpus abstention.

## Implementation choices

1. **Shared corpus = Lab 33's entity-rich ecosystem** (`../33-graph-rag-from-scratch/corpus`), so Graph RAG's global/multi-hop strengths are visible. On Lab 06's concept corpus the patterns would look interchangeable.
2. **Common pipeline interface.** Every pipeline returns `{answer, retrieved_docs, retrieved}`, which is what makes uniform scoring possible. Forcing this shape is the key design move.
3. **Abstention is a first-class metric.** Off-corpus correctness = *did it refuse*. Without this, static RAG (which fabricates) would rank too high.
4. **Doc-level recall, not chunk-level.** The eval set labels relevant *docs*; recall is computed at doc granularity, which is comparable across flat and graph patterns (graph reaches docs via entity provenance).
5. **Graph built once.** `build_graph` + community summaries run at setup, not per query — the expensive index-time step amortized across the eval run.

## Expected shape of the result

Static wins specific-lookup/paraphrase but scores 0 on off-corpus (fabricates). CRAG matches static and abstains on off-corpus. Self-RAG wins parametric (skips retrieval). Graph wins global-theme and is competitive on multi-hop. **No pattern dominates** — the case for Lab 35.

## What's out of scope

- Re-deriving the patterns (Labs 06/31/32/33).
- Full LLM-judge faithfulness (token-presence stands in; wiring a judge is a marked extension).
- Statistical significance (16 queries show shape, not effect size).

## Running

```bash
uv add 'networkx>=3.0'
cd labs/34-rag-pattern-head-to-head/solution
jupyter notebook lab.ipynb
```

## Next

[Lab 35: Adaptive RAG router](../../35-adaptive-rag-router/) — route to the category winners this lab identifies.
