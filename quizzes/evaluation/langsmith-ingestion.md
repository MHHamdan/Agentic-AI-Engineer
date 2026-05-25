---
quiz_id: langsmith-trace-ingestion
title: LangSmith trace ingestion
path: 06-evaluation-observability
module: 2
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "Why is production observability a categorically different problem from the from-scratch evaluation harness (Lab 09 / Lab 16) — not just 'scale it up'?"
    options:
      - "Because production needs more metrics than the harness implements"
      - "Because the harness reads from a fixture file but production needs live trace ingestion, distribution drift detection over time, and distributed-tracing correlation across parallel sub-agents — none of which the harness addresses"
      - "Because production uses different LLM providers than the harness"
      - "Because production datasets must be larger than 30 fixtures"
    answer: "Because the harness reads from a fixture file but production needs live trace ingestion, distribution drift detection over time, and distributed-tracing correlation across parallel sub-agents — none of which the harness addresses"
  - id: q2
    text: "Which observability pillar is best for answering 'why is this trace slow'?"
    options:
      - "Logs — discrete events with timestamps tell you exactly when each step happened"
      - "Metrics — aggregated time-series data is what makes latency comparisons possible"
      - "Traces in the timeline view — the flame-graph rendering shows wall-clock duration per Run, surfacing the slow spans visually"
      - "Traces in the messages view — the chat-like rendering surfaces the supervisor's routing decisions"
    answer: "Traces in the timeline view — the flame-graph rendering shows wall-clock duration per Run, surfacing the slow spans visually"
  - id: q3
    text: "What does the OpenTelemetry GenAI semantic conventions standard provide that platform-native instrumentation does not?"
    options:
      - "Lower per-span overhead — OTel is faster than platform SDKs"
      - "Vendor-neutral attribute names (`gen_ai.system`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, etc.) so the same instrumentation works across LangSmith, Phoenix, Langfuse, Datadog, and others without rewriting"
      - "Automatic dashboard generation across all backends"
      - "Built-in LLM-as-judge evaluators"
    answer: "Vendor-neutral attribute names (`gen_ai.system`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, etc.) so the same instrumentation works across LangSmith, Phoenix, Langfuse, Datadog, and others without rewriting"
  - id: q4
    text: "You have a LangGraph supervisor agent. You set LANGSMITH_TRACING=true and LANGSMITH_API_KEY. You also have a custom Python helper function `preprocess_text(...)` that runs before the graph. Which of the following will be visible in the LangSmith UI?"
    options:
      - "Only the graph's nodes (LangChain/LangGraph auto-trace) — `preprocess_text` won't appear unless you add the `@traceable` decorator"
      - "The graph's nodes AND `preprocess_text` — env vars alone auto-trace everything in the process"
      - "Only `preprocess_text` because graph nodes need explicit instrumentation"
      - "Neither, because tracing requires the `tracing_v2_enabled` context manager"
    answer: "Only the graph's nodes (LangChain/LangGraph auto-trace) — `preprocess_text` won't appear unless you add the `@traceable` decorator"
  - id: q5
    text: "When does `agentevals.trajectory.match` (deterministic) make more sense than `agentevals.trajectory.llm` (LLM-judged)?"
    options:
      - "When you don't have an expected trajectory but want to evaluate appropriateness — deterministic match doesn't require a reference"
      - "When the workflow is well-defined and you can enumerate the expected tool-call sequence; deterministic match is fast, free per call, and CI-friendly"
      - "When the trajectory varies stochastically and you need nuance"
      - "Always — LLM-as-judge is too biased to be useful"
    answer: "When the workflow is well-defined and you can enumerate the expected tool-call sequence; deterministic match is fast, free per call, and CI-friendly"
  - id: q6
    text: "What does `extract_langgraph_trajectory_from_thread(graph, config)` require to work correctly?"
    options:
      - "The graph must be compiled with a checkpointer (e.g., `InMemorySaver`); the function reads the saved state to reconstruct the trajectory"
      - "The graph must use the `Send` primitive for parallel dispatch"
      - "The graph must run inside a `tracing_v2_enabled` context manager"
      - "Nothing — it works on any compiled graph regardless of checkpointer"
    answer: "The graph must be compiled with a checkpointer (e.g., `InMemorySaver`); the function reads the saved state to reconstruct the trajectory"
  - id: q7
    text: "What does the annotation-queue workflow close that neither offline nor online evaluation alone closes?"
    options:
      - "It eliminates the need for human reviewers entirely"
      - "It closes the production → fixture-set loop: low-scoring online traces get routed to human annotators, labeled, and added to the offline Dataset; the next CI run catches the regression deterministically. Without it, the offline fixture set goes stale as production surfaces new failure modes."
      - "It replaces the LLM-as-judge evaluators with rule-based ones"
      - "It automatically generates new fixture sets without human input"
    answer: "It closes the production → fixture-set loop: low-scoring online traces get routed to human annotators, labeled, and added to the offline Dataset; the next CI run catches the regression deterministically. Without it, the offline fixture set goes stale as production surfaces new failure modes."
  - id: q8
    text: "Lab 16's `routing_accuracy` (LCS-based) and `agentevals.graph_trajectory.strict_match` both score routing. What's the practical relationship?"
    options:
      - "They're identical implementations of the same algorithm"
      - "`agentevals` is always preferable to the from-scratch metric"
      - "Same problem, different wiring: Lab 16's algorithm is portable and can be wrapped as a custom `agentevals` evaluator (`def evaluator(outputs, reference_outputs, **kwargs) -> dict`). Strict_match uses exact sequence equality, while LCS-based scoring is more forgiving on extra steps. Pick based on what 'correct routing' means for your agent."
      - "The from-scratch metric is for development; agentevals is for production — never mix them"
    answer: "Same problem, different wiring: Lab 16's algorithm is portable and can be wrapped as a custom `agentevals` evaluator (`def evaluator(outputs, reference_outputs, **kwargs) -> dict`). Strict_match uses exact sequence equality, while LCS-based scoring is more forgiving on extra steps. Pick based on what 'correct routing' means for your agent."
---

# LangSmith trace ingestion · 🧠 Check your understanding

Calibrate against the [LangSmith tracing shape](../../concepts/evaluation/langsmith-tracing-shape.md) and [online vs offline evaluation](../../concepts/evaluation/online-vs-offline-evaluation.md) concept pages plus [Lab 17](../../labs/17-langsmith-trace-ingestion/). 8 single-select questions covering Module 1 framing + Module 2 LangSmith specifics. Passing: 6/8.

---

**1.** Why is production observability a categorically different problem from the from-scratch evaluation harness (Lab 09 / Lab 16) — not just "scale it up"?

- (a) Because production needs more metrics than the harness implements
- (b) Because the harness reads from a fixture file but production needs live trace ingestion, distribution drift detection over time, and distributed-tracing correlation across parallel sub-agents — none of which the harness addresses
- (c) Because production uses different LLM providers than the harness
- (d) Because production datasets must be larger than 30 fixtures

<details>
<summary>Answer</summary>

**(b)** — The three production needs are infrastructural, not algorithmic. The from-scratch harness handles the metric computation cleanly; the production layer adds (1) live trace ingestion at scale (the JSONL file shape doesn't scale), (2) distribution drift detection over time (the harness produces one number per run; production needs historical state), (3) distributed-tracing correlation across parallel sub-agents (the harness traces are single-process; production multi-agent is multi-process). Same metric algorithms; different infrastructure.

See: [from-harness-to-production.md → "Three things production needs"](../../concepts/evaluation/from-harness-to-production.md#three-things-production-needs-that-the-harness-doesnt-provide).
</details>

---

**2.** Which observability pillar is best for answering "why is this trace slow"?

- (a) Logs — discrete events with timestamps tell you exactly when each step happened
- (b) Metrics — aggregated time-series data is what makes latency comparisons possible
- (c) Traces in the timeline view — the flame-graph rendering shows wall-clock duration per Run, surfacing the slow spans visually
- (d) Traces in the messages view — the chat-like rendering surfaces the supervisor's routing decisions

<details>
<summary>Answer</summary>

**(c)** — Traces in the timeline view are the right tool for latency. The flame-graph rendering shows each Run's wall-clock duration as a horizontal bar with nested children below; one slow span dominates the visual. Metrics surface aggregate trends ("p99 latency has climbed"); logs help when the trace-level structure isn't sufficient ("what was the underlying timeout?"). For a single slow trace, the timeline view is the fastest path to the culprit.

See: [observability-three-pillars.md → "The two views in the UI"](../../concepts/evaluation/observability-three-pillars.md#what-an-agent-trace-looks-like).
</details>

---

**3.** What does the OpenTelemetry GenAI semantic conventions standard provide that platform-native instrumentation does not?

- (a) Lower per-span overhead — OTel is faster than platform SDKs
- (b) Vendor-neutral attribute names (`gen_ai.system`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, etc.) so the same instrumentation works across LangSmith, Phoenix, Langfuse, Datadog, and others without rewriting
- (c) Automatic dashboard generation across all backends
- (d) Built-in LLM-as-judge evaluators

<details>
<summary>Answer</summary>

**(b)** — The OTel GenAI semantic conventions are a portable schema. Instrumenting once with these attributes makes the trace ingestible by any OTel-compatible backend without re-instrumentation. The trade-off: per-LangChain's docs, OTel has slightly higher per-span overhead than the platform-native SDK, and the platform-specific UI affordances (agent-conversation rendering, eval registration) may need adaptation. Pick by lock-in tolerance and ecosystem fit.

See: [observability-three-pillars.md → "OTel-native vs platform-native"](../../concepts/evaluation/observability-three-pillars.md#otel-native-vs-platform-native--what-trades).
</details>

---

**4.** You have a LangGraph supervisor agent. You set LANGSMITH_TRACING=true and LANGSMITH_API_KEY. You also have a custom Python helper function `preprocess_text(...)` that runs before the graph. Which of the following will be visible in the LangSmith UI?

- (a) Only the graph's nodes (LangChain/LangGraph auto-trace) — `preprocess_text` won't appear unless you add the `@traceable` decorator
- (b) The graph's nodes AND `preprocess_text` — env vars alone auto-trace everything in the process
- (c) Only `preprocess_text` because graph nodes need explicit instrumentation
- (d) Neither, because tracing requires the `tracing_v2_enabled` context manager

<details>
<summary>Answer</summary>

**(a)** — Auto-tracing only captures LangChain/LangGraph primitives. Plain Python functions are invisible until you decorate them with `@traceable`. The pattern: rely on auto-tracing for the graph itself; `@traceable` the helpers, preprocessors, and post-processors that contribute to the trace's value but aren't graph nodes. `@traceable` is a no-op without the env vars, but the env vars alone don't make plain Python visible.

See: [langsmith-tracing-shape.md → "Three tracing methods"](../../concepts/evaluation/langsmith-tracing-shape.md#three-tracing-methods-ranked-by-automation).
</details>

---

**5.** When does `agentevals.trajectory.match` (deterministic) make more sense than `agentevals.trajectory.llm` (LLM-judged)?

- (a) When you don't have an expected trajectory but want to evaluate appropriateness — deterministic match doesn't require a reference
- (b) When the workflow is well-defined and you can enumerate the expected tool-call sequence; deterministic match is fast, free per call, and CI-friendly
- (c) When the trajectory varies stochastically and you need nuance
- (d) Always — LLM-as-judge is too biased to be useful

<details>
<summary>Answer</summary>

**(b)** — Deterministic `trajectory.match` requires an expected trajectory (you can enumerate the right tool sequence). It's the right tool for well-defined workflows: cheap, fast, no LLM call, CI-friendly because deterministic. `trajectory.llm` is for cases where you can't enumerate every valid trajectory but you know what "good" looks like; flexible at the cost of LLM call + non-determinism + the Zheng et al. biases. The two are complementary, not competitive.

See: [online-vs-offline-evaluation.md → "The agentevals package"](../../concepts/evaluation/online-vs-offline-evaluation.md#the-agentevals-package-one-evaluator-format-two-modes).
</details>

---

**6.** What does `extract_langgraph_trajectory_from_thread(graph, config)` require to work correctly?

- (a) The graph must be compiled with a checkpointer (e.g., `InMemorySaver`); the function reads the saved state to reconstruct the trajectory
- (b) The graph must use the `Send` primitive for parallel dispatch
- (c) The graph must run inside a `tracing_v2_enabled` context manager
- (d) Nothing — it works on any compiled graph regardless of checkpointer

<details>
<summary>Answer</summary>

**(a)** — The function reads the graph's saved state (via the checkpointer) to reconstruct the trajectory. Without a checkpointer, there's no saved state to read; the function returns empty. Lab 17 uses `InMemorySaver` throughout. Production deployments use `SqliteSaver` or `PostgresSaver` for persistence.

See: [Lab 17 step 7](../../labs/17-langsmith-trace-ingestion/), [online-vs-offline-evaluation.md → "agentevals.graph_trajectory"](../../concepts/evaluation/online-vs-offline-evaluation.md#agentevalsgraph_trajectory--langgraph-specific-node-trajectory).
</details>

---

**7.** What does the annotation-queue workflow close that neither offline nor online evaluation alone closes?

- (a) It eliminates the need for human reviewers entirely
- (b) It closes the production → fixture-set loop: low-scoring online traces get routed to human annotators, labeled, and added to the offline Dataset; the next CI run catches the regression deterministically. Without it, the offline fixture set goes stale as production surfaces new failure modes.
- (c) It replaces the LLM-as-judge evaluators with rule-based ones
- (d) It automatically generates new fixture sets without human input

<details>
<summary>Answer</summary>

**(b)** — The annotation queue is the bridge between online evaluation (which surfaces new failure modes from real traffic) and offline evaluation (which gates CI deterministically). Without it, offline fixture sets stay frozen at curation time while production surfaces failure modes the curator didn't anticipate. With it, the loop closes: online flags low-score traces → humans annotate → annotations become Dataset entries → CI catches the regression on the next run. Required for offline gates to stay sharp at production scale.

See: [online-vs-offline-evaluation.md → "Annotation queues"](../../concepts/evaluation/online-vs-offline-evaluation.md#annotation-queues--the-bootstrap-loop).
</details>

---

**8.** Lab 16's `routing_accuracy` (LCS-based) and `agentevals.graph_trajectory.strict_match` both score routing. What's the practical relationship?

- (a) They're identical implementations of the same algorithm
- (b) `agentevals` is always preferable to the from-scratch metric
- (c) Same problem, different wiring: Lab 16's algorithm is portable and can be wrapped as a custom `agentevals` evaluator (`def evaluator(outputs, reference_outputs, **kwargs) -> dict`). Strict_match uses exact sequence equality, while LCS-based scoring is more forgiving on extra steps. Pick based on what "correct routing" means for your agent.
- (d) The from-scratch metric is for development; agentevals is for production — never mix them

<details>
<summary>Answer</summary>

**(c)** — Same problem (does the trajectory match the expected sequence), different scoring discipline. `strict_match` is binary equality; LCS-based scoring is fractional with partial credit for matching subsequences. Pick by what "correct routing" means for your case: zero tolerance for deviation → strict; some tolerance for extra supervisor visits → LCS. The from-scratch algorithm wraps into the `agentevals` evaluator signature with minor adaptation; the bridge is straightforward.

See: [Lab 17 step 11](../../labs/17-langsmith-trace-ingestion/), [online-vs-offline-evaluation.md → "From-scratch metrics vs agentevals"](../../concepts/evaluation/online-vs-offline-evaluation.md#from-scratch-metrics-vs-agentevals).
</details>

---

✓ **Module 2 complete after this quiz.** Path 06 Modules 3-7 in future batches.
