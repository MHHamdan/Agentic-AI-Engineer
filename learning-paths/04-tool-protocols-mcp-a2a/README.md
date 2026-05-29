# Path 04 — Tool Protocols (MCP + A2A)

> 🟡 Intermediate · ⏱ 6–10 hours (planned, ~6 hours shipped via Modules 1+2+3+4+5+6) · 📍 Start here once you've completed Path 01 · 🚧 **In progress — Modules 1+2+3+4+5+6 shipped (Batch 49); Module 7 planned**

> ✅ **Modules 1+2+3+4+5+6 are live.** Six concept pages ([MCP foundations](../../concepts/tools/mcp-foundations.md) + [Building an MCP server](../../concepts/tools/building-an-mcp-server.md) + [Building an MCP client](../../concepts/tools/building-an-mcp-client.md) + [MCP security threat model](../../concepts/tools/mcp-security-threat-model.md) + [A2A foundations](../../concepts/tools/a2a-foundations.md) + [A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md)), five labs ([Lab 25](../../labs/25-mcp-server-from-scratch/) + [Lab 26](../../labs/26-mcp-client-from-scratch/) + [Lab 27](../../labs/27-mcp-security-threat-model/) + [Lab 28](../../labs/28-a2a-endpoint-from-scratch/) + [Lab 29](../../labs/29-a2a-endpoint-production-depth/)), and five quizzes ([MCP foundations and server](../../quizzes/foundations/mcp-foundations-and-server.md) + [MCP client and discovery](../../quizzes/foundations/mcp-client-and-discovery.md) + [MCP security threat model](../../quizzes/foundations/mcp-security-threat-model.md) + [A2A foundations](../../quizzes/foundations/a2a-foundations.md) + [A2A endpoint production-depth](../../quizzes/foundations/a2a-endpoint-production-depth.md)) ship as of Batch 49. Module 7 (MCP + A2A composition; the orchestrator pattern that closes the path) remains planned — the "What you can read right now" section below lists every shipped artifact plus the existing adjacent material that future module will build on.

## Who this path is for

Engineers who've built single agents and want them to talk to external tools (MCP) and to other agents (A2A) without writing bespoke integrations for every combination. You've felt the pain of "every tool needs a different SDK wrapper" or "every agent vendor speaks a different dialect" and you want the standard that fixes it.

## What you'll be able to do

When this path is complete, you'll be able to:

- Explain the **MCP vs A2A** split — MCP is agent-to-tool (vertical integration), A2A is agent-to-agent (horizontal collaboration). Confusing the two is the most common mistake in 2026 production deployments per dev.to March 2026.
- **Build an MCP server** that exposes tools, resources, and prompts to any MCP-compatible client (Claude Desktop, Cursor, agent SDKs). MCP is JSON-RPC 2.0 over Streamable HTTP; the client-server architecture matters.
- **Build an MCP client** in your own agent and consume external servers. As of 2026 there are 18,000+ community-indexed MCP servers per zylos.ai and tens of millions of monthly SDK downloads.
- **Deploy an A2A endpoint** so other agents can delegate to yours. A2A v1.0 ships under the Linux Foundation's Agentic AI Foundation (AAIF) governance per intuz April 2026.
- **Choose between MCP, A2A, and ACP** for a given problem. The 2026 emerging consensus per zylos.ai March 2026 is a three-layer stack: MCP for tool access, A2A for agent coordination, ACP (REST-native, IBM/AGNTCY) where you want HTTP-toolchain compatibility.
- **Defend against MCP-layer attacks**. The arxiv:2601.10955 *"Beyond Max Tokens"* paper showed how MCP tool layers can be weaponized for resource amplification — a benign-looking server that produces correct but extremely expensive trajectories. Path 04 will cover the threat model.

## Prerequisites

- **Path 01 Foundations** complete. You have a working agent loop and you understand tool-calling at the contract level.
- Comfort with JSON-RPC and HTTP basics is helpful but not strictly required.
- Familiarity with **Path 03 Multi-Agent Systems** is recommended for the A2A half — multi-agent topology decisions affect A2A endpoint design.

## Path structure (planned)

The planned module breakdown:

| Module | Topic | Status |
|---|---|---|
| 1 | **[MCP foundations](../../concepts/tools/mcp-foundations.md)** — protocol spec, JSON-RPC 2.0 wire format, client-server lifecycle, transports (stdio vs Streamable HTTP) | ✅ Shipped (Batch 43) |
| 2 | **[Building an MCP server](../../concepts/tools/building-an-mcp-server.md)** — FastMCP 3.0, decorator-based registration, type-hint-driven schemas, MCP Inspector workflow, deployment patterns. Lab: [Lab 25 — MCP server from scratch](../../labs/25-mcp-server-from-scratch/). Quiz: [MCP foundations and server](../../quizzes/foundations/mcp-foundations-and-server.md) | ✅ Shipped (Batch 43) |
| 3 | **[Building an MCP client](../../concepts/tools/building-an-mcp-client.md)** — consuming external servers from your agent; multi-server orchestration with collision-free routing; production defenses (timeout, schema-drift, circuit-breaker, retry-on-auth, response-size limits); MCP Registry + Server Cards discovery; FastMCP 3.1 code mode. Lab: [Lab 26 — MCP client from scratch](../../labs/26-mcp-client-from-scratch/). Quiz: [MCP client and discovery](../../quizzes/foundations/mcp-client-and-discovery.md) | ✅ Shipped (Batch 46) |
| 4 | **[MCP security and the tool-layer threat model](../../concepts/tools/mcp-security-threat-model.md)** — both [arxiv:2601.10955 (Zhou et al., January 2026)](https://arxiv.org/abs/2601.10955) resource-amplification DoS (658× token inflation) and [arxiv:2601.17549 (Maloyan, January 2026)](https://arxiv.org/abs/2601.17549) protocol-level vulnerabilities (23-41% attack amplification); tool poisoning + response injection + rug pulls; OWASP MCP Top 10; defense-in-depth across allowlists, sanitization, fingerprinting, HITL, audit, sandboxing. Lab: [Lab 27 — MCP security threat model](../../labs/27-mcp-security-threat-model/). Quiz: [MCP security threat model](../../quizzes/foundations/mcp-security-threat-model.md) | ✅ Shipped (Batch 47) |
| 5 | **[A2A foundations](../../concepts/tools/a2a-foundations.md)** — the three primitives (Agent Cards / Tasks / Transport); v1.0 Signed Agent Cards and v1.2 spec (March 2026); Linux Foundation governance (150+ orgs by April 2026); A2A-vs-MCP complementarity; the protobuf-based SDK 1.0.3 surface; protocol-version negotiation. Lab: [Lab 28 — A2A endpoint from scratch](../../labs/28-a2a-endpoint-from-scratch/). Quiz: [A2A foundations](../../quizzes/foundations/a2a-foundations.md) | ✅ Shipped (Batch 48) |
| 6 | **[A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md)** — DatabaseTaskStore for persistence (SQLite/PostgreSQL/MySQL); JWS-signed Agent Cards per RFC 7515 with RS256; API-key authentication via Starlette middleware; SSE streaming via SendStreamingMessage; push notifications (discussed, deferred); OpenTelemetry auto-instrumentation of DefaultRequestHandler + JsonRpcDispatcher + EventQueue. Lab: [Lab 29 — A2A endpoint at production depth](../../labs/29-a2a-endpoint-production-depth/). Quiz: [A2A endpoint production-depth](../../quizzes/foundations/a2a-endpoint-production-depth.md) | ✅ Shipped (Batch 49) |
| 7 | **MCP + A2A together** — the hybrid 40-60% workflow-velocity improvement pattern per a2a-mcp.org March 2026; CRM-and-knowledge-base-via-MCP + technical-delegation-via-A2A | 📋 Planned |

Each module follows the Path 01/03/06 shape: concept page(s) + lab + quiz, with reference solutions where labs apply. Modules 1+2 demonstrate this shape; Modules 3-7 will follow the same pattern.

## What you can read right now

The repo already has substantive material that maps to this path. Modules 1+2+3+4+5+6 are now live; the artifacts below include both the shipped module content and the adjacent existing material the remaining Module 7 will build on:

**Shipped — Modules 1+2+3+4+5+6** (Batches 43 + 46 + 47 + 48 + 49):
- 📖 [MCP foundations](../../concepts/tools/mcp-foundations.md) — Module 1 concept page (~14 min). Protocol architecture, the three primitives (tools/resources/prompts), JSON-RPC 2.0 wire format, host/client/server topology, the five-phase session lifecycle, OAuth 2.1 authentication, what MCP is *not*.
- 📖 [Building an MCP server](../../concepts/tools/building-an-mcp-server.md) — Module 2 concept page (~13 min). FastMCP 3.0 workflow, the three decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`), type-hint-driven JSON Schema inference, MCP Inspector debugging workflow, the Python client (`fastmcp.Client`), stdio vs Streamable HTTP deployment, common mistakes.
- 📖 [Building an MCP client](../../concepts/tools/building-an-mcp-client.md) — Module 3 concept page (~13 min). Multi-server orchestration with collision-free routing via server-name prefixes; the five production defenses (per-tool timeout, schema-cache TTL, circuit-breaker, retry-on-auth-error, response-size limits); discovery patterns (config file → MCP Registry → Server Cards); the FastMCP 3.1 code-mode escape hatch for token-bloat (15K → 2-3K per request per Apigene April 2026).
- 📖 [MCP security threat model](../../concepts/tools/mcp-security-threat-model.md) — Module 4 concept page (~14 min). The five MCP attack classes (tool poisoning, response injection, rug pulls, credential sprawl, audit blind spots) plus resource amplification as a sixth; protocol-level vulnerabilities from arxiv:2601.17549 (Maloyan January 2026, 23-41% amplification) and resource-amplification DoS from arxiv:2601.10955 (Zhou et al. January 2026, 658× token inflation) and server lifecycle threats from arxiv:2503.23278 (Hou et al.); the 43% command-injection finding across 1,899 real servers (arxiv:2506.13538); OWASP MCP Top 10 (beta); defense-in-depth across six layers (allowlists, sanitization, least-agency, HITL, audit, sandboxing).
- 📖 [A2A foundations](../../concepts/tools/a2a-foundations.md) — Module 5 concept page (~14 min). The three primitives (Agent Cards at `/.well-known/agent-card.json`, Tasks with 8-state lifecycle, Transport via JSON-RPC 2.0 + SSE); the A2A-vs-MCP complementarity (MCP for agent-to-tool, A2A for agent-to-agent); the v1.0 → v1.2 evolution (Linux Foundation governance June 2025; IBM ACP merger August 2025; Signed Agent Cards in v1.0 early 2026; 150+ orgs at April 2026 one-year mark); native framework support (Google ADK, LangGraph, CrewAI, LlamaIndex Agents, Semantic Kernel, AutoGen); the protobuf-based SDK 1.0.3 surface (route factory pattern; AgentExecutor; TaskUpdater); when A2A is the right shape vs when it's HTTP overhead.
- 📖 [A2A endpoint at production depth](../../concepts/tools/a2a-endpoint-production-depth.md) — Module 6 concept page (~15 min). The six production concerns layered onto Lab 28's in-memory baseline: persistence via `DatabaseTaskStore` (SQLite/PostgreSQL/MySQL via SQLAlchemy AsyncEngine); cryptographic identity via JWS-signed Agent Cards per RFC 7515 (RS256 recommended over the RFC 9864-deprecated bare `EdDSA`); authentication via declarative `SecurityScheme` plus Starlette middleware enforcement (with `.well-known/` kept public by design); streaming via `SendStreamingMessage` and the canonical 4-event SSE sequence; push notifications (discussed; deferred to Module 7 since they need a webhook receiver); OpenTelemetry auto-instrumentation of `DefaultRequestHandler` + `JsonRpcDispatcher` + `EventQueue` + `TaskManager`. Three key-distribution patterns covered (PKI, JWKS, out-of-band); the schema-migration gotcha (SDK doesn't yet ship Alembic migrations).
- 🧪 [Lab 25 — MCP server from scratch](../../labs/25-mcp-server-from-scratch/) — 90-110 min intermediate lab. Build a notes server with 3 tools + 2 resources + 1 prompt; test with MCP Inspector + Python client; walk through 4 schema-inference failure modes; deploy over Streamable HTTP with token-based auth.
- 🧪 [Lab 26 — MCP client from scratch](../../labs/26-mcp-client-from-scratch/) — 90-110 min intermediate lab. Build a `MultiServerMcpClient` with collision-free routing across two servers; layer the five production defenses; wire into a Pattern 01 agent loop with a real Anthropic API call; measure tool-schema token cost; observe why FastMCP 3.1 code mode exists.
- 🧪 [Lab 27 — MCP security threat model](../../labs/27-mcp-security-threat-model/) — 90-110 min intermediate lab. Implement three canonical MCP attacks against an in-process toy server (tool poisoning, response injection, rug-pull); implement three defenses (description-pattern scanner, response sanitization with wrap-and-mark, fingerprint cache + audit log); measure side-by-side what each defense catches and what slips through. No exfiltration, no live attacks against third-party services.
- 🧪 [Lab 28 — A2A endpoint from scratch](../../labs/28-a2a-endpoint-from-scratch/) — 90-110 min intermediate lab. Build a working A2A v1.0 server (`hello-agent`) using the official Python SDK 1.0.3 — Agent Card + AgentExecutor + TaskUpdater + route factory mounted on Starlette. Subprocess-based uvicorn server driven by an httpx client; real JSON-RPC `SendMessage` roundtrip with the `A2A-Version: 1.0` header; full Task lifecycle observed (`submitted` → `working` → `completed`); both common gotchas demonstrated (enqueue-Task-before-TaskUpdater; protocol-version header requirement). Step 8b corrected in Batch 49 — `GetTaskRequest` field is `id`, not the v0.3 `name` alias.
- 🧪 [Lab 29 — A2A endpoint at production depth](../../labs/29-a2a-endpoint-production-depth/) — 110-130 min intermediate lab. Extend Lab 28's `hello_agent_server.py` with five production concerns wired together end-to-end. `DatabaseTaskStore` over SQLite via SQLAlchemy AsyncEngine; JWS-RS256 signed Agent Card with `joserfc`; `APIKeyMiddleware` as Starlette `BaseHTTPMiddleware`; SSE streaming via `SendStreamingMessage` (the canonical 4-event sequence observed via `httpx.AsyncClient.stream`); OpenTelemetry tracing via `SimpleSpanProcessor` writing JSON-line spans (~40 spans across ~15 unique names per request, captured to disk and inspected after the request completes). Three signature-verification gotchas surfaced — the SDK injects three v0.3 backward-compat fields (`preferredTransport`, `protocolVersion`, `url`) into the served card JSON that aren't in the protobuf schema, so the verifier must round-trip through `ParseDict(..., ignore_unknown_fields=True)` + `MessageToDict()` to recover the canonical signed bytes; the JWS payload must be byte-identical to what was signed. Push notifications and OAuth2 deferred to Module 7.
- 🧠 [MCP foundations and server quiz](../../quizzes/foundations/mcp-foundations-and-server.md) — 8 single-select questions covering Modules 1+2 + Lab 25; pass at 6/8.
- 🧠 [MCP client and discovery quiz](../../quizzes/foundations/mcp-client-and-discovery.md) — 8 single-select questions covering Module 3 + Lab 26; pass at 6/8.
- 🧠 [MCP security threat model quiz](../../quizzes/foundations/mcp-security-threat-model.md) — 8 single-select questions covering Module 4 + Lab 27; pass at 6/8.
- 🧠 [A2A foundations quiz](../../quizzes/foundations/a2a-foundations.md) — 8 single-select questions covering Module 5 + Lab 28; pass at 6/8.
- 🧠 [A2A endpoint production-depth quiz](../../quizzes/foundations/a2a-endpoint-production-depth.md) — 8 single-select questions covering Module 6 + Lab 29 (persistence + signed cards + auth + streaming + observability); pass at 6/8.

**Architecture-pattern entries** (the catalog of agent topologies; the top-level patterns directory):
- [Pattern 11 — MCP integration](../../patterns/11-mcp-integration.md) — the architecture-level companion to Modules 1+2; cross-process tool access via MCP. Authored in Batch 44 alongside Pattern 12.
- [Pattern 12 — A2A federation](../../patterns/12-a2a-federation.md) — the architecture-level companion to Modules 5+6 and future Module 7; cross-agent task delegation via the Agent-to-Agent protocol. Authored in Batch 44; Modules 5+6 now operationalize it (foundations + production depth).
- [Top-level `patterns/` catalog](../../patterns/) — the full pattern catalog has 12 entries spanning single-agent through swarm; Patterns 01, 11, 12 authored as of Batch 44

**Existing cross-references that now resolve as module deep-links**:
- [Path 03 Multi-Agent Systems](../03-multi-agent-systems/) — Path 03 covers in-process multi-agent coordination; Path 04 covers cross-process and cross-vendor coordination. The two are complementary, not alternatives
- [Lab 10 supervisor-worker](../../labs/10-supervisor-worker-from-scratch/), [Lab 11 generator-critic](../../labs/11-generator-critic-from-scratch/), [Lab 12 plan-and-execute](../../labs/12-plan-and-execute-from-scratch/), [Lab 13 multi-agent RAG](../../labs/13-multi-agent-rag-from-scratch/) — each lab's anti-scope section currently says *"MCP / A2A coverage — Path 04"*; those forward references now resolve to Modules 1+2+3+4+5+6 (and will resolve to Module 7 once it ships)
- [Path 03 Pattern 5 — Retry policies](../03-multi-agent-systems/patterns/05-retry-policies.md) — the idempotency-key conventions Module 2 references for side-effectful MCP tools

**Security context** (for Module 4's threat model):
- [`security/README.md`](../../security/README.md) — defense-in-depth principles, OWASP Top 10 for LLM Applications, prompt-injection threat model. Path 04 Module 4 will extend with the MCP-specific tool-layer attacks
- [Path 06 v2 Adversarial Red-Teaming concept](../../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the indirect-prompt-injection threat model that MCP tool outputs can carry into the agent

**Observability context** (for Module 2's OTel hook):
- [`concepts/evaluation/opentelemetry-genai-conventions.md`](../../concepts/evaluation/opentelemetry-genai-conventions.md) — what FastMCP 3.0's OTel integration plugs into; Module 2 references this for observability of MCP server tool calls

**Foundational reading** (background for the modules):
- The official MCP specification at [modelcontextprotocol.io](https://modelcontextprotocol.io)
- The [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and [FastMCP framework](https://github.com/prefecthq/fastmcp)
- The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) (used in Lab 25)
- Google's A2A specification at [google-a2a.github.io/A2A](https://google-a2a.github.io/A2A)
- Anthropic's [Building effective agents](https://www.anthropic.com/research/building-effective-agents) (2024) — orchestrator-worker pattern that A2A formalizes

## What's not in this path (anti-scope)

When Path 04 ships, these are explicitly out of scope:

- **In-process multi-agent orchestration** — that's [Path 03](../03-multi-agent-systems/). MCP/A2A are for *cross-process* and *cross-vendor* coordination.
- **Tool selection and design at the prompt level** — that's [Lab 02 from Path 01](../../labs/02-tool-design-and-selection/) and the `concepts/tools/` directory. Path 04 covers the *protocol* layer below those abstractions.
- **General agent observability** — that's [Path 06](../06-evaluation-observability/). Path 04 will mention MCP-specific tracing patterns (Streamable HTTP span attributes) but won't re-derive the observability stack.
- **Vendor lock-in to a specific framework's MCP integration** — Path 04 covers the protocol; LangGraph's MCP support, OpenAI Agents SDK's MCP support, and CrewAI's MCP support are integration *details* that move quickly. The protocol contract is more stable than any framework's wrapper.
- **The protocol turf war** — Path 04 will cover MCP, A2A, and briefly ACP (the three protocols in serious production conversation per zylos.ai March 2026). UCP and other niche protocols are out of scope.

## What comes next

Modules 1+2+3+4+5+6 (MCP build-consume-secure trio + A2A foundations + A2A production depth) shipped across Batches 43, 46, 47, 48, and 49. The natural next priority closes the path:

- **Module 7 (MCP + A2A composition)** — the orchestrator pattern with `A2ACardResolver` + `ClientFactory`; agents using MCP for their own tools while using A2A to coordinate; the canonical hybrid pattern per Pattern 12; the natural home for push notifications (cross-agent delegation is where webhook callbacks earn their keep) and OAuth2 token flows (cross-organizational deployments).

Contributions are welcome. The way to help build Path 04:

1. **Open an issue or discussion** describing which module you want to contribute to (concept page, lab, or both).
2. **Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the source-citation rules and the per-content-type templates are non-negotiable.
3. **Pick one module's scope, not the whole path.** The Path 01/03/06 model is one module per batch with concept + lab + quiz.

## References

Seed references for the modules that will land. Each module will add its own; these are the foundational sources Path 04 will build on:

**MCP**:
- Anthropic (November 2024), *[Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)* — the launch announcement; the foundational design rationale
- The official MCP specification at modelcontextprotocol.io
- dev.to (April 2026), *[Complete Guide to MCP in 2026](https://dev.to/x4nent/complete-guide-to-mcp-model-context-protocol-in-2026-architecture-implementation-and-4a11)* — production architecture, Streamable HTTP transport, OAuth 2.1, FastMCP, A2A comparison; cites 97M monthly SDK downloads + 81,000 GitHub stars as of March 2026
- truthifi.com (May 2026), *[State of MCP 2026](https://truthifi.com/education/state-of-mcp-2026-ai-agents-custom-connectors)* — 10,000+ active public MCP servers under Linux Foundation governance
- arxiv:2601.10955, *Beyond Max Tokens: Stealthy Resource Amplification via Tool Calling Chains in LLM Agents* — the MCP-tool-layer threat model that Module 4 will cover

**A2A**:
- Google Cloud (April 2025), *Announcing the Agent-to-Agent Protocol* — initial launch with 50+ enterprise partners (Salesforce, Accenture, SAP, Deloitte)
- The official A2A specification at google-a2a.github.io/A2A
- intuz.com (April 2026), *[MCP vs A2A: AI Agent Protocol Comparison 2026](https://www.intuz.com/blog/mcp-vs-a2a)* — protocol-comparison framing; Agentic AI Foundation (AAIF) governance with 146 member orgs

**Governance and ecosystem**:
- zylos.ai (March 2026), *[Agent Interoperability Protocols 2026](https://zylos.ai/research/2026-03-26-agent-interoperability-protocols-mcp-a2a-acp-convergence)* — three-protocol landscape (MCP + A2A + ACP); 18,000+ community-indexed MCP servers via Glama.ai and MCP.so
- a2a-mcp.org (March 2026), *[MCP 2026 Roadmap](https://a2a-mcp.org/blog/mcp-2026-roadmap)* — H2 2026 priorities: stateless server operation, automatic discovery through MCP Server Cards, A2A coordination maturation
- digitalapplied.com (March 2026), *[AI Agent Protocol Ecosystem Map 2026](https://www.digitalapplied.com/blog/ai-agent-protocol-ecosystem-map-2026-mcp-a2a-acp-ucp)* — visual ecosystem map of the protocol landscape

**Adjacent repo content**:
- [Top-level `patterns/` catalog](../../patterns/) — architecture-level pattern entries for MCP integration and A2A federation
- [`security/README.md`](../../security/README.md) — security threat models and defense-in-depth principles
- [Path 03 Multi-Agent Systems](../03-multi-agent-systems/) — in-process multi-agent coordination (the complement to Path 04's cross-process focus)
