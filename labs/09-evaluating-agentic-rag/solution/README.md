# Lab 09 · Reference solution

The polished final implementation of [Lab 09: Evaluating agentic RAG](../README.md).

## What this is

A from-scratch eval harness producing the comparison table that motivates Path 02:

- **30 hand-curated queries** (`../eval_set.jsonl`) across 5 categories: lexical, paraphrase, referential, compound, off-corpus.
- **4 retrieval pipelines** as same-shape callables: `dense_baseline`, `hybrid_rrf`, `hybrid_rerank`, `contextual_rerank`.
- **4 retrieval metrics** as pure functions: `hits@k`, `recall@k`, `MRR`, `rank_of_expected_doc`.
- **Aggregate + per-category tables** showing where each intervention earns its place.
- **3 rule-based answer-quality metrics** (refusal detection, groundedness, refusal quality).
- **5 agent-loop runs** scored against the rule-based metrics.
- **LLM-as-judge faithfulness** on 3 sample queries, compared to the rule-based groundedness signal.

## How it differs from `../lab.ipynb`

| Lab notebook (40 cells) | Solution (33 cells) |
|---|---|
| Step 5 interprets the table at length with diagnostic walkthroughs | Interpretation as a brief comment under each table |
| Step 9 synthesis section discusses next moves (Path 06) | Out of scope here |
| Wires individual primitives separately for didactic effect | Composed end-to-end |
| Cells alternate between metric-by-metric and pipeline-by-pipeline | Pipelines defined once; metrics applied uniformly |

## Implementation choices

1. **Pipelines as callables with one signature.** Every pipeline takes `(query, top_k)` and returns `list[chunk_id]`. This is the single biggest design choice — it makes A/B comparison trivial. Adding a 5th pipeline (e.g., HyDE + contextual) is a 5-line function and one entry in the `PIPELINES` dict.
2. **Loose-match relevance, not strict chunk annotation.** A chunk is relevant if its `doc_id` matches `expected_doc`. The eval set's annotations are at the document level. This is robust to chunker changes (chunk IDs shift; doc IDs don't) at the cost of distinguishing "found the exact paragraph" from "found some other chunk of the same document." See [`concepts/evaluation/eval-set-construction.md`](../../../concepts/evaluation/eval-set-construction.md).
3. **Aggregate first, per-category second.** The aggregate table is the headline; the per-category table is where the interventions stop being a black box. Read across categories: each intervention helps a specific failure shape.
4. **Rule-based answer quality before LLM-as-judge.** Rule-based is cheap, deterministic, CI-friendly. LLM-as-judge is the second signal for cases rules can't reach. Lab 09 runs it on 3 queries to demonstrate the pattern, not as a primary metric.
5. **Contextual indexes are auto-skipped if Lab 08's cache isn't present.** The contextual pipeline depends on `../../08-contextual-retrieval-and-query-rewriting/context_cache.json` (Lab 08's cache file, two levels up and into its sibling lab). If you skipped Lab 08, the comparison runs across 3 pipelines instead of 4 — no crash, no fake numbers, explicit message.
6. **5-query sample for the agent loop**, not the full eval set. Running the full agent loop across 30 queries × 4 pipelines is ~30 minutes of LLM calls. The sample (one query per category) is enough to show the integration.

## What's deliberately out of scope

- **RAGAS / TruLens / DeepEval.** Mentioned only, not used. These are production-grade eval suites with built-in LLM-as-judge bias controls (Zheng et al. 2023). They're Path 06 territory — see [`concepts/evaluation/answer-quality-metrics.md`](../../../concepts/evaluation/answer-quality-metrics.md) for the bias discussion that motivates needing them in production.
- **Synthetic query expansion.** The lab uses 30 hand-curated queries — generally better than 300 synthetic ones for surfacing failure modes the synthetic generator doesn't model. Production teams converge on a hybrid (hand-curate seed; expand synthetically); out of scope here.
- **Drift detection / monitoring.** Lab 09 measures the pipelines at a point in time. Production tracks retrieval metrics over time and alerts on regressions.
- **A/B testing with deployed traffic.** That's a Path 06 topic.
- **Strict chunk-level annotations.** Lab 09's annotations are at the document level for robustness. Production systems with pinned chunkers often switch to strict annotation.

## Running the solution

```bash
cd labs/09-evaluating-agentic-rag/solution
jupyter notebook lab.ipynb
```

Expected wall-clock: ~30 seconds for the retrieval-metrics portion (pure-Python, no LLM); ~2 minutes for the 5 agent-loop runs; ~10 seconds for the LLM-judge on 3 queries.

Cost: roughly $0.02 at gpt-4o-mini rates for the full notebook run, assuming Lab 08's context cache already exists. Without Lab 08's cache, the contextual pipeline is skipped (no extra cost) and the comparison runs across 3 pipelines.

## Reading the headline table

A representative run produces something like:

```
pipeline               hits@10   recall@10   mrr     mean_rank
─────────────────────────────────────────────────────────────────
dense_baseline         0.833     0.342       0.531   2.85
hybrid_rrf             0.875     0.378       0.598   2.43
hybrid_rerank          0.917     0.401       0.682   1.95
contextual_rerank      0.958     0.435       0.731   1.71
```

The cumulative improvement from `dense_baseline` to `contextual_rerank` is what Path 02 buys you on this eval set. The per-category breakdown is where you see *which* intervention helped *which* failure shape — that's the diagnostic table to actually use when deciding which intervention to invest in for your corpus.

## Next

- Take the [RAG evaluation quiz](../../../quizzes/agentic-rag/rag-evaluation.md) if you haven't already.
- Path 02 v1 is now complete. Possible next moves: Path 03 (Multi-Agent Systems) or Path 06 (Evaluation & Observability — the production-grade version of this lab).
