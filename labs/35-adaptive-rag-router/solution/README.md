# Lab 35 · Reference solution

The complete implementation of [Lab 35: Adaptive RAG router](../README.md).

## What this is

A query router over the patterns from Labs 31–34:

- **`classify_query`** — one `chat_token` call mapping a query to one of five routes (parametric, global, multihop, off_corpus_risk, specific).
- **Dispatch targets** — `strat_parametric` (skip retrieval), `strat_specific` (flat), `strat_corrective` (CRAG grade+abstain), `strat_graph` (cross-document synthesis). Condensed; full versions are Labs 06/31/32/33.
- **`adaptive_rag`** — classify once, dispatch once.
- **Evaluation** — routing accuracy (did the classifier pick the right route?) and answer accuracy, on Lab 34's shared eval set, plus the cost argument.

## Implementation choices

1. **One classification call is the only fixed overhead.** Then exactly one pattern runs — cheaper than the head-to-head's run-all-four.
2. **`CAT_TO_ROUTE` maps eval categories to expected routes**, so routing accuracy is measurable against the eval set's category labels.
3. **Global and multi-hop both route to the graph strategy.** Both need cross-document information; a finer router could split them.
4. **Off-corpus-risk routes to CRAG** — the only strategy with an abstention path, so risky queries refuse rather than fabricate.
5. **`chat_token` word-boundary matching** (same helper as Lab 32) avoids substring mis-classification among the route labels.

## Expected shape of the result

High answer accuracy across *all* categories — coverage no single fixed pattern achieved in Lab 34 — capped by routing accuracy. Every misroute is an unrecoverable miss, which is why the classifier is the single point of failure and routing accuracy is tracked separately.

## What's out of scope

- A trained complexity classifier (the paper's approach); ours is prompt-based.
- Full pattern pipelines (condensed here; import from Labs 06/31/32/33 in the repo).
- A domain-general route taxonomy (these five are tuned to this corpus).

## Running

```bash
cd labs/35-adaptive-rag-router/solution
jupyter notebook lab.ipynb
```

Reuses Lab 33's corpus and Lab 34's `eval_set.jsonl` by relative path, so those labs must be present.

## Next

Train the classifier on a labeled set; add an agentic fallback for low-confidence routes; wrap the router in the evaluation framework's CI gate.
