# Project 05 — Multi-server MCP agent

> 🟡 Intermediate · ⏱ 25-30 hours · 📍 Build Challenge after Path 01 + Path 04 (deeply) · 🛠 Verified 2026-05-29

## What you're building

A single-agent (or lightly multi-agent) system that consumes **3+ MCP servers** to compose tools across heterogeneous backends — a filesystem server + a GitHub server + a database server, for example, or your own custom combination. The agent demonstrates the *MCP-everywhere architecture*: instead of writing one-off API integrations for each backend, the agent talks to every backend through the same protocol.

Per [Skyvern's May 2026 MCP architecture explainer](https://www.skyvern.com/blog/mcp-server-architecture-explained/): "When a host connects to multiple servers simultaneously (for example, a filesystem server and a GitHub server at the same time) it spawns a separate client instance for each one. This one-to-one mapping keeps connections isolated and prevents [cross-server interference]." Your agent will be a host running multiple client instances.

## Why this matters

Three distinguishing claims:

1. **Multi-server composition is the production MCP pattern** — per [Atlan's March 2026 MCP guide](https://atlan.com/know/mcp-server-implementation-guide/): "An agent might connect to one server for database queries, another for file access, and a third for API integrations, all in the same session. This is a core design principle of the protocol." Single-server usage is the tutorial; multi-server is the production deployment.
2. **The MCP market is moving fast in 2026** — per [CData December 2025](https://www.cdata.com/blog/mcp-server-best-practices-2026): "The MCP server market is projected to reach $10.4 billion by 2026, growing at a 24.7% CAGR." Building multi-server-fluent agents is positioned for where the ecosystem is heading.
3. **Tool composition has its own failure modes** — per [Getknit April 2026](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent): tool-name collisions, ambiguous routing, schema mismatches, and unclear failure attribution all emerge when 3+ servers are in play. Exposing yourself to those failure modes is the point of the project.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 04 — Tool Protocols (MCP + A2A)** (deeply — Modules 1-5) | MCP host/client/server architecture; consume + author + multi-server composition |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic API key (or OpenAI / similar) | Model the agent runs on |
| 3+ MCP servers to consume | Mix of official + community + (optionally) one you author. See [Resources](#resources) for current servers. |
| Comfort with multi-day software builds | Intermediate-tier scope |

Helpful but not required: Path 03 (only if you go multi-agent for the stretch goal); Docker (for running self-hosted MCP servers locally).

## What you'll build

Four concrete deliverables:

1. **A multi-server agent** — single agent connected to 3+ MCP servers, with documented routing logic for tool selection across servers
2. **Three example workflows** — `examples/workflow-01/` (cross-backend task: e.g., "find issues in this GitHub repo, save the analysis as a file, log to our database"); `examples/workflow-02/` and `workflow-03/` exercising different server combinations
3. **A `topology-diagram.md`** — a mermaid or ASCII diagram showing your agent + the 3+ MCP servers + which tools come from which server
4. **A `WRITEUP.md`** — architecture decisions; server choices; failure modes observed

## Architecture overview

The system has four layers. Each maps to specific 2026 best practices.

| Layer | Components | 2026 source |
|---|---|---|
| **1 — The host/client mesh** | Your agent is the MCP host; spawns one client per server (3+ concurrent connections) | [Skyvern May 2026](https://www.skyvern.com/blog/mcp-server-architecture-explained/) — one-to-one mapping pattern |
| **2 — Server selection** | Three official + community + one self-authored (recommended); or three managed-platform servers | [Truto April 2026](https://truto.one/blog/what-is-an-mcp-server-the-2026-architecture-guide-for-saas-pms/) — pick-your-build-path framing |
| **3 — Tool routing** | The agent's logic for picking which server's tool to call when capabilities overlap | [Getknit April 2026](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent) — schema validation + routing |
| **4 — Cross-server observability** | Per-server trace baggage so failures attribute correctly | [Getknit April 2026](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent) — "When agents fail to complete tasks, it's unclear which server or tool was responsible" |

The minimal client surface (your agent calls these to interact with each server):

| Operation | What it does |
|---|---|
| `connect(server_config)` → client instance | Establishes the JSON-RPC connection (stdio or Streamable HTTP) |
| `list_tools()` per server | Discovery: what tools does each server expose? |
| `call_tool(server_id, tool_name, args)` → result | The actual tool invocation; routed to the right client |
| `disconnect()` per server | Clean shutdown for graceful exit |

The agent does the orchestration: it sees the union of tools across all servers and picks which to call.

## The three failure modes you'll hit

Per the 2026 sources, three failure modes emerge when 3+ servers are in play. Defending against them is part of the project.

### Failure mode 1 — Tool name collision

Two servers expose tools with the same name (e.g., `search`). The agent can't disambiguate. Per [Getknit April 2026](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent): "Standardize on schema definitions for tools (e.g., OpenAPI-style contracts or LangChain tool signatures). Validate inputs and outputs rigorously."

**Defense**: namespace tools at the agent layer. When you load tools from each server, prefix each with the server identifier (`github__search`, `filesystem__search`). The agent sees disambiguated names; the routing layer strips the prefix before calling the right client.

### Failure mode 2 — Ambiguous routing

A capability exists on multiple servers (e.g., "save this content" — filesystem server or notion server or both). The agent picks the wrong one or picks inconsistently.

**Defense**: per-tool metadata in the system prompt. For each tool, document which contexts it's preferred for. Example: "`filesystem__write` for ephemeral analysis; `notion__create_page` for shareable team artifacts."

### Failure mode 3 — Unclear failure attribution

A workflow fails. Which server's tool was responsible? Per [Getknit April 2026](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent): "When agents fail to complete tasks, it's unclear which server or tool was responsible."

**Defense**: per-server trace baggage. Every tool call gets logged with the server identifier, tool name, arguments, latency, success/failure, and (if failed) the error class. The trace is the audit trail; failures stop being mysteries.

These three defenses are the minimum bar. The Milestone 6 fault-injection test verifies each.

## Milestones

Six phases.

### Milestone 1 — Pick the 3+ servers + sketch the topology (3-4 hours)

Pick which 3+ MCP servers your agent will consume. Recommended starter mix:

| Slot | Recommended choice | Why |
|---|---|---|
| **Slot 1 — Filesystem** | [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | Official; stdio transport; clean reference |
| **Slot 2 — GitHub** | [GitHub MCP server](https://github.com/github/github-mcp-server) | Official from GitHub; substantial real-world tool surface |
| **Slot 3 — One of**: SQLite / PostgreSQL / Notion / Slack / Brave Search | [Servers list](https://github.com/modelcontextprotocol/servers) | Pick the one that maps to your example workflows |

Optional 4th slot: a custom MCP server you author yourself (covers the *author* side of Path 04). For this project's intermediate-tier scope, authoring is a stretch goal; consuming is the requirement.

Write a one-page topology diagram showing the host + clients + servers + which tools each server exposes (or a representative subset).

**Done when**: 3+ servers picked; you can run each one in isolation; you have a written topology with tool inventory.

### Milestone 2 — Connect to one server (2-3 hours)

Build the agent with one MCP client connecting to one server. The agent uses the listed tools to complete a simple task. The goal: verify your MCP client library works before scaling to multiple servers.

Recommended Python MCP client: [`mcp`](https://pypi.org/project/mcp/) — the official Anthropic SDK. Alternative: [`mcp-python-sdk`](https://github.com/modelcontextprotocol/python-sdk).

**Done when**: single-server tool call works end-to-end; the agent completes a task using a tool from that server.

### Milestone 3 — Connect to 3+ servers concurrently (4-6 hours)

Extend to 3+ concurrent client connections. Per [Skyvern May 2026](https://www.skyvern.com/blog/mcp-server-architecture-explained/), one client instance per server. Implement:

- Connection pool: client per server; managed lifecycle (connect on agent start, disconnect on shutdown)
- Tool aggregation: union of tools across all servers, presented to the agent with server-prefixed names (Defense 1: tool name collision)
- Per-server logging: each tool call records which server, which tool, latency, success/failure (Defense 3: failure attribution)

**Done when**: the agent sees a unified tool list from 3+ servers; can call tools from any of them; the tool call log shows which server handled each call.

### Milestone 4 — Implement the routing logic (3-4 hours)

Add the per-tool metadata in the system prompt (Defense 2: ambiguous routing). For each tool, document its preferred context. The agent's reasoning chain should pick the right tool based on this metadata.

**Done when**: when a capability exists on multiple servers, the agent consistently picks the documented-preferred one. Test with at least 3 such overlapping cases.

### Milestone 5 — Build the three example workflows (5-7 hours)

Run three workflows that exercise multi-server composition. Examples:

- **Workflow 1 — Cross-backend integration**: "find the 5 most recent issues in repo X, summarize them in a markdown file, log the summary to our database with today's date"
- **Workflow 2 — Discovery + action**: "search GitHub for repos matching <criteria>, write the top 10 to a CSV file, create a Notion page summarizing the findings"
- **Workflow 3 — Multi-step pipeline**: "read this CSV from disk, query our database for related records, post a summary to Slack"

Each workflow must exercise at least 2 of your 3+ servers. The agent's trace shows which servers were called in what order.

**Done when**: all three workflows run end-to-end; the trace shows multi-server composition; each workflow produces the expected outputs.

### Milestone 6 — Fault injection + write-up (3-5 hours)

Deliberately introduce failures to verify the defenses:

- **Test 1** — bring down one server mid-workflow; verify the agent's error handling and failure attribution
- **Test 2** — introduce a tool with a colliding name; verify namespacing prevents misrouting
- **Test 3** — give an ambiguous request that could route to two servers; verify the agent picks the documented-preferred one

Document each test's outcome. Write the WRITEUP.

**Done when**: all three fault tests are documented; the defenses worked as designed for 2 of 3 at minimum.

## Evaluation criteria

The intermediate-tier rubric — five dimensions:

| Dimension | What it measures | Intermediate-tier target |
|---|---|---|
| **Multi-server fluency** | Does the agent genuinely use 3+ servers, or does one server dominate? | All three workflows exercise at least 2 servers; across workflows, all 3+ servers see substantial usage |
| **Routing discipline** | Are the three failure-mode defenses implemented and exercised? | All three defenses in code; fault tests pass for at least 2 of 3 |
| **MCP integration depth** | Does the agent use real MCP, not just import the library? | Tools come from MCP servers (verifiable via the trace); the agent doesn't bypass MCP for direct API calls |
| **Workflow completeness** | Do all three example workflows run end-to-end? | All three workflows produce expected outputs; the trace shows multi-server composition |
| **Cost per workflow** | What does an average workflow run cost? | <$0.50 per workflow at Sonnet pricing; <$0.10 at Haiku-class |

The intermediate-tier dimensions follow the [Project 03](../03-project-management-agent/) pattern with substitutions specific to multi-server: *multi-server fluency* replaces *topology defense* (the architectural decision is server selection rather than topology choice); *routing discipline* is the new dimension specific to this project.

## Stretch goals

Pick at most two.

- **Author your own MCP server** — covers the producer side of Path 04. Build a small MCP server (e.g., an in-memory key-value store, a wrapper around an API you use) and have your agent consume it as one of the 3+ servers. Production-ready or local-only; either works.
- **MCP gateway** — instead of 3+ direct connections, route through a single MCP gateway that aggregates the backends. Per [Obot March 2026](https://obot.ai/blog/single-mcp-gateway-vs-multiple-mcp-servers/): "The most practical setup in growing organizations is a hybrid one." Demonstrates the enterprise pattern.
- **Streamable HTTP transport** — at least one of your servers uses Streamable HTTP instead of stdio. Per [Skyvern May 2026](https://www.skyvern.com/blog/mcp-server-architecture-explained/): "Local tools and CLI-driven agents typically default to STDIO for its simplicity. Hosted infrastructure generally requires Streamable HTTP."
- **Per-tenant scoping** — agent runs as a single-tenant scope per session. Per [Truto April 2026](https://truto.one/blog/what-is-an-mcp-server-the-2026-architecture-guide-for-saas-pms/): "Scope each MCP server to a single tenant's connected account."
- **Multi-agent variant** — split into supervisor + specialist agents where each specialist owns a subset of servers. Demonstrates Path 03 multi-agent topology with the MCP-everywhere substrate.
- **Security audit** — per the documented 2026 risks (43% of early MCP servers had command injection vulnerabilities in 2025 audits, per [Atlan March 2026](https://atlan.com/know/mcp-server-implementation-guide/)), run a manual security review of each consumed server: input sanitization, permission scoping, credential handling.

## Anti-scope

What you don't need to build for this project:

- **Full multi-agent topology with handoff contracts** — that's Project 03's surface or capstone tier; this project is single-agent multi-server (or stretch-goal multi-agent)
- **Custom MCP server in production** — authoring is a stretch goal; consuming is the requirement
- **MCP-everywhere observability stack** — basic per-server tracing is sufficient; full OTel + judge ensemble is capstone-tier
- **MCP registry / discovery layer** — Q4 2026 ecosystem feature per Truto; out of scope for this project
- **Sovereign-cloud MCP deployments** — Path 07 deployment territory
- **Real-time bidirectional streaming over MCP** — request-response is the assumed shape

## Resources

**Architecture references**:
- [Skyvern (May 2026), MCP Server Architecture Explained](https://www.skyvern.com/blog/mcp-server-architecture-explained/) — host/client/server model; STDIO vs Streamable HTTP transport; one-client-per-server pattern
- [Atlan (March 2026), MCP Server Implementation Guide](https://atlan.com/know/mcp-server-implementation-guide/) — the canonical multi-server framing; security risks (43% command injection in 2025 audits)
- [Getknit (April 2026), Scaling AI Capabilities: Multiple MCP Servers](https://www.getknit.dev/blog/scaling-ai-capabilities-using-multiple-mcp-servers-with-one-agent) — the three failure modes this project defends against
- [Obot (March 2026), Single MCP Gateway vs Multiple MCP Servers](https://obot.ai/blog/single-mcp-gateway-vs-multiple-mcp-servers/) — gateway pattern for the stretch goal
- [Truto (April 2026), MCP Server 2026 Architecture Guide](https://truto.one/blog/what-is-an-mcp-server-the-2026-architecture-guide-for-saas-pms/) — pick-your-build-path framing; per-tenant scoping
- [Clarifai (March 2026), MCP Architecture for Infra Teams](https://www.clarifai.com/blog/mcp-architecture-explained) — deployment suitability matrix (SaaS / VPC / on-prem)

**MCP server documentation**:
- [Official MCP servers list](https://github.com/modelcontextprotocol/servers) — the canonical directory; filesystem / GitHub / SQLite / PostgreSQL / Slack / Brave Search / Notion and more
- [Model Context Protocol specification](https://modelcontextprotocol.io/) — the protocol your clients speak
- [GitHub MCP server](https://github.com/github/github-mcp-server) — official from GitHub; substantial tool surface
- [`mcp` PyPI package](https://pypi.org/project/mcp/) — official Anthropic SDK
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — alternative client/server library

**Repo cross-references**:
- [Project 03 — Project management agent](../03-project-management-agent/) — the prior intermediate-tier project; single-server MCP at intermediate tier
- [Project 04 — Data analysis agent](../04-data-analysis-agent/) — the prior intermediate-tier project; code-execution sandbox at intermediate tier
- [Project 07 — Evaluated multi-agent system](../../capstone/07-evaluated-multi-agent-system/) — capstone-tier; adds the full eval/observability layer to multi-server architectures
- [Path 04 — Tool Protocols (MCP + A2A)](../../../learning-paths/04-tool-protocols-mcp-a2a/) — the canonical MCP path; this project is the cross-path integration
- [`patterns/11-mcp-integration.md`](../../../patterns/11-mcp-integration.md) — the MCP integration pattern this project implements at multi-server tier

## Submission guide

Four artifacts go in your repo when you're done:

1. **The agent code** — clean structure (agent/, clients/, examples/, tests/); README with setup + MCP server configurations + usage; `.env.example` for required keys
2. **The topology diagram** — `topology-diagram.md` showing your agent + the 3+ servers + which tools each exposes
3. **Three example workflow transcripts** — `examples/workflow-XX/` each containing the request, the trace (showing which servers were called), and the outputs
4. **`WRITEUP.md`** — a ~1,000-word document covering:
   - Which 3+ servers you chose and why (ADR format: chose / alternatives / why / tradeoffs)
   - How each of the three failure-mode defenses was implemented
   - The fault-injection test outcomes (which defenses worked, which didn't)
   - One thing that surprised you about multi-server composition
   - Two stretch goals you considered and your reasoning

Add yourself to `docs/community/showcase.md` when you submit.

## What this project leads to

After Multi-Server MCP Agent, the natural progressions:

- Project 06 (Financial research analyst) — capstone-tier; same multi-server substrate with regulated-domain provenance (planned)
- Project 07 (Evaluated multi-agent system) — capstone-tier; the eval/observability layer this project's basic tracing scaffolds toward
- Project 08 (Production-ready deep research) — capstone-tier; combines multi-server MCP with long-running execution patterns (planned)
- Path 04 deeper material (Modules 6-7 if applicable) — A2A federation; cross-system orchestration

This is the canonical Build Challenge for engineers who want to internalize the MCP-everywhere architecture before committing to capstone-tier scope.
