# Path 04 — Tool Protocols (MCP + A2A)

> 🟡 Intermediate · ⏱ 6–10 hours (planned) · 📍 Start here once you've completed Path 01 · 📋 **Scaffold — content forthcoming**

> ⚠️ **This path is a scaffold.** The structure, prerequisites, and learning outcomes are locked. The actual concept pages, labs, and module content land in future batches. The "What you can read right now" section below points at real, existing artifacts in the repo that cover adjacent material — those links work today.

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
| 1 | **MCP foundations** — protocol spec, JSON-RPC 2.0 wire format, client-server lifecycle, transports (stdio vs Streamable HTTP) | 📋 Planned |
| 2 | **Building an MCP server** — FastMCP / TypeScript SDK; exposing tools, resources, prompts; OAuth 2.1 authentication | 📋 Planned |
| 3 | **Building an MCP client** — consuming external servers from your agent; tool discovery via Server Cards (2026 H2 spec); error handling | 📋 Planned |
| 4 | **MCP security and the tool-layer threat model** — the arxiv:2601.10955 resource-amplification attack; safe-default tool exposure; rate limits and idempotency at the server | 📋 Planned |
| 5 | **A2A foundations** — protocol spec, agent capability discovery, task delegation, result sharing | 📋 Planned |
| 6 | **Building an A2A endpoint** — exposing your agent for delegation; capability descriptors; multi-agent task graphs | 📋 Planned |
| 7 | **MCP + A2A together** — the hybrid 40-60% workflow-velocity improvement pattern per a2a-mcp.org March 2026; CRM-and-knowledge-base-via-MCP + technical-delegation-via-A2A | 📋 Planned |

Each module will follow the Path 01/03/06 shape: concept page(s) + lab + quiz, with reference solutions where labs apply.

## What you can read right now

The repo already has substantive material that maps to this path. None of it is a duplicate of what Path 04 will eventually ship — these are adjacent artifacts that will be cross-referenced from the modules above when they land:

**Architecture-pattern entries** (the catalog of agent topologies; the top-level patterns directory):
- [Top-level `patterns/` catalog](../../patterns/) — Patterns 11 (MCP integration) and 12 (A2A federation) are the architecture-level views; this path will build the implementation-level companion content
- The full pattern catalog has 12 entries spanning single-agent through swarm; the MCP/A2A entries sit alongside the topologies Path 03 implements

**Existing cross-references that will become module deep-links**:
- [Path 03 Multi-Agent Systems](../03-multi-agent-systems/) — Path 03 covers in-process multi-agent coordination; Path 04 covers cross-process and cross-vendor coordination. The two are complementary, not alternatives
- [Lab 10 supervisor-worker](../../labs/10-supervisor-worker-from-scratch/), [Lab 11 generator-critic](../../labs/11-generator-critic-from-scratch/), [Lab 12 plan-and-execute](../../labs/12-plan-and-execute-from-scratch/), [Lab 13 multi-agent RAG](../../labs/13-multi-agent-rag-from-scratch/) — each lab's anti-scope section currently says *"MCP / A2A coverage — Path 04"*; those forward references will resolve to Path 04's modules

**Security context** (for Module 4's threat model):
- [`security/README.md`](../../security/README.md) — defense-in-depth principles, OWASP Top 10 for LLM Applications, prompt-injection threat model. Path 04 Module 4 will extend with the MCP-specific tool-layer attacks
- [Path 06 v2 Adversarial Red-Teaming concept](../../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the indirect-prompt-injection threat model that MCP tool outputs can carry into the agent

**Foundational reading** (start here before the path lands):
- The official MCP specification at modelcontextprotocol.io
- The MCP GitHub organization at github.com/modelcontextprotocol
- Google's A2A specification at google-a2a.github.io/A2A
- Anthropic's [Building effective agents](https://www.anthropic.com/research/building-effective-agents) (2024) — orchestrator-worker pattern that A2A formalizes

## What's not in this path (anti-scope)

When Path 04 ships, these are explicitly out of scope:

- **In-process multi-agent orchestration** — that's [Path 03](../03-multi-agent-systems/). MCP/A2A are for *cross-process* and *cross-vendor* coordination.
- **Tool selection and design at the prompt level** — that's [Lab 02 from Path 01](../../labs/02-tool-design-and-selection/) and the `concepts/tools/` directory. Path 04 covers the *protocol* layer below those abstractions.
- **General agent observability** — that's [Path 06](../06-evaluation-observability/). Path 04 will mention MCP-specific tracing patterns (Streamable HTTP span attributes) but won't re-derive the observability stack.
- **Vendor lock-in to a specific framework's MCP integration** — Path 04 covers the protocol; LangGraph's MCP support, OpenAI Agents SDK's MCP support, and CrewAI's MCP support are integration *details* that move quickly. The protocol contract is more stable than any framework's wrapper.
- **The protocol turf war** — Path 04 will cover MCP, A2A, and briefly ACP (the three protocols in serious production conversation per zylos.ai March 2026). UCP and other niche protocols are out of scope.

## What comes next

Contributions are welcome. The way to help build Path 04:

1. **Open an issue or discussion** describing which module you want to contribute to (concept page, lab, or both).
2. **Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the source-citation rules and the per-content-type templates are non-negotiable.
3. **Pick one module's scope, not the whole path.** The Path 01/03/06 model is one module per batch with concept + lab + quiz.

The natural first batch for Path 04 would be Module 1 (MCP foundations) + Module 2 (Building an MCP server) shipped together — the architectural-pair shape that Path 03 v1 used for Module 1 supervisor-worker.

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
