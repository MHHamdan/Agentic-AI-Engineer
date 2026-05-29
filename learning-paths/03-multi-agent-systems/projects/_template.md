# Project N — [Project name]

> 🔴 Advanced · ⏱ ~XX min reading · 🛠 ~X-X day build · Verified YYYY-MM-DD

<!--
This is the template for adding a Path 03 production capstone project.
Copy this file, rename to NN-project-name.md, fill in each section, delete these comments.

Project shape is deliberately larger than patterns (8 sections) — 12 sections, ~35-50 min
reading, multi-day build. Four sections distinguish projects from patterns —
milestones, integration layer, acceptance rubric, failure modes — because projects are
buildable capstones rather than reference docs.

See README.md for the shape rationale and Projects 01/02/03 for examples.

PLACEHOLDER CONVENTION: For path placeholders in the body, use prose with inline-code
(e.g. "the relevant lab at `labs/NN-some-lab/`") NOT actual markdown link syntax. The
link-sweep tool flags placeholder paths inside markdown link syntax as broken — even
when they're documentation of patterns. The prose+code form sidesteps the parser false
positive. See the references section for the recommended pattern for citing real links.

LINK-CHECKER FALSE-POSITIVE: Python dict-then-call syntax like
`handler = HANDLERS["foo"]; return handler(args)` is the safe form; the unsafe
form (dictionary access immediately followed by call parentheses) triggers a
link-checker false positive (the `]` + `(` adjacency gets misparsed as a
markdown link target). Always restructure to two-line variable-assignment form.
-->

## Project brief

<!--
1-2 paragraphs.

What are you building? Deployment target? Scale assumption? Why pick this project over
the other two? Reference the patterns this project composes.
-->

[1-2 paragraphs.]

**Deployment target**: [stack choice with rationale]

**Scale assumption**: [traffic / team size / framework constraint]

This project composes Pattern X (placeholder path `patterns/XX-name.md`) + Pattern Y (placeholder path `patterns/YY-name.md`) + Path 03 v2 patterns NN, MM (placeholder path `patterns/`). [Brief framing of when to pick this vs the other projects.]

## Prerequisites

<!--
- Required Path 03 v1 labs
- Required Path 03 v2 patterns
- Required top-level patterns
- Required Path 04 modules (if applicable)
- External tooling assumptions

Be explicit: "If any of these are gaps, fix them first."
-->

Before starting, you should have completed:

- **Required Path 03 v1 labs**: [Labs NN with paths]
- **Required Path 03 v2 patterns**: [pattern names with links]
- **Required top-level patterns**: [pattern names with links]
- **Required Path 04 modules** (if applicable): [modules with links]
- **External**: [accounts, infrastructure, framework choices, API keys]

If any of those are gaps, fix the gaps first. Projects assume the prerequisites are solid.

## What you'll have when done

<!--
8-12 bullets. Concrete deliverable list. Each should be testable.

Example: "A FastAPI service running [agent], instrumented with [tooling], deployed in Docker."
Not: "An understanding of how to instrument an agent."
-->

- [Concrete deliverable 1]
- [Concrete deliverable 2]
- ...

## Architecture at a glance

<!--
One detailed mermaid diagram of the full system. Includes:
- User-facing entry point
- Agent components (router, supervisor, specialists)
- State store / checkpointing
- Observability layer
- External API integrations
- Failure / fallback paths

Use consistent color coding:
- fill:#fff4e6 — user/external entry
- fill:#e6f2ff — workers / specialists
- fill:#ffd6a5 — supervisor / orchestrator
- fill:#f3e8ff — observability / state
- fill:#e6f6ec — terminal / success state
- fill:#f7e4d4 — degraded / fallback
-->

```mermaid
flowchart LR
    [your diagram here]
```

[1-2 paragraph narrative explaining the architecture choices.]

## Build milestones

<!--
4-7 milestones in build order. Each gets:
- Header (M1, M2, ...) with name + time estimate
- Goal (one sentence)
- Scope (3-6 bullets — what's IN this milestone)
- Done when (1-3 bullets — testable completion check)

The time estimates should be realistic (days not hours for most milestones).
The "done when" check is what a code reviewer would look for.
-->

### M1 — [Name] (~X day(s))

**Goal**: [one sentence]

**Scope**:
- [3-6 bullets]

**Done when**:
- [1-3 testable bullets]

### M2 — [Name] (~X day(s))

[...]

## The integration layer

<!--
Table mapping each milestone to the existing repo content it builds on.
Columns: Milestone | Path 03 v1 lab | Path 03 v2 pattern | Top-level pattern | Path 04 (if applicable)

This is the section that distinguishes a project from a recipe — projects EXPLICITLY
map every milestone back to the prerequisite content the learner has already done.
-->

| Milestone | Path 03 v1 lab | Path 03 v2 pattern | Top-level pattern | Path 04 module |
|---|---|---|---|---|
| M1 | Lab X — placeholder `labs/NN-lab-name/` | Pattern N — placeholder `learning-paths/03-multi-agent-systems/patterns/NN-name.md` | Pattern NN — placeholder `patterns/NN-name.md` | — |
| M2 | ... | ... | ... | ... |

## Acceptance rubric

<!--
6-11 testable PR-review criteria. Each line should answer "did the team actually
ship this correctly?" Concrete enough that a reviewer can check it against the code.

NOT philosophical ("the agent handles errors well"). Concrete ("every tool call has
a try-except that escalates to the supervisor on the third retry with a structured
error envelope").
-->

A PR is ready to ship when:

1. [Concrete criterion]
2. [Concrete criterion]
...

## Common failure modes and recoveries

<!--
5-8 mistakes that derail teams. Each entry:
- Failure mode name (bold)
- 1-2 sentence description of how it manifests
- 1-2 sentence recovery / how to fix

Pull from real production experience and from the 2026 literature. The point is to
let teams skip the mistakes others have already made.
-->

### [Failure mode name]

[Description.]

**Recovery**: [Fix.]

### [Failure mode name]

[...]

## Operational checklist (pre-launch)

<!--
12-18 items grouped by layer: instrumentation, deployment, security, monitoring,
runbook. Each item is a yes/no question.

The list is deliberately exhaustive — the team going through it before launch should
catch the things they would have otherwise discovered in incident response.
-->

### Instrumentation

- [ ] [Item]
- [ ] [Item]

### Deployment

- [ ] [Item]

### Security

- [ ] [Item]

### Monitoring

- [ ] [Item]

### Runbook

- [ ] [Item]

## Cost envelope

<!--
Table: scale tier × monthly cost. Three columns minimum: 10K, 100K, 1M units/month
(units = conversations, queries, traces — define per project).

Cite the source of each cost component. Note the high-variance components.

Add a paragraph below the table calling out the components most likely to change
within 6 months.
-->

| Scale | LLM tokens | Infrastructure | Observability | Total |
|---|---|---|---|---|
| 10K [units]/mo | $XX | $XX | $XX | $XX |
| 100K [units]/mo | $XX | $XX | $XX | $XX |
| 1M [units]/mo | $XX | $XX | $XX | $XX |

[1 paragraph on the high-variance components.]

## Extensions and where to go next

<!--
4-6 follow-ups. Each is a sentence or two pointing at the next build the team can
take on after shipping this project.

These are NOT "what we didn't ship" (that's a different list). These are "given the
shipped version works, what's the natural next move?"
-->

- **[Extension 1]** — [Description.]
- **[Extension 2]** — [Description.]
- ...

## References + further reading

<!--
Group references:
- Path 03 + Path 04 repo content (with links)
- 2026 production guides (with links)
- Foundational papers (with links and dates)
- Framework docs (with links)

For the recommended-pattern of citing repo content as reference (NOT as the body's
forward-reference annotations), use markdown links here. The link checker accepts
the references-section pattern.
-->

**Path 03 + Path 04 repo content**:
- [Path 03 README](../README.md)
- Pattern X (top-level) — placeholder path `patterns/XX-name.md`
- ...

**2026 production guides**:
- [Author/Org (Month YYYY), *Title*](https://url) — [1-sentence framing of what's relevant]
- ...

**Foundational papers**:
- [Author et al. (Year), *Title*](https://url) — [1-sentence framing]
- ...

**Framework docs**:
- [Framework name docs](https://url) — [version + verified date]
- ...
