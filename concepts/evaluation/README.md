# 📖 Concepts · Evaluation

> 🟢 Stable explainers · concepts/evaluation/ covers RAG evaluation as a discipline. This is the *primer* on evaluation that the rest of Path 02 needs; the production-grade treatment (frameworks, observability, drift detection) lives in [Path 06](../../learning-paths/).

The pages here are a four-step progression from "what is RAG evaluation" to "what metrics to compute on what." They're prerequisites for [Lab 09](../../labs/09-evaluating-agentic-rag/) and the synthesis of Path 02's Labs 06-08.

## Current pages

### The primer

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [what-is-rag-evaluation.md](./what-is-rag-evaluation.md) | ~10 min | Orientation: retrieval vs generation, offline vs online, correctness vs groundedness, what evaluation can and can't tell you. |
| 📖 [eval-set-construction.md](./eval-set-construction.md) | ~10 min | The foundation: 30-50 hand-curated queries beat 1000 synthetic ones; expected_chunks/expected_doc, reference answers, category and failure-label tagging. |
| 📖 [retrieval-metrics.md](./retrieval-metrics.md) | ~11 min | Hits@k, recall@k, precision@k, MRR, nDCG@k, mean rank of expected chunk. What each reveals and what it hides. |
| 📖 [answer-quality-metrics.md](./answer-quality-metrics.md) | ~11 min | Faithfulness, groundedness, citation accuracy, answer relevance, refusal quality. Rule-based vs LLM-as-judge; Zheng et al. 2023's documented biases. |

These four pages are prerequisites for [Lab 09: Evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/).

## Path 06 — Production evaluation & observability (Modules 1-3 shipped)

The pages above (Path 02's RAG-evaluation primer) cover offline evaluation against hand-curated fixture sets. Path 06 extends that mechanism to production: live trace ingestion, drift detection, agent-as-judge calibration, distributed-tracing correlation across parallel sub-agents.

### Module 1 — From harness to production observability (batch 24)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [from-harness-to-production.md](./from-harness-to-production.md) | ~14 min | The framing. Why production is a categorically different problem from the from-scratch harness: live ingestion at scale, distribution drift on metric trends, distributed-tracing correlation across parallel sub-agents. The decision boundary for when to use each. What production tooling absorbs and what stays in the harness. |
| 📖 [observability-three-pillars.md](./observability-three-pillars.md) | ~12 min | Traces, metrics, logs mapped onto agent execution. Why agent traces look different from web-service traces (deeply nested, heavy LLM payloads, parallel sub-agent branches). The OpenTelemetry GenAI semantic conventions as the portable layer. OTel-native vs platform-native instrumentation trade-offs. |

### Module 2 — LangSmith trace ingestion (batch 25)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [langsmith-tracing-shape.md](./langsmith-tracing-shape.md) | ~12 min | The LangSmith data model: Runs, traces, projects. Three tracing methods ranked by automation: env-var auto-trace for LangChain/LangGraph, `@traceable` for custom Python functions, `tracing_v2_enabled` for project scoping. Messages-view vs timeline-view distinction. Adding tags + metadata for filtering. When LangSmith-native helps vs costs lock-in. |
| 📖 [online-vs-offline-evaluation.md](./online-vs-offline-evaluation.md) | ~10 min | The dataset-vs-live-stream distinction; why both matter; the closed loop via annotation queues. `agentevals` package overview (`trajectory.match`, `trajectory.llm`, `graph_trajectory`). How Lab 16's seven from-scratch metrics map onto agentevals — three direct, three custom-evaluator, one set-level. When the from-scratch harness still earns its keep. |

Lab applying these: [🧪 Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/).

Quiz: [🧠 LangSmith trace ingestion](../../quizzes/evaluation/langsmith-ingestion.md) — 8 questions covering Modules 1-2.

### Module 3 — OpenTelemetry portable layer (batch 26)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [opentelemetry-genai-conventions.md](./opentelemetry-genai-conventions.md) | ~14 min | The six layers of GenAI conventions (events, exceptions, metrics, model spans, agent spans, client spans). Core attributes that stabilized (`gen_ai.system`, `gen_ai.request.model`, token usage, tool/agent attributes). The v1.37 transition from per-message events to aggregated `gen_ai.input.messages`/`output.messages` attributes. `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` for new code. Span-kind discipline (CLIENT for LLM calls, INTERNAL for tools/agents). Auto-instrumentation libraries (`OpenAIInstrumentor`, OpenLLMetry covering 8+ frameworks). |
| 📖 [platform-fanout-and-portability.md](./platform-fanout-and-portability.md) | ~10 min | The fanout pattern: one TracerProvider, multiple SpanProcessors, multiple exporters. Three configurations (dev/staging/production). Platform landscape: 6 agent-native platforms + 4 APM tools that ingest OTel. The lock-in cost reframed (instrumentation locks you in, not the platform). Decision boundary for picking Lab 17 vs Lab 18 paths. A concrete migration story across team scale stages. |

Lab applying these: [🧪 Lab 18 — OpenTelemetry portable tracing](../../labs/18-opentelemetry-portable-tracing/).

Quiz: [🧠 OpenTelemetry portable tracing](../../quizzes/evaluation/opentelemetry-portable.md) — 8 questions covering Module 3 + Lab 17 vs Lab 18 trade-offs.

These six pages open [Path 06 — Evaluation & Observability](../../learning-paths/06-evaluation-observability/). The path is incremental; Modules 1-3 ship framing + LangSmith-native + OTel-portable; Modules 4-7 build on top of either path in future batches.

## Pending pages (future Path 06 modules)

The following are planned but not yet authored:

- `drift-detection.md` — KS-test, PSI, rolling-window comparisons for metric distributions (Module 5).
- `agent-as-judge-calibration.md` — periodic human-calibrated judge; Zheng et al. 2023 biases in production (Module 5).
- `cost-attribution.md` — per-user / per-task / per-tenant cost via tagging + propagation (Module 6).
- `multi-turn-evaluation.md` — trajectory metrics across conversation turns; LangChain Oct 2025 thread-level evals (Module 7).
- `evaluation-frameworks-deep-dive.md` — LangSmith vs Braintrust vs Langfuse vs Phoenix vs Laminar; concrete code; migration paths.

## Where this is used

- 🧪 [Lab 09: Evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/) — implements the metrics from this section from scratch over Labs 06-08's pipeline.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — Module 11 (this section + Lab 09) closes Path 02 v1.
