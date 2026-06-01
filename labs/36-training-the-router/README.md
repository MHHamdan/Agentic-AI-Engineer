# Lab 36: Training and hardening the router

> 🔴 Advanced · ⏱ ~100–130 min · 📚 Builds on Lab 35

## 🎯 Goal

Take Lab 35's prompt-based router and make it production-shaped. Replace the per-query LLM classification call with a **trained classifier** (query embeddings + logistic regression on a labeled set), add a **confidence gate** from `predict_proba`, and route low-confidence queries to an **agentic fallback** that tries the top-2 candidate strategies and verifies before answering.

By the end you should be able to:

- Train and cross-validate a query-type classifier on embeddings, and read the reliable accuracy on a small set.
- Compare a trained router to a prompt-based one on both accuracy and per-query cost/latency.
- Use classifier confidence to gate an expensive fallback so it only runs on the uncertain tail.
- Reason about the failure mode that matters most here — calibration, not raw accuracy.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 35: Adaptive RAG router](../35-adaptive-rag-router/) — this lab trains the classifier that Lab 35 prompted for, and reuses its dispatch targets.
- 🧪 [Lab 34: Head-to-head evaluation](../34-rag-pattern-head-to-head/) — supplies the held-out eval set used to compare routers.

**Assumed background:** logistic regression, train/test splitting, cross-validation, class imbalance, and calibration. This is a applied-ML lab; the RAG parts are scaffolding around a classification problem.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn>=1.4`, `sentence-transformers`, `numpy`. Your LLM provider key (for the prompt-router comparison and the fallback's verifier).

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | `LogisticRegression`, `StratifiedKFold` |
| `sentence-transformers` | `>=5.0,<6.0` | Query embeddings (features) |
| `numpy` | `>=1.26` | Arrays |
| `openai` *or* `anthropic` | from prior labs | Prompt-router baseline + fallback verifier |

## What you'll build

A labeled query set (`router_trainset.jsonl`, 81 queries × 5 routes) → embeddings → a `LogisticRegression` classifier with cross-validated accuracy; `route_with_confidence` (returns route + confidence + top-2); a trained-vs-prompt comparison on the eval set; and `adaptive_rag_v2` — a confidence gate that dispatches directly when confident and calls `agentic_fallback` (try top-2 strategies, self-check, prefer a clean abstention over a failed guess) when not.

## The data and a leakage warning

`router_trainset.jsonl` ships with the lab: 81 queries grounded in Lab 33's corpus, labeled with one of `parametric / global / multihop / off_corpus_risk / specific`. **It's small.** Several queries are near-paraphrases, so a single random split can leak a paraphrase across the train/test boundary and flatter the score. The lab reports stratified cross-validation for that reason — and a real deployment needs far more data, refreshed as the query distribution drifts.

## Steps

1. **Setup** (0).
2. **Labeled set + embeddings** (1): features for the classifier.
3. **Train** (2): stratified CV is the number to trust; in-sample is optimistic.
4. **Confidence** (3): `predict_proba` max as the gate input.
5. **Trained vs prompt** (4): accuracy and cost.
6. **Dispatch targets** (5): the strategies the router selects among.
7. **Confidence gate + fallback** (6): the new control flow.
8. **When the fallback helps** (7): the low-confidence tail.

## Design choices and tradeoffs

- **Why logistic regression.** Small labeled set, an interpretable linear boundary, and — the load-bearing reason — `predict_proba` gives the confidence the gate needs. A linear SVM or small MLP are alternatives; plain SVM lacks calibrated probabilities without extra work.
- **Trained vs prompt classifier.** The trained router pays a one-time labeling + training cost, then classifies for near-zero per-query cost and latency, and you can monitor its confidence distribution for drift. The prompt router needs no labels but bills an LLM call every query and is harder to watch. Neither is strictly better — it's a data-availability and ops decision.
- **Why gate the fallback on confidence.** The multi-strategy fallback costs several calls. Running it on every query would erase the trained router's cost advantage. The gate spends that budget only where the model is unsure.

## Common gotchas

- **Calibration, not accuracy, is the real risk.** A confidently wrong route skips the gate entirely. Monitor confidence *against correctness* (a reliability curve), not just top-line accuracy — an over-confident classifier defeats the fallback.
- **Tiny-data overfitting.** With 81 examples, a single split is noisy. Trust cross-validation, and resist tuning hyperparameters against the eval set (that leaks the eval set into model selection).
- **Embedding-model coupling.** The classifier's features come from a specific embedder. Swap the embedder and you must retrain. Pin it, and version the trainset with it.
- **Distribution shift.** The trainset queries are clean prototypes; real user queries are messier. Expect deployed accuracy below your CV number and plan to collect real queries for a second training round.

## 🧮 Going deeper

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — Adaptive RAG in context.
- 🧮 [Retrieval and ranking metrics](../../math-foundations/14-retrieval-ranking-metrics.md) — for the downstream answer evaluation.

## What comes next

- 🧪 [Lab 37: Evaluation gates for RAG](../37-rag-eval-gates/) — wrap this router in a CI gate so routing regressions fail the build, and swap Lab 34's token-presence scoring for an LLM judge.
