# Capstone Projects

> 🔴 Capstone · ⏱ 30-40+ hours per project · 📍 After Paths 01 + 02 + 03 + 06 (the production-readiness backbone)

The capstone tier covers full-stack agentic systems. These are end-to-end builds that combine work from at least four paths, include evaluation and observability infrastructure, and produce portfolio-quality artifacts a recruiter or tech lead can review.

Capstones aren't measured in lines of code — they're measured in *cross-path integration* and *operational discipline*. The portfolio claim is "I can ship production-mature agentic systems," not "I can write a lot of code."

## Projects

| # | Project | Time | Draws from | Status |
|---|---|---|---|---|
| 06 | Financial research analyst | 30-40+ hours | Paths 01-04 + Path 06; Path 03 Pattern 6 (provenance) load-bearing | 📋 Brief planned |
| 07 | [Evaluated multi-agent system](./07-evaluated-multi-agent-system/) | 30-40 hours | Paths 01-03 + Path 06 (deeply); Path 06 v2 all six directions | ✅ Brief shipped (Batch 62) |
| 08 | Production-ready deep research | 30-40+ hours | Paths 01-03 + Path 06 + Path 07; Path 03 v2 patterns as operational substrate | 📋 Brief planned |

## What "done" looks like at capstone tier

Per the [`projects/README.md`](../README.md) tier framing, capstone-tier projects produce:

- **A running system** — not just code; an end-to-end deployment (local, hosted, or production) someone else can use
- **Observable traces** — every decision the system makes is inspectable; the trace export sample is part of the submission
- **A defended architecture** — every layer has an Architecture Decision Record (chose / alternatives / why / tradeoffs)
- **A regression set** — failures get captured and re-run; deploys can be blocked by regressions
- **A long-form write-up** (~2,000-3,000 words) — the architecture story, the failure modes you observed, what you'd do differently
- **A screenshot or 2-3 minute screen recording** of the working system + its observability layer
- **Submission to `docs/community/showcase.md`** — capstone-tier submissions get highlighted in the project gallery

Capstone tier requires: cross-path integration (at least 4 of Paths 01-07); production-mature discipline (observability, eval, deployment); architectural defensibility (ADRs per layer). These are the differentiators that make the capstone portfolio-worthy.

## Picking a project

The three capstone-tier projects each emphasize different production surfaces:

- **#06 (Financial research analyst)** — regulated-domain discipline. Provenance, audit trails, structured reports. The "regulatory compliance" angle.
- **#07 (Evaluated multi-agent system)** — observability and evaluation depth. Judge ensembles, drift detection, regression promotion. The "I know when my system is broken" angle.
- **#08 (Production-ready deep research)** — long-running execution. Checkpointing, durable execution, cost budgets, HITL approval gates. The "I can ship a system that runs for hours without falling over" angle.

Pick the one whose differentiation maps to a role or domain you care about. The capstone time investment is significant; the project should align with where you're trying to land.

## Architecture decision records (ADRs)

Every capstone-tier project includes ADRs per architecture layer. The format:

> **Decision**: [what I chose]
>
> **Alternatives considered**: [what else was on the table]
>
> **Rationale**: [why I picked this one]
>
> **Tradeoffs**: [what I gave up to get this]

ADRs are 3-5 sentences each. The total ADR set (typically 5-7 per capstone) becomes a section of the WRITEUP.md. Defending architecture choices is what separates a tutorial recreation from a portfolio artifact.

## Submission

When you finish, the `docs/community/showcase.md` submission lists your repo + a one-paragraph description + a screenshot or screen recording + a one-line capstone-tier badge ("Capstone #07: Evaluated multi-agent system"). Capstone-tier submissions get featured in the project gallery and the README rotation.

## Cross-references

- [`../README.md`](../README.md) — the canonical project catalog and template
- [`../beginner/`](../beginner/) — the beginner tier (entry-point Build Challenges)
- [`../../learning-paths/09-capstones/`](../../learning-paths/09-capstones/) — the curated reading-list view of this catalog, organized by which prior paths each project draws on
- [Path 03 v2 patterns](../../learning-paths/03-multi-agent-systems/patterns/) — the six production patterns all three capstones build on
- [Path 06 v2](../../learning-paths/06-evaluation-observability/) — the eval/observability material capstones 06-08 all integrate
