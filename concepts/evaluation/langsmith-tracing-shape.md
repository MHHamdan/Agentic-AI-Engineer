# LangSmith tracing shape

> ⏱ ~12 min · 🔴 Advanced · Prerequisites: [observability's three pillars](./observability-three-pillars.md) (the framing), familiarity with at least one LangGraph agent from Path 03 (Lab 14 is the closest reference)

This page is the implementation companion to the framing in Module 1. It covers how LangSmith — the LangChain-native observability platform — sees your agent. Three tracing methods, what each captures, what each costs, when to reach for which. By the end you should be able to read a LangSmith trace and know what produced each span; conversely, you should be able to look at agent code and predict the trace shape it'll generate.

Path 06 covers LangSmith first because it's the path of least resistance for Path 03's LangGraph-based agents (Lab 14, Lab 15). Module 3 covers the OpenTelemetry-native path for the same agents, where the trade-off is portability vs ecosystem fit.

## The LangSmith data model

LangSmith organizes everything around three concepts:

- **Run** — one function execution. A Run captures inputs, outputs, start/end timestamps, parent reference, status, errors, and arbitrary metadata. Runs are typed: `chain`, `llm`, `tool`, `retriever`, `parser`, `prompt`.
- **Trace** — a tree of Runs sharing a root. The root Run represents the top-level user request; child Runs nest underneath via parent_run_id. A trace from a Lab 14 supervisor agent has the supervisor root, a researcher child, the researcher's LLM call as a grandchild, the researcher's tool calls as great-grandchildren, and so on.
- **Project** — a namespace for traces, scoped per environment (dev / staging / prod) or per agent variant (v1 / v2). Projects let you separate runs cleanly without polluting one workspace.

This shape maps cleanly onto an agent's execution. A LangGraph supervisor graph produces one Run per node visit; the `chat_with_tools` loop inside a `create_agent` worker produces one Run per LLM call plus one Run per tool call. The nesting reflects the actual call stack.

## Three tracing methods, ranked by automation

LangSmith offers three ways to feed Runs into the platform, each at a different point on the automation-vs-control axis. You usually mix them.

### 1. Auto-tracing for LangChain + LangGraph

Set two environment variables:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=ls__...
```

Optionally specify a project name:

```bash
export LANGSMITH_PROJECT=my-agent-staging
```

Now every LangChain chain, every LangGraph graph node, every `ChatOpenAI` / `ChatAnthropic` call, every tool invocation through `langchain_core.tools.tool` — all are automatically captured as Runs with the right type and the right parent. No code changes.

This is the path of least resistance for a Lab 14-style agent. Run the existing notebook; traces appear in LangSmith within seconds.

What auto-tracing captures, specifically:
- LangGraph node entries and exits (one Run per node visit per execution)
- LLM calls (`ChatOpenAI`, `ChatAnthropic`, etc.) — full prompts and full responses, plus token usage and latency
- Tool calls made via `langchain_core.tools.tool` decorators — args, results, errors
- State transitions in `StateGraph` — what changed in state at each node
- `create_agent`'s internal agent-loop iterations — each LLM-call + tool-call cycle as nested Runs

What auto-tracing does NOT capture:
- Plain Python functions that aren't LangChain primitives. Your custom preprocessor, your retry wrapper, your business-logic helper — these are invisible.
- Functions in non-LangChain SDKs (raw `openai` or `anthropic` client calls, unless you wrap them via `wrap_openai`).
- Code outside the agent's invocation path (data prep, batch jobs).

For everything auto-tracing misses, you reach for method 2.

### 2. The `@traceable` decorator for custom Python functions

```python
from langsmith import traceable

@traceable
def preprocess_text(raw: str) -> str:
    """Lowercase, strip whitespace, normalize Unicode."""
    return raw.lower().strip()
```

Now `preprocess_text` produces a Run each time it's called. Nested under the active trace if there is one; orphan top-level otherwise.

The decorator accepts metadata for filtering:

```python
@traceable(
    name="preprocess_text",
    tags=["preprocessing", "stable"],
    metadata={"version": "2.1"},
    run_type="chain",
)
def preprocess_text(raw: str) -> str:
    ...
```

`name` overrides the auto-derived function name (useful when wrapping). `tags` are filterable in the UI ("show me all traces tagged `preprocessing`"). `metadata` is arbitrary structured data ("show me runs where `version` is `2.1`"). `run_type` overrides the default `"chain"` if the function is actually an LLM call, tool, etc.

Two practical patterns:
- Decorate your *entry point* — the function that takes a user query and returns a final answer. This gives every Run in the call stack a coherent root.
- Decorate your *helpers* — preprocessing, retry logic, custom retrieval — so they appear nested in the trace tree where they belong.

What `@traceable` does NOT do on its own: it doesn't enable tracing if the environment variables aren't set. A decorated function in a process without `LANGSMITH_TRACING=true` is a no-op. The decorator is the *what to capture*; the env vars are the *whether to capture*.

### 3. The `tracing_v2_enabled` context manager

```python
from langsmith.run_helpers import tracing_v2_enabled

with tracing_v2_enabled(project_name="experiment-1"):
    result = my_agent.invoke({"messages": [...]})
```

Useful for scoping a block of code to a specific project. Common pattern: your CI run sends traces to a `ci` project, your manual experiments go to `dev`, production goes to `prod`. The context manager swaps projects without touching env vars.

Also useful when running multiple agent variants in the same process for A/B comparison:

```python
with tracing_v2_enabled(project_name="agent-v1"):
    result_v1 = agent_v1.invoke(query)

with tracing_v2_enabled(project_name="agent-v2"):
    result_v2 = agent_v2.invoke(query)
```

Each variant's traces land in its own project; you can compare results in the UI side-by-side without cross-contamination.

### 4. `RunTree` API — full manual control (rarely needed)

For code where neither auto-tracing nor `@traceable` fits — non-LangChain agents using a non-standard execution model — there's a `RunTree` API for full manual control. You explicitly start a Run, attach children, end it. Out of scope for this module; the official docs cover it when you need it.

## The two views in the UI

LangSmith renders traces in two ways. Each answers a different question.

**Messages view** — a chat-like sequential rendering of the message history at the top of the trace tree. Best for: "what did the agent say at each step?" The user's input message, the assistant's response, the tool calls, the tool results — all in order, like a conversation log. This is the view to start with when you're debugging *what the agent did*.

**Timeline view** — a flame-graph rendering of the Run tree with wall-clock duration. Best for: "where is the time going?" Each Run is a horizontal bar sized by duration; nested Runs sit underneath their parent. You can see in one glance that 80% of the trace duration is in one slow `fetch_page` tool call. This is the view to start with when you're debugging *why the agent is slow*.

The two views are complementary. Most debugging sessions toggle between them — messages view to understand the logic, timeline view to find the cost.

## Adding the right metadata

Production traces become useful — really useful — when you add the right metadata at the right level. The patterns that work:

**At the trace root**: tag every trace with the dimensions you want to aggregate over later.
- `user_id` (or hashed equivalent) for per-user analysis
- `tenant_id` for multi-tenant deployments
- `agent_version` for A/B testing
- `experiment_id` for tracking a specific rollout
- `environment` (`dev` / `staging` / `prod`)

These propagate to all child Runs automatically. Aggregations in the UI (or via `client.list_runs(...)`) can filter on any of them.

**At specific Runs**: tag individual functions with context relevant to that function.
- A retrieval function: tag with `top_k`, `index_name`, `query_type`
- An LLM call: model_name and temperature are auto-captured, but adding `prompt_version` lets you correlate quality changes with prompt changes

**Don't dump everything**: tags are filterable; metadata is searchable. Both are stored per-Run. Tagging every Run with everything makes the UI noisy and storage costs creep. Tag what you'll actually filter on.

## What this costs

LangSmith's free tier covers 5,000 traces per month — enough for development and for most courses. Production deployments quickly exceed this. Pricing scales with traces ingested; the storage of those traces is the underlying cost driver.

Two cost-management patterns worth flagging early:
- **Sample at the ingestion layer.** Module 6 covers tail-based sampling — keep failed/expensive/anomalous traces in full; drop most happy-path traces before they're ingested. Cuts storage by 90%+ without losing diagnostic depth.
- **Trim large LLM payloads.** A `ChatOpenAI` call's prompt + response can be tens of kilobytes. If you don't need the full content, set `LANGSMITH_HIDE_INPUTS=true` / `LANGSMITH_HIDE_OUTPUTS=true` per Run, or use the `process_inputs` / `process_outputs` callbacks to redact. The trace shape is preserved; the bulk content isn't.

Neither is needed for the Module 2 lab. Both become relevant in production.

## The LangSmith-native vs OpenTelemetry-native trade

LangSmith offers two ingestion paths in 2026:

- **Native SDK**: the patterns above. Lowest setup cost; tightest LangChain/LangGraph integration; the UI's purpose-built features (messages view, agent-conversation rendering, `agentevals` integration, dataset workflow) all work out of the box. Lock-in trade: switching to a different observability platform means rewriting instrumentation.
- **OpenTelemetry-native**: instrument with the OpenTelemetry GenAI semantic conventions; LangSmith's API ingests OTel format alongside other backends. Higher setup cost; vendor-neutral; fanout to multiple backends works.

The [March 2026 LangSmith update](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/) added end-to-end OTel support: previously LangSmith ingested OTel but used a proprietary SDK; the update makes the SDK itself OTel-native, so a single instrumentation layer can fanout to LangSmith + a corporate Datadog + a self-hosted Langfuse without re-instrumenting.

For Module 2 we use the native LangSmith SDK because it's the path of least resistance and the patterns (`@traceable`, `tracing_v2_enabled`, the dataset workflow) are LangSmith-specific. Module 3 covers the OTel-native path.

## When LangSmith is the right pick

A practical guide:

**Use LangSmith** when:
- Your stack is LangChain or LangGraph-heavy. The auto-tracing alone is worth the ecosystem fit.
- You want the platform's purpose-built agent UIs (messages view, dataset workflow, `agentevals` integration). These take real engineering to replicate elsewhere.
- You're using LangGraph Studio for graph debugging. LangSmith feeds it.
- Single-vendor commitment is acceptable for the development velocity payoff.

**Consider alternatives** when:
- You have existing observability infrastructure on OpenTelemetry (your corporate Datadog / New Relic / self-hosted Grafana stack). You want fanout, not migration.
- You're building agents in non-LangChain SDKs (raw OpenAI / Anthropic / Vercel AI / custom). LangSmith still works via `@traceable` + `wrap_openai`, but the auto-tracing payoff shrinks.
- You need self-hosted observability for compliance reasons. LangSmith supports self-hosting but only on Enterprise tier; Langfuse (MIT) or Phoenix (open-source) may fit better at any scale.

The point isn't to pick a winner. The point is to know what each costs and what each helps with so you can pick for your situation.

## Related concepts

- [Observability's three pillars for agents](./observability-three-pillars.md) — the framing this page implements. LangSmith fits the "traces" pillar; its UI surfaces "metrics" via aggregation; "logs" are emitted as a side channel.
- [Online vs offline evaluation](./online-vs-offline-evaluation.md) — the next page. How `agentevals` runs both modes against the same trace shape.
- [Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/) — where these patterns are applied to a Lab 14-style agent.
- [Lab 14 — LangGraph supervisor bridge](../../labs/14-langgraph-supervisor-bridge/) — the agent Lab 17 instruments. Its solution README is the reference.

## References

- LangSmith Python SDK (`langsmith` on PyPI) — the `@traceable` decorator, `tracing_v2_enabled` context manager, `Client.evaluate` for offline runs. [pypi.org/project/langsmith](https://pypi.org/project/langsmith/).
- LangChain Docs, *Trace LangGraph applications* — auto-tracing semantics for graph nodes; nesting behavior with `@traceable` inside graphs. [docs.langchain.com/langsmith/trace-with-langgraph](https://docs.langchain.com/langsmith/trace-with-langgraph).
- LangChain Docs, *Trace with OpenTelemetry* — the OTel-native ingestion path; how `LANGSMITH_OTEL_ENABLED` configures the SDK. [docs.langchain.com/langsmith/trace-with-opentelemetry](https://docs.langchain.com/langsmith/trace-with-opentelemetry).
- LangChain blog (March 2026), *Introducing End-to-End OpenTelemetry Support in LangSmith* — the SDK-level OTel pivot; the fanout pattern. [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/).
- DeepWiki, *Tracing and Observability* (`langchain-ai/intro-to-langsmith`) — reference for the five tracing methods, with the `@traceable` deep-dive. [deepwiki.com](https://deepwiki.com/langchain-ai/intro-to-langsmith/3-tracing-and-observability).
