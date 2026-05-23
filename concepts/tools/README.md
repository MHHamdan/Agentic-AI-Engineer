# 📖 Concepts · Tools

> 🟢 Stable concepts about how tools work in LLM agents.

Tools are how an agent acts on the world. Designing them well is one of the highest-leverage things you can do for agent reliability — and getting them wrong is one of the most common reasons agents misbehave in production.

This section is paired: **design first, then selection**. Design is about making each tool legible to the model; selection is about helping the model pick correctly when several tools coexist.

## Pages in this section

| Page | What it covers | When to read |
|---|---|---|
| 📖 [Tool design](./tool-design.md) | Name, description, schema, return contract, executor. Patterns and common mistakes. | Before building any tool-using agent. |
| 📖 [Tool selection](./tool-selection.md) | How the model picks among tools; the four levers (prompt, descriptions, history, `tool_choice`); failure taxonomy; pruning strategies. | After your first agent has 3+ tools and starts picking wrong. |

## Hands-on

- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) — implement the patterns above, watch a deliberately-broken toolset fail, fix it step by step.

## Quizzes

- 🧠 [`quizzes/foundations/tool-design-and-selection.md`](../../quizzes/foundations/tool-design-and-selection.md) — 8 questions on the material in this section.

## Related

- 📖 [`concepts/agents/`](../agents/) — the broader agent context tools sit inside.
- 🏛 [`patterns/01-single-agent-tool-use.md`](../../patterns/01-single-agent-tool-use.md) — the architectural perspective.
- 🧮 [`math-foundations/04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md) — the action-space framing.

## Forthcoming pages in this section

- *Tool composition* — combining tools into pipelines, fan-out/fan-in patterns.
- *Tool versioning* — handling schema evolution without breaking running agents.
- *Tool security* — sandboxing, capability scoping, side-effect gates.

Open a [Discussion](https://github.com/MHHamdan/Agentic-AI-Engineer/discussions) if you want to claim one of these.
