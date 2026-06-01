# Lab 35: Adaptive RAG router

> 🔴 Advanced · ⏱ ~80–110 min · 📚 Synthesis of Labs 31–34

## 🎯 Goal

Build the system the Lab 34 head-to-head points to: a query classifier that routes each query to the RAG strategy that wins its category. Parametric queries skip retrieval (Self-RAG), global and multi-hop queries go to Graph RAG, off-corpus-risk queries go to CRAG (which can abstain), and specific lookups use flat retrieval. This is Adaptive-RAG: match effort and strategy to query type.

By the end you should be able to:

- Implement a query classifier that routes to a strategy in one cheap call.
- Dispatch to the right pattern and measure both routing accuracy and answer accuracy.
- Explain why the router achieves per-category coverage no single fixed pattern does — and why the classifier is its single point of failure.
- Reason about the cost argument: one classify call + one pattern, versus running every pattern.

## 📋 Prerequisites

**Read first:**

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Pattern 3 (Adaptive RAG).

**Complete first:**

- 🧪 [Lab 34: Head-to-head RAG pattern evaluation](../34-rag-pattern-head-to-head/) — this lab routes to the category winners that Lab 34 identifies. Do 34 first or the routing table is unmotivated.
- 🧪 Labs [31](../31-corrective-rag-from-scratch/), [32](../32-self-rag-from-scratch/), [33](../33-graph-rag-from-scratch/) — the strategies being routed to.

**Setup:** Python 3.11+ with the repo environment, `sentence-transformers`, `numpy`. Your LLM provider key. (Reuses Lab 33's corpus and Lab 34's eval set by relative path.)

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `sentence-transformers` | `>=5.0,<6.0` | Shared retriever |
| `numpy` | `>=1.26` | Index |
| `openai` *or* `anthropic` | from prior labs | Classifier + dispatched strategies |

## What you'll build

`classify_query` (the router — one call to one of five routes), a `DISPATCH` map from route to strategy, `adaptive_rag` (classify once, dispatch once), and an evaluation that reports routing accuracy and answer accuracy on the shared eval set, plus the cost comparison against running all patterns.

## Steps

1. **Setup + shared index** (Steps 0–1): same corpus as Labs 33/34.
2. **The query classifier** (Step 2): map a query to one of five routes.
3. **Dispatch targets** (Step 3): compact representatives of each strategy.
4. **The adaptive router** (Step 4): classify then dispatch.
5. **See it route** (Step 5): one query per type.
6. **Evaluate** (Step 6): routing accuracy + answer accuracy on the shared eval set.
7. **Read the result** (Step 7): high accuracy across all categories; the classifier caps it.

## What we don't do in this lab

- **We don't train the classifier.** The paper trains a complexity classifier on a labeled dataset; ours is prompt-based. Faithful to the routing idea; not the trained implementation.
- **We don't re-derive the strategies.** The dispatch targets are condensed; full versions are Labs 06/31/32/33. In the repo you would import them.
- **The route taxonomy is corpus-specific.** Five routes tuned to this corpus's query types; a different domain needs a different taxonomy.

## Common gotchas

- **The router is a single point of failure.** Every misroute caps the achievable answer accuracy — a query sent to the wrong strategy cannot recover. Track routing accuracy as its own metric, separate from answer accuracy.
- **Routing accuracy and answer accuracy are different numbers.** A correct route can still produce a wrong answer (the strategy failed); an incorrect route can occasionally still answer correctly (a forgiving query). Report both.
- **Cheap-path bias.** A classifier that is uncertain should not default to the cheapest route — that sends hard queries to flat retrieval and they fail silently. Choose the conservative default deliberately.

## Solution discussion

- **Why route global and multi-hop both to Graph RAG.** Both need information that spans documents — global by synthesis, multi-hop by traversal — which is exactly the graph's strength. A finer router could split them; this taxonomy keeps them together.
- **Why off-corpus-risk routes to CRAG.** CRAG is the only strategy here with a built-in abstention path. Routing risky queries to it means the system refuses rather than fabricates, which is the correct behavior when the corpus cannot answer.

## 🧮 Going deeper

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — wrap the router in an `eval_gate` to catch routing regressions in CI.
- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Adaptive RAG in the context of the full landscape.

## ✅ Check your understanding

- 🧠 [SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md) — question 3 is exactly this routing problem.

## What comes next

This closes the SOTA-RAG arc: Labs 31–33 built the patterns, Lab 34 measured them head-to-head, and Lab 35 routes among them. Natural extensions: train the classifier on a labeled set instead of prompting; add a fallback-to-agentic path for queries the router is unsure about; or wrap the whole router in the evaluation framework's CI gate so routing regressions are caught automatically.
