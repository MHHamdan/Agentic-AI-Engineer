# Lab 17 — LangSmith trace ingestion

> ⏱ 80-100 min · 🔴 Advanced · Prerequisites: [Lab 14 solution](../14-langgraph-supervisor-bridge/solution/) (the agent being instrumented), [LangSmith tracing shape](../../concepts/evaluation/langsmith-tracing-shape.md), [online vs offline evaluation](../../concepts/evaluation/online-vs-offline-evaluation.md), a free LangSmith account.

Instrument a Lab 14-style LangGraph supervisor agent with LangSmith. Three modes: automatic tracing for LangGraph nodes, `@traceable` for custom Python helpers, and `tracing_v2_enabled` for scoped projects. Wire two `agentevals` evaluators (deterministic trajectory match + LLM-judged) to score traces. Run an offline evaluation experiment against a tiny Dataset. Close with one stretch: a custom evaluator that reuses Lab 16's `routing_accuracy` algorithm — the bridge from from-scratch metrics to platform-native ones.

This is the first Path 06 lab. Path 06 v1 has 6 labs total (Modules 2-7); this batch ships Module 2.

## What you'll build

```mermaid
flowchart TD
    A[Lab 14 supervisor agent<br/>inline minimal version] --> B[Set LANGSMITH_TRACING=true]
    B --> C[Auto-traced LangGraph nodes]
    A --> D[@traceable on helpers]
    D --> C
    C --> E[LangSmith UI<br/>messages view + timeline view]
    E --> F[Convert trace via<br/>extract_langgraph_trajectory_from_thread]
    F --> G[graph_trajectory_strict_match<br/>deterministic]
    F --> H[create_trajectory_llm_as_judge<br/>LLM-judged]
    G --> I[client.evaluate against a 3-example Dataset]
    H --> I
    I --> J[Compare scores across runs]
    J --> K[Stretch: custom routing_accuracy<br/>via Lab 16 algorithm]
```

No new from-scratch agent code — the lab uses Lab 14's pattern inline (one supervisor, one researcher, one writer) and focuses on the *instrumentation* layer. You'll touch ~30 lines of LangSmith / agentevals code and produce 3-5 traces in the LangSmith UI.

## Goal

By the end of the lab you should be able to:

- Set `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` and see your LangGraph agent's traces appear in the LangSmith UI within seconds, with zero code changes.
- Decorate a custom Python helper with `@traceable` (with name, tags, metadata) and see it nest under the auto-trace.
- Use the `tracing_v2_enabled` context manager to scope traces to a specific project — useful for A/B comparing two agent variants in one process.
- Read a trace in both the messages view (logic) and the timeline view (latency cost) and know which view to use for which question.
- Convert a LangGraph trace into the `GraphTrajectory` shape via `extract_langgraph_trajectory_from_thread`.
- Wire `create_trajectory_match_evaluator` (deterministic, free per call) and `create_trajectory_llm_as_judge` with `TRAJECTORY_ACCURACY_PROMPT` (LLM-judged, ~$0.005 per call).
- Create a tiny LangSmith Dataset (3 input/output pairs) and run `client.evaluate(...)` to get experiment results that compare scores across the two evaluators.
- Implement a custom evaluator that reuses Lab 16's `routing_accuracy` algorithm (LCS-based), showing the bridge from from-scratch to platform-native.
- Explain when to register an evaluator online vs run it offline — and how the platform's annotation-queue workflow closes the production-to-fixture-set loop.

## Prerequisites

- **Lab 14 (LangGraph supervisor bridge)** — required reading. The agent we instrument is its pattern, simplified inline. Without familiarity, the lab's first three cells will need extra context the lab doesn't repeat.
- **Concept pages** — read [LangSmith tracing shape](../../concepts/evaluation/langsmith-tracing-shape.md) and [online vs offline evaluation](../../concepts/evaluation/online-vs-offline-evaluation.md) first. The lab moves fast through patterns those pages establish.
- **Free LangSmith account** — sign up at smith.langchain.com. The free tier covers 5,000 traces/month; this lab uses ~10.
- **OpenAI or Anthropic API access** — same provider you used for Path 03.
- **Working pip environment** — the lab installs `langsmith` and `agentevals` in the setup cell. Both are small.

## 🛠 Tools and versions

| Library | Version | Used for |
|---|---|---|
| `langsmith` | latest from PyPI (Apr 2026+) | trace ingestion, `@traceable`, `tracing_v2_enabled`, `Client.evaluate` |
| `agentevals` | latest from PyPI | trajectory evaluators (`trajectory.match`, `trajectory.llm`, `graph_trajectory`) |
| `langgraph` | already pinned | the agent runtime |
| `langchain-openai` or `langchain-anthropic` | already pinned | provider-agnostic chat model |

The two new packages are installed in the lab's setup cell with explicit pip install. They're not in the repo's `pyproject.toml` yet; pinning them is a hygiene-batch task.

## Structure

26 cells, 14 markdown / 12 code, output-stripped, sample-output markdown cells where useful.

- **Step 0**: Setup — install `langsmith` + `agentevals`, set env vars, verify the import.
- **Step 1**: Inline minimal Lab 14 agent — supervisor + researcher + writer in compact form. ~3 cells. References Lab 14's solution for full pattern.
- **Step 2**: Run once with `LANGSMITH_TRACING=true`. Observe auto-tracing in the LangSmith UI. No decorators required for LangGraph nodes.
- **Step 3**: Add `@traceable` to a custom helper function (a citation post-processor). See it nest in the trace tree.
- **Step 4**: Add tags + metadata via `@traceable(name=..., tags=[...], metadata={...})`. Filter the UI by tag.
- **Step 5**: Use `tracing_v2_enabled(project_name="...")` to scope two consecutive runs to separate projects. A/B comparison setup.
- **Step 6**: Read the trace in both views: messages-view (logic) and timeline-view (latency).
- **Step 7**: Extract the trajectory via `extract_langgraph_trajectory_from_thread`. Inspect the `GraphTrajectory` shape.
- **Step 8**: Wire `create_trajectory_match_evaluator(trajectory_match_mode="strict")` — deterministic; ~50 lines of evaluator setup; instant scoring.
- **Step 9**: Wire `create_trajectory_llm_as_judge(prompt=TRAJECTORY_ACCURACY_PROMPT)` — LLM-judged; ~$0.005 per evaluation; nuanced scoring.
- **Step 10**: Create a LangSmith Dataset with 3 examples; run `client.evaluate(...)` with both evaluators; observe the experiment view.
- **Step 11**: Stretch — write a custom evaluator that reuses Lab 16's `routing_accuracy` (LCS-based) on the graph trajectory. Demonstrates the bridge from from-scratch metrics to platform-native ones.
- **Step 12**: Synthesis — what we instrumented, what `agentevals` adds vs Lab 16's harness, when to use which.

## What to watch for

**1. `@traceable` is a no-op without environment variables.** The decorator captures Runs *if* tracing is enabled. A common confusion: decorated functions in a process without `LANGSMITH_TRACING=true` don't produce traces and don't error. If you don't see traces in the UI, the env vars are the first thing to check.

**2. LangGraph nodes auto-trace; non-LangGraph functions need `@traceable`.** The lab demonstrates both. The pattern is: env-var-only for the graph itself; `@traceable` for the helpers, preprocessors, and post-processors that aren't graph nodes but contribute to the trace's value.

**3. `extract_langgraph_trajectory_from_thread` needs a checkpointer.** The function reads the graph's saved state to reconstruct the trajectory. Without a checkpointer attached to the compile, the function returns empty. The lab uses `InMemorySaver` throughout.

**4. The two evaluators score on different criteria.** `trajectory_match` cares about message-sequence equality; `trajectory_llm_as_judge` cares about appropriateness. They will disagree often, and that disagreement is informative. The lab's Step 11 includes one case where they disagree on purpose.

**5. LLM-as-judge biases are real.** Zheng et al. 2023 documented three (position, verbosity, self-enhancement). The lab uses `TRAJECTORY_ACCURACY_PROMPT` as-is; in production you'd calibrate against periodic human labels. Module 5 covers calibration; this lab only flags the issue.

**6. Free-tier rate limits exist.** LangSmith's free tier is 5,000 traces/month and rate-limits trace ingestion to a steady-state rate. Running the lab once is fine; running it 50 times in five minutes might hit the rate limit. Pace your runs.

## What's not in this lab (anti-scope)

- **OpenTelemetry instrumentation.** Module 3 covers it (same agent, different SDK).
- **Online evaluator registration via the LangSmith UI.** Mentioned in the concept page; doing the UI walkthrough in a notebook doesn't work well. Reader does the UI step manually if interested.
- **Drift detection over time.** Module 5.
- **Multi-turn (threaded) evaluation.** Module 7.
- **Cost-attribution patterns.** Module 6.
- **Phoenix / Langfuse / Laminar / Braintrust integration.** Concept page covers the landscape; this lab is LangSmith-specific by design.
- **Custom evaluator beyond `routing_accuracy`.** Lab 16's `citation_preservation` / `groundedness` / `plan_validity` etc. would each be similar patterns; the lab ships one as the canonical example.
- **A solution directory.** Following the Lab 09/16 pattern, the solution lands in a follow-up batch.

## Cost and timing

- LangSmith free tier: 5,000 traces/month. This lab uses ~10. No charge.
- LLM calls for the agent's own execution: ~$0.01-0.03 per agent run (gpt-4o-mini rates). 5 runs ≈ $0.05-0.15.
- LLM calls for the `trajectory_llm_as_judge` evaluator: ~$0.005 per evaluation. 3 evaluations ≈ $0.015.
- Total cost per full lab run: **~$0.05-0.20**.
- Wall-clock: **80-100 minutes** including reading both concept pages and working through the synthesis.

## Solution

The reference solution lands in a follow-up batch. Two design choices worth flagging up front:

- **The agent is inline-minimal, not a copy of Lab 14's solution.** Lab 17 isn't about rebuilding Lab 14; it's about instrumenting it. The inline version is ~50 lines so the trace structure is readable; the production pattern reads from `from labs.14_langgraph_supervisor_bridge.solution import build_supervisor_graph`.
- **The Dataset has 3 examples, not 30.** Datasets in production are 100s to 1000s. The lab demonstrates the pattern; the production fixture set is built via the annotation queue over weeks of real traffic.

## Next

After this lab, [Module 3](../../learning-paths/06-evaluation-observability/) (planned, future batch) covers the OpenTelemetry-native instrumentation path for the same agent — fanout to LangSmith + a generic OTel collector, vendor-neutral. The two modules together establish the LangSmith-native and OTel-portable paths; later modules build on both.

## References

- [LangSmith tracing shape](../../concepts/evaluation/langsmith-tracing-shape.md) — the instrumentation patterns this lab applies.
- [Online vs offline evaluation](../../concepts/evaluation/online-vs-offline-evaluation.md) — the agentevals integration this lab demonstrates.
- [Lab 14 — LangGraph supervisor bridge](../14-langgraph-supervisor-bridge/) — the agent pattern being instrumented.
- LangSmith Python SDK: [pypi.org/project/langsmith](https://pypi.org/project/langsmith/).
- LangChain `agentevals` repo: [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- LangChain Docs, *Trace LangGraph applications*: [docs.langchain.com](https://docs.langchain.com/langsmith/trace-with-langgraph).
