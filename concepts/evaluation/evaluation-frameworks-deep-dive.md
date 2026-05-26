# Evaluation frameworks deep dive — LangSmith, Braintrust, Langfuse, Phoenix, Laminar, MLflow, DeepEval, RAGAS, TruLens

> 🔴 Advanced · ⏱ ~25 min · 🛠 Verified 2026-05-26 · 📍 Read after Path 06 v1 modules + Batch 33 recipes

## What this page is for

A practical selection guide for production evaluation and observability tools. It is **not a vendor ranking** and it does not pick a "best" tool. The point is to help a team pick the tool that fits their constraints — stack commitments, deployment model, eval discipline, team size, OSS licensing requirements — without reading nine vendor blog posts.

Each tool covered below is in active production use somewhere in mid-2026. They differ in what they are optimized for, not in whether they work. The pages in Path 06 v1 already cover the **mechanisms** (tracing, online evaluation, drift, calibration, cost attribution, multi-turn evaluation). This page covers **which tools implement which mechanisms well** — and where they leave gaps your team will need to fill.

Three audiences for this page:

1. **Teams picking a stack from scratch** — section 4 (Decision guide) is the entry point.
2. **Teams already on a tool, considering a migration** — section 6 (Recipes/projects mapping) and the per-tool "Limiting factor" cells in section 2 are the entry points.
3. **Teams running hybrid stacks** — section 5 (Path 06 module mapping) plus the integration tables in [Project 3](../../learning-paths/06-evaluation-observability/projects/03-hybrid-production-stack.md) are the entry points.

What the page does **not** do is in section 7 (Anti-scope).

## Comparison table

Nine tools, eleven dimensions. Sources for each row are in the references section at the bottom; each claim is dated and cited.

| Tool | Best fit | Strongest feature | Limiting factor | Trace support | Dataset support | Online eval | Human review | OpenTelemetry | Self-host / deployment | Best Path 06 module connection |
|---|---|---|---|---|---|---|---|---|---|---|
| **LangSmith** | LangChain/LangGraph teams; fastest zero-to-production eval UX | LangGraph Studio + first-class threads + replay-against-new-models | Closed source; per-seat + per-trace pricing scales unpredictably; self-host is Enterprise-only | Native LangChain integration; full OTLP endpoint (March 2026) | First-class versioned Datasets + Dataset diffs | Automation Rules with sample-rate triggers | First-class annotation queues with reviewer assignment | Full OTLP receive AND emit since March 2026 | Cloud only (Plus, Enterprise); self-host is Enterprise hybrid contract | Module 2 (LangSmith trace ingestion) |
| **Braintrust** | Eval-first teams using CI/CD gates to block regressions | Native CI/CD enforcement; deployment-blocking on quality regression; statistical-significance analysis | Closed source; trace UX bolted on rather than agent-first; eval-first means debugger second | Trace ingestion present but secondary to evals | First-class Datasets; experiment-versioning baked in | Production evaluators run as Python scorers | Annotation present; not the primary UX | Partial — not the central instrumentation surface | Cloud; self-host via Enterprise hybrid contract | Module 4 (online evaluation registration) |
| **Langfuse** | Self-host-mandatory teams; prompt-centric workflows; OSS evaluation + observability with full data ownership | MIT license; v3 OTel-native rebuild; mature prompt management; 12M+ monthly PyPI downloads | Eval depth shallow vs DeepEval/RAGAS; trace UX not agent-first; acquired by ClickHouse Jan 2026 (long-term roadmap influenced by infrastructure parent) | OTLP endpoint at `/api/public/otel`; OpenLLMetry + OpenInference compatible | First-class datasets + prompt versioning | LLM-as-judge evaluators; scoring API | Annotation present; less polished than LangSmith | Native OTel from v3 onwards | Self-host (Docker, K8s) — full MIT OSS; cloud also available | Module 3 (OpenTelemetry portable layer) |
| **Arize Phoenix** | OpenInference/OTel-native teams; eval-heavy notebook workflows; teams already on Arize for classical ML | OpenInference owner — most widely adopted OTel semantic conventions for LLMs; 50+ research-backed metrics; multi-step trajectory analysis | Elastic License 2.0 (restricts managed-service offering); span-tree-first UX not agent-first; online evaluators + Alyx Copilot paid-only | Native OTel via OpenInference (40+ integrations) | First-class datasets; experiment tracking | Available; gated behind paid Arize AX plans | Annotation present; full version requires Arize AX | Native — Phoenix owns the OpenInference semantic conventions | Self-host single-node (free OSS); Arize AX commercial; 2 Phoenix Cloud instances free | Module 3 (OpenTelemetry portable layer) |
| **Laminar** | Long-running agent debugging in production; OTel-native teams wanting an agent-first trace UX | Apache 2.0; transcript view (not span tree); Signals for natural-language outcome tracking; SQL over traces; agent rollout debugger | Less prompt-management focus than Langfuse; smaller ecosystem; newer product | Native OTel ingestion (OTLP); OpenLLMetry/OpenInference compatible | Datasets present; less central than evals | Live evaluators present | Annotation present; transcript-first review UX | Native — OTel from day one | Apache 2.0; one-command Helm chart self-host; every feature on OSS image | Module 1 (instrumentation) + Module 7 (multi-turn) |
| **MLflow GenAI evaluation** | Teams already on MLflow for classical ML; widest pluggable scorer ecosystem | `mlflow.genai.evaluate()` natively integrates RAGAS + DeepEval + Phoenix + TruLens + Guardrails AI as scorers; automatic issue detection via LLM + clustering | GenAI extensions still catching up to LLM-native platforms; trace UX inherited from ML workflows | OTel support via the same instrumentation as standalone MLflow | First-class via MLflow's existing experiment + dataset abstractions | Via pluggable scorers + `@scorer` decorator | Annotation via the MLflow UI | Available via the underlying tracing layer | Apache 2.0 OSS self-host; Databricks managed | Module 4 (online evaluation registration) |
| **DeepEval / Confident AI** | Pytest-integrated CI workflows; multi-component AI stacks (agents, multi-turn, MCP, multimodal) | 50+ research-backed metrics including G-Eval custom LLM-as-judge; native pytest integration; multi-turn simulation | DeepEval OSS depth ≠ Confident AI managed depth (the platform is where the auto-curation, alerting, no-code workflows live) | DeepEval is a metric library, not a tracing tool; Confident AI adds tracing | Confident AI auto-curates production traces into eval datasets | DeepEval is offline-first; Confident AI adds production monitoring | Confident AI has cross-functional review workflows (PMs, QA, domain experts) | DeepEval ≠ instrumentation; Confident AI uses its own tracing | DeepEval: Apache 2.0; Confident AI: commercial cloud | Module 4 (online evaluation registration) + Module 5 (calibration) |
| **RAGAS** | Pure RAG evaluation; research-backed metrics; library-only (no platform) | Deepest RAG-specific metric library: faithfulness, answer relevancy, context precision/recall/utilization, noise sensitivity, agent goal accuracy, tool call accuracy; EACL 2024 paper origin | Pure metric library — no tracing, no datasets UI, no annotation queue, no production monitoring | None (library only) | None | None | None | None | Apache 2.0 library; pip install | Module 4 (online evaluation registration) — as a scorer inside another platform |
| **TruLens** | Teams wanting evaluation and tracing in one workflow; agentic systems with hard-to-isolate multi-hop failures | Inline trace + evaluation coupling — every LLM and retrieval call is traced and evaluated together; production-friendly | Smaller ecosystem; less platform-tooling around the library; originally TruEra (now part of Snowflake) | Native trace UI; OTel via instrumentation packages | Present | Inline evaluators on every traced call | Limited UI; programmatic | Via instrumentation packages | Apache 2.0 OSS; cloud via Snowflake | Module 1 (instrumentation) + Module 4 (online evaluation) |

Everything in this table is verified mid-2026 per the references at the bottom of the page. Tool capabilities shift quarterly; check the cited sources for current state before committing.

## Code-level comparison

Five canonical operations every team needs to do. Snippets show the **smallest viable API surface** per tool — not production-ready code, just enough to recognize the shape. The full reference docs are linked at the bottom of the page.

### A — Logging a trace/span

The instrumentation surface is the single most divergent thing across these tools. Three families:

**LangChain-rooted (LangSmith)** — env-var-driven auto-tracing on LangChain primitives, explicit `@traceable` decorator for non-LangChain helpers:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "agent-prod"

from langsmith import traceable

@traceable
def my_retriever(query: str) -> list[dict]:
    ...
```

**OTel-native (Langfuse, Phoenix, Laminar)** — decorator API on top of the OTel SDK. Same pattern across all three (the OTel SDK is the shared substrate); the destination is what varies:

```python
# Langfuse — @observe decorator, OTel under the hood
from langfuse import observe

@observe
def my_retriever(query: str) -> list[dict]:
    ...

# Phoenix — OpenInference instrumentation
from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument()
# Spans flow to whichever OTel backend Phoenix is configured to send to.

# Laminar — Laminar SDK over OTel
from lmnr import Laminar
Laminar.initialize(project_api_key="lm-...")
# All OTel-instrumented LLM calls flow to Laminar automatically.
```

**Pure-library (RAGAS, DeepEval, TruLens)** — no tracing API at the library level; they're called from inside an instrumented application, or TruLens couples trace + eval via its own wrapper.

```python
# TruLens — coupled trace + eval
from trulens.apps.basic import TruBasicApp
from trulens.feedback import Feedback

f_relevance = Feedback(provider.relevance).on_input_output()
tru_app = TruBasicApp(my_agent, app_id="my-agent", feedbacks=[f_relevance])

with tru_app:
    tru_app.app("user query")
# Tracing and evaluation happen in the same step.
```

**Pluggable platform (MLflow)** — uses the same OTel instrumentation as the standalone OTel path, plus MLflow-specific autologging.

```python
import mlflow

mlflow.autolog()  # also autologs the LLM provider's SDK calls
# Or via tracing decorator:

@mlflow.trace
def my_agent(query: str) -> str:
    ...
```

### B — Creating an evaluator (offline)

Two patterns dominate: **decorator/registered scorers** (LangSmith, Braintrust, MLflow, DeepEval, Phoenix) and **metric-instance objects** (RAGAS, TruLens).

```python
# LangSmith — Python function evaluator
from langsmith.evaluation import EvaluationResult

def faithfulness_evaluator(run, example):
    score = compute_faithfulness(run.outputs, example.outputs)
    return EvaluationResult(key="faithfulness", score=score)

# Braintrust — scorer pattern
from braintrust import Eval

Eval("my-project",
    data=lambda: dataset,
    task=lambda input: my_agent(input),
    scores=[Faithfulness],
)

# DeepEval — pytest-native + LLMTestCase
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

def test_faithfulness():
    test_case = LLMTestCase(input=q, actual_output=ans, retrieval_context=ctx)
    assert_test(test_case, [FaithfulnessMetric(threshold=0.7)])

# RAGAS — metric-instance over a dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

ds = Dataset.from_dict({"question": [...], "answer": [...], "contexts": [...]})
results = evaluate(ds, metrics=[faithfulness, answer_relevancy])

# MLflow — @scorer decorator + native integration with the libraries above
from mlflow.genai import scorer

@scorer
def my_faithfulness(predictions, targets):
    return compute_faithfulness(predictions, targets)

mlflow.genai.evaluate(
    data=df,
    scorers=[my_faithfulness, ragas_scorer("faithfulness")],
)

# Phoenix — Evaluator from the OpenInference evals package
from phoenix.evals import OpenAIModel, run_evals, HALLUCINATION_PROMPT_TEMPLATE
results = run_evals(
    dataframe=df,
    evaluators=[HALLUCINATION_PROMPT_TEMPLATE],
    provide_explanation=True,
)
```

The pattern that matters most across these tools is that **evaluator-as-Python-function** is universal — every platform either wraps your function as a scorer (LangSmith, Braintrust, MLflow, Phoenix) or you pass a callable with a well-known signature (DeepEval, RAGAS).

### C — Attaching scores to a trace

The two camps here are **score-on-trace** (LangSmith, Langfuse, Phoenix, Laminar — scores live as feedback events tied to a trace ID) and **score-as-result** (DeepEval, RAGAS, MLflow — scores are returned from a function, then optionally attached to a trace).

```python
# LangSmith — attach feedback to a run by ID
from langsmith import Client
ls = Client()
ls.create_feedback(run_id, key="faithfulness", score=0.85, comment="...")

# Langfuse — attach score to a trace
from langfuse import Langfuse
lf = Langfuse()
lf.score(trace_id=trace_id, name="faithfulness", value=0.85)

# Phoenix — log evaluations against trace IDs
from phoenix.trace import SpanEvaluations
import pandas as pd

evals_df = pd.DataFrame({"span_id": [...], "label": [...], "score": [...]})
px.Client().log_evaluations(SpanEvaluations(eval_name="faithfulness", dataframe=evals_df))

# Laminar — score is attached via the SDK
from lmnr import Laminar
Laminar.score(trace_id=trace_id, name="faithfulness", value=0.85)
```

For the score-as-result tools (RAGAS, DeepEval, MLflow), attaching scores to a specific trace requires bridging code — the score object is in your hand, and you call the trace-platform's feedback API to attach it. The "score replication worker" in [Project 3](../../learning-paths/06-evaluation-observability/projects/03-hybrid-production-stack.md) M5 does exactly this when bridging LangSmith judge scores into APM metrics.

### D — Running a dataset evaluation

This is where the platforms differ most. **Hosted dataset platforms** (LangSmith, Braintrust, Langfuse, Phoenix, Confident AI) version datasets server-side; you push a dataset, kick off a run, results live in their UI. **Library-style** (DeepEval, RAGAS, MLflow, TruLens) treat the dataset as a local DataFrame.

```python
# LangSmith — dataset is server-side, run is async
from langsmith import Client
from langsmith.evaluation import evaluate

results = evaluate(
    lambda input: my_agent(input),
    data="my-dataset-v3",  # versioned name resolves to a specific dataset
    evaluators=[faithfulness_evaluator],
    experiment_prefix="post-prompt-change",
)

# Braintrust — Eval kicks off an experiment + CI gate
from braintrust import Eval, init_dataset

Eval("my-project",
    data=init_dataset("my-project", "regression-v3"),
    task=my_agent,
    scores=[Faithfulness, AnswerRelevance],
)
# Returns a comparison vs the previous experiment; non-zero exit code if regressed.

# Langfuse — datasets are first-class; run via SDK
from langfuse import Langfuse
lf = Langfuse()
dataset = lf.get_dataset("regression-v3")
for item in dataset.items:
    result = my_agent(item.input)
    item.link(trace_id=trace.id, observation_id=obs.id)

# DeepEval — local dataset, runs via pytest or evaluate()
from deepeval import evaluate
from deepeval.dataset import EvaluationDataset

ds = EvaluationDataset(test_cases=[...])
evaluate(test_cases=ds.test_cases, metrics=[FaithfulnessMetric()])

# MLflow — model-card style; integrates the libraries above as scorers
import mlflow

results = mlflow.genai.evaluate(
    data=eval_df,
    predict_fn=my_agent,
    scorers=[my_faithfulness, ragas_scorer("faithfulness"), deepeval_scorer("g-eval")],
)
# Results land in MLflow's experiment UI; scorers come from any plugged library.
```

### E — Production / online evaluation

Online evaluation means running scorers against live production traces, not against a static dataset. The four platforms with first-class support:

```python
# LangSmith — Automation Rules (configured in the UI; trigger filter + sample rate + evaluator)
# Conceptual shape (the actual configuration is server-side):
#   trigger: tags contains "prod"
#   sample_rate: 0.1
#   evaluator: faithfulness_evaluator
#   target: feedback writes to the trace

# Langfuse — LLM-as-judge evaluations on production traces
# Configured via the Langfuse UI or via the SDK; runs as a worker against the trace stream.

# Phoenix — online evaluators (gated behind paid Arize AX in production deployments)
from phoenix.evals import OpenAIModel, run_evals  # Same as offline; the production deployment
# wires this into a worker that runs against the trace stream.

# Custom worker pattern (MLflow, RAGAS, DeepEval, TruLens running against a trace stream)
# These libraries don't ship a built-in "production evaluator" abstraction —
# you wire them into a streaming worker that subscribes to the trace stream
# (typically via the OTel Collector's OTLP receiver or via the trace-platform's API)
# and applies the metric library to each sampled trace.
#
# This is the pattern documented in concepts/evaluation/online-evaluator-registration.md
# and implemented in Lab 19, Recipe 2 Step 4, and Project 2 M4.
```

The "Pattern A streaming worker" in [Recipe 2](../../learning-paths/06-evaluation-observability/recipes/02-opentelemetry-native.md) is the right abstraction when your eval library doesn't have a built-in production-evaluator concept. It generalizes across MLflow, RAGAS, DeepEval, TruLens, and bespoke metrics.

## Decision guide

The single most important question: **what is your hard constraint?** Pick the row that matches yours.

**Choose LangSmith if** your application is built on LangChain or LangGraph, your team values the lowest possible time to first eval, vendor coupling is acceptable, LangGraph Studio's IDE workflow is a genuine productivity gain, and you can absorb per-seat + per-trace pricing as you scale. The strongest fit when the entire team is LangChain-rooted; the weakest fit when half the codebase is framework-agnostic.

**Choose Braintrust if** your central pain is CI/CD regression — every prompt change goes through automated eval gates that block merges on quality regression. Strong when eval-driven shipping is your discipline (and your team has the engineering culture to maintain regression sets); weak when you primarily need a debugger or an annotation-heavy human-review workflow.

**Choose Langfuse if** self-host + OSS license is non-negotiable (regulated industries, air-gapped deployments, data-sovereignty contracts), your workload is LLM-only (not classical ML), and your team can operate database performance + Kubernetes scaling. The MIT license + 12M+ monthly PyPI downloads make it the safest OSS choice; the ClickHouse acquisition (Jan 2026) means the OSS roadmap is now influenced by an infrastructure parent.

**Choose Phoenix if** you're already on Arize for classical ML, your team values OpenInference's standardization of OTel semantic conventions for LLMs, and your workflows are notebook-first or eval-heavy. The OpenInference license (Apache 2.0 — the conventions are open) is permissive; the Phoenix license (Elastic License 2.0 — the backend) restricts you from offering it as a managed service to third parties. Online evaluators and the Alyx Copilot are gated behind paid Arize AX plans.

**Choose Laminar if** your workload is **long-running agents** (multi-step, tool-calling, sub-agent-spawning), you need a transcript-first trace UX rather than span-tree drilldowns, and Apache 2.0 + one-command self-host is the right fit. The strongest agent-debugging UX in mid-2026; less prompt-management focus than Langfuse.

**Choose MLflow if** your team is already on MLflow for classical ML and you want **one platform for both ML and GenAI**. The widest pluggable scorer ecosystem (RAGAS, DeepEval, Phoenix, TruLens, Guardrails AI all integrate as `@scorer` decorators inside `mlflow.genai.evaluate()`), and the GenAI extensions are catching up to LLM-native platforms quarter by quarter. The right pick when you have an MLflow installation already and don't want to operate two evaluation stacks.

**Choose DeepEval if** you want a **library** (not a platform), pytest-native integration, and the ability to bring 50+ research-backed metrics into your CI pipeline. Pair with Confident AI when you need the managed platform on top (production monitoring, dataset auto-curation, multi-turn simulation, no-code workflows for non-engineers). The DeepEval-only path is the right fit when you want a metric library that lives in your codebase, not a vendor that owns your traces.

**Choose RAGAS if** your workload is **RAG specifically** and you want the deepest, most research-backed metric library: faithfulness, answer relevancy, context precision/recall/utilization, noise sensitivity, agent goal accuracy, tool call accuracy. RAGAS is a metric library only — no tracing, no datasets UI, no production monitoring. The right pick when you have an existing observability stack and want to slot in best-in-class RAG metrics.

**Choose TruLens if** you want **inline trace + evaluation** in a single workflow — every LLM and retrieval call is traced and evaluated in the same step. Particularly strong for agentic systems where multi-hop failures are hard to isolate after the fact. Smaller ecosystem than the platforms above; the right pick when you specifically want trace-and-eval coupling rather than trace-then-eval.

## How the tools map to Path 06

| Module | Best-fit tools | Why |
|--------|----------------|-----|
| **Module 1 — From harness to production observability** | All 9 tools play here. Laminar + TruLens are the strongest *instrumentation* fits (Laminar for agent traces; TruLens for inline trace + eval). | Every tool implements some form of trace ingestion; choose by deployment shape. |
| **Module 2 — LangSmith trace ingestion** | LangSmith primarily. | Module 2 is literally LangSmith-shaped. The Path 06 module covers the surface; if you pick another platform, this module's mechanics map to that platform's analog. |
| **Module 3 — OpenTelemetry portable layer** | Langfuse v3, Phoenix, Laminar — all OTel-native. LangSmith joined the OTel-native tier in March 2026. | Module 3 is OTel-as-substrate; any tool that ingests OTLP is a fit. The OpenInference + OpenLLMetry semantic conventions are what make tools interchangeable at this layer. |
| **Module 4 — Online evaluation + tail-based sampling** | LangSmith (Automation Rules), Braintrust (CI/CD-coupled), Confident AI, MLflow + pluggable scorers, custom workers using RAGAS/DeepEval/TruLens. | Module 4's "registered evaluator" abstraction maps to each platform's evaluator/scorer/Automation Rule concept. The Pattern A streaming worker in Recipe 2 is the universal escape hatch when the platform doesn't have a built-in production-evaluator concept. |
| **Module 5 — Drift detection + agent-as-judge calibration** | Phoenix (50+ research-backed metrics + drift analytics), DeepEval (calibration patterns), MLflow (pluggable scorers + automatic issue detection), bespoke workers consuming any platform's score stream. | Drift detection is mechanically the same across tools — KS, PSI, Wasserstein on score arrays. The differentiator is *which* tool's score stream you're reading from. |
| **Module 6 — Cost attribution + adaptive sampling** | OTel-native platforms (Langfuse v3, Phoenix, Laminar) because baggage propagation works natively. LangSmith partial (since March 2026 OTel support). | Cost attribution depends on identity propagation via OTel baggage; OTel-native platforms get this for free. Non-OTel platforms require manual attribute propagation. |
| **Module 7 — Multi-turn (threaded) evaluation** | LangSmith (first-class threads + Multi-turn Evals), Confident AI (multi-turn simulation), Laminar (transcript view), DeepEval (multi-turn test cases). | Module 7's threaded evaluation depends on `thread.id` propagation. Tools with first-class thread/session abstractions are the strongest fits. |

## Tools mapped to the Batch 33 recipes and Batch 35 projects

| Recipe / Project | Primary tools | Optional / supplementary tools |
|---|---|---|
| [Recipe 1 — LangSmith-native](../../learning-paths/06-evaluation-observability/recipes/01-langsmith-native.md) | LangSmith | DeepEval / RAGAS / TruLens as scorers via custom evaluators |
| [Recipe 2 — OpenTelemetry-native](../../learning-paths/06-evaluation-observability/recipes/02-opentelemetry-native.md) | Phoenix, Langfuse v3, Laminar (pick one) | RAGAS / DeepEval / TruLens as the eval library inside the streaming evaluator worker |
| [Recipe 3 — Hybrid LangSmith + OTel](../../learning-paths/06-evaluation-observability/recipes/03-hybrid-langsmith-and-otel.md) | LangSmith (eval UX) + Phoenix or Langfuse v3 or Laminar (OTel-native operational layer) | RAGAS / DeepEval as scorers; MLflow if classical ML coexists |
| [Project 1 — LangSmith eval stack](../../learning-paths/06-evaluation-observability/projects/01-langsmith-eval-stack.md) | LangSmith | DeepEval scorers via Automation Rules custom evaluators; Confident AI if multi-turn simulation is needed |
| [Project 2 — OTel observability stack](../../learning-paths/06-evaluation-observability/projects/02-otel-observability-stack.md) | Phoenix or Langfuse v3 or Laminar (pick one); plus Datadog or Tempo+Grafana+Prometheus as the APM backend | RAGAS for RAG-specific metrics; DeepEval for the broader metric library; MLflow if the platform team needs ML+GenAI unified |
| [Project 3 — Hybrid production stack](../../learning-paths/06-evaluation-observability/projects/03-hybrid-production-stack.md) | LangSmith + Phoenix or Langfuse v3 or Laminar + APM | Full optionality on the scorer library; the architecture is tool-agnostic at the scorer layer |

The recipes and projects are deliberately tool-agnostic at the scorer layer. The choice of LangSmith / Phoenix / Langfuse / Laminar shapes the deployment; the choice of RAGAS / DeepEval / TruLens shapes which metrics run inside it. These choices are independent.

## Migration paths

Three common transitions in mid-2026:

- **LangSmith-only → Hybrid (LangSmith + OTel)**. The natural path when an existing LangSmith deployment needs APM-integrated paging or per-tenant cost attribution. Recipe 3 documents the shape; Project 3 builds it. The LangSmith March 2026 OTLP endpoint made this transition substantially cheaper than it was in 2025.
- **Phoenix (self-host single-node) → Langfuse or Laminar (scaled self-host)**. Common when the Phoenix OSS single-node deployment hits scaling limits and the Elastic License 2.0 prevents offering it as a managed service internally. Langfuse (MIT) and Laminar (Apache 2.0) both have permissive licenses + scaled self-host stories.
- **Single-tool → MLflow with pluggable scorers**. When the platform team mandates MLflow as the experiment-tracking layer for both ML and GenAI workloads. MLflow's `@scorer` decorator + native integration with RAGAS / DeepEval / Phoenix / TruLens means you keep your existing metrics; the platform layer changes.

## Anti-scope (what this page does not do)

- **No "best tool overall" conclusion.** Different teams have different constraints; there is no single answer. Reading this page and concluding "X is the best" misuses it. The right output is "X fits *our* constraints."
- **No benchmark claims without sources.** Every quantitative claim in the comparison table (pricing, OTel support, license type, integrations) carries a citation in the references section with a publication date. Claims without sources have been omitted rather than included.
- **No pricing claims unless time-bounded.** All pricing data in this page carries the form "as of [month-year] per [source]". Pricing changes quarterly; verify against current vendor docs before committing budgets.
- **No comparison of tools the page hasn't actually verified.** Mid-2026 capabilities only; older capabilities are noted only when they materially affect the migration story (e.g., LangSmith's pre-March-2026 OTel state).
- **No platform recommendations driven by Anthropic, LangChain, or any vendor.** This page is written for the open-source Agentic AI Engineer course; the path uses LangSmith heavily in Recipe 1 and Project 1 but does not recommend LangSmith as the universal answer.
- **No mention of pricing in dollar amounts beyond what's verifiable from the cited sources.** Where pricing is mentioned, it's the figure in the cited source on its publication date.
- **No replacement for vendor documentation.** Every tool's docs are linked in the references; this page summarizes their differences but does not duplicate them.

## References

All claims in the comparison table and decision guide cite at least one of these sources. Sources are listed with their publication date so readers can assess freshness.

**Vendor docs (primary sources, undated — verify against current docs)**:

- LangSmith documentation — [docs.langchain.com](https://docs.langchain.com/langsmith) — official tracing, eval, dataset, annotation queue surface
- LangChain blog (March 2026), *Introducing End-to-End OpenTelemetry Support in LangSmith* — [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/) — the OTLP endpoint announcement
- Braintrust documentation — [www.braintrust.dev](https://www.braintrust.dev/) — official eval, dataset, CI/CD gate surface
- Langfuse documentation — [langfuse.com/docs](https://langfuse.com/docs) — official tracing, eval, dataset surface; OTel endpoint at `/api/public/otel`
- Arize Phoenix documentation — [docs.arize.com/phoenix](https://docs.arize.com/phoenix) — official tracing, eval surface; OpenInference SDK
- Laminar documentation — [docs.lmnr.ai](https://docs.lmnr.ai/) — official agent observability surface
- MLflow GenAI evaluation documentation — [mlflow.org/docs](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html) — `mlflow.genai.evaluate()` surface
- DeepEval documentation — [docs.confident-ai.com](https://docs.confident-ai.com/) — DeepEval library + Confident AI platform
- RAGAS documentation — [docs.ragas.io](https://docs.ragas.io/) — metric library reference
- TruLens documentation — [trulens.org](https://www.trulens.org/) — inline trace + eval reference

**Industry comparison posts (secondary sources, dated)**:

- Latitude blog (Q2 2026), *Best LLM Observability Tools for AI Agents: Latitude vs Langfuse, LangSmith, Arize, and Braintrust (2026)* — [latitude.so/blog](https://latitude.so/blog/best-llm-observability-tools-agents-latitude-vs-langfuse-langsmith) — 8-platform comparison; documents Langfuse acquisition by ClickHouse Jan 2026; Braintrust free tier (1M spans/month + 10K evals)
- Laminar blog (April 2026), *Top 6 Agent Observability Platforms (2026): A Developer's Ranking* — [laminar.sh/article](https://laminar.sh/article/2026-04-23-top-6-agent-observability-platforms) — OTel support classification across platforms (Laminar/Phoenix native; Langfuse/LangSmith full OTLP endpoint as of March 2026; Braintrust/Weave partial)
- Laminar blog (April 2026), *Langfuse Alternatives 2026: 7 Top Picks for Agent Observability* — [laminar.sh/article](https://laminar.sh/article/langfuse-alternatives-2026) — pricing data: Laminar (data-volume; free 1GB; Hobby $30/3GB; Pro $150/10GB); LangSmith ($39/seat + $0.50/1K traces); Phoenix free OSS / Arize AX custom
- Laminar blog (April 2026), *Arize Phoenix Alternatives 2026: Top 7 for Agent Observability* — [laminar.sh/article](https://laminar.sh/article/arize-phoenix-alternatives-2026) — license details across platforms (Phoenix ELv2; Laminar Apache 2.0; Langfuse MIT; LangSmith closed)
- FutureAGI (2 weeks ago, May 2026), *LangSmith Alternatives in 2026: Open-Source vs Hosted LLM Eval Stacks* — [futureagi.com/blog](https://futureagi.com/blog/langsmith-alternatives-2026) — the four-stage eval loop framing (simulate → evaluate → observe → optimize)
- Braintrust blog (April 2026), *LangSmith vs. Braintrust: Which AI evaluation platform is better?* — [www.braintrust.dev/articles](https://www.braintrust.dev/articles/langsmith-vs-braintrust) — Braintrust's positioning vs LangSmith (eval-driven shipping vs framework integration); per-seat vs team pricing
- Braintrust blog (March 2026), *LangSmith alternatives (2026): Best tools for LLM tracing, evals, and prompt iteration* — [www.braintrust.dev/articles](https://www.braintrust.dev/articles/langsmith-alternatives-2026) — competitive landscape framing
- Braintrust blog (January 2026), *Langfuse alternatives: Top 5 competitors compared (2026)* — [www.braintrust.dev/articles](https://www.braintrust.dev/articles/langfuse-alternatives-2026) — the "choose X if" decision-guide pattern adopted in section 4
- Techsy (April 2026), *Langfuse vs LangSmith: An Independent Verdict* — [techsy.io/en/blog](https://techsy.io/en/blog/langfuse-vs-langsmith) — Langfuse v3 OTel rebuild; @observe decorator API stability; OTel architecture as an advantage for teams with existing observability stacks
- CB Insights, *Compare Braintrust vs Langfuse* — [www.cbinsights.com/compare](https://www.cbinsights.com/compare/braintrust-data-vs-langfuse) — Langfuse acquired by ClickHouse Jan 2026; Braintrust $80M Series B Feb 2026
- MLflow blog, *Top 5 LLM and Agent Observability Tools in 2026* — [mlflow.org](https://mlflow.org/top-5-agent-observability-tools/) — Phoenix as OpenInference owner; Phoenix's ELv2 license analysis
- MLflow blog, *Top 5 Agent Evaluation Tools in 2026* — [mlflow.org](https://mlflow.org/top-5-agent-evaluation-frameworks/) — MLflow's native integration with RAGAS / DeepEval / Phoenix / TruLens / Guardrails AI as pluggable scorers
- Atlan (April 2026), *RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks (2026)* — [atlan.com/know](https://atlan.com/know/llm-evaluation-frameworks-compared/) — DeepEval Apache 2.0; G-Eval metric reference; TruLens as TruEra origin
- Confident AI blog (4 days ago, May 2026), *Best MLflow Alternatives for LLM Evaluation (2026)* — [www.confident-ai.com/knowledge-base](https://www.confident-ai.com/knowledge-base/compare/best-mlflow-alternatives-for-llm-evaluation) — Langfuse 12M+ monthly PyPI downloads; Confident AI's auto-curation + quality-aware alerting features
- AppSecSanta (April 2026), *Arize AI Review 2026: AI Observability & LLM Evaluation* — [appsecsanta.com](https://appsecsanta.com/arize-ai) — Phoenix 9.1k+ GitHub stars; Arize AX traces 1 trillion spans + 50 million evaluations monthly
- CallSphere blog (2 weeks ago, May 2026), *RAG Evaluation Frameworks 2026: RAGAS, TruLens, and DeepEval in Practice* — [callsphere.ai/blog](https://callsphere.ai/blog/rag-evaluation-frameworks-2026-ragas-trulens-deepeval) — three-failure-mode decomposition of RAG evals
- genai.qa (April 2026), *Promptfoo vs DeepEval vs RAGAS: 2026 LLM Evaluation Tools Comparison* — [genai.qa/blog](https://genai.qa/blog/promptfoo-vs-deepeval-vs-ragas/) — DeepEval 50+ metrics; RAGAS metrics from EACL 2024 paper; Apache 2.0 license classifications

**Path 06 internals (the rest of the path)**:

- [`concepts/evaluation/README.md`](./README.md) — the full Path 06 v1 concept-page index
- [`langsmith-tracing-shape.md`](./langsmith-tracing-shape.md), [`opentelemetry-genai-conventions.md`](./opentelemetry-genai-conventions.md), [`platform-fanout-and-portability.md`](./platform-fanout-and-portability.md), [`online-evaluator-registration.md`](./online-evaluator-registration.md), [`online-vs-offline-evaluation.md`](./online-vs-offline-evaluation.md), [`agent-as-judge-calibration.md`](./agent-as-judge-calibration.md), [`drift-detection.md`](./drift-detection.md), [`cost-attribution.md`](./cost-attribution.md), [`adaptive-sampling.md`](./adaptive-sampling.md), [`tail-based-sampling.md`](./tail-based-sampling.md), [`multi-turn-evaluation.md`](./multi-turn-evaluation.md) — the mechanism pages this deep dive builds on
- [Lab 17](../../labs/17-langsmith-trace-ingestion/), [Lab 18](../../labs/18-opentelemetry-portable-tracing/), [Lab 19](../../labs/19-online-evaluation-and-sampling/), [Lab 20](../../labs/20-drift-detection-and-calibration/), [Lab 21](../../labs/21-cost-attribution-and-adaptive-sampling/), [Lab 22](../../labs/22-multi-turn-evaluation/) — the lab implementations
- [Recipe 1](../../learning-paths/06-evaluation-observability/recipes/01-langsmith-native.md), [Recipe 2](../../learning-paths/06-evaluation-observability/recipes/02-opentelemetry-native.md), [Recipe 3](../../learning-paths/06-evaluation-observability/recipes/03-hybrid-langsmith-and-otel.md) — Batch 33 recipes
- [Pattern 1](../../learning-paths/06-evaluation-observability/patterns/01-cost-aware-retrieval.md), [Pattern 2](../../learning-paths/06-evaluation-observability/patterns/02-drift-triggered-review.md), [Pattern 3](../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) — Batch 34 patterns
- [Project 1](../../learning-paths/06-evaluation-observability/projects/01-langsmith-eval-stack.md), [Project 2](../../learning-paths/06-evaluation-observability/projects/02-otel-observability-stack.md), [Project 3](../../learning-paths/06-evaluation-observability/projects/03-hybrid-production-stack.md) — Batch 35 projects
