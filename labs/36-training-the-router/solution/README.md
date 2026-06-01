# Lab 36 · Reference solution

The complete implementation of [Lab 36: Training and hardening the router](../README.md).

## What this is

A trained replacement for Lab 35's prompt-based router, plus a confidence-gated agentic fallback:

- **Trained classifier** — `router_trainset.jsonl` (81 queries × 5 routes) → `sentence-transformers` embeddings → `LogisticRegression(class_weight="balanced")`. Reported with 5-fold stratified cross-validation (the reliable number on small data).
- **`route_with_confidence`** — embed → `predict_proba` → `{route, confidence, top2}`.
- **Trained-vs-prompt comparison** — accuracy and wall-clock/cost on Lab 34's eval set.
- **`agentic_fallback` + `adaptive_rag_v2`** — confidence gate dispatches directly when confident; otherwise tries the top-2 candidate strategies, keeps the first that passes a self-check and isn't an abstention, and prefers a clean abstention over a failed guess.

## Implementation choices

1. **Logistic regression for the calibrated `predict_proba`.** The confidence gate needs probabilities; LR gives them directly and stays interpretable on a small set. `class_weight="balanced"` guards the minority routes.
2. **Cross-validation, not a single split.** 81 examples with near-paraphrases — a single split is noisy and can leak paraphrases across the boundary. CV is the reported metric; the in-sample report is shown only to make the optimism visible.
3. **Top-2 from the classifier as the fallback's candidate set.** When the router is unsure, its top-2 routes are the plausible options — exactly what to try and verify.
4. **Prefer abstention over a guess.** If neither candidate passes the self-check, a clean "INSUFFICIENT EVIDENCE" beats a confident-sounding wrong answer.
5. **Gate keeps cost bounded.** The multi-call fallback runs only below the confidence threshold, so steady-state cost stays near the single-dispatch router.

## Expected shape of the result

CV accuracy with real embeddings exceeds the TF-IDF stand-in used in repo verification; the trained router matches or beats the prompt router on the eval set at near-zero per-query cost. The fallback fires on the low-confidence tail (the borderline specific-vs-multihop paraphrases), giving those queries a verified second look.

## What's out of scope

- A large, refreshed, real-query training set (81 prototypes is a teaching size).
- The strongest possible classifier (LR is a deliberate, interpretable baseline).
- A full agentic loop in the fallback (the verifier is one cheap LLM check).

## The open risk: calibration

Accuracy is not the metric to watch — **calibration** is. A confidently wrong route skips the gate. Monitor a reliability curve (confidence vs empirical correctness), not just top-line accuracy.

## Running

```bash
pip install "scikit-learn>=1.4"
cd labs/36-training-the-router/solution
jupyter notebook lab.ipynb
```

Reads `../router_trainset.jsonl`, Lab 33's corpus, and Lab 34's eval set by relative path.

## Next

[Lab 37: Evaluation gates for RAG](../../37-rag-eval-gates/) — gate this router in CI and add an LLM judge.
