# Path 09 — Capstone Projects

> 🔴 Advanced · ⏱ 15–40 hours per project · 📍 Start here after at least three of Paths 01-07 · ✅ **v1 COMPLETE — all 8 project briefs shipped** (Batches 62-65)

> ✅ **v1 COMPLETE — all 8 project briefs shipped across 4 batches.** Batch 62 opened Path 09 with the bookend pair (Beginner #01 + Capstone #07); Batch 63 continued with the next bookend pair (Beginner #02 + Intermediate #03), opening [`projects/intermediate/`](../../projects/intermediate/); Batch 64 completed the Intermediate tier (Projects #04 + #05); **Batch 65 closes Path 09 v1 with the final capstone-tier pair (Projects #06 Financial research analyst + #08 Production-ready deep research)**. All three tiers are complete; the v1 phase of Path 09 is structurally done. Future work on this path is continuous improvement (project starter code; reference solutions; community-contributed variants), not gap-filling.

## Who this path is for

Engineers past the learning phase who want a portfolio project. You've completed at least three of Paths 01-07 and you have a real deployment target — local, hosted, or production. You want a substantial build that combines work from multiple paths, with traces, evals, deployment, and a write-up you can put in front of a recruiter or a tech lead.

This path is *not* a learning path in the same sense as 01-08. It's a catalog of substantial Build Challenges and Capstone Projects — each one a multi-day to multi-week build that draws on material from across the repo.

## What you'll be able to do

When this path is complete (i.e., when you've finished one or more of the projects), you'll have:

- **End-to-end agentic systems** with concept-grounded design, executable labs as references, observable traces, evaluation harnesses, and deployment configurations
- **A portfolio artifact you can show off** — repository, write-up, screenshots, traces. Real systems, not tutorial recreations
- **Cross-path integration practice** — every capstone draws from at least three of Paths 01-07. The capstones are where the paths' individually useful skills compose into something larger than any one path covers
- **A defensible architecture decision record** — every capstone has a written rationale for the choices you made: which framework, which topology, which retrieval strategy, which observability stack, which deployment target

## Prerequisites

- **At least three of Paths 01-07 complete.** The exact three depend on the project. Beginner projects need only Path 01. Capstone projects typically need Paths 01 + 02 + 03 + 06 at minimum.
- **A real deployment target.** Local-only, FastAPI + Docker, hosted (Render, Railway, Fly.io), serverless (Vercel, AWS Lambda), or production (your team's actual infrastructure). Pick one before you start; the architecture depends on it.
- **Real-world software-engineering practice.** Capstones are full-stack builds; comfort with git, testing, deployment, and writing technical documentation is assumed.

## Path structure — the project catalog

Capstones come in three tiers. The catalog (mirrored from [`projects/README.md`](../../projects/README.md), the canonical source):

### Beginner tier — Build Challenges (~15-20 hours)

For engineers who've completed Path 01 and want a first substantial build:

| # | Project | Draws from | Status |
|---|---|---|---|
| 01 | **Personal research assistant** — multi-source web research with citations | Path 01 (foundations); Path 02 (light retrieval) | ✅ Brief shipped (Batch 62) — [`projects/beginner/01-personal-research-assistant/`](../../projects/beginner/01-personal-research-assistant/) |
| 02 | **PDF Q&A bot** — chunked PDF ingestion, retrieval, citation-grounded answers | Path 01; Path 02 (canonical RAG) | ✅ Brief shipped (Batch 63) — [`projects/beginner/02-pdf-qa-bot/`](../../projects/beginner/02-pdf-qa-bot/) |

### Intermediate tier — Build Challenges (~25-30 hours)

For engineers who've completed 2-3 paths and want to combine them:

| # | Project | Draws from | Status |
|---|---|---|---|
| 03 | **Project management agent** — task decomposition, status tracking, multi-tool orchestration | Path 01; Path 03 (plan-and-execute or supervisor-worker); Path 04 (MCP for tool access) | ✅ Brief shipped (Batch 63) — [`projects/intermediate/03-project-management-agent/`](../../projects/intermediate/03-project-management-agent/) |
| 04 | **Data analysis agent** — analyze CSVs, generate visualizations, write reports with citations | Path 01; Path 02; Path 06 (light evaluation) | ✅ Brief shipped (Batch 64) — [`projects/intermediate/04-data-analysis-agent/`](../../projects/intermediate/04-data-analysis-agent/) |
| 05 | **Multi-server MCP agent** — agent that consumes 3+ MCP servers; demonstrates the MCP-everywhere architecture | Path 01; Path 04 (MCP, deeply); Path 03 (multi-agent if needed) | ✅ Brief shipped (Batch 64) — [`projects/intermediate/05-multi-server-mcp-agent/`](../../projects/intermediate/05-multi-server-mcp-agent/) |

### Capstone tier — Full-stack systems (~30-40+ hours)

For engineers who've completed Paths 01 + 02 + 03 + 06 (the production-readiness backbone):

| # | Project | Draws from | Status |
|---|---|---|---|
| 06 | **Financial research analyst** — multi-agent system with regulated-domain provenance, structured reports, audit trail | Path 01-04 + Path 06; Path 03 Pattern 6 (provenance) as load-bearing | ✅ Brief shipped (Batch 65) — [`projects/capstone/06-financial-research-analyst/`](../../projects/capstone/06-financial-research-analyst/) |
| 07 | **Evaluated multi-agent system** — fully instrumented multi-agent system with online evals, drift detection, calibrated judges, regression promotion | Path 01-03 + Path 06 (deeply); Path 06 v2 (all six v2 directions) | ✅ Brief shipped (Batch 62) — [`projects/capstone/07-evaluated-multi-agent-system/`](../../projects/capstone/07-evaluated-multi-agent-system/) |
| 08 | **Production-ready deep research** — long-running research agent with checkpointing, durable execution, cost budgets, HITL approval gates | Path 01-03 + Path 06 + Path 07 (when shipped); Path 03 v2 patterns as the operational substrate | ✅ Brief shipped (Batch 65) — [`projects/capstone/08-production-ready-deep-research/`](../../projects/capstone/08-production-ready-deep-research/) |

## What you can read right now

The [`projects/`](../../projects/) directory and the supporting infrastructure are already on disk:

**The project catalog and template** (existing):
- [`projects/README.md`](../../projects/README.md) — the canonical project catalog; project brief template; tier definitions; the "how to approach a project" five-step heuristic (read brief end-to-end → pick deployment target up front → build a tiny version first → add observability early → evaluate before you ship)

**Reference labs that approach capstone scope** (existing — these are the closest thing to capstones the repo currently ships):
- [Lab 13 — Multi-agent RAG from scratch](../../labs/13-multi-agent-rag-from-scratch/) — the multi-agent + RAG combination that capstones 06 and 07 will extend
- [Lab 16 — Multi-agent evaluation from scratch](../../labs/16-multi-agent-evaluation-from-scratch/) — the evaluation harness that capstone 07 will productionize
- [Lab 22 — Multi-turn evaluation](../../labs/22-multi-turn-evaluation/) — the conversational evaluation pattern that capstone 08 will build on
- [Lab 24 — Adversarial red-teaming at scale](../../labs/24-adversarial-red-teaming-at-scale/) — the safety dimension that capstones 06-08 will incorporate

**The community showcase** (where finished work lands):
- [`docs/community/showcase.md`](../../docs/community/showcase.md) — when you finish a capstone, this is where you add a screenshot + paragraph. We highlight community builds in the README rotation.

**Architecture and operational substrate** (what your capstone will build on):
- [Path 03 v2 patterns](../03-multi-agent-systems/patterns/) — six production patterns (handoff contracts, shared-state boundaries, escalation/fallback, per-agent cost budgeting, retry policies, cross-agent provenance) that capstones 06-08 will all use
- [Path 06 v2 directory](../06-evaluation-observability/) — recipes, patterns, projects (Path 06 already has its own three projects under [`projects/`](../06-evaluation-observability/projects/) for the eval/observability slice); these are evaluation-focused capstones that complement Path 09's broader capstones
- [Top-level `patterns/` catalog](../../patterns/) — the architecture-pattern catalog you'll consult when making topology decisions
- [`production/README.md`](../../production/README.md) and [`security/README.md`](../../security/README.md) — the playbooks capstone 08 will lean on

## How to approach a capstone

The five-step heuristic from [`projects/README.md`](../../projects/README.md):

1. **Read the brief end-to-end** before writing any code. The architecture diagram tells you which paths the project draws from.
2. **Pick a deployment target up front** — local-only, FastAPI + Docker, or hosted. Different targets change the architecture.
3. **Build a tiny version first.** Get end-to-end flow working with stub data before optimizing any one piece.
4. **Add observability early.** A traced agent is a debuggable agent. Path 06's tracing patterns apply at the capstone scale.
5. **Evaluate before you ship.** Even a 20-example golden set tells you more than running it once and checking the output.

Adding two heuristics specific to Path 09 capstones:

6. **Write the architecture decision record (ADR) as you go.** Not at the end. The decisions you'll be asked about in a portfolio review are the ones you made and forgot, not the ones you remember vividly.
7. **Pick patterns over frameworks.** Frameworks change quarterly; patterns survive. A capstone that demonstrates Pattern 1 (handoff contracts) + Pattern 4 (cost budgeting) + Pattern 6 (provenance) is more durable as a portfolio artifact than a capstone that demonstrates "I used LangGraph v0.3."

## What's not in this path (anti-scope)

When the capstone briefs land, these are explicitly out of scope:

- **Toy reproductions of existing tutorials.** Every capstone must produce a system that solves a real problem; "build a chatbot" doesn't qualify.
- **Pure-research benchmarks.** Capstones are engineering artifacts; if you want to publish a benchmark, that's a different (also worthwhile) discipline.
- **Single-path projects.** Every capstone draws from at least three of Paths 01-07. A project that uses only Path 01 belongs in the Foundations path as a Build Challenge.
- **Vendor-bound builds.** Capstones should be portable enough that swapping LangGraph → CrewAI or OpenAI → Anthropic is a documented exercise, not a rewrite. The architecture-decision record should make this explicit.

## What comes next

Contributions are welcome but go through more design review than recipes or concept pages — per [`projects/README.md`](../../projects/README.md), open a Discussion before drafting a new capstone brief.

The way to help:

1. **Open a GitHub Discussion** describing the capstone brief you want to write. Include: the problem the project solves, which paths it draws from, the architecture sketch, and the deliverable rubric.
2. **After discussion approval, write the brief** following the per-tier template that will land in [`projects/`](../../projects/) once the first briefs ship.
3. **Optional: contribute a reference solution.** Capstones don't require reference implementations the way labs do — the value of a capstone is the *brief*, the rubric, and the architecture decisions. Reference solutions are useful but optional.

The natural first batch for Path 09 would be capstones 06 and 07 (the multi-agent-evaluation pair) — they exercise the highest concentration of already-shipped paths (Paths 01 + 02 + 03 + 06).

## References

The foundational sources Path 09 builds on:

**Capstone design philosophy**:
- [`projects/README.md`](../../projects/README.md) — the canonical project catalog and template
- Anthropic (2024), *[Building effective agents](https://www.anthropic.com/research/building-effective-agents)* — the production-grounded essay; every capstone draws on this

**Portfolio-project standards** (what makes a capstone defensible):
- Architecture Decision Record (ADR) format — see Michael Nygard's *Documenting Architecture Decisions* (2011) for the canonical short-form template
- The Twelve-Factor App methodology — for the production-deployment dimension

**Adjacent repo content**:
- [`projects/`](../../projects/) — the canonical project directory; this path is the curated reading-list view of it
- [Path 06 v2 Projects](../06-evaluation-observability/projects/) — three evaluation/observability capstones; complementary to Path 09's broader capstones
- [Path 03 v2 patterns](../03-multi-agent-systems/patterns/) — the operational substrate every capstone will use
- [`production/README.md`](../../production/README.md), [`security/README.md`](../../security/README.md) — the playbooks capstone 08 in particular leans on
- [`docs/community/showcase.md`](../../docs/community/showcase.md) — where finished capstones land
