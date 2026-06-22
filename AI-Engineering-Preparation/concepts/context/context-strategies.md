# Context strategies: retrieval, compaction, note-taking, isolation

> Concept note. ~9 min. Builds on [context engineering](./context-engineering.md).

The four moves — write, select, compress, isolate — show up in practice as a handful of concrete techniques. These are the levers you actually pull to keep an agent's window clean over a long task.

## Just-in-time retrieval (select)

Instead of front-loading everything an agent might need, keep lightweight references — file paths, identifiers, queries — and load the underlying content only when a step needs it. A coding agent does not hold every file in context; it holds the paths and reads a file when it acts on it. This keeps the window small and current, and mirrors how a person works from references rather than memorizing the whole codebase. It is [retrieval](../rag/) applied to the agent's own working set.

## Compaction vs. summarization (compress)

When history grows long, you reduce it — but there are two distinct ways, and the difference matters.

- **Compaction (reversible).** Strip content that is recoverable from the environment, replacing it with a pointer. If a tool returned a 500-line file earlier, the history does not need the full contents — it needs the path, because the agent can re-read the file if required. Nothing is truly lost; it is offloaded. This is the safest, lightest-touch reduction, and clearing old raw tool results is the low-hanging fruit.
- **Summarization (lossy).** Use a model to summarize a stretch of history into a shorter form, typically when the window nears a threshold, then continue from the summary. This recovers a lot of room but discards detail permanently, so the art is choosing what survives — over-aggressive summarization drops a fact whose importance only surfaces later.

The guidance is to prefer reversibility where you can (offload, keep a pointer) and reserve lossy summarization for when you must.

## Structured note-taking (write)

Have the agent write durable notes *outside* the context window — a scratchpad, a running plan, a file — and read them back later, rather than holding everything in the conversation. This persists progress across compaction and even across sessions, and it gives the agent an explicit, inspectable working memory instead of an implicit one buried in chat history.

## Sub-agent isolation (isolate)

For a complex task, give a subtask its own context window via a sub-agent: it does focused work in isolation and returns only a concise result to the main agent. The main thread never sees the subtask's intermediate clutter, which keeps its window clean and its attention on the overall goal. The cost is coordination and the risk of losing detail in the handoff, so isolation pays off when subtasks are genuinely separable.

## What to remember

- Just-in-time retrieval loads content on demand from lightweight references instead of front-loading it.
- Prefer reversible compaction (offload, keep a pointer) over lossy summarization; summarize only when you must.
- Structured note-taking externalizes working memory; sub-agent isolation keeps subtask clutter out of the main window.

## References

- Anthropic (2025). *Effective context engineering for AI agents* — official engineering guidance. See [`../../references/references.md`](../../references/references.md).
