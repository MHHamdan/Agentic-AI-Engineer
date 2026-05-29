# Build Challenges — Intermediate tier

> 🟡 Intermediate · ⏱ 25-30 hours per project · 📍 After 2-3 paths complete

The intermediate tier covers Build Challenges that combine 2-3 paths and produce systems with real architectural decisions. Where the beginner tier (Projects 01-02) used a single agent loop with multiple tools, the intermediate tier introduces multi-agent topology, MCP integration, or RAG-augmented workloads that span multiple paths.

## Projects

| # | Project | Time | Status |
|---|---|---|---|
| 03 | [Project management agent](./03-project-management-agent/) | 25-30 hours | ✅ Brief shipped (Batch 63) |
| 04 | [Data analysis agent](./04-data-analysis-agent/) | 25-30 hours | ✅ Brief shipped (Batch 64) |
| 05 | [Multi-server MCP agent](./05-multi-server-mcp-agent/) | 25-30 hours | ✅ Brief shipped (Batch 64) |

## What "done" looks like at intermediate tier

Per the [`projects/README.md`](../README.md) tier framing, intermediate-tier projects produce:

- **A running system with multi-agent OR multi-tool-server architecture** — single-agent systems are beginner tier; intermediate tier introduces real composition
- **At least one substantial architectural decision documented** — topology choice OR retrieval strategy OR MCP server selection, defended with the ADR format
- **Three example workflows** — concrete demonstrations of the system's capabilities, committed to the repo with transcripts
- **A short screen recording** (1-2 minutes) — shows the system running end-to-end
- **A medium-length write-up** (~1,000 words) — architecture decisions + observed failure modes + what you'd change

Intermediate tier doesn't require: full eval harness with judge ensemble (capstone tier), production deployment at scale (capstone tier), or compliance/audit infrastructure (capstone tier).

## Picking a project

The three intermediate projects each emphasize different production surfaces:

- **#03 (Project management agent)** — multi-agent topology + MCP integration. Path 03 + Path 04. The "I built a multi-agent system that does something useful" portfolio piece.
- **#04 (Data analysis agent)** — single-agent + Path 02 RAG + Path 06 light evaluation. The "I built a data agent" portfolio piece.
- **#05 (Multi-server MCP agent)** — single-agent + 3+ MCP servers + Path 03 if multi-agent. The "I built the MCP-everywhere architecture" portfolio piece.

Pick the one whose deliverable maps to a role or domain you care about. The intermediate-tier time investment is significant; the project should align with where you're trying to land.

## The intermediate-tier rubric pattern

Intermediate-tier rubrics typically have 5 dimensions:

- **Topology/architecture defense** — the chosen architecture is genuinely necessary
- **Production substrate** — at least 3 of Path 03 v2 patterns implemented (or equivalent for non-multi-agent projects)
- **Tool/MCP integration** — real protocol integration, not just direct API calls bypassed as "MCP"
- **Workflow completeness** — multiple end-to-end workflows demonstrably work
- **Cost discipline** — per-workflow cost meets the tier target

Each dimension has a concrete check. The rubric expands the beginner-tier 4-dimension rubric with the architecture-defense dimension that's new at intermediate scope.

## Cross-references

- [`../README.md`](../README.md) — the canonical project catalog and template
- [`../beginner/`](../beginner/) — the beginner tier (entry-point Build Challenges)
- [`../capstone/`](../capstone/) — the capstone tier (full-stack systems)
- [`../../learning-paths/09-capstones/`](../../learning-paths/09-capstones/) — the curated reading-list view of this catalog
- [Path 03 v2 patterns](../../learning-paths/03-multi-agent-systems/patterns/) — the operational substrate intermediate and capstone projects build on
- [Path 04 — Tool Protocols](../../learning-paths/04-tool-protocols-mcp-a2a/) — the MCP consumption + integration material
