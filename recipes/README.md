# Recipes

Copy-paste solutions to specific problems. A recipe is the answer when you searched for *"how do I make my LangGraph agent retry on tool timeout"* and you don't want to read a 10-minute concept page first.

Each recipe is a single Markdown file, named as an imperative: `add-retry-with-backoff.md`, `parse-structured-output-safely.md`, `deploy-agent-to-fastapi.md`.

## Format

Every recipe follows the same five-section template:

1. **Problem** — one or two sentences.
2. **Solution** — working code at the top of the file, copy-pasteable.
3. **Why this works** — three or four sentences of engineering intuition.
4. **Gotchas** — common pitfalls.
5. **See also** — links to relevant concepts, labs, and patterns.

Full template is in [`CONTRIBUTING.md`](../CONTRIBUTING.md#how-to-add-a-recipe).

## Recipe collections

Most recipes are single imperative-named files. Coherent multi-recipe series live in a subfolder:

| Collection | Covers |
|---|---|
| [`recipes/rag/`](./rag/) | Basic RAG, hybrid + reranked RAG, Corrective RAG (CRAG). Runnable, with a local-models note for Ollama / OpenAI-compatible endpoints. |

## Categories

Recipes are grouped by what they fix:

| Category | Examples |
|---|---|
| **Reliability** | Retries with backoff, timeout handling, graceful failure, structured output parsing |
| **Performance** | Caching, model routing, parallel tool calls, streaming |
| **Memory** | Checkpointing, summarization, retrieval-based memory |
| **RAG** | Chunking with metadata, hybrid search, re-ranking |
| **Multi-agent** | Handoffs, supervisor message passing |
| **Protocols** | MCP server boilerplate, MCP client setup, A2A task delegation |
| **Evaluation** | Golden datasets, LLM-as-judge with calibration |
| **Safety** | Prompt-injection detection, output filtering, sandboxing |
| **Deployment** | FastAPI wrapper, durable execution, human-in-the-loop approval |

The full list lives in the file tree above this README. GitHub's repo-level search (`/` then type) is the fastest way to find a specific recipe.

## When to reach for a recipe (vs a lab or concept)

| You need... | Go to... |
|---|---|
| The exact code to solve a known problem | `recipes/` |
| To learn a topic step-by-step with explanation | [`labs/`](../labs/) |
| To understand *what* something is and *when* to use it | [`concepts/`](../concepts/) |
| To pick between architectures | [`patterns/`](../patterns/) |

## Version notes on recipes

Recipes age faster than concepts. Each recipe carries a header like:

```
> ⏱ ~5 min · 🛠 langgraph v1.x.y (verified YYYY-MM-DD)
```

If a recipe's code no longer runs against the version installed via `uv sync`, please open an issue with the `bug` label and link the recipe.

## Contributing

Recipes are some of the highest-value contributions. If you've solved a specific agentic-AI problem in production, a five-minute write-up using the recipe template is genuinely useful to the community. See [`CONTRIBUTING.md`](../CONTRIBUTING.md#how-to-add-a-recipe).

> 🟡 Recipes are classified **slow-moving**. Tool versions in the snippets are refreshed during routine sweeps.
