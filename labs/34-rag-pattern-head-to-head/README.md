# Lab 34: Head-to-head RAG pattern evaluation

> 🔴 Advanced · ⏱ ~90–120 min · 📚 Uses Lab 33's entity-rich corpus + a shared eval set

## 🎯 Goal

Stop arguing about which RAG pattern is "best" and measure it. Run static RAG, CRAG, Self-RAG, and Graph RAG over **one shared corpus and one shared eval set**, score them with the [Batch 69 evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md), and produce a comparison table sliced by query category. The result is the empirical case for adaptive routing (Lab 35).

By the end you should be able to:

- Reduce four different RAG pipelines to a common interface so they are comparable.
- Apply the evaluation framework's retrieval and generation metrics across patterns.
- Score abstention correctness (does a pattern refuse unanswerable queries?) as a first-class metric.
- Read a pattern-by-category comparison table and draw the right conclusion: no single pattern dominates.

## 📋 Prerequisites

**Read first:**

- 📖 [The RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — the six layers and metrics this lab applies.
- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — the four patterns being compared.

**Complete first:**

- 🧪 [Lab 31 (CRAG)](../31-corrective-rag-from-scratch/), [Lab 32 (Self-RAG)](../32-self-rag-from-scratch/), [Lab 33 (Graph RAG)](../33-graph-rag-from-scratch/) — this lab condenses their pipelines into a common harness; you should know what each does before comparing them.
- 🧪 [Lab 09 (Evaluating agentic RAG)](../09-evaluating-agentic-rag/) — the from-scratch eval harness this builds on.

**Setup:** Python 3.11+ with the repo environment, `sentence-transformers`, `numpy`, and `networkx>=3.0` (for the Graph RAG pipeline). Your LLM provider key.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `sentence-transformers` | `>=5.0,<6.0` | Shared retriever |
| `numpy` | `>=1.26` | Index + scoring |
| `networkx` | `>=3.0` | Graph RAG pipeline |
| `openai` *or* `anthropic` | from prior labs | Generation + LLM-judged scoring |

## What you'll build

A harness with four condensed pipelines (`pipe_static`, `pipe_crag`, `pipe_self_rag`, `pipe_graph`), each returning `{answer, retrieved_docs, retrieved}`; a scoring layer (doc-level recall, answer correctness via expected tokens, abstention correctness); and `run_harness` + a comparison table that slices answer correctness by pattern × category.

## The shared corpus and eval set

Both ship with the lab. The corpus is [Lab 33's entity-rich ecosystem](../33-graph-rag-from-scratch/corpus/) (reused so Graph RAG's strengths are visible — a conceptual corpus like Lab 06's would hide them). The eval set ([`eval_set.jsonl`](./eval_set.jsonl)) has 16 queries across six categories chosen to exercise each pattern's strength:

| Category | What it tests | Expected winner |
|---|---|---|
| specific-lookup | single-fact retrieval | static / flat |
| paraphrase | reworded lookup | static / flat (dense) |
| multi-hop | chaining facts across docs | graph |
| global-theme | corpus-wide synthesis | graph |
| off-corpus | unanswerable; should abstain | CRAG |
| parametric | general knowledge; skip retrieval | Self-RAG |

## Steps

1. **Setup + shared index** (Steps 0–1).
2. **Three flat pipelines** (Step 2): static, CRAG, Self-RAG, common interface.
3. **Graph RAG pipeline** (Step 3): build the graph once, route global/local.
4. **Scoring** (Step 4): recall, answer correctness, abstention.
5. **Run the harness** (Step 5): every pattern × every query.
6. **Comparison table** (Step 6).
7. **Read the result** (Step 7): each pattern wins its category; none dominates.

## What we don't do in this lab

- **We don't re-derive the patterns.** The pipelines are condensed; the full from-scratch versions are Labs 06/31/32/33. This lab is about the *comparison*.
- **We don't use full LLM-judge faithfulness by default.** Answer correctness uses expected-token presence, which is cheap and deterministic. Wiring in an LLM judge from the evaluation framework is a marked extension.
- **We don't claim statistical significance.** 16 queries on a small corpus illustrate the *shape* of the tradeoff, not publishable effect sizes.

## Common gotchas

- **Abstention must be scored, not assumed.** Static RAG has no abstention mechanism, so it answers off-corpus queries by fabricating — and only an abstention-correctness metric catches that. A harness that only scores answerable queries would rank static too highly.
- **Retrieval metrics don't apply uniformly.** Doc-level recall is meaningful for the flat patterns; Graph RAG reaches documents by traversal, so its recall is reported with that caveat. The framework's retrieval/generation split is exactly this distinction.
- **Comparable interfaces matter.** If each pipeline returns a different shape, you can't score them uniformly. Forcing `{answer, retrieved_docs, retrieved}` is what makes the table possible.

## Solution discussion

- **Why slice by category.** An aggregate "accuracy" hides the whole story — it would average static's lookup wins against its off-corpus fabrication. The per-category table is what reveals that each pattern has a lane.
- **Why this motivates a router.** If no single pattern dominates but each wins a category, the optimal system classifies the query and dispatches to the category winner. That is Lab 35.

## 🧮 Going deeper

- 🧮 [Retrieval and ranking metrics](../../math-foundations/14-retrieval-ranking-metrics.md) — the recall the harness computes.
- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — the `eval_gate` you could wrap this in for CI.

## ✅ Check your understanding

- 🧠 [SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md) — the cost/benefit-by-failure-mode questions map directly onto this table.

## What comes next

- 🧪 [Lab 35: Adaptive RAG router](../35-adaptive-rag-router/) — turn this comparison into a router that picks the category winner per query.
