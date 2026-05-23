# Patterns

Architecture patterns for agentic systems. Each page answers: *what is this pattern, when does it work, when does it fail, and what does it cost?*

A pattern page is the right read when you're trying to make an architecture decision — not when you're trying to understand a concept (use [`concepts/`](../concepts/)) or run code (use [`labs/`](../labs/) or [`recipes/`](../recipes/)).

## Format

Every pattern page follows the same structure:

1. **Intent** — one sentence on what the pattern does.
2. **Diagram** — a Mermaid diagram of the topology or flow.
3. **When to use** — two or three concrete situations.
4. **When NOT to use** — two or three anti-patterns.
5. **Implementation sketch** — pseudocode or a minimal real snippet.
6. **Real-world examples** — known systems or papers using it.
7. **Tradeoffs** — cost / latency / complexity / reliability.
8. **Related patterns** — links to alternatives and combinations.

Full template is in [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Catalog

| # | Pattern | What it solves |
|---|---|---|
| 01 | Single-agent tool use | One LLM + a few tools, no orchestration |
| 02 | Router | Send each request to a specialized handler |
| 03 | Supervisor + workers | One coordinator delegates to several specialists |
| 04 | Hierarchical teams | Supervisors of supervisors for large problems |
| 05 | Swarm hand-off | Peer agents hand off control without a central coordinator |
| 06 | Plan-and-execute | Generate a plan, then execute steps |
| 07 | Reflection / self-correction | Critique and revise outputs in a loop |
| 08 | Agentic RAG | Retrieval as a tool the agent chooses to use |
| 09 | Deep research | Iterative search, synthesis, and citation |
| 10 | Human-in-the-loop | Pause for human approval at decision points |
| 11 | MCP integration | Standard protocol for tools and data |
| 12 | A2A federation | Standard protocol between agents |

## Picking a pattern

A first-pass decision aid:

| If you're solving... | Start with pattern |
|---|---|
| A single, scoped task with a few tools | 01 Single-agent |
| Multiple distinct task types | 02 Router |
| One complex task that decomposes cleanly | 03 Supervisor or 06 Plan-and-execute |
| A complex task with hierarchical subproblems | 04 Hierarchical |
| Loosely-coupled specialists that pass work peer-to-peer | 05 Swarm |
| A task where the first answer is usually wrong | 07 Reflection |
| Anything retrieval-heavy | 08 Agentic RAG |
| A research / synthesis task | 09 Deep research |
| Anything with high stakes or compliance | 10 Human-in-the-loop |
| Multi-source tool access | 11 MCP |
| Multi-agent across orgs or codebases | 12 A2A |

Patterns combine. A common production stack is *supervisor* + *agentic RAG* + *human-in-the-loop* + *MCP*. The individual pattern pages call out the most common combinations.

## Contributing

A new pattern page is a substantial contribution. We'd rather have 12 strong patterns than 30 thin ones, so new additions go through more review than recipes or concepts. Open a Discussion before investing time on a new pattern.

> 🟢 Patterns are classified **stable**. The names and shapes don't change quickly, even when the implementations do.
