# Lab 01: First agent from scratch

> 🟢 Beginner-friendly · ⏱ ~60–90 min · 📊 Beginner

## 🎯 Goal

Build a working **ReAct-style agent** in pure Python — no LangGraph, no LangChain, no framework — so you can see every part of the agent loop with nothing hidden. By the end you'll have an agent that uses two tools to answer multi-step questions, with retry handling, structured errors, and a step cap.

## 📋 Prerequisites

**Concepts to read first:**

- 📖 [What is an agent?](../../concepts/agents/what-is-an-agent.md)
- 📖 [The agent loop](../../concepts/agents/agent-loop.md)
- 📖 [The ReAct pattern](../../concepts/agents/react-pattern.md)

**Setup:**

- Python 3.11+ ([setup guide](../../setup/README.md))
- An LLM provider API key:
  - **OpenAI** (default in this lab) — get one at <https://platform.openai.com/api-keys>
  - **Anthropic** (alternative, swap the provider in one place) — get one at <https://console.anthropic.com/settings/keys>
- Dependencies installed via `uv sync` or `pip install -r requirements.txt`

**Skills assumed:**

- You can read and write Python at intermediate level (type hints, dataclasses, dictionaries).
- You've called an LLM API before — even just a `chat.completions.create` once.
- No prior agent or framework experience required.

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `openai` | ≥ 1.40 | 2026-05-23 |
| `anthropic` | ≥ 0.34 | 2026-05-23 |
| `pydantic` | ≥ 2.7 | 2026-05-23 |

Source: pinned in [`pyproject.toml`](../../pyproject.toml).

## What you'll build

A single Python module (~150 lines) implementing a ReAct agent with:

1. A **provider-agnostic LLM wrapper** — same agent code works against OpenAI or Anthropic.
2. Two **tools**: a deterministic calculator and a mock web-search function (so you don't need a Tavily key for this lab).
3. A **typed action representation** built with Pydantic — no string parsing of the model's output.
4. A **loop** with explicit termination conditions: final answer, step cap, repeated-action detection.
5. **Structured error handling** so failed tool calls become observations the model can react to.
6. A short **test script** showing the agent solving a multi-step problem.

The agent will be able to answer questions like:

> *"What's 17% of the average of 234, 891, and 1502? And is that number greater than 100?"*

A pure LLM call without tools gets this wrong (LLMs are bad at multi-step arithmetic without a calculator). With the calculator tool, the agent decomposes the problem, calls the tool three or four times, and produces a correct grounded answer.

## What you'll learn

- The four parts of an agent loop and where each one lives in code.
- Why ReAct's thought-action interleaving improves reliability (you'll see the difference by toggling it off).
- How to design tools that the model can actually use — schema, descriptions, error handling.
- Why structured outputs matter and what happens without them.
- The minimum set of termination conditions a real agent needs.

You'll also see — concretely — what every framework you'll use later (LangGraph, ADK, CrewAI) is doing under the hood. Once you've written this lab, the frameworks become legible.

## Steps

The notebook walks through these in order:

**0. Setup** — environment, API key, provider selection.

**1. The bare minimum** — a one-shot LLM call. Confirm it gets the arithmetic question wrong.

**2. Define tools** — a `calculator` and a `web_search` (mocked). Use Pydantic models for arguments and structured returns.

**3. Wire up function calling** — let the model emit tool calls. See your first tool invocation succeed.

**4. Build the loop** — perceive → reason → act → observe, with a step cap. The agent should now solve the multi-step question correctly.

**5. Add the ReAct thoughts** — make the system prompt elicit explicit reasoning. Compare reliability against the no-thoughts baseline.

**6. Handle failures** — what happens when the tool raises? Convert exceptions to structured error observations.

**7. Add repeated-action detection** — protect against the agent calling the same failing tool in a loop.

**8. Run the full test scenarios** — verify the agent handles each case.

**9. (Stretch) Provider swap** — change the wrapper's backend from OpenAI to Anthropic and confirm everything still works.

## Stretch goals

If you finish early or want to push further:

- Add a third tool — date/time lookup, unit conversion, or a real web search via [Tavily](https://tavily.com/) if you have a key.
- Replace the mock web search with a real one and watch how observation length affects the loop.
- Implement parallel tool calls — modern APIs let one LLM response emit multiple tool calls at once. Execute them concurrently with `asyncio.gather`.
- Add a token-usage tracker. Print cumulative tokens after each step. This is the simplest possible cost observability — you'll build on it in the Evaluation & Observability path.

## Solution discussion

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) (added in a follow-up batch). The solution doesn't add anything dramatic over the in-notebook code — it just packages it cleanly as a single module you can copy into your own project.

The two design choices worth flagging in the solution:

- **The provider wrapper is a thin abstraction, not a framework.** It exposes one function: `chat(messages, tools, ...) → response`. We deliberately don't add abstractions for retries, streaming, or batching here — those belong in later labs and recipes.
- **The agent loop is iterative, not recursive.** Recursive implementations look elegant but make step-cap enforcement and state inspection harder. A `for` loop is the right shape.

## 🧮 Going deeper

The math behind what you build:

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — the loop in this lab implements $\pi_\theta(a_t \mid s_t)$ in code.
- 🧮 [ReAct formalization](../../math-foundations/06-react-formalization.md) — the thought-action split corresponds to a specific factorization of the policy.
- 🧮 [Notation reference](../../math-foundations/notation.md) — symbols used in the above.

## Common gotchas

- **API rate limits.** A debugging loop with `max_steps=8` runs eight LLM calls. Each rerun while debugging burns calls. Cache results during development; consider using OpenAI's cheapest model for the first pass.
- **Tool descriptions are part of the prompt.** Vague descriptions cause the model to mis-route. Treat them as code, not docs.
- **`tool_choice="auto"` is not always what you want.** For Step 1 (force a tool call), use `"required"`. For final-answer steps, use `"auto"` or `"none"`.
- **Don't strip `None` from tool arguments.** The model sometimes legitimately omits optional fields. Pass `None` through; let Pydantic apply defaults.

## What comes next

After this lab, you'll have all the vocabulary you need for:

- **Lab 02** — same loop, slightly different shape: deeper dive into tool design and selection.
- **Lab 05** — LangGraph rewrite of this exact agent. You'll see what the framework adds (state machines, checkpoints, human-in-the-loop) and what stays the same (the loop you just built).
- **The Agentic RAG path** — your `web_search` tool was a stub. Real retrieval is the next thing to make agents useful on knowledge work.
- **The Evaluation & Observability path** — you'll add tracing to this exact agent so you can debug failures systematically.
