# Concepts

Short, focused explainers — *what something is and when to use it*. Average reading time per page is around 10 minutes. Concept pages are the most stable content in the repo: they're written to outlive any specific framework version.

## What lives here

A page in `concepts/` answers one question well, with no tool-specific syntax. If you need code, look in [`labs/`](../labs/) (guided exercises), [`recipes/`](../recipes/) (copy-paste solutions), or [`examples/`](../examples/) (minimal reference implementations).

Concept pages are organized into subfolders by topic area:

| Subfolder | Topic area |
|---|---|
| `agents/` | The agent loop, ReAct, plan-and-execute, reflection |
| `llms/` | Autoregressive generation, sampling, structured outputs, function calling |
| `rag/` | Retrieval-augmented generation, chunking, hybrid search, agentic RAG |
| `tools/` | Tool design, tool selection, parallel tool calls |
| `multi-agent/` | Supervisor, hierarchical, swarm topologies |
| `protocols/` | MCP, A2A, comparison |
| `context/` | Context budget, compression, selection strategies |
| `memory/` | Short-term, long-term, retrieval memory |
| `evaluation/` | Eval fundamentals, LLM-as-judge, RAG eval |
| `safety/` | Prompt injection, tool abuse, guardrails |

## How concept pages are structured

Every page follows the same template — TL;DR, the problem it solves, how it works, when to use / when NOT to use, failure modes, see-also, references. Full template is in [`CONTRIBUTING.md`](../CONTRIBUTING.md#how-to-add-a-concept-page).

## Cross-links

- Each concept links to related [`labs/`](../labs/) for hands-on practice.
- Where useful, each concept has a *"🧮 Math behind it"* callout linking to [`math-foundations/`](../math-foundations/).
- Architectural concepts link to corresponding [`patterns/`](../patterns/) for the decision-making view.

## Contributing

See [`CONTRIBUTING.md`](../CONTRIBUTING.md#how-to-add-a-concept-page). Concept pages are a good first contribution if you want to write about an idea you understand well.

> 🟢 Content in this folder is classified **stable** — the underlying ideas change on a scale of years, not months.
