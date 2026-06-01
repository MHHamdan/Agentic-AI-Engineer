# Lab 32: Self-RAG from scratch

> 🔴 Advanced · ⏱ ~90–120 min · 📚 Builds on Lab 06's corpus and retrieval stack

## 🎯 Goal

Add Self-RAG's reflection-driven control flow to the Lab 06 agent: decide *whether* to retrieve at all, grade each retrieved passage for relevance, generate a candidate answer per relevant passage, and select the best by how well it is *supported* and how *useful* it is. These are the ISREL / ISSUP / ISUSE reflection tokens, approximated with constrained classification calls.

By the end you should be able to:

- Implement the on-demand retrieval decision (skip retrieval for parametric queries).
- Implement the three reflection graders (relevance, support, usefulness) as constrained categorical calls.
- Generate one candidate per relevant passage and select by a support+usefulness score.
- Explain precisely what the prompt-based approximation loses versus the fine-tuned original.

## 📋 Prerequisites

**Read first:**

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Pattern 1 (Self-RAG)
- 📖 [What is RAG evaluation?](../../concepts/evaluation/what-is-rag-evaluation.md) — the support/groundedness idea underpins ISSUP

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../06-agentic-rag-from-scratch/) — reuses its corpus and index.
- 🧪 [Lab 31: Corrective RAG from scratch](../31-corrective-rag-from-scratch/) recommended — Self-RAG and CRAG are siblings (self-grading retrieval); doing CRAG first makes the contrast clear.

**Setup:** Python 3.11+ with the repo environment. No new dependencies beyond Lab 06.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `sentence-transformers` | `>=5.0,<6.0` | Lab 06's embedding model |
| `numpy` | `>=1.26` | Index math |
| `openai` *or* `anthropic` | from prior labs | LLM for the decision, the three graders, and generation |

## What you'll build

A `self_rag(query)` loop with: `decide_retrieve` (the Retrieve token), `grade_relevance` / `grade_support` / `grade_usefulness` (ISREL / ISSUP / ISUSE), `generate_from_passage` (one candidate per relevant passage), and a selection step that scores candidates by `support_weight + usefulness/5`.

## Steps

1. **Setup + reuse Lab 06's retrieval** (Steps 0–1).
2. **The Retrieve decision** (Step 2). Skip retrieval for parametric queries.
3. **The reflection tokens** (Step 3). Three constrained graders.
4. **Per-passage generation** (Step 4). One candidate per relevant passage.
5. **The Self-RAG loop** (Step 5). Decide → grade → generate → score → select.
6. **See the two signature behaviors** (Step 6). Skipping retrieval; grading and selecting.

## What we don't do in this lab

- **We don't fine-tune reflection tokens.** The paper trains a model to emit ISREL/ISSUP/ISUSE inline during decoding. We approximate each with a separate classification call. This is faithful to the *logic* but more expensive than the original, which folds reflection into one generation pass.
- **Candidate generation is one-per-passage.** The paper supports richer segment-level decoding with beam-style selection over reflection tokens.

## Common gotchas

- **Substring traps in token parsing.** `"relevant"` is a substring of `"irrelevant"`. The `chat_token` helper matches on **word boundaries** for exactly this reason — naive `in` matching would grade every passage relevant. (This is a real bug the lab's helper avoids; note it.)
- **Conservative defaults matter.** When the grader's output is unparseable, default to the safe verdict (e.g. `no_retrieve`, `no_support`) rather than the permissive one.
- **More calls, not fewer.** Self-RAG trades extra grading calls for fewer hallucinations and fewer needless retrievals. If your queries are uniformly retrieval-needing and single-passage, the overhead may not pay off — measure.

## Solution discussion

- **Why score `support_weight + usefulness/5`.** A fully-supported but useless answer and a useful but unsupported answer are both bad in different ways; combining the two reflection signals selects answers that are both grounded and on-target. The exact weighting is a knob to tune on your eval set.
- **Why fall back to parametric on zero relevant passages.** If every retrieved passage grades irrelevant, forcing an answer from them invites fabrication; answering from parametric knowledge (clearly) is the safer move.

## 🧮 Going deeper

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — ISSUP is faithfulness; ISUSE is answer relevance.
- 🧮 [Uncertainty and safety](../../math-foundations/12-uncertainty-safety.md) — the abstention idea behind skipping retrieval.

## ✅ Check your understanding

- 🧠 [SOTA RAG patterns quiz](../../quizzes/agentic-rag/sota-rag-patterns.md) — question 4 covers the reflection tokens.

## What comes next

- 🧪 [Lab 33: Graph RAG from scratch](../33-graph-rag-from-scratch/) — restructure the index for global and multi-hop questions.
