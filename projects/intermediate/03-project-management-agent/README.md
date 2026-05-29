# Project 03 — Project management agent

> 🟡 Intermediate · ⏱ 25-30 hours · 📍 Build Challenge after Path 01 + Path 03 + Path 04 · 🛠 Verified 2026-05-29

## What you're building

A multi-agent system that takes a high-level project goal ("ship the v2 launch by Friday"), decomposes it into tasks, tracks task status across a real backend (Linear / Jira / GitHub Projects / a flat file), and orchestrates tools to move work forward. The system has at least 2 cooperating agents (planner + executor, or supervisor + workers) and consumes 1-2 MCP servers for tool access.

This is the first project where multiple agents work together. Where Projects 01-02 used a single agent loop with multiple tools, this project introduces topology decisions: who owns the plan, who executes, how do they communicate, what happens when execution fails.

## Why this matters

Three distinguishing claims:

1. **Multi-agent topology is a real architectural decision** — supervisor-worker vs plan-and-execute vs handoff topologies have different failure modes. Building a system that exercises one of them, defending the choice, and observing its failure modes is the canonical multi-agent learning experience.
2. **MCP exposure** — the project consumes existing MCP servers rather than building everything from scratch. This is how production multi-agent systems integrate with the wider ecosystem.
3. **A useful deliverable** — project management is a real workflow. If the system works, you'll use it, and the dogfooding loop surfaces the same failure modes commercial systems hit.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 03 — Multi-Agent Systems** (v1 + at least 3 v2 patterns) | Topology choice + handoff contracts + escalation patterns |
| **Path 04 — Tool Protocols (MCP + A2A)** (at least MCP consumption — Modules 1-3) | Consuming existing MCP servers as tool surfaces |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic API key (or OpenAI / similar) | Model for the agents |
| One project-tracking backend account | Linear, Jira, GitHub Projects, Notion, or even SQLite for fully-local; pick one |
| Comfort with multi-day software builds | Intermediate-tier scope |

Helpful but not required: Path 05 Module 2 (token budgets) — useful if you want per-agent cost budgeting from Path 03 v2 Pattern 4.

## What you'll build

Four concrete deliverables:

1. **A multi-agent system** — at least 2 agents in a defended topology with handoff contracts
2. **An MCP integration** — at least 1 consumed MCP server providing tool access (GitHub, Linear, file system, Notion, etc.)
3. **Three example workflows** — `examples/workflow-01-launch.md`, `examples/workflow-02-bug-triage.md`, `examples/workflow-03-feature-planning.md`. Each demonstrates a different project-management scenario the agents handle end-to-end.
4. **A `WRITEUP.md`** — architecture decisions + topology rationale + observed failure modes

## Architecture overview

The system has four layers. Each maps to specific repo material.

| Layer | Components | Repo material |
|---|---|---|
| **1 — Topology** | Planner agent + Executor agent(s); choose supervisor-worker OR plan-and-execute OR handoff | [Path 03 v1 patterns](../../../learning-paths/03-multi-agent-systems/) |
| **2 — Production substrate** | Handoff contracts (Pattern 1); escalation/fallback (Pattern 3); per-agent retry policies (Pattern 5) | [Path 03 v2 patterns 1, 3, 5](../../../learning-paths/03-multi-agent-systems/patterns/) — at least these three are load-bearing |
| **3 — Tool access** | MCP server consumption for the project-tracking backend; possibly file system or other tools | [Path 04 Modules 1-3](../../../learning-paths/04-tool-protocols-mcp-a2a/) — MCP consume side |
| **4 — State management** | Task state stored in the backend; conversation state in agent memory | [`concepts/memory/`](../../../concepts/memory/) Modules 1-2 |

The recommended starting topology is **supervisor-worker** because the planning/execution split maps naturally to project-management workflows. Plan-and-execute and handoff topologies also work; the choice is one of the ADRs you'll defend.

## The topology decision

Three viable shapes for this project:

| Topology | When to pick it | Tradeoffs |
|---|---|---|
| **Supervisor-worker** | The planner agent reviews each task before delegating; workers report back; supervisor decides next steps | Cleanest separation; planner-agent load can become a bottleneck |
| **Plan-and-execute** | Planner builds the full plan upfront; executor runs each step sequentially; replanning happens on failure | Less coordination overhead; replanning logic must handle failure cases carefully |
| **Handoff** | Agents hand off control as the task progresses; no central coordinator | Hardest to defend in WRITEUP; failure modes harder to trace |

The expected default for this project is supervisor-worker. If you pick a different topology, the WRITEUP needs to defend it against the supervisor-worker alternative.

## Milestones

Six phases, each ending with a working checkpoint.

### Milestone 1 — Pick the backend, define the workflows (2-3 hours)

Choose your project-tracking backend (Linear / Jira / GitHub Projects / Notion / SQLite-flat-file). Define the three workflows you'll exercise:

- **Workflow 1 — Launch coordination**: "ship the v2 launch by Friday" → decompose to subtasks, assign to people, track status
- **Workflow 2 — Bug triage**: "triage these 12 open bugs" → categorize by severity, assign owners, create followup tickets
- **Workflow 3 — Feature planning**: "plan the Q3 roadmap" → decompose initiatives into milestones with dependencies

Write a one-paragraph description of each workflow with the specific inputs (free-text request) and outputs (concrete tasks created in the backend).

**Done when**: backend account is set up; three workflow descriptions are written; you can manually walk through what success looks like for each.

### Milestone 2 — Pick the topology, sketch the agents (3-4 hours)

Pick from the three topology options. For supervisor-worker, design:
- The supervisor agent — system prompt + decision criteria for delegation
- The worker agent(s) — system prompt + tool surface they have access to
- The handoff contract — what data the supervisor passes the worker, what the worker returns

Document the choice in WRITEUP draft. Note the two alternative topologies you rejected and why.

**Done when**: one-page sketch with agent responsibilities, prompts (placeholder OK), and the handoff data structures.

### Milestone 3 — Build the agents without MCP (5-6 hours)

Implement the agents with mock tools first. The mock backend stores tasks in a Python dict; the workflow runs end-to-end against the mock data. The goal is to verify the topology works before adding MCP complexity.

**Done when**: each of the three workflows runs end-to-end against mock data; agents communicate correctly; the supervisor agent makes reasonable delegation decisions.

### Milestone 4 — Add MCP integration (4-5 hours)

Replace the mock backend with an MCP server connection. The available MCP server depends on your backend choice — GitHub MCP server, Linear MCP server, file-system MCP server for the SQLite case. Per [Path 04 Modules 1-3](../../../learning-paths/04-tool-protocols-mcp-a2a/), MCP consumption is the entry point.

**Done when**: the three workflows run against the real backend; tasks are created, updated, queried via MCP; agents see the actual task state.

### Milestone 5 — Add the production substrate (4-5 hours)

Layer 2 — the three Path 03 v2 patterns that are load-bearing for this project:

- **Pattern 1 (Handoff contracts)** — already in Milestones 2-4; verify it's tight
- **Pattern 3 (Escalation and fallback)** — define escalation paths: when does the supervisor escalate to the user? When does a worker fall back to a simpler approach?
- **Pattern 5 (Retry policies)** — distinguish transient (retry) from permanent (escalate) failures

If you have additional time, add Pattern 4 (per-agent cost budgeting) — it composes with the others naturally.

**Done when**: the WRITEUP draft names one failure mode each pattern catches; deliberate fault injection (e.g., make the MCP server return errors) triggers the right escalation path.

### Milestone 6 — Polish, examples, write-up (3-5 hours)

Run the three example workflows end-to-end against the real backend. Capture the conversations. Add error handling for the canonical failures: MCP server timeout, backend rate limit, malformed agent output. Write the WRITEUP.

**Done when**: someone unfamiliar with the project can install dependencies, configure their MCP server, and run one of the example workflows from a description in your repo.

## Evaluation criteria

The intermediate-tier rubric — five dimensions:

| Dimension | What it measures | Intermediate-tier target |
|---|---|---|
| **Topology defense** | Is the multi-agent choice genuinely necessary, or could a single agent have done it? | WRITEUP defends the multi-agent choice with specific scenarios where a single agent would fail |
| **Production substrate** | Are Path 03 v2 Patterns 1, 3, 5 implemented and exercised? | All three patterns visible in code; WRITEUP names one failure mode each pattern catches |
| **MCP integration** | Does the agent system actually use MCP, not just import the library? | Tools genuinely come from an MCP server; the agent doesn't bypass MCP for direct backend calls |
| **Workflow completeness** | Do all three example workflows run end-to-end? | All three workflows execute against the real backend; each produces the expected backend state changes |
| **Cost per workflow** | What does an average workflow run cost? | < $1.00 per workflow at Sonnet pricing; < $0.20 at Haiku-class |

The intermediate-tier dimensions are wider than the beginner-tier's four-dimension rubric because the system surface is wider — topology + multi-pattern substrate + MCP + state.

## Stretch goals

Pick at most two.

- **Pattern 6 (Cross-agent provenance)** — every task action traces back to which agent produced it, with which inputs. Useful for the audit-trail use case.
- **A2A federation** — the supervisor agent calls out to a second agent system via A2A per [Path 04 Modules 4-5](../../../learning-paths/04-tool-protocols-mcp-a2a/). Demonstrates cross-system orchestration.
- **Human-in-the-loop approval gate** — high-stakes actions (assigning to a person, closing a milestone) require user confirmation before execution. Demonstrates the [`patterns/10-human-in-the-loop.md`](../../../patterns/10-human-in-the-loop.md) pattern.
- **Multi-backend support** — agents work against both Linear AND GitHub Projects via different MCP servers. Demonstrates the MCP-everywhere architecture from Project 05's brief.
- **Slack/Discord interface** — the agent posts updates and accepts commands in a channel. Portfolio-screenshot territory.
- **Per-agent cost budgeting (Path 03 v2 Pattern 4)** — soft caps + hard caps per agent. Composes with the other v2 patterns naturally.

## Anti-scope

What you don't need to build for this project:

- **Custom MCP server authoring** — that's Project 05 (Multi-server MCP agent) territory; this project consumes existing servers
- **Full eval harness with judge ensemble** — that's capstone-tier; manual workflow walkthroughs are sufficient at this tier
- **Production deployment at scale** — local + a small hosted demo is fine
- **Multi-tenant support** — single-user system is the assumed shape
- **Custom topology beyond the three named** — pick one of supervisor-worker / plan-and-execute / handoff; don't invent a new shape for this project
- **Background workers / scheduled execution** — synchronous request-response is fine at this tier

## Resources

**Architecture references**:
- [Path 03 — Multi-Agent Systems](../../../learning-paths/03-multi-agent-systems/) — topologies + v2 patterns
- [Path 04 — Tool Protocols (MCP + A2A)](../../../learning-paths/04-tool-protocols-mcp-a2a/) — MCP consumption + integration
- [`patterns/02-router.md`](../../../patterns/02-router.md), [`patterns/03-supervisor-workers.md`](../../../patterns/03-supervisor-workers.md), [`patterns/06-plan-and-execute.md`](../../../patterns/06-plan-and-execute.md) — the three viable topology patterns
- [`patterns/11-mcp-integration.md`](../../../patterns/11-mcp-integration.md) — the MCP integration pattern

**Tool / MCP server documentation**:
- [Model Context Protocol specification](https://modelcontextprotocol.io/) — the protocol your tools speak
- [GitHub's official MCP server](https://github.com/modelcontextprotocol/servers) — recommended starting MCP server if you choose GitHub Projects
- [Linear's API documentation](https://developers.linear.app/) — if you choose Linear
- [Notion's API documentation](https://developers.notion.com/) — if you choose Notion

**Repo cross-references**:
- [Project 02 — PDF Q&A bot](../../beginner/02-pdf-qa-bot/) — the prior beginner project; single-agent + RAG; this project's multi-agent layer is the new dimension
- Project 04 (Data analysis agent) — next intermediate project; same Path 04 prerequisite, different domain (planned)
- Project 05 (Multi-server MCP agent) — next intermediate project; MCP-everywhere architecture (planned)
- [Project 07 (Evaluated multi-agent system)](../../capstone/07-evaluated-multi-agent-system/) — the capstone-tier version of what you'll build here

## Submission guide

Four artifacts go in your repo when you're done:

1. **The system code** — clean structure (agents/, tools/, workflows/, examples/); README with setup + MCP server configuration + usage; `.env.example` for required keys
2. **Three example workflows with transcripts** — `examples/workflow-XX/` each containing the input, the conversation transcript, and the backend state changes
3. **A short screen recording** (1-2 minutes) — one workflow running end-to-end. Helps reviewers see the system without setting it up.
4. **`WRITEUP.md`** — a ~1,000-word document covering:
   - The backend you chose and why
   - The topology decision (with the ADR format: chose / alternatives / why / tradeoffs)
   - ADRs for the three Path 03 v2 patterns you implemented
   - The MCP server choice and one thing that surprised you about integrating it
   - Two failure modes you observed during testing
   - One thing you'd do differently with 2× the time

Add yourself to `docs/community/showcase.md` when you submit.

## What this project leads to

After Project Management Agent, the natural progressions:

- **Project 04 (Data analysis agent)** — same multi-agent + Path 04 foundation, different domain (data + visualizations)
- **Project 05 (Multi-server MCP agent)** — extends MCP consumption from 1 to 3+ servers
- **Project 07 (Evaluated multi-agent system)** — the capstone-tier version; adds Path 06 evaluation + observability deeply

This is the first project where multi-agent topology is genuinely necessary; the patterns you learn here carry forward to every multi-agent project after.
