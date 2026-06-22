# Context engineering

> Concept note. ~9 min. Builds on [the context window](../llm/context-window.md). Runnable companion: [`labs/04-memory-and-context/`](../../labs/04-memory-and-context/) (`context_budget.py`).

**Context engineering** is the practice of deliberately designing what a model sees on every inference call. It is the discipline that grew up once builders realized that for agents, the wording of a prompt was no longer the bottleneck — the bottleneck was assembling the right instructions, the right tools, the right slice of history, and the right retrieved facts into a finite window, turn after turn, without it collapsing under its own weight.

## Beyond prompt engineering

Prompt engineering optimizes a single, mostly static instruction. Context engineering optimizes a *system* that builds the context dynamically, every call, from many moving sources: system and developer instructions, the conversation so far, retrieved knowledge, [memory](../memory/), tool definitions, and tool outputs. In an agent that runs for dozens of steps, what fills the window changes constantly, and managing that flow — not phrasing one prompt — is where reliability is won or lost.

## Four moves: write, select, compress, isolate

A useful way to organize the techniques is by what they do to information relative to the window:

- **Write** — put information *outside* the context window so it persists without consuming tokens: a scratchpad of working notes, or durable [memory](../memory/). The agent writes results down and reads them back when needed.
- **Select** — pull *into* the window only what the current step needs. This is [retrieval](../rag/), and increasingly **just-in-time retrieval**: hold lightweight identifiers (file paths, queries) and load the underlying content at runtime rather than front-loading everything.
- **Compress** — reduce what is already in the window when it grows long: summarize history, or strip content that is recoverable from the environment (see [strategies](./context-strategies.md)).
- **Isolate** — split context across boundaries so one subtask does not pollute another, typically by giving sub-agents their own windows and passing back only summaries.

The single principle under all four is signal-to-noise: every token in the window should earn its place, because tokens that do not help actively hurt (see [context rot](./context-rot-and-failure-modes.md)).

## Why it is a discipline, not a trick

It would be convenient if a large enough window made this unnecessary. It does not: windows have grown to millions of tokens and the problem remains, because models use long contexts unevenly and degrade as they fill. So context engineering is ongoing work — measuring what is in the window, deciding what to keep, and building the machinery to assemble it well on every call. The lab builds the smallest version of that machinery: an assembler that selects by priority and compresses the overflow to stay within a budget.

## What to remember

- Context engineering is designing what the model sees each call — a dynamic system, not a static prompt.
- Organize the techniques as write, select, compress, isolate; the unifying goal is signal-to-noise in a finite window.
- A bigger window does not retire the discipline, because long contexts are used unevenly.

## References

- Anthropic (2025). *Effective context engineering for AI agents* — official engineering guidance.
- Hong, K., Troynikov, A., Huber, J. (2025). *Context Rot: How Increasing Input Tokens Impacts LLM Performance.* Chroma technical report. See [`../../references/references.md`](../../references/references.md).
