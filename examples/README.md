# Examples

Minimal, runnable reference implementations. Each example is the *smallest* thing that demonstrates how a particular tool or pattern works — no teaching prose, no exercises, just clean code with a short README.

## Examples vs labs

| | Examples | Labs |
|---|---|---|
| Purpose | Reference for engineers who already know the topic | Teaching with explanation |
| Format | Standalone Python file or small folder | Notebook + README |
| Comments | Sparse, only where non-obvious | Extensive, woven through |
| Length | As small as possible | Whatever the lesson needs |

If you wrote one and the other felt redundant, you probably wrote one of them wrong.

## Planned set

| Folder | Demonstrates |
|---|---|
| `mcp-server-financial/` | A complete MCP server + client wired to a real (or mock) data source |
| `langgraph-react-agent/` | The smallest end-to-end LangGraph agent with tools and memory |
| `crewai-team/` | A multi-agent team in CrewAI |
| `autogen-conversation/` | A multi-agent conversation in AutoGen |
| `openai-agents-sdk/` | A minimal agent using OpenAI's Agents SDK |
| `google-adk-agent/` | A minimal agent using Google's ADK |

Each subfolder has its own README pinning the verified tool version and explaining how to run the example.

## Tool snapshots

Examples are the most version-sensitive content in the repo. Every example carries:

```
> 🔴 Tool snapshot — <tool> v<version>, verified YYYY-MM-DD
> Source: <official docs / changelog link>
```

When a tool ships a breaking change, the example is updated and the relevant entry is added to [`CHANGELOG.md`](../CHANGELOG.md) under **Verified Tool Snapshots**.

## Contributing

A new example is a great way to contribute if a framework you use isn't yet represented. Keep it minimal — under ~150 lines of Python, ideally — and include a "what this does NOT cover" note pointing readers to the corresponding lab or tool page when they want more.

> 🔴 Examples are classified **fast-changing**. Expect them to need updates every quarter or two as their underlying frameworks evolve.
