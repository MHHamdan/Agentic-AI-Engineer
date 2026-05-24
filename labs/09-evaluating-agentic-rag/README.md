# Lab 09: Evaluating agentic RAG

> 🟡 Intermediate · ⏱ ~100–130 min · 📚 Same corpus as Labs 06+07+08; from-scratch eval harness

## 🎯 Goal

Build a from-scratch evaluation harness for the retrieval pipeline you've assembled in Labs 06-08. The harness consumes a hand-curated 30-question eval set and produces comparison tables across every Path 02 intervention, so you can finally answer the question Labs 06-08 implicitly asked: **did the engineering actually help, on this corpus, on these queries?**

By the end you should be able to:

- Load and validate a JSONL eval set with `expected_doc`, `expected_chunks`, `category`, `failure_label` annotations.
- Implement retrieval metrics from scratch: hits@k, recall@k, MRR, mean rank of expected chunk.
- Run the same eval set through 4-5 retrieval pipelines (baseline dense, hybrid+RRF, hybrid+rerank, contextual+hybrid+rerank, with optional query rewriting) and produce per-pipeline metric tables.
- Slice metrics by `category` so the per-failure-mode picture is visible, not just the aggregate.
- Implement rule-based answer-quality metrics: groundedness, citation accuracy, refusal quality.
- Add an optional LLM-as-judge faithfulness check for a small subset of queries.
- Reason about what each metric reveals and which interventions actually move it.

## 📋 Prerequisites

**Read first:**

- 📖 [What is RAG evaluation?](../../concepts/evaluation/what-is-rag-evaluation.md)
- 📖 [Eval set construction](../../concepts/evaluation/eval-set-construction.md)
- 📖 [Retrieval metrics](../../concepts/evaluation/retrieval-metrics.md)
- 📖 [Answer quality metrics](../../concepts/evaluation/answer-quality-metrics.md)

**Complete first:**

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/)
- 🧪 [Lab 07: Retrieval strategies and reranking](../../labs/07-retrieval-strategies-and-reranking/)
- 🧪 [Lab 08: Contextual retrieval and query rewriting](../../labs/08-contextual-retrieval-and-query-rewriting/)

This lab evaluates the retrieval stack you built across Labs 06-08. Without all three, the comparison table is mostly empty.

**Setup:**

Python 3.11+ with the repo's environment. **No new dependencies on top of Lab 08.** The eval harness uses:

- `rank-bm25 >= 0.2.2` (from Lab 07)
- `sentence-transformers >= 5.0` (from Lab 06; provides both bi-encoder and cross-encoder)
- `openai` or `anthropic` (from Lab 01; optional for LLM-as-judge)
- `numpy` (already a dep)

If you only want the rule-based metrics, you don't need an LLM API key at all — most of the lab runs offline against the pre-indexed corpus.

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| All Lab 08 dependencies | — | 2026-05-24 |
| (no new pins introduced by this lab) | — | — |

The eval set is shipped as `eval_set.jsonl` in this directory. 30 hand-curated queries; verified to compile against the Lab 06 corpus with no impossible annotations (every on-corpus query's `expected_doc` is reachable by at least one retrieval strategy).

## What you'll build

A four-component evaluation system:

```text
┌────────────────────┐
│ eval_set.jsonl     │  ← 30 queries with expected_doc,
│                    │    category, failure_label
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ Pipeline registry  │  ← baseline, hybrid, reranked,
│                    │    contextual+rerank, with rewriting
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ Retrieval metrics  │  ← hits@k, recall@k, MRR,
│                    │    mean rank of expected chunk
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│ Answer-quality     │  ← groundedness, citation accuracy,
│ metrics (optional) │    refusal quality, LLM-as-judge
└──────────┬─────────┘
           │
           ▼
   Comparison tables
   sliced by category
```

The harness is ~200 lines of pure Python. No external evaluation framework. Same `search_corpus_v3` envelope contract as Labs 06-08 — the harness just calls each pipeline as a function.

## Steps

The notebook covers these in order:

**0. Setup.** Imports, paths, sanity-check the eval set loads.

**1. Load the eval set.** Open `eval_set.jsonl`, validate every entry's required fields. Show the category distribution (14 lexical / 6 paraphrase / 4 referential / 3 compound / 3 off-corpus).

**2. Recreate Labs 06-08 pipelines as callables.** Each pipeline takes `(query, top_k)` and returns a ranked list of chunks. Five pipelines: `dense_baseline`, `hybrid_rrf`, `hybrid_rrf_rerank`, `contextual_hybrid_rerank`, `contextual_hybrid_rerank_hyde`. Note: contextual indexes use the `context_cache.json` from Lab 08 if present, or regenerate.

**3. Implement retrieval metrics from scratch.** `hits_at_k`, `recall_at_k`, `mrr`, `mean_rank`. Pure functions, no dependencies. ~30 lines total.

**4. Run the harness — retrieval metrics.** For each pipeline, run all 30 queries, compute metrics, build a comparison table. Show both aggregate (overall hits@5, MRR, mean rank) and per-category slices.

**5. Interpret the table.** Walk through what each pipeline gained or lost vs. baseline, sliced by category. Honest framing: small corpus → small absolute gains, but the *shape* of which interventions help which queries is visible.

**6. Implement answer-quality metrics — rule-based.** `groundedness` (does the answer's content appear in the cited chunks?), `citation_accuracy` (for compound queries, do the citations cover the right docs?), `refusal_quality` (off-corpus queries: did the system refuse?). All pure functions, no LLM call.

**7. Run the agent loop on a sample of queries.** For ~5 queries spanning categories, run Lab 06's agent loop with Lab 08's `search_corpus_v3`. Collect the answer, citations, and which chunks were read. Score with the rule-based metrics from step 6.

**8. (Optional) LLM-as-judge faithfulness.** For 3 of the answers from step 7, run an LLM-as-judge faithfulness check. Compare to the rule-based groundedness. Show the agreement (and disagreement); discuss the biases from Zheng et al. 2023.

**9. The synthesis.** What did we learn? Which pipeline is "best" on this corpus, and is the "best" pipeline category-dependent? When would you reach for which intervention in production?

## What we don't do in this lab

Anti-scope, kept explicit:

- **No RAGAS, TruLens, DeepEval, Phoenix.** Mentioned in [answer-quality-metrics.md](../../concepts/evaluation/answer-quality-metrics.md) only as future/production tools. Path 06 covers them.
- **No synthetic eval generation.** The 30-question set is hand-curated; [eval-set-construction.md](../../concepts/evaluation/eval-set-construction.md) explains why this matters more than scale early on.
- **No production observability** (LangSmith, LangFuse, W&B). Different problem; Path 06.
- **No CI integration.** The harness is a notebook; turning it into a Pytest suite is a worthwhile exercise but out of scope for this lab.
- **No drift detection, no A/B testing on real traffic.** Path 06.
- **No correctness-against-ground-truth metric.** Only 5 of 30 queries have `reference_answer` and we use them sparingly. Most evaluation is groundedness, which doesn't need a reference. The next iteration of the lab could add a small correctness suite.
- **No reranker recall measurement.** The reranker can only reorder the candidate set the bi-encoder/BM25 produced. If a relevant chunk isn't in the top-30 candidates, reranking can't recover it. Lab 08 step 9 walks this; Lab 09 captures it via the metric tables.

## Common gotchas

- **Eval set drift when the chunker changes.** Today's `eval_set.jsonl` uses `expected_doc` (loose) annotations, not `expected_chunks` (strict). When you adjust `TARGET_TOKENS`, `OVERLAP_TOKENS`, or the chunker logic, doc-level metrics stay valid but chunk-level metrics would invalidate. Stick with `expected_doc` until you pin the chunker.
- **Re-running the harness is cheap; re-running with LLM-as-judge is not.** Step 8 makes ~3-5 LLM calls per evaluation run. Cache results if you're iterating.
- **One off-corpus query genuinely surfaces a real chunk.** `q23` ("Who is the CEO of Anthropic?") triggers a BM25 score of ~6.6 because the corpus mentions Anthropic. This is failure mode 8 in the wild — the corpus *mentions* the entity but doesn't *answer* the question. A score floor catches it; topic-matching doesn't. Real production corpora are full of this.
- **Compound queries don't have a single `expected_doc`.** The harness handles `expected_doc: null` by not scoring retrieval metrics for those — they go into the qualitative bucket. If you wanted a metric, you'd annotate `expected_chunks` as a union across the sub-questions.
- **The 30-question eval set is small enough to maintain by hand and big enough to surface category differences.** It's deliberately not bigger. The [eval-set-construction.md](../../concepts/evaluation/eval-set-construction.md) page makes the case.
- **Aggregate metrics will lie to you.** The harness prints per-category slices for exactly this reason. Always read the category table, not just the headline number.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 33 cells vs the lab's 40 — the per-category interpretation walkthrough is condensed; the harness runs 4 pipelines end-to-end with the comparison tables as the headline output. Two design choices worth flagging now:

- **`expected_doc` over `expected_chunks` for loose matching.** Robust to chunker changes; loses the "which chunk specifically" information. Production teams that have pinned their chunker should switch to `expected_chunks`. The lab notebook shows how the metrics would change.
- **Rule-based metrics first, LLM-as-judge only on a subset.** Cheap to iterate, deterministic, runs in CI. LLM-as-judge is reserved for substance-of-claim checks where rules can't reach.

## 🧮 Going deeper

- 📖 [Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md) — the qualitative version of what this lab quantifies. The decision tree there pairs naturally with the metric tables here.
- 📖 [Eval set construction](../../concepts/evaluation/eval-set-construction.md) — when you outgrow this lab's eval set and need to build your own.

## ✅ Check your understanding

- 🧠 [`quizzes/agentic-rag/rag-evaluation.md`](../../quizzes/agentic-rag/rag-evaluation.md) — 8 single-select questions covering the retrieval/generation split, eval set construction, recall vs. precision, LLM-as-judge biases, and the canonical mis-diagnosis (faithful answer to the wrong question).

If you score below 6/8, re-read the four concept pages and walk through step 9 of the notebook.

## What comes next

Lab 09 closes Path 02's first complete version. You can now:

1. **Build retrieval pipelines** (Labs 06-08).
2. **Diagnose failure modes** ([failure modes page](../../concepts/rag/retrieval-failure-modes.md)).
3. **Measure whether your interventions helped** (Lab 09).

That's the closed loop. Real production RAG work uses these three capabilities together iteratively.

What's next in this curriculum:

- **Solutions batch** ✅ — polished reference implementations for Labs 01-09 now live in each lab's `solution/` directory. Compare your work against them.
- **Path 03 — Multi-Agent Systems** — the next major track. Lab 06-08's patterns transfer; a multi-agent RAG is just two agents talking.
- **Path 06 — Evaluation & Observability** — the production-grade version of Lab 09 with RAGAS, TruLens, DeepEval, drift detection, A/B testing.
- **Path 02 expansion batches** — conversational RAG (multi-turn) and framework bridge (LangChain/LangGraph) are scoped but not authored.

The repo is at the point where any of these directions makes sense. Pick based on what your projects actually need next.
