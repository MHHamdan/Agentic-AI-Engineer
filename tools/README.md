# Tools

Versioned snapshots of fast-moving frameworks and protocols. Everything in this folder carries a verification date and links to the primary source.

This is the most volatile part of the repo. If you read a page in `tools/` and the snapshot date is months old, double-check against the linked official documentation before trusting the syntax.

## Snapshot format

Every tool page (and every code snippet that depends on a specific version) starts with this header:

```
> 🔴 Tool snapshot — <tool> v<version>, verified YYYY-MM-DD
> Source: <link to official docs / changelog / spec>
```

When a tool ships a breaking change:

1. The relevant page is updated.
2. A migration note is added on the same page.
3. An entry lands in [`CHANGELOG.md`](../CHANGELOG.md) under **Verified Tool Snapshots**.

The PR carries the `tool-snapshot` label so maintainers prioritize review.

## Coverage

Each tool / family of tools lives in its own subfolder:

| Folder | Covers |
|---|---|
| `langgraph/` | LangGraph state machines, checkpoints, human-in-the-loop, streaming |
| `langsmith/` | Tracing, evaluation, datasets, experiment workflows |
| `google-adk/` | Google Agent Development Kit |
| `crewai/` | CrewAI multi-agent framework |
| `autogen/` | Microsoft AutoGen |
| `openai-agents-sdk/` | OpenAI Agents SDK |
| `mcp/` | Model Context Protocol — servers, clients, transports |
| `a2a/` | Agent2Agent protocol |
| `vector-databases/` | pgvector, Pinecone, Qdrant, Weaviate, Chroma |
| `comparisons/` | Side-by-side comparison matrices |

## Comparison matrices

`tools/comparisons/` is where high-utility comparison tables live:

- Framework comparison (LangGraph vs ADK vs CrewAI vs AutoGen vs raw)
- Vector DB comparison (latency, recall, hybrid search support, hosting)
- MCP vs A2A — when each is the right tool

These are some of the most-linked pages in the repo. If you want to contribute, comparison tables with honest tradeoffs (not benchmarks-as-marketing) are highly welcome.

## How to keep tool pages fresh

Stale tool pages are tracked via the [`stale-tool-version`](https://github.com/MHHamdan/Agentic-AI-Engineer/issues?q=is%3Aissue+label%3Astale-tool-version) issue label. Opening such an issue is a real contribution even if you don't fix it yourself.

Maintainers run periodic sweeps to refresh verification dates against the upstream sources. Sweeps are noted in [`CHANGELOG.md`](../CHANGELOG.md).

## Initial verification baseline

The verified snapshots at v0.1.0 are listed in [`CHANGELOG.md`](../CHANGELOG.md#verified-tool-snapshots). Highlights:

- **MCP** spec `2025-11-25` is the current stable; RC `2026-07-28` was announced.
- **A2A** is at v1.0 and lives under the Linux Foundation.
- **LangGraph** and **LangChain** are both at 1.0 GA.
- LangSmith, Google ADK, CrewAI, AutoGen, OpenAI Agents SDK, and individual vector DBs are tracked per page as they're authored.

> 🔴 All content in this folder is classified **fast-changing**. Trust the snapshot date, then trust the upstream docs more.
