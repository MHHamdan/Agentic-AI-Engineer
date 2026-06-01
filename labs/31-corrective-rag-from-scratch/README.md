# Lab 31: Corrective RAG (CRAG) from scratch

> 🔴 Advanced · ⏱ ~90–120 min · 📚 Builds on Lab 06's corpus and retrieval stack

## 🎯 Goal

Take the static RAG agent from Lab 06 and make it *corrective*: add a retrieval evaluator that grades what came back, refine the retrieved context down to its load-bearing sentences, and take corrective action when retrieval is poor — rewrite-and-retry for ambiguous results, fall back to web search (or abstain) when the corpus does not contain the answer.

By the end you should be able to:

- Implement a retrieval evaluator that classifies retrieval as correct / ambiguous / incorrect.
- Refine retrieved context with a decompose-then-recompose step that preserves citation provenance.
- Wire corrective actions (query rewrite, fallback) into the loop and route by verdict.
- Show CRAG catching an off-corpus query that static RAG would answer by fabrication.
- Calibrate the evaluator threshold and measure its accuracy as its own number.

## 📋 Prerequisites

**Read first:**

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Pattern 2 (CRAG)
- 📖 [Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md)
- 🍳 [Recipe: Corrective RAG](../../recipes/rag/03-corrective-rag.md) — the compact version of this lab

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../06-agentic-rag-from-scratch/) — this lab reuses its corpus, chunker, and numpy index directly.
- 🧪 [Lab 09: Evaluating agentic RAG](../09-evaluating-agentic-rag/) — the calibration step uses the same eval mindset.

**Setup:** Python 3.11+ with the repo environment. No new dependencies beyond Lab 06 (`sentence-transformers`, `numpy`) plus your LLM provider key.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `sentence-transformers` | `>=5.0,<6.0` | Same embedding model as Lab 06 (`all-MiniLM-L6-v2`) |
| `numpy` | `>=1.26` | Index math |
| `openai` *or* `anthropic` | from prior labs | LLM for the grader, rewriter, and generator |

The retrieval evaluator, rewriter, and generator are all LLM calls. The web-search fallback is **stubbed** so the lab runs offline; swapping in a real search tool is a one-function change.

## What you'll build

A `corrective_rag(query)` loop with four new components on top of Lab 06's retriever: `grade_retrieval` (the evaluator), `decompose_recompose` (knowledge refinement), `rewrite_query` and `web_search_fallback` (corrective actions). The loop routes on the grader's verdict and records a trace of every decision.

## Steps

1. **Setup + reuse Lab 06's retrieval stack** (Steps 0–1). Point `CORPUS_DIR` at Lab 06's corpus; rebuild the index.
2. **The retrieval evaluator** (Step 2). One LLM call grades passages and returns a verdict.
3. **Knowledge refinement** (Step 3). Strip context to relevant sentences, keep chunk-id provenance.
4. **Corrective actions** (Step 4). Rewrite-and-retry; fallback.
5. **The CRAG loop** (Step 5). Route by verdict, generate, trace.
6. **See it correct a failure** (Step 6). Off-corpus query → fallback instead of fabrication.
7. **Calibrate the grader** (Step 7). Measure verdict accuracy on a small labeled set.

## What we don't do in this lab

- **We don't fine-tune the retrieval evaluator.** The paper's evaluator is a lightweight trained model; ours is an LLM call. The logic is identical; the cost profile differs.
- **We don't implement a real web search.** The fallback is a stub so the lab is offline-runnable and the routing decision is visible without a search dependency.
- **Refinement is sentence-level, not strip-level.** The paper decomposes into finer knowledge strips. Sentence granularity keeps the mechanics legible.

## Common gotchas

- **The grader is itself fallible.** A miscalibrated grader is the main failure mode — too strict wastes fallbacks, too lax defeats the purpose. Treat grader accuracy as a tracked metric (Step 7).
- **Provenance must survive refinement.** If you strip sentences without keeping chunk ids, you lose citations. The `decompose_recompose` function keeps `[chunk_id]` prefixes for exactly this reason.
- **Verdict distribution tells you if CRAG is worth it.** If the grader returns `correct` 95% of the time on your corpus, the corrective machinery rarely fires and you are paying for a step that does little.

## Solution discussion

- **Why route three ways instead of two.** A binary correct/incorrect split discards the common "partially relevant" case, where combining retrieved context with a fallback beats choosing one source.
- **Why the grader returns per-passage scores, not just a verdict.** The scores feed `decompose_recompose`'s keep-threshold, so one call does double duty: routing and refinement.

## 🧮 Going deeper

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — the error taxonomy CRAG's verdicts map onto.
- 🧮 [Retrieval and ranking metrics](../../math-foundations/14-retrieval-ranking-metrics.md) — measuring whether CRAG improved retrieval.

## ✅ Check your understanding

- 🧠 [SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md) — questions 2 and 8 cover CRAG directly.

## What comes next

- 🧪 [Lab 32: Self-RAG from scratch](../32-self-rag-from-scratch/) — the on-demand-retrieval cousin of CRAG.
- 🧪 [Lab 33: Graph RAG from scratch](../33-graph-rag-from-scratch/) — restructure the index instead of correcting retrieval.
