# Lab 17 · Reference solution

The polished final implementation of [Lab 17: LangSmith trace ingestion](../README.md).

## What this is

A LangSmith-instrumented Lab 14-style supervisor agent + the `agentevals` evaluator package + an end-to-end offline experiment run via `client.evaluate`. Demonstrates the LangSmith-native instrumentation path that pairs naturally with LangChain/LangGraph applications.

- **Inline supervisor agent** (~30 LOC) — a minimal Lab 14 variant; planner → researcher → writer → end.
- **`@traceable` decorator** on the agent runner — every call lands as a LangSmith run.
- **Tags + metadata** on the runs (model, temperature, task type) for downstream filtering.
- **`tracing_v2_enabled` context manager** for project scoping (CI traces in a separate project from dev traces).
- **`extract_langgraph_trajectory_from_thread`** → trajectory extraction from LangSmith runs.
- **`graph_trajectory_strict_match`** + **`create_trajectory_llm_as_judge`** → two evaluator flavors (deterministic vs LLM-judged).
- **`client.evaluate`** → offline experiment run that ties the three together.
- **Custom evaluator** (Lab 16's `routing_accuracy_lcs`) demonstrating that any callable that returns a score can be a LangSmith evaluator.

## How it differs from `../lab.ipynb`

| Lab notebook (33 cells) | Solution (33 cells) |
|---|---|
| Tutorial framing under every `## Step N` header | One-line headers; the explanation lives in the concept page |
| "Watch for" callouts in markdown cells | Removed (those belong in the lab) |
| Sanity-test cells demonstrating each evaluator works | Combined into the offline-experiment call site |
| Build the agent piece by piece (imports, then planner, then graph) | Single composed setup cell |

The cell count matches the lab because each step still gets a one-line header — the condensation is in the explanatory paragraphs, not in the step structure.

## Implementation choices

1. **`@traceable` for the application surface; `RunTree` only where you need explicit tree manipulation.** The decorator is the right default — it captures inputs/outputs/timing automatically. `RunTree` is for cases where you're constructing the trace manually (e.g., wrapping a non-Python service). The supervisor agent uses `@traceable`; the lab references `RunTree` for completeness without using it.
2. **`agentevals` for ready-made evaluators rather than hand-rolling.** The `graph_trajectory_strict_match` and `create_trajectory_llm_as_judge` evaluators handle the LangSmith-run-to-trajectory extraction implicitly. Hand-rolling these is a Lab 16 exercise; Lab 17 is about wiring them up.
3. **Sync evaluators over async for clarity.** The async story is straightforward (`aevaluate` instead of `evaluate`) but adds cognitive load without changing the patterns. Production deployments often use async for throughput; the lab uses sync for pedagogy.
4. **Project scoping via `tracing_v2_enabled` is the lever that makes CI and dev coexist.** Without it, CI runs pollute the dev project. The pattern: `with tracing_v2_enabled(project_name="path-06-lab-17-ci"): ...`.
5. **Custom evaluator from Lab 16 demonstrates the integration pattern.** Any function with signature `(run, example) -> {"key": str, "score": float}` is a valid LangSmith evaluator. The Lab 16 routing-accuracy code drops in unchanged.

## What's deliberately out of scope

- **Production-grade LangSmith project hygiene** (tag taxonomies, run retention policies, evaluator versioning). Mentioned in concept pages; out of scope for the lab.
- **`aevaluate` for large eval sets.** The lab uses 4 examples; production teams running 1000+ examples switch to async. Same API surface.
- **Streaming traces / partial runs.** The lab assumes runs complete before evaluators score them.
- **The LangSmith REST API.** The Python SDK is sufficient for everything in the lab.
- **Cost-aware sampling on the LangSmith side.** That's Module 6 territory (cost attribution) and Module 4 territory (tail sampling at the Collector).

## Running the solution

```bash
cd labs/17-langsmith-trace-ingestion/solution

# Required environment variables
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=...    # from smith.langchain.com
export OPENAI_API_KEY=...        # for the supervisor agent's LLM calls

jupyter notebook lab.ipynb
```

**Wall-clock**: ~3-5 minutes including the agent runs and the offline experiment. Most time is LLM latency, not evaluator overhead.

**Cost**: ~$0.05-0.10 at gpt-4o-mini rates for the supervisor agent + the LLM-judge trajectory evaluator. The judge evaluator can be skipped (commented out in Step 9) to drop cost to ~$0.02.

## Next

- Take the [LangSmith ingestion quiz](../../../quizzes/evaluation/langsmith-ingestion.md).
- Lab 18 implements the same agent with the OpenTelemetry-portable variant — read the two solutions side-by-side to see the vendor-native vs vendor-neutral trade-off.
