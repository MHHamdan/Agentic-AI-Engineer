# The RAG evaluation framework

> 🟡 Slow-moving · ⏱ ~16 min read · 🏷 rag, evaluation, framework, metrics, ci

## TL;DR

This page is the map. The repo has deep individual pages on [eval set construction](./eval-set-construction.md), [retrieval metrics](./retrieval-metrics.md), [answer quality metrics](./answer-quality-metrics.md), [online vs offline evaluation](./online-vs-offline-evaluation.md), and more. This page ties them into one A-Z framework so you can see how the pieces fit and in what order to build them.

The framework has six layers, built bottom-up: (1) an eval set, (2) component metrics, (3) automated scoring, (4) an error taxonomy, (5) CI/CD gates, (6) production monitoring. Skipping a layer is the usual reason RAG eval efforts stall.

The single most important principle, repeated from [what-is-rag-evaluation.md](./what-is-rag-evaluation.md): **evaluate retrieval and generation separately before testing end-to-end.** Retrieval quality sets the ceiling on answer quality. If you only measure end-to-end, you cannot tell whether a bad answer came from finding the wrong evidence or from misusing the right evidence. Those are different bugs with different fixes.

---

## The six layers

See [`diagrams/rag-bundle.md#3-rag-evaluation-lifecycle`](../../diagrams/rag-bundle.md#3-rag-evaluation-lifecycle) for the lifecycle diagram and [`#4-retrieval-evaluation-vs-generation-evaluation`](../../diagrams/rag-bundle.md#4-retrieval-evaluation-vs-generation-evaluation) for the split.

| Layer | Question it answers | Repo page |
|---|---|---|
| 1. Eval set | What are we measuring against? | [eval-set-construction.md](./eval-set-construction.md) |
| 2. Component metrics | Retrieval and generation, scored separately | [retrieval-metrics.md](./retrieval-metrics.md), [answer-quality-metrics.md](./answer-quality-metrics.md) |
| 3. Automated scoring | How do we score at scale? | [evaluation-frameworks-deep-dive.md](./evaluation-frameworks-deep-dive.md), [agent-as-judge-calibration.md](./agent-as-judge-calibration.md) |
| 4. Error taxonomy | When it fails, what kind of failure? | [retrieval-failure-modes.md](../rag/retrieval-failure-modes.md) + below |
| 5. CI/CD gates | Does this change ship? | [online-vs-offline-evaluation.md](./online-vs-offline-evaluation.md) + below |
| 6. Production monitoring | Is it still good in the wild? | [drift-detection.md](./drift-detection.md), [observability-three-pillars.md](./observability-three-pillars.md) |

---

## Layer 1: the eval set

You cannot measure without ground truth. The eval set is a collection of queries paired with what a correct response looks like. For RAG you typically need three things per query:

- The **query** itself.
- The **relevant chunks or documents** (for retrieval metrics that need relevance labels).
- The **reference answer** or a **rubric** (for generation metrics).

Build the set to cover query categories you actually see: lexical (exact-term) queries, paraphrase queries, referential queries, multi-hop/compound queries, and off-corpus queries (questions your corpus cannot answer, where the correct behavior is to abstain). A set that is all easy lexical queries will pass everything and predict nothing.

Reference-free metrics (Ragas-style faithfulness, context relevance) reduce but do not eliminate the labeling burden: you still need the queries and, for trustworthy numbers, periodic human spot-checks. Full detail: [eval-set-construction.md](./eval-set-construction.md).

---

## Layer 2: component metrics

### Retrieval metrics

These need relevance labels (which chunks are relevant to which query). The math, with worked numerical examples, is in [`math-foundations/14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md).

| Metric | What it measures | Use when |
|---|---|---|
| **Precision@k** | Fraction of top-k that are relevant | You care about signal-to-noise in the context window |
| **Recall@k** | Fraction of all relevant docs found in top-k | You care about not missing evidence |
| **MRR** | Reciprocal rank of the first relevant doc | One right answer; position matters |
| **MAP** | Mean average precision across relevant docs | Multiple relevant docs; full-ranking quality |
| **NDCG@k** | Rank-weighted, graded relevance | Graded relevance; the de facto IR benchmark metric |
| **Context precision** | Of retrieved context, how much is actually relevant | RAG-specific; signal-to-noise for the generator |
| **Context recall** | Of needed information, how much was retrieved | RAG-specific; retrieval-gap detection |

NDCG@10 is the headline metric for retrieval benchmarks like BEIR because it handles graded relevance and is comparable across tasks. Context precision and context recall are the RAG-specific framings popularized by Ragas; they map onto the classical precision/recall ideas but are scored per-query over the retrieved context. Full detail: [retrieval-metrics.md](./retrieval-metrics.md).

### Generation metrics

These measure the answer given the retrieved context. Most are scored by an LLM judge (see Layer 3).

| Metric | What it measures | Catches |
|---|---|---|
| **Faithfulness / groundedness** | Are the answer's claims supported by the retrieved context? | Hallucination |
| **Answer relevance** | Does the answer address the query? | Off-topic or evasive answers |
| **Citation correctness** | Do the cited sources actually support the cited claims? | Fabricated or mismatched citations |
| **Context relevance** | Is the retrieved context relevant to the query? | Retrieval problems surfaced at generation time |
| **Answer correctness** | Does the answer match the reference (when one exists)? | Factual errors vs ground truth |

Faithfulness is the central RAG metric: it directly measures whether the generator is grounding its output in the evidence or making things up. The classical NLP metrics (BLEU, ROUGE) measure surface fluency and do not capture grounding; they are not sufficient for RAG. Full detail: [answer-quality-metrics.md](./answer-quality-metrics.md) and [`math-foundations/11-evaluation-metrics.md`](../../math-foundations/11-evaluation-metrics.md).

---

## Layer 3: automated scoring

Hand-labeling does not scale. Three scoring approaches, in increasing order of cost and nuance:

1. **Rule-based / lexical** (exact match, string presence, ROUGE). Cheap, deterministic, blind to meaning. Useful for retrieval hit/miss against labeled relevant chunks, useless for answer quality.
2. **Embedding similarity** (semantic similarity to a reference). Cheap, captures rough meaning, misses fine-grained correctness.
3. **LLM-as-judge.** An LLM scores the output against a rubric. Scales, captures nuance, and is the workhorse for faithfulness and relevance. Subject to biases (verbosity preference, position bias, self-preference) and calibration drift.

**Frameworks that implement these** (verify versions against current docs; these move quarterly):

| Framework | Focus | Note |
|---|---|---|
| Ragas | Reference-free RAG metrics (faithfulness, context precision/recall) | LLM-judge based; [docs.ragas.io](https://docs.ragas.io/) |
| DeepEval | Component + end-to-end RAG metrics, pytest-style | Open source; [github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval) |
| ARES | Trained LLM judges with confidence intervals | Uses fine-tuned judges; [arXiv:2311.09476](https://arxiv.org/abs/2311.09476) |
| TruLens | Groundedness, answer/context relevance, tracing | [trulens.org](https://www.trulens.org/) |
| Arize Phoenix | OpenTelemetry-native eval + observability | [phoenix.arize.com](https://phoenix.arize.com/) |

Because LLM judges have biases, use a judge ensemble (multiple judges with different rubrics or model families) for high-stakes scoring, and track inter-judge agreement as its own signal. Full detail: [evaluation-frameworks-deep-dive.md](./evaluation-frameworks-deep-dive.md) and [agent-as-judge-calibration.md](./agent-as-judge-calibration.md).

---

## Layer 4: the RAG error taxonomy

When the end-to-end answer is wrong, localize the failure before fixing it. See the decision tree at [`diagrams/rag-bundle.md#8-rag-failure-diagnosis`](../../diagrams/rag-bundle.md#8-rag-failure-diagnosis). The taxonomy:

| # | Failure | Where | Detected by | Fix |
|---|---|---|---|---|
| 1 | Evidence not in corpus | Ingest | Context recall = 0, no relevant chunk exists | Add sources |
| 2 | Evidence in corpus, not retrieved | Chunking / embedding | Context recall low, relevant chunk exists but absent from top-k | Re-chunk, better embedding model, hybrid search |
| 3 | Retrieved but ranked low | Ranking | Relevant chunk in top-k but below cutoff | Add reranking |
| 4 | Retrieved, ignored by model | Generation (attention) | Faithfulness low despite good context; lost-in-the-middle | Reduce k, reorder context, prompt |
| 5 | Used but unfaithful | Generation | Faithfulness low; claims not in context | Prompt, verification step, lower temperature |
| 6 | Faithful but off-topic | Generation | Answer relevance low | Prompt, query understanding |
| 7 | Right answer, wrong/no citation | Generation | Citation correctness low | Citation-forcing prompt, post-hoc verification |
| 8 | Correct refusal failure | Generation | Off-corpus query answered instead of abstaining | Abstention prompt, confidence threshold |

This taxonomy maps one-to-one onto the [retrieval-failure-modes.md](../rag/retrieval-failure-modes.md) page and extends it to the generation side. The point of a taxonomy is that each failure class has a *different* fix; without localizing, teams apply random fixes and measure noise.

---

## Layer 5: CI/CD evaluation gates

Treat the eval set like a test suite. On every change to prompts, chunking, embedding model, retrieval strategy, or generation model:

1. Run the **baseline set** (the golden dataset). Failures here block the merge.
2. Run the **regression set** (failures promoted from production). New failures here block the merge.
3. Compare aggregate metrics against the previous release. A drop beyond a threshold on any slice blocks the merge or triggers review.

The gate is per-slice, not just aggregate: a change that improves the median while tanking multi-hop queries should be caught. Version the rubric alongside the code, or scores across time are not comparable. Full detail: [online-vs-offline-evaluation.md](./online-vs-offline-evaluation.md).

A minimal gate in pseudocode:

```python
def eval_gate(system, baseline_set, regression_set, prev_metrics, thresholds):
    """Return (pass: bool, report: dict). Block merge if pass is False."""
    results = run_eval(system, baseline_set + regression_set)
    report = {}
    passed = True

    # Per-slice regression check.
    for slice_name, slice_metrics in results.by_slice().items():
        prev = prev_metrics.get(slice_name, {})
        for metric, value in slice_metrics.items():
            drop = prev.get(metric, 0) - value
            report[f"{slice_name}.{metric}"] = {"value": value, "drop": drop}
            if drop > thresholds.get(metric, 0.05):
                passed = False  # regression beyond tolerance

    # Hard floors on regression set (no promoted failure may regress).
    for case in regression_set:
        if not results.passes(case):
            passed = False
            report.setdefault("regression_failures", []).append(case.id)

    return passed, report
```

---

## Layer 6: production monitoring

Offline eval answers "did this change break what we know about?" Online eval answers "is the system staying good in the wild?" You need both.

In production, every RAG request emits spans (query rewrite, retrieve, rerank, generate). Traces feed:

- **Online evaluators** - sampled requests scored asynchronously for faithfulness, context relevance, and answer relevance. See [online-evaluator-registration.md](./online-evaluator-registration.md).
- **Drift detectors** - score drift (judge scores trending down), embedding drift (query/result distribution shifting), context drift (multi-turn degradation). See [drift-detection.md](./drift-detection.md) and [embedding-space-drift-detection.md](./embedding-space-drift-detection.md).
- **Dashboards** - latency, cost, token usage per stage. See [observability-three-pillars.md](./observability-three-pillars.md).

Failures caught in production get promoted into the regression set, closing the loop back to Layer 5. The observability diagram is at [`diagrams/rag-bundle.md#7-production-rag-observability`](../../diagrams/rag-bundle.md#7-production-rag-observability).

---

## Benchmarks and datasets

For evaluating *retrieval models* (as opposed to your specific RAG system), standard public benchmarks let you compare embedding and retrieval approaches:

| Benchmark | Covers | Headline metric | Reference |
|---|---|---|---|
| **BEIR** | Zero-shot retrieval across 18 datasets / 9 task types | NDCG@10 | [Thakur et al. 2021](https://arxiv.org/abs/2104.08663) |
| **MTEB** | 56+ embedding tasks (retrieval, clustering, classification); superset of BEIR | Task-specific | [Muennighoff et al. 2023](https://arxiv.org/abs/2210.07316) |

A finding worth internalizing from BEIR: BM25 is a strong baseline, and reranking plus late-interaction models (ColBERT) tend to top zero-shot retrieval, at higher compute cost. Use these benchmarks to choose a retrieval approach; use your own eval set (Layers 1-2) to measure your specific system. The two are not substitutes.

For building your own eval set rather than using public benchmarks, the construction guidance is in [eval-set-construction.md](./eval-set-construction.md).

---

## A build order that works

If you are starting from zero, build the layers in this order. Each layer is usable before the next exists.

1. **Week 1: 30-query eval set** covering your real query categories, with relevant chunks labeled. Even hand-labeling 30 queries beats no measurement.
2. **Week 1-2: retrieval metrics** (recall@k, MRR) computed against the labels. This alone catches most retrieval bugs.
3. **Week 2: faithfulness via LLM-judge** on the generation side. Catches hallucination.
4. **Week 3: the error taxonomy** wired into your debugging, so failures get localized.
5. **Week 3-4: a CI gate** running the set on every change.
6. **Ongoing: production monitoring** with sampled online eval and the promote-to-regression loop.

Teams that try to start at Layer 5 or 6 without Layers 1-2 end up with dashboards full of numbers they cannot act on.

---

## Repo cross-references

- [what-is-rag-evaluation.md](./what-is-rag-evaluation.md) - the orientation page; read first.
- [retrieval-metrics.md](./retrieval-metrics.md), [answer-quality-metrics.md](./answer-quality-metrics.md) - Layer 2 in depth.
- [evaluation-frameworks-deep-dive.md](./evaluation-frameworks-deep-dive.md) - Layer 3 in depth.
- [`concepts/rag/retrieval-failure-modes.md`](../rag/retrieval-failure-modes.md) - Layer 4 (retrieval side).
- [`concepts/rag/sota-rag-patterns.md`](../rag/sota-rag-patterns.md) - what to do when eval reveals a pattern-level gap.
- [`math-foundations/14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md) - the metric math with worked examples.
- [Lab 09](../../labs/09-evaluating-agentic-rag/) - a from-scratch harness implementing Layers 1-3.

## References

- Es, S., et al. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). Reference-free faithfulness and context metrics.
- Saad-Falcon, J., et al. (2023). [*ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*](https://arxiv.org/abs/2311.09476). Trained-judge evaluation with statistical confidence.
- Thakur, N., et al. (2021). [*BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*](https://arxiv.org/abs/2104.08663). NeurIPS Datasets and Benchmarks.
- Muennighoff, N., et al. (2023). [*MTEB: Massive Text Embedding Benchmark*](https://arxiv.org/abs/2210.07316). The embedding-model leaderboard superset of BEIR.
- Zheng, L., et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS. Establishes LLM-as-judge methodology and its biases.
- Manning, C., Raghavan, P., and Schutze, H. (2008). [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/). Cambridge University Press. The classical source for precision, recall, MAP, NDCG.
- Brown, A., Roman, M., and Devereux, B. (2025). [*A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges*](https://arxiv.org/abs/2508.06401). Survey covering RAG metrics through May 2025.

> 🟡 Slow-moving. The framework is stable; specific eval-framework versions and benchmark leaderboards change. Verify tooling details against current docs.
