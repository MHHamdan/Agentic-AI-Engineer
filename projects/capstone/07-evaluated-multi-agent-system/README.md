# Project 07 — Evaluated multi-agent system

> 🔴 Capstone · ⏱ 30-40 hours · 📍 Capstone-tier — after Paths 01 + 03 + 06 (v1+v2 deeply) · 🛠 Verified 2026-05-29

## What you're building

A fully instrumented multi-agent system with online evaluation, drift detection, calibrated judges, and regression promotion. The system has at least 3 agents working in a real topology (supervisor-worker, plan-and-execute, or specialized routing — pick one and defend it); every agent decision is traced via OpenTelemetry; every output is scored by a judge ensemble; drift signals fire when performance degrades; and failed conversations promote into a versioned regression set that re-runs on every change.

This is the *production-evaluation pattern* from Path 06 v1 + v2 made real. Where Path 06 walks through each piece in isolation, this capstone integrates all of them into one running system. The deliverable is a system with traces and dashboards a non-engineer can look at and understand whether the system is working.

Per the [Coralogix April 2026 framing](https://coralogix.com/ai-blog/agentic-ai-observability/): "AI observability has matured significantly... evaluation layer on top, since agent-specific failures like wrong tool selection or drifted retrieval don't show up in HTTP-level metrics." This capstone builds the evaluation layer concretely.

## Why this matters

Three distinguishing claims for a portfolio:

1. **Production multi-agent systems are hard** — the ones in the wild routinely fail in ways the team doesn't notice for days. Building one with observable failure modes is what separates "I ran a tutorial" from "I shipped to production-mature discipline."
2. **The eval/observability layer is the differentiator** — every team can wire up agents. The teams that ship reliably are the ones that catch regressions before users do. This capstone demonstrates the catching machinery.
3. **It composes the entire repo** — Path 01 (foundations), Path 03 (multi-agent topologies + the six v2 patterns), Path 06 (v1 evaluation + v2 production directions). If you can ship this, you've internalized the production-readiness backbone.

The 2026 production reality per [Maxim May 2026](https://www.getmaxim.ai/articles/best-ai-observability-platform-in-2026-a-comparison-guide/): "Gartner predicts that LLM observability investments will rise to 50% of GenAI deployments by 2028, up from 15% today." The capstone is on the side of that trend; building it positions you for what production teams will need to do anyway.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 03 — Multi-Agent Systems** v1 + v2 patterns | Topologies + the six v2 patterns (handoff contracts, shared-state boundaries, escalation/fallback, per-agent cost budgeting, retry policies, cross-agent provenance) |
| **Path 06 — Evaluation & Observability** v1 + v2 deeply | LLM-as-judge, judge ensembles, adaptive sampling, cost attribution, drift detection, online evaluators, multi-turn evaluation, embedding-space drift, adversarial red-teaming |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic or OpenAI API key | Models for the agents AND for the judge ensemble |
| Trace storage backend | One of: Langfuse (self-hosted), Phoenix (OSS), Braintrust (managed), Latitude (managed) |
| Comfort with multi-day software builds | Capstone-tier scope |

Helpful but not required: Path 04 (if you want MCP tool access), Path 02 (if your multi-agent system includes a RAG agent), Path 07 (if you want production deployment).

## What you'll build

Five concrete deliverables:

1. **A running multi-agent system** — at least 3 agents in a defended topology with a real workload (customer support, research, code assistance — pick a domain you can describe with specifics)
2. **A trace store** with conversation-level OTel traces showing every agent decision, tool call, retrieval, and judge score
3. **A judge ensemble** — 3 calibrated judges with different biases ([Path 06 Pattern 3](../../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md)) scoring every output
4. **A drift detection layer** — at least 2 of: rolling-window judge score drift (Lab 20), embedding-space drift (Lab 23), context-drift signals (Path 05 Module 5)
5. **A versioned regression set** that grows over time from production failures and runs on every deploy

Plus a `WRITEUP.md` that defends every architecture choice.

## Architecture overview

The system has five layers. Each maps to specific repo material.

| Layer | Components | Repo material |
|---|---|---|
| **1 — Agent topology** | Supervisor + N specialists, OR plan-and-execute, OR specialized routing | [Path 03 v1 patterns](../../../learning-paths/03-multi-agent-systems/) + the topology choice |
| **2 — Production substrate** | Handoff contracts, shared-state boundaries, escalation, per-agent cost budgets, retry policies, provenance | [Path 03 v2 patterns 1-6](../../../learning-paths/03-multi-agent-systems/patterns/) — all six are load-bearing |
| **3 — Trace and telemetry** | OTel spans per agent step + tool call + retrieval; per-tenant baggage propagation | [Path 06 Modules 1-6](../../../learning-paths/06-evaluation-observability/) + OTel propagation patterns |
| **4 — Evaluation layer** | Judge ensemble; online evaluators; multi-turn eval; adversarial red-team on regression set | [Path 06 v1 Modules 1-7 + Path 06 v2 directions](../../../learning-paths/06-evaluation-observability/) |
| **5 — Detection and promotion** | Drift detectors; severity routing; regression-set promotion; dashboards | [Lab 20 (score drift)](../../../labs/20-drift-detection-and-calibration/) + [Lab 23 (embedding-space drift)](../../../labs/23-embedding-space-drift-detection/) + [Lab 24 (red-team orchestration)](../../../labs/24-adversarial-red-teaming-at-scale/) |

The system is a graph: requests flow through Layer 1; Layer 2 enforces the patterns; Layer 3 instruments everything; Layer 4 scores it; Layer 5 catches drift and promotes failures.

### The architecture-decision-record requirement

Per the path framing — "every capstone has a written rationale for the choices you made: which framework, which topology, which retrieval strategy, which observability stack, which deployment target" — your WRITEUP.md includes an ADR (architecture decision record) for each of the five layers above. Each ADR is 3-5 sentences answering: what I chose, what the alternatives were, why I picked this one, what I gave up.

## Milestones

Eight phases, each ending with a working checkpoint. The capstone scope means each milestone takes ~3-6 hours.

### Milestone 1 — Pick the domain and the topology (3-5 hours)

Choose a specific domain you can describe with workload examples. Examples that work:

- **Customer support triage** — router agent + escalation-decision agent + specialist agents per category
- **Research synthesis** — planner agent + multiple specialist research agents + a synthesis agent (the multi-agent version of Project 01)
- **Code-review committee** — security-focused reviewer + style-focused reviewer + correctness-focused reviewer + a synthesizer

For the topology, [Path 03 Pattern 1 (handoff contracts)](../../../learning-paths/03-multi-agent-systems/patterns/01-handoff-contracts.md) tells you what shape the agents need to be. Pick supervisor-worker or plan-and-execute as the topology; document the choice and the rejected alternatives.

**Done when**: a one-page architecture sketch with the agents named, their responsibilities defined, and the handoff contracts specified.

### Milestone 2 — Build the bare topology (5-7 hours)

Implement the 3+ agents without any observability or evaluation yet. Each agent has its system prompt, its tool set, and its handoff contract. The system runs end-to-end on a few test inputs.

**Done when**: a request comes in, agents hand off correctly, a final answer comes out. No traces, no eval — just the topology working.

### Milestone 3 — Add the production substrate (5-7 hours)

Layer 2 — the six Path 03 v2 patterns. All of them. Each gets implemented:

- **Pattern 1 (Handoff contracts)** — already done in Milestone 2; verify it's tight
- **Pattern 2 (Shared-state boundaries)** — define what state each agent reads vs writes; enforce at the type level
- **Pattern 3 (Escalation and fallback)** — explicit escalation paths for each agent's failure modes
- **Pattern 4 (Per-agent cost budgeting)** — soft caps + hard caps per agent (the [Path 05 Module 2](../../../concepts/context/token-budgets.md) extension to per-zone is optional)
- **Pattern 5 (Retry policies)** — distinguish transient (retry) from permanent (escalate) failures per error type
- **Pattern 6 (Cross-agent provenance)** — every output traces back to which agent produced it, with which inputs, in which step

**Done when**: each of the six patterns has visible code; the WRITEUP draft notes which v2 pattern handles which failure mode.

### Milestone 4 — Trace and telemetry (4-6 hours)

Layer 3 — OpenTelemetry spans. Per [Arthur April 2026](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026): "An OpenTelemetry (OTel)-first posture is now table stakes." Pick your trace backend (Langfuse / Phoenix / Braintrust / Latitude) and instrument:

- Root span per request
- Nested spans per agent step
- Nested spans per tool call
- Nested spans per retrieval (if RAG is in the system)
- Per-tenant baggage propagation if multi-tenancy applies

**Done when**: open any trace in your backend's UI and you can see the full causal chain from request to response, with every decision visible.

### Milestone 5 — Judge ensemble (4-5 hours)

Layer 4, part 1 — the judge ensemble per [Path 06 Pattern 3](../../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md). Three deterministic judges with intentionally different biases (e.g., one strict on factuality, one strict on tone, one strict on completeness). For each final output:

- All three judges score independently
- Disagreement structure determines routing: unanimous pass → trend tracking; split → human review queue; unanimous fail → confirmed failure → regression promotion

**Done when**: every output has 3 judge scores in its trace; the dashboard shows score distributions per judge over time.

### Milestone 6 — Drift detection (3-5 hours)

Layer 5, part 1 — drift detectors. Pick at least 2 of the three the repo provides:

- **Score drift (Lab 20)** — rolling-window detection on judge scores
- **Embedding-space drift (Lab 23)** — query distribution or retrieval-result clustering
- **Context drift (Path 05 Module 5)** — the four early-warning signals (re-reads, re-decisions, task reframing, retrieval-precision collapse) on multi-turn conversations

Each detector runs continuously on the live trace stream; alerts fire when thresholds get exceeded.

**Done when**: you can deliberately introduce a regression (e.g., swap the supervisor's system prompt for a degraded version) and at least one drift detector fires within 10 conversations.

### Milestone 7 — Regression set and promotion (3-5 hours)

Layer 5, part 2 — the failure → regression-set loop. Per the [Path 06 v2 Lab 24 framing](../../../labs/24-adversarial-red-teaming-at-scale/): unanimous-fail outcomes and split-verdict conversations get promoted (JSON-serialized) into a versioned regression set. On every deploy, the regression set runs first; regressions block the deploy.

**Done when**: the regression set has at least 20 cases (synthetic plus real failures from Milestones 4-6); the deploy script blocks if any regression case fails.

### Milestone 8 — Polish, dashboards, write-up (3-5 hours)

The system works. Now:

- Build a one-page dashboard (Grafana, your trace backend's UI, or even a static HTML page) showing: per-day request volume, per-judge score distributions, drift signal status, regression set growth, current open failures
- Write the architecture decision records (ADRs) — one per layer
- Write the WRITEUP.md (see Submission guide)
- Record a 2-3 minute screen recording of the system handling a workload + the dashboard reflecting it

**Done when**: someone unfamiliar with the project can follow your dashboard + WRITEUP and explain to a third person what the system does and how you know it's working.

## Evaluation criteria

The capstone-tier rubric. Six dimensions:

| Dimension | What it measures | Capstone-tier target |
|---|---|---|
| **Topology defense** | Is the agent topology genuinely necessary for the workload, or could a single agent have done it? | The WRITEUP defends the multi-agent choice against a single-agent alternative with specific scenarios |
| **Production substrate completeness** | Are all 6 of Path 03 v2 patterns implemented and exercised? | All 6 patterns visible in code; the WRITEUP names one failure mode each pattern catches |
| **Observability depth** | Can a reader-of-traces reconstruct the decision chain for any conversation? | Yes — every conversation has a complete causal trace; the dashboard shows aggregate health |
| **Eval rigor** | Are outputs scored by a judge ensemble with documented inter-judge agreement? | Inter-judge agreement measured; >70% unanimous pass on natural traffic; reasonable disagreement distribution |
| **Drift discipline** | Do detectors actually catch regressions? | The Milestone 6 deliberate-regression test passes — a detector fires within 10 conversations |
| **Regression integrity** | Does the regression set actually block bad deploys? | Yes — manual verification that introducing a regression-set-failing change blocks the deploy script |

The six-dimension rubric is what separates capstone-tier from intermediate-tier projects. Each dimension has a concrete check.

## Stretch goals

Pick at most three. The capstone-tier bar is already substantial; stretch goals should add specific value.

- **Multi-tenancy** — multiple "customer" tenants share the system with isolated traces, budgets, and dashboards. Demonstrates [Path 05 Module 2's per-tenant tier table](../../../concepts/context/token-budgets.md) and Path 06's per-tenant cost attribution.
- **Adversarial red-team integration** — Path 06 v2 Lab 24's six-step red-team workflow runs against your system on a schedule, promoting findings into the regression set automatically.
- **MCP tool surface** — at least one of your specialists exposes its tools via MCP per Path 04. Demonstrates protocol-level interoperability.
- **A2A federation** — your supervisor calls out to a second agent system via A2A per Path 04 Modules 4-5. Demonstrates cross-system orchestration.
- **Long-running checkpointing** — conversations that take >5 minutes use LangGraph's checkpointer or equivalent for crash recovery. Production-readiness depth.
- **Cost-tier routing** — Path 05 Module 6's effective-context routing applied: simple queries go to Haiku-class; complex multi-needle queries go to Opus. Demonstrates the [`production/cost-engineering.md`](../../../production/cost-engineering.md) Layer 2 (routing) discipline.

## Anti-scope

What this capstone does NOT need to include:

- **Custom model fine-tuning** — frontier models off the shelf are the target; fine-tuning belongs in a different project (and isn't covered in the repo's paths)
- **A custom inference engine** — you're consuming model APIs, not running vLLM yourself
- **A novel evaluation methodology** — Path 06 v1 + v2 methodologies are sufficient; the capstone shows you can implement them, not invent new ones
- **Production deployment at scale** — local + a small hosted demo is fine; running 10K req/sec belongs in [Path 07 production deployment](../../../learning-paths/07-production-and-safety/) capstone territory
- **Compliance and audit infrastructure** — the regression set and audit-friendly traces are sufficient; full GDPR/SOC 2 implementation is out of scope
- **Multi-modal inputs (vision, audio)** — text-in / text-out keeps the eval surface manageable

If you find yourself building any of the above, you're scope-creeping. The capstone-tier scope is already large; adding more dimensions makes finishing harder, not better.

## Resources

**Architecture references**:
- [Coralogix April 2026, Agentic AI Observability: A Practical Guide](https://coralogix.com/ai-blog/agentic-ai-observability/) — trace-tree foundation; the four telemetry categories; session-level evaluation; trajectory mapping
- [Arthur April 2026, Agentic AI Observability: A 2026 Playbook](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026) — OTel-first as table stakes; full telemetry stack correlation with KPIs
- [Latitude March 2026, Best AI Agent Observability Tools](https://latitude.so/blog/best-ai-agent-observability-tools-2026-comparison) — 11-platform comparison; GEPA (auto-generated evals from production failures)
- [Maxim May 2026, Best AI Observability Platform 2026](https://www.getmaxim.ai/articles/best-ai-observability-platform-in-2026-a-comparison-guide/) — Gartner 50%-by-2028 prediction; semantic-quality tracking
- [Braintrust January 2026, AI observability buyer's guide](https://www.braintrust.dev/articles/best-ai-observability-tools-2026) — BraintrustSpanProcessor OTEL integration

**Repo cross-references — load-bearing**:
- [Path 01 — Foundations](../../../learning-paths/01-foundations/) — agent loop fundamentals
- [Path 03 — Multi-Agent Systems v1 + v2 patterns](../../../learning-paths/03-multi-agent-systems/) — topologies + the six v2 patterns
- [Path 06 — Evaluation & Observability v1 + v2](../../../learning-paths/06-evaluation-observability/) — every concept this capstone integrates
- [Lab 20 — Drift detection and calibration](../../../labs/20-drift-detection-and-calibration/) — score-side drift detector
- [Lab 23 — Embedding-space drift detection](../../../labs/23-embedding-space-drift-detection/) — input-side drift detector
- [Lab 24 — Adversarial red-teaming at scale](../../../labs/24-adversarial-red-teaming-at-scale/) — the regression-promotion workflow

**Repo cross-references — supporting**:
- [`patterns/`](../../../patterns/) — the 12-pattern catalog; the architecture-decision view
- [Path 05 Module 5 (context drift detection)](../../../concepts/context/context-drift-detection.md) — the third drift detector option
- [`production/cost-engineering.md`](../../../production/cost-engineering.md) — the cost discipline this capstone exercises in Milestones 3 + Pattern 4

## Submission guide

When you're done, four artifacts go in your repo:

1. **The system code** — repo with clear directory structure (agents/, evals/, traces/, dashboards/, runbooks/); README explains setup, running locally, deploying to your trace backend
2. **A trace export** — sample traces from 10 representative conversations exported as JSON; the reader can replay your system's behavior without running it
3. **The dashboard screenshot or recording** — one image or 2-3 minute screen recording demonstrating the live system + dashboard reflecting it
4. **`WRITEUP.md`** — a 2,000-3,000 word document covering:
   - The domain you chose and why
   - The topology decision (with the ADR format: chose / alternatives / why / tradeoffs)
   - Five ADRs — one per architecture layer
   - The deliberate-regression test from Milestone 6 — what you broke, which detector fired, how long it took
   - The regression-set growth pattern over your build period
   - Two failure modes you observed that surprised you
   - What you'd do differently with 2× the time

Add yourself to `docs/community/showcase.md` when you submit. Capstone-tier submissions get highlighted in the README rotation and may be featured in the project gallery.

## What this capstone leads to

After Evaluated Multi-Agent System, the natural progressions:

- **Project 08 (Production-ready deep research)** — adds long-running execution, durable checkpointing, HITL approval gates. Path 07 production-deployment depth.
- **Project 06 (Financial research analyst)** — same capstone-tier scope but with a regulated-domain constraint; provenance per Path 03 Pattern 6 becomes load-bearing.
- **Open-source contribution** — the multi-agent eval stack you built is non-trivial; consider extracting a small framework and publishing it. Several Path 06 v2 directions started as exactly this kind of extraction.

This capstone is where Paths 01 + 03 + 06 compose. Finishing it means you've built one of the most-asked-for production patterns in 2026 agentic AI: a multi-agent system that knows when it's broken.
