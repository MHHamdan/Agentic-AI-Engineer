# Lab 02: Tool design and selection

> 🟢 Beginner-friendly · ⏱ ~90–120 min · 📊 Beginner

## 🎯 Goal

Take Lab 01's working ReAct agent and **deliberately give it bad tools** — vague descriptions, overlapping intents, loose schemas, noisy returns. Watch it fail in characteristic ways. Then fix the tools, *one design problem at a time*, and watch the same agent (unchanged code) become reliable.

This is the most direct way to internalize tool design: build a broken toolset, see what breaks, then see what the fix changes.

## 📋 Prerequisites

**Concepts to read first:**

- 📖 [What is an agent?](../../concepts/agents/what-is-an-agent.md), [Agent loop](../../concepts/agents/agent-loop.md), [ReAct pattern](../../concepts/agents/react-pattern.md)
- 📖 [Tool design](../../concepts/tools/tool-design.md) — the design principles this lab applies
- 📖 [Tool selection](../../concepts/tools/tool-selection.md) — the failure modes this lab triggers

**Setup:**

- Same as Lab 01 — Python 3.11+, an OpenAI or Anthropic API key, `uv sync` already run.
- Lab 01 completed (the agent loop and `chat_with_tools` wrapper from Lab 01 are reused here).

**Skills assumed:**

- Comfortable with Lab 01's agent loop and tool schemas.
- Comfortable with Pydantic models (we use a few patterns Lab 01 didn't).

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `openai` | ≥ 1.40 | 2026-05-23 |
| `anthropic` | ≥ 0.34 | 2026-05-23 |
| `pydantic` | ≥ 2.7 | 2026-05-23 |

Same as Lab 01.

## What you'll build

A small mock e-commerce system the agent interacts with: customers, orders, and inventory. The system has **two versions of the tool set**:

- **`tools_v0` — the broken set.** Overlapping intents, vague descriptions, loose types, and one tool with a destructive side effect that's poorly gated.
- **`tools_v1` — the improved set.** Same capabilities, redesigned: per-intent tools, tight types, structured errors, explicit negative guidance, side-effect confirmation.

Then you'll **run the same agent against the same queries** with each toolset and observe the difference. The agent code doesn't change. The tools do.

## What you'll learn

By the end of this lab you will be able to:

- Identify and fix each of the five common tool-design failure modes from the concept pages.
- Choose between split-per-intent and combined-mode tools using a clear heuristic.
- Use Pydantic `Literal`, `Annotated`, and `Field` to express the right schema constraints.
- Distinguish "not found", "error", and "empty" in return contracts.
- Use `tool_choice` (`auto` / `required` / `none` / named) and `parallel_tool_calls` to control selection.
- Recognize a tool-selection issue (model picks the wrong tool, or invents one) from a trace.

## Steps

The notebook walks through these in order:

**0. Setup** — same imports/wrapper as Lab 01. Briefly reuse the Lab 01 loop.

**1. Build the bad toolset (`tools_v0`).** Three tools with deliberately overlapping descriptions, loose schemas, and noisy returns. Run the agent on a small set of test queries and watch the failures.

**2. Diagnose.** For each failure, identify which of the five failure modes from [`tool-selection.md`](../../concepts/tools/tool-selection.md) is in play.

**3. Fix the tool names and descriptions.** Tightest single intervention — improves selection without changing capability.

**4. Fix the schemas.** Add `Literal`, mark fields appropriately, enable strict mode.

**5. Fix the return contracts.** Distinguish error types; compress noisy returns; return handles instead of raw payloads.

**6. Add a destructive-action gate.** The "cancel order" tool needs explicit confirmation.

**7. Run the test queries against `tools_v1`.** Same agent code, fixed tools. Compare outcomes.

**8. Explore `tool_choice` and `parallel_tool_calls`.** Force one tool, force a final answer, run two lookups in parallel.

**9. (Stretch) Add a router.** When the toolset grows beyond ~10 tools, pruning helps. Build a tiny router step that exposes only the relevant subset.

## Stretch goals

- Add a fourth domain (returns, refunds) to push the toolset past 10 tools. Observe what happens to selection. Add a router to fix it.
- Implement embedding-based tool retrieval: embed each tool description, embed the user request, expose only the top-K tools per step.
- Add a tool whose result *changes the available toolset* (the discovery pattern — calling `list_capabilities()` reveals what else can be done).
- Write a small evaluation harness that runs the agent on N queries against each toolset and reports success rates. This is the first lab where evaluation becomes interesting — we go deep on it in Path 06.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) (added in a follow-up batch). The two design choices to flag in the solution:

- **The "broken" toolset isn't pathological** — it looks like real code many engineers ship. The failures it causes are realistic, not contrived.
- **The "fixed" toolset doesn't add capabilities** — it implements the same operations. The only change is design quality. This is intentional. The point is that *design alone* moves agent reliability by a large margin.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — tool design changes the action space $\mathcal{A}$; selection is a distribution over it.
- 🧮 [ReAct formalization](../../math-foundations/06-react-formalization.md) — how the thought-action split helps with selection too.

## Common gotchas

- **Strict mode and optional fields.** OpenAI's strict mode requires *all* properties to be in `required`. Optional fields are expressed by allowing `null` as a type, not by being absent from `required`. Pydantic does this correctly with `field: int | None = None`.
- **Tool descriptions are part of the prompt budget.** Long descriptions cost tokens. Aim for the *shortest description that's still complete*, not the most thorough one.
- **Negative guidance only helps when there's a real choice.** "Do not use this for X" is wasted text if no tool can do X. Add negatives only when you have actually-overlapping tools.
- **Parallel tool calls have order assumptions.** When the model emits multiple calls in one response, they're often logically parallel. But your code may not handle them concurrently. Test with `parallel_tool_calls=true` *and* `false` and confirm both work.
- **The repeated-action guard from Lab 01 still belongs here.** Don't drop it. With more tools, the chance of the agent looping on a confusingly-failing tool goes *up*, not down.

## ✅ Check your understanding

After finishing, take the quiz:

- 🧠 [`quizzes/foundations/tool-design-and-selection.md`](../../quizzes/foundations/tool-design-and-selection.md)

If you score below 6/8, revisit the concept pages — the questions map directly to specific sections.

## What comes next

- **Lab 03** (forthcoming) — A multi-step research agent that uses the toolset you just designed, with a real search backend.
- **Lab 05** (forthcoming) — Rewrite Lab 01's agent in **LangGraph**. You'll see what the framework adds (durable state, conditional edges, checkpointing) and what stays the same.
- **The Agentic RAG path** — the obvious next domain. A retrieval tool is just another tool, with extra design considerations.
