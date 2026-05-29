# 📖 Concepts · Tools

> 🟢 Stable concepts about how tools work in LLM agents.

Tools are how an agent acts on the world. Designing them well is one of the highest-leverage things you can do for agent reliability — and getting them wrong is one of the most common reasons agents misbehave in production.

This section is paired: **design first, then selection**. Design is about making each tool legible to the model; selection is about helping the model pick correctly when several tools coexist.

## Pages in this section

| Page | What it covers | When to read |
|---|---|---|
| 📖 [Tool design](./tool-design.md) | Name, description, schema, return contract, executor. Patterns and common mistakes. | Before building any tool-using agent. |
| 📖 [Tool selection](./tool-selection.md) | How the model picks among tools; the four levers (prompt, descriptions, history, `tool_choice`); failure taxonomy; pruning strategies. | After your first agent has 3+ tools and starts picking wrong. |
| 📖 [MCP foundations](./mcp-foundations.md) | The Model Context Protocol architecture, three primitives (tools/resources/prompts), JSON-RPC 2.0 wire format, lifecycle, transports (stdio vs Streamable HTTP), authentication. | When you want agents to access tools that live in another process or another team's codebase. Path 04 Module 1. |
| 📖 [Building an MCP server](./building-an-mcp-server.md) | FastMCP 3.0 workflow, decorator-based registration, type-hint-driven schema inference, MCP Inspector debugging, deployment patterns (stdio vs Streamable HTTP with auth). | After MCP foundations; when you're ready to expose your own tools to MCP-compatible hosts. Path 04 Module 2. |
| 📖 [Building an MCP client](./building-an-mcp-client.md) | Consuming external servers from your agent; multi-server orchestration with collision-free routing; the five production defenses (timeout, schema-drift, circuit-breaker, retry-on-auth, response-size limits); discovery via MCP Registry + Server Cards; FastMCP 3.1 code mode for token-bloat reduction. | After Building an MCP server; when you're ready to wire an agent to external MCP servers. Path 04 Module 3. |
| 📖 [MCP security threat model](./mcp-security-threat-model.md) | The five MCP attack classes (tool poisoning, response injection, rug pulls, credential sprawl, audit blind spots); protocol-level vulnerabilities (arxiv:2601.17549); empirical state (43% command-injection rate); OWASP MCP Top 10; defense-in-depth across six layers. | After the build-and-consume pair; before deploying any MCP integration to production. Path 04 Module 4. |
| 📖 [A2A foundations](./a2a-foundations.md) | The agent-to-agent protocol; three primitives (Agent Cards, Tasks, Transport); Task lifecycle with 8 states; A2A vs MCP complementarity; v1.0 Signed Agent Cards + v1.2 spec; Linux Foundation governance (150+ orgs by April 2026); protobuf-based SDK 1.0.3 surface; framework support across Google ADK / LangGraph / CrewAI / LlamaIndex Agents / Semantic Kernel / AutoGen. | After the MCP build-consume-secure trio. Path 04 Module 5. |

## Hands-on

- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) — implement the patterns above, watch a deliberately-broken toolset fail, fix it step by step.
- 🧪 [Lab 25: MCP server from scratch](../../labs/25-mcp-server-from-scratch/) — build a working MCP server with tools, resources, and prompts; test with MCP Inspector + Python client; walk through schema-inference failure modes; deploy over Streamable HTTP.
- 🧪 [Lab 26: MCP client from scratch](../../labs/26-mcp-client-from-scratch/) — build a multi-server MCP client with collision-free routing; layer the five production defenses; wire into a Pattern 01 agent loop; measure tool-schema token cost.
- 🧪 [Lab 27: MCP security threat model](../../labs/27-mcp-security-threat-model/) — implement three canonical MCP attacks (tool poisoning, response injection, rug-pull) against an in-process toy server and three defenses; measure what each catches and what slips through.
- 🧪 [Lab 28: A2A endpoint from scratch](../../labs/28-a2a-endpoint-from-scratch/) — build a working A2A v1.0 server with the official Python SDK 1.0.3; Agent Card discovery + AgentExecutor + TaskUpdater; subprocess-based uvicorn + real httpx client roundtrip with the `A2A-Version: 1.0` header.

## Quizzes

- 🧠 [`quizzes/foundations/tool-design-and-selection.md`](../../quizzes/foundations/tool-design-and-selection.md) — 8 questions on tool design and selection.
- 🧠 [`quizzes/foundations/mcp-foundations-and-server.md`](../../quizzes/foundations/mcp-foundations-and-server.md) — 8 questions on MCP foundations + Building an MCP server + Lab 25.
- 🧠 [`quizzes/foundations/mcp-client-and-discovery.md`](../../quizzes/foundations/mcp-client-and-discovery.md) — 8 questions on Building an MCP client + Lab 26.
- 🧠 [`quizzes/foundations/mcp-security-threat-model.md`](../../quizzes/foundations/mcp-security-threat-model.md) — 8 questions on MCP security threat model + Lab 27.
- 🧠 [`quizzes/foundations/a2a-foundations.md`](../../quizzes/foundations/a2a-foundations.md) — 8 questions on A2A foundations + Lab 28.

## Related

- 📖 [`concepts/agents/`](../agents/) — the broader agent context tools sit inside.
- 🏛 [`patterns/01-single-agent-tool-use.md`](../../patterns/01-single-agent-tool-use.md) — the architectural perspective on single-agent tools. Authored in Batch 44.
- 🏛 [`patterns/11-mcp-integration.md`](../../patterns/11-mcp-integration.md) — the architectural perspective on cross-process tool access via MCP. Authored in Batch 44.
- 🏛 [`patterns/12-a2a-federation.md`](../../patterns/12-a2a-federation.md) — the architectural perspective on cross-agent task delegation via A2A. Authored in Batch 44.
- 🏛 [Top-level `patterns/README.md`](../../patterns/) — the full pattern catalog; 12 entries spanning single-agent through swarm.
- 🛣 [Path 04 — Tool Protocols (MCP + A2A)](../../learning-paths/04-tool-protocols-mcp-a2a/) — the learning path where MCP and A2A are developed in depth.
- 🧮 [`math-foundations/04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md) — the action-space framing.

## Forthcoming pages in this section

The MCP foundations, Building an MCP server, Building an MCP client, MCP security threat model, and A2A foundations pages shipped across Batches 43, 46, 47, and 48 (Path 04 Modules 1+2+3+4+5). Still planned for this directory:

- *Building an A2A endpoint at production depth* — Path 04 Module 6 (future batch); Signed Agent Cards, persistent task stores, OAuth2 auth, streaming, push notifications, OpenTelemetry.
- *MCP + A2A composition* — Path 04 Module 7 (future batch); orchestrator pattern combining MCP for tools with A2A for cross-agent delegation.
- *Tool composition* — combining tools into pipelines, fan-out/fan-in patterns.
- *Tool versioning* — handling schema evolution without breaking running agents.

Open a [Discussion](https://github.com/MHHamdan/Agentic-AI-Engineer/discussions) if you want to claim one of these.
