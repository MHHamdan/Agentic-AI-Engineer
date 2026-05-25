# Online vs offline evaluation

> ⏱ ~10 min · 🔴 Advanced · Prerequisites: [LangSmith tracing shape](./langsmith-tracing-shape.md) (the underlying instrumentation layer), [from harness to production](./from-harness-to-production.md) (the framing).

Once traces are flowing into a production observability platform, you have two ways to evaluate them: **offline** (replay against a fixture set, like Lab 09 and Lab 16) and **online** (run evaluators on live trace stream as production traffic flows through). They answer different questions and they coexist in mature stacks.

This page covers the distinction, why neither alone is sufficient, and how the LangChain `agentevals` package provides a unified evaluator format that runs in both modes. By the end you should be able to decide which mode answers a given question and how to wire each one against your traces.

## The two modes side-by-side

| | Offline (replay) | Online (live stream) |
|---|---|---|
| What it evaluates | A fixed fixture set (`trace_set.jsonl`, `eval_set.jsonl`) | Whatever the production system actually saw |
| When evaluators run | At build time, or in CI | Continuously, as traces are ingested |
| Determinism | Yes — same inputs, same scores every time | No — distribution shifts as traffic changes |
| Cost per run | Bounded by fixture-set size | Scales with traffic; tail-based sampling helps |
| Answers questions like | "Did my change regress on the 30 cases we curate against?" | "Has the citation rate drifted in production over the last 7 days?" |
| Catches | Regressions on known failure modes | New failure modes the fixture didn't anticipate |
| Doesn't catch | Behavior on traffic patterns you didn't curate | Slow degradations buried in aggregate metrics |

The from-scratch harness from Lab 09 and Lab 16 is the offline path. Production observability platforms (LangSmith / Phoenix / Langfuse / Braintrust / Laminar) are where online evaluation lives.

## Why both matter

Offline alone misses real failures. Your fixture set encodes the failure modes you knew about when you curated it. Production users find failure modes you didn't think of — a new tool returns a malformed response, users phrase queries in a way that breaks routing, an external API changes its rate-limit headers. None of these appear in your 30 hand-curated traces. Offline tells you "you didn't regress on the known cases"; it doesn't tell you "users are unhappy in a new way."

Online alone misses the discipline of regression testing. Live traffic isn't reproducible. The same user query at 9am might route differently from the same query at 2pm because the LLM's stochastic output landed on a different tool choice. Online evaluation can tell you "metric X is trending down"; it can't tell you "this PR caused that trend" with the same confidence a deterministic regression test gives.

The pattern that works in production: **offline as the gate, online as the signal**.
- Offline (from-scratch harness or platform-evaluated Dataset) is the gate: it runs in CI; below threshold blocks merge.
- Online evaluation is the signal: it runs continuously; drift triggers an alert; the team investigates; the new failure mode (once understood) gets added to the offline fixture set.

The flow is closed-loop: production surfaces a failure → annotation queue routes it to a human → the human labels it → it joins the fixture set → next iteration's CI catches the regression deterministically.

## The agentevals package: one evaluator format, two modes

LangChain's `agentevals` package provides evaluators that work in both modes. Same evaluator function; offline runs it against a Dataset, online runs it against a live trace stream.

The package has three evaluator families:

### `agentevals.trajectory.match` — deterministic trajectory comparison

Compares an actual trajectory against an expected one, message by message.

```python
from agentevals.trajectory.match import create_trajectory_match_evaluator

evaluator = create_trajectory_match_evaluator(
    trajectory_match_mode="strict",   # or "unordered", "subset", "superset"
)
```

The mode controls what counts as a match:
- **strict**: exact message sequence; both tool calls and args must match in order.
- **unordered**: same set of tool calls, any order.
- **subset**: actual trajectory must be a subset of expected (every actual step appears in expected).
- **superset**: actual trajectory must be a superset of expected (every expected step appears in actual).

`strict` is what you want for well-defined workflows (Lab 14's supervisor → researcher → writer; deviations are bugs). `unordered` is for plan-and-execute when execution order isn't deterministic but step set is fixed. `subset` is for cases where the agent might do extra work; `superset` is for cases where it must do at least these steps.

The evaluator is **fast and cheap** — no LLM call. Returns a `{score, comment}` dict per evaluation. Good for the offline gate.

### `agentevals.trajectory.llm` — LLM-judged trajectory quality

For when you can't enumerate the expected trajectory but you know what "good" looks like.

```python
from agentevals.trajectory.llm import (
    create_trajectory_llm_as_judge,
    TRAJECTORY_ACCURACY_PROMPT,
)

evaluator = create_trajectory_llm_as_judge(
    model="openai:o3-mini",
    prompt=TRAJECTORY_ACCURACY_PROMPT,
)
```

The default `TRAJECTORY_ACCURACY_PROMPT` asks an LLM to judge whether the agent's trajectory was appropriate for the user's request. You can pass a custom prompt to score on different criteria (efficiency, principled refusals, citation discipline).

The evaluator is **slow and expensive** relative to `trajectory.match` — each evaluation is an LLM call. Costs add up at production scale. Typical use: sample a percentage of online traces (5-10%) and run the LLM judge on the sample.

Subject to the Zheng et al. (2023) biases (position, verbosity, self-enhancement). Calibration against human ground truth is required for production use; this becomes a Module 5 topic.

### `agentevals.graph_trajectory` — LangGraph-specific node trajectory

For LangGraph users who think in node visits rather than message lists.

```python
from agentevals.graph_trajectory.utils import extract_langgraph_trajectory_from_thread
from agentevals.graph_trajectory.strict import graph_trajectory_strict_match

# After running your LangGraph agent with a checkpointer:
trajectory = extract_langgraph_trajectory_from_thread(
    graph=my_graph,
    config={"configurable": {"thread_id": "..."}},
)

result = graph_trajectory_strict_match(
    outputs=trajectory,
    reference_outputs=expected_trajectory,
)
```

The `GraphTrajectory` shape:

```python
class GraphTrajectory(TypedDict):
    inputs: Optional[list[dict]]      # only when reference is provided
    results: list[dict]                # per-turn final state
    steps: list[list[str]]             # nodes visited per turn
```

`steps` is the sequence of node names — for Lab 14's pattern it'd be `[["supervisor", "researcher", "supervisor", "writer", "supervisor"]]`. `graph_trajectory_strict_match` compares this against an expected sequence. This is what `routing_accuracy` from Lab 16 looks like in the production-tooling layer.

## The trace shape `agentevals` expects

`agentevals` doesn't invent a new trace format. It accepts what LangChain produces natively:

**For `trajectory.match` and `trajectory.llm`**:
- A list of OpenAI-format message dicts: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "...", "tool_calls": [...]}, {"role": "tool", "content": "...", "tool_call_id": "..."}]`
- OR a list of LangChain `BaseMessage` instances (`HumanMessage`, `AIMessage`, `ToolMessage`)

**For `graph_trajectory`**:
- The `GraphTrajectory` TypedDict (`inputs`, `results`, `steps`)

The trace-extraction utilities convert from your agent's runtime format. For a LangGraph agent with a checkpointer, `extract_langgraph_trajectory_from_thread` walks the checkpointer's saved state and produces the `GraphTrajectory` shape automatically.

For a Lab 16-style trace (custom from-scratch agents), you'd convert your `Trace.trajectory` list to OpenAI message format before passing it to `agentevals`. The conversion is mechanical; the metric logic carries over.

## Wiring agentevals offline

The pattern for offline evaluation is `client.evaluate(target, data, evaluators)`:

```python
from langsmith import Client
from agentevals.trajectory.match import create_trajectory_match_evaluator

client = Client()

evaluator = create_trajectory_match_evaluator(trajectory_match_mode="strict")

results = client.evaluate(
    lambda inputs: my_agent.invoke(inputs),
    data="my-dataset-name",     # LangSmith Dataset by name
    evaluators=[evaluator],
)
```

The Dataset is a versioned collection of input/output examples stored in LangSmith. Schema:

```python
input:  {"messages": [...]}             # what to call the agent with
output: {"messages": [...]}              # the expected message history
```

For trajectory evaluation, the `output.messages` can be just the assistant messages (the trajectory steps) rather than the full conversation.

This is what `agentevals` calls "experiment-based" evaluation. Run an experiment; compare results across runs. CI-friendly. Equivalent to Lab 09 / Lab 16's harness pattern, with LangSmith managing the storage and the dashboard layer.

## Wiring agentevals online

The pattern for online evaluation is **registering the evaluator with the project** so it fires automatically on every ingested trace:

```python
# In the LangSmith UI: Project Settings → Online Evaluators → Add
# Pick the evaluator (your registered create_trajectory_match_evaluator instance)
# Pick the sampling rate (5-100%)
# Pick the threshold for alerts
```

This is configuration, not code, for the most common case. The platform stores the evaluator definition; every new trace gets scored asynchronously; results land on the trace itself; alerts fire when scores drop below threshold.

For custom evaluators not in `agentevals` — e.g., a Lab 16 `citation_preservation` function — you register them as a custom evaluator via the platform's API. The function signature matches:

```python
def my_evaluator(outputs, reference_outputs=None, **kwargs) -> dict:
    return {"key": "citation_preservation", "score": 0.95}
```

The platform stores this and runs it on every ingested trace.

## Annotation queues — the bootstrap loop

Datasets don't appear from nothing. The pattern that scales for building a production fixture set is the **annotation queue**:

1. Online evaluators score traces; some get low scores or flag for human review.
2. Flagged traces land in an annotation queue — a UI for domain experts to label.
3. The expert labels: "this trajectory should have gone supervisor → researcher → writer; it went supervisor → writer instead. Reason: missed retrieval signal."
4. The labeled example becomes a Dataset entry.
5. The Dataset is what offline evaluation runs against in CI.

The loop is what closes production → fixture → regression test. Without it, your fixture set goes stale; production keeps surfacing new failure modes; CI doesn't catch them until you manually add them.

## From-scratch metrics vs agentevals

Lab 16 implemented seven metrics from scratch. Three map onto `agentevals` directly:

- **Lab 16 `routing_accuracy` (LCS-based)** ↔ `graph_trajectory_strict_match` (strict) or `create_trajectory_match_evaluator(mode="unordered")` (loose).
- **Lab 16 `handoff_success_rate`** ↔ a custom evaluator over the trace's tool-call statuses (no direct agentevals match; ~20 lines).
- **Lab 16 `plan_validity` / `plan_coverage`** ↔ custom evaluators reading from state; not in agentevals.

Three are LLM-judged in both directions:

- **Lab 16 `groundedness` (rule-based)** ↔ rule-based custom evaluator + optionally `create_trajectory_llm_as_judge` with a groundedness prompt.
- **Lab 16 `citation_preservation`** ↔ custom evaluator (no direct agentevals match).

One is set-level:

- **Lab 16 `replan_rate`** ↔ aggregate over traces in the project (not per-trace; computed in dashboard).

The takeaway: `agentevals` covers the common-case trajectory match and trajectory-LLM-judge patterns out of the box. Lab 16's domain-specific metrics (citation preservation, plan validity) need to be reimplemented as custom evaluators. Same algorithm, different wiring.

## When the from-scratch harness still earns its place

Three cases where Lab 09 / Lab 16's offline harness remains the right tool even with production observability in place:

1. **CI gating.** The harness is deterministic, runs in seconds, requires no API keys (for the rule-based tier). A PR that drops `citation_preservation` from 0.81 to 0.65 should fail in CI, not in production. Platform-based offline evaluation works for this too, but the from-scratch harness has zero infrastructure dependency.
2. **Educational reference.** When someone joins the team, the from-scratch harness is what they read to understand *what the metrics mean*. The platform's UI is too abstracted; the function definitions are the explanation.
3. **Cross-platform portability.** If you switch from LangSmith to Phoenix to Langfuse, the from-scratch metrics carry over verbatim. The wiring changes; the algorithm doesn't.

Production observability and the from-scratch harness are not competitors. The from-scratch harness is what you start with and keep maintaining; the production platform is what you add when the system reaches scale where the harness alone can't answer the questions you have.

## Related concepts

- [LangSmith tracing shape](./langsmith-tracing-shape.md) — the instrumentation layer this page evaluates on top of.
- [Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/) — where these patterns are applied end-to-end.
- [Lab 16 — Multi-agent evaluation harness from scratch](../../labs/16-multi-agent-evaluation-from-scratch/) — the from-scratch baseline whose metrics map onto agentevals.
- [Trajectory-level metrics](../multi-agent/trajectory-level-metrics.md) — the seven metrics this page maps to agentevals equivalents.

## References

- LangChain `agentevals` repository — the package this page covers. `create_trajectory_match_evaluator`, `create_trajectory_llm_as_judge`, `graph_trajectory_strict_match`, `extract_langgraph_trajectory_from_thread`. [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- LangChain Docs, *How to evaluate your agent with trajectory evaluations* — the canonical agentevals usage guide. [docs.langchain.com/langsmith/trajectory-evals](https://docs.langchain.com/langsmith/trajectory-evals).
- LangChain Docs, *Evaluate performance* (LangGraph agents/evals) — the `client.evaluate(...)` Dataset pattern. [langchain-ai.lang.chat/langgraph/agents/evals](https://langchain-ai.lang.chat/langgraph/agents/evals/).
- LangChain blog (Feb 2025), *Quickly Start Evaluating LLMs With OpenEvals* — the agentevals + openevals split, the dataset-from-production-traces workflow. [blog.langchain.com](https://blog.langchain.com/evaluating-llms-with-openevals/).
- LangChain articles (April 2026), *LLM Evaluation Framework: Trajectories vs. Outputs* — the trace-to-dataset workflow, multi-turn online evaluators, annotation queues. [langchain.com/articles](https://www.langchain.com/articles/llm-evaluation-framework).
- Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — biases in `trajectory.llm` evaluators that motivate Module 5's calibration discussion. [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
