# Project 08 — Production-ready deep research

> 🔴 Capstone · ⏱ 30-40+ hours · 📍 Capstone-tier — after Paths 01 + 02 + 03 + Path 06 + Path 07 · 🛠 Verified 2026-05-29

## What you're building

A long-running research agent — designed to execute for **minutes to hours**, not seconds — with durable checkpointing, explicit cost budgets, retry policies, and human-in-the-loop approval gates at high-stakes decision points. The system can be killed mid-execution and resumed from the exact point of interruption; spans real wall-clock time with bounded cost; has the failure-handling discipline that turns "the agent ran" into "the agent completed despite three transient API failures, two server restarts, and one approval pause."

This is the *deployment-discipline capstone* — where the engineering challenge isn't the agent's reasoning quality, it's the agent's ability to survive its own runtime. Where [Project 01 (Personal research assistant)](../../beginner/01-personal-research-assistant/) is a 3-5 minute research run, Project 08 is the version designed to run for an hour and survive what an hour entails: API rate limits, container restarts, network hiccups, human approval delays, partial cost overruns.

## Why this matters

Three distinguishing claims for a portfolio:

1. **Long-horizon agents are the 2026 production frontier** — per [LangChain April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "Durable execution is the foundation everything else depends on. Agents that run for minutes or hours, pause for human approval, or survive mid-run deploys all need checkpointed execution that can stop, resume, and retry across process boundaries." Building one is the canonical demonstration of the runtime-discipline skill.
2. **The right architecture is a two-layer pattern** — per [Cordum April 2026](https://cordum.io/blog/temporal-vs-langgraph): "For side-effecting production agents, the winning pattern is often LangGraph for reasoning plus Temporal for orchestration." This project exercises that two-layer architecture concretely.
3. **HITL is non-optional at this scope** — per [LangGraph 1.0 framing](https://www.clickittech.com/ai/langchain-1-0-vs-langgraph-1-0/): "Long-running or Stateful Agents: Workflows that span hours or days, such as multi-stage approvals or research pipelines. Human-in-the-Loop (HITL) Systems: Nodes can pause for manual validation before resuming automatically." Long-running without HITL is mostly an anti-pattern; the project demonstrates the right shape.

The portfolio claim: "I can ship agentic systems that survive production runtimes." This positions for any role building infrastructure around AI agents — platform teams, MLOps, AI deployment, agent infrastructure.

## Prerequisites

| Required | Why |
|---|---|
| **Path 01 — Foundations** complete | Agent loop, tool calling, structured outputs |
| **Path 02 — Agentic RAG** (canonical RAG portion) | Web search + retrieval as the research substrate |
| **Path 03 — Multi-Agent Systems** v1 + v2 patterns | Topology + the six v2 patterns; **Patterns 4 (per-agent cost budgeting) + 5 (retry policies) are load-bearing** |
| **Path 06 — Evaluation & Observability** v1 (modules 1-3) | Trace instrumentation for the long-running runtime |
| **Path 07 — Production & Safety** (v1 deployment + cost modules) | Deployment patterns; cost engineering |
| Working Python 3.10+ environment | Repo baseline |
| Anthropic / OpenAI API key | Models for the agent |
| Web search API account | Tavily / Exa / Perplexity / Serper — pick one |
| Durable orchestration choice | One of: [LangGraph 1.0](https://docs.langchain.com/) with checkpointer, [Temporal](https://temporal.io/), [Deep Agents runtime](https://www.langchain.com/blog/runtime-behind-production-deep-agents), or a manual implementation |
| PostgreSQL or Redis | Checkpoint persistence layer |
| Comfort with multi-day software builds | Capstone-tier scope; longer than other capstones because the runtime discipline takes real time to exercise |

Helpful but not required: Path 04 (only if you go MCP for tool surface), Path 05 Module 2 (token budgets — useful for the cost-budget layer).

## What you'll build

Six concrete deliverables:

1. **A long-running research agent** that completes 30+ minute research runs end-to-end
2. **A checkpointing layer** — the agent can be killed mid-execution and resumed from the exact point
3. **A cost-budget enforcement layer** — soft caps trigger warnings; hard caps trigger graceful termination
4. **A retry-policy layer** — distinguishes transient (retry with backoff) from permanent (escalate to HITL) failures
5. **HITL approval gates** at 2-3 documented decision points (e.g., "is the research scope still on-track?", "approve this set of high-cost sources?")
6. **A `WRITEUP.md`** with ADRs per architecture decision; chaos-test results

## Architecture overview

The system has six layers. Each maps to a specific 2026 best practice.

| Layer | Components | Repo material | 2026 source |
|---|---|---|---|
| **1 — Agent reasoning** | LangGraph (or equivalent) state machine; plan-research-synthesize loop | [Path 01](../../../learning-paths/01-foundations/) + [Path 02](../../../learning-paths/02-agentic-rag/) | [LangGraph 1.0 docs](https://docs.langchain.com/) |
| **2 — Orchestration durability** | Checkpoints at every super-step; state persisted to PostgreSQL/Redis | [Path 03 v2 Pattern 5](../../../learning-paths/03-multi-agent-systems/patterns/) | [LangChain April 2026 — Deep Agents runtime](https://www.langchain.com/blog/runtime-behind-production-deep-agents) |
| **3 — Cost budgets** | Per-step + per-run cost tracking; soft cap (warning) + hard cap (terminate) | [Path 03 v2 Pattern 4 (per-agent cost budgeting)](../../../learning-paths/03-multi-agent-systems/patterns/) + [`production/cost-engineering.md`](../../../production/cost-engineering.md) | [LangGraph April 2026](https://www.alphabold.com/langgraph-agents-in-production/) — cost overrun risks |
| **4 — Retry policies** | Transient (timeout / 429 / 502) → exponential backoff retry; Permanent (auth / quota / bad request) → escalate to HITL | [Path 03 v2 Pattern 5](../../../learning-paths/03-multi-agent-systems/patterns/) | Standard production engineering |
| **5 — HITL approval gates** | Pause-and-resume at 2-3 high-stakes decisions; state persists across the pause | [`patterns/10-human-in-the-loop.md`](../../../patterns/10-human-in-the-loop.md) | [LangGraph 1.0 framing](https://www.clickittech.com/ai/langchain-1-0-vs-langgraph-1-0/) — `interrupt_before` |
| **6 — Observability** | Trace instrumentation for the long runtime; cost dashboards | [Path 06 v1 Modules 1-3](../../../learning-paths/06-evaluation-observability/) | Standard for any production agent |

The six layers compose: requests flow into Layer 1; Layer 2 checkpoints every state transition; Layer 3 tracks cost and enforces caps; Layer 4 handles failures intelligently; Layer 5 pauses for human input at the right moments; Layer 6 makes the whole thing inspectable.

## The two-layer architecture decision

The biggest architectural choice in this project is the orchestration approach. Per [Cordum April 2026](https://cordum.io/blog/temporal-vs-langgraph): "For side-effecting production agents, the winning pattern is often LangGraph for reasoning plus Temporal for orchestration."

Three viable approaches:

| Approach | When to pick it | Tradeoffs |
|---|---|---|
| **LangGraph-only** | Reasoning-heavy workloads; tolerable to lose work inside long-running nodes on crash | Simpler; one framework; "checkpointers save state between nodes, not inside nodes" per [AgentMarketCap April 2026](https://agentmarketcap.ai/blog/2026/04/08/langgraph-vs-temporal-long-running-agent-workflows-2026) |
| **LangGraph + Temporal** | Side-effecting workflows (API calls with cost, external state changes); need event-history-backed durability | More complex; two frameworks; "event-history-backed orchestration durability, replay, and long-running execution semantics measured in days or years" per [Cordum](https://cordum.io/blog/temporal-vs-langgraph) |
| **Deep Agents runtime** | Want LangGraph reasoning + LangChain-managed durability without standing up Temporal | Newer; managed; [LangChain April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents) describes the pattern |

The recommended default for this project is **LangGraph + checkpointer + manual cost/retry layers** as the baseline, with LangGraph + Temporal as the documented upgrade path. The WRITEUP defends your choice with an ADR.

### The "checkpoints between nodes, not inside" limitation

Per [AgentMarketCap April 2026](https://agentmarketcap.ai/blog/2026/04/08/langgraph-vs-temporal-long-running-agent-workflows-2026): "LangGraph's checkpointers save state between nodes, not inside nodes. If an agent is halfway through a long loop inside a single node — say, processing item 47 of 200 in a batch — and the process crashes, all intermediate work is lost and the node restarts from the beginning."

This is a load-bearing design constraint. The project explicitly works around it:

- Decompose long loops into multiple nodes (process item 47 vs process items 1-200 in one node)
- For unavoidably long operations, use Temporal for that segment (the two-layer pattern)
- Document the granularity choice in the WRITEUP

The chaos test (Milestone 7) verifies the granularity is actually safe.

## Milestones

Eight phases. Capstone-tier scope; each milestone takes ~4-6 hours.

### Milestone 1 — Pick the orchestration approach, sketch the state graph (3-4 hours)

Pick LangGraph-only, LangGraph + Temporal, or Deep Agents runtime. Document the choice as an ADR.

Sketch the agent's state graph:
- **Nodes**: plan / search / fetch / extract / synthesize / review (and any others your workload needs)
- **Edges**: state transitions; which nodes can transition to which
- **State schema**: typed dict tracking research_plan, current_sub_question, fetched_sources, extracted_findings, draft_synthesis, etc.
- **Checkpoint granularity**: which transitions persist state

**Done when**: a one-page state graph diagram; the state schema defined as a TypedDict (or equivalent); the checkpoint granularity documented per node.

### Milestone 2 — Build the reasoning layer (5-6 hours)

Implement the agent's reasoning layer in your chosen orchestrator. This is the [Project 01 (Personal research assistant)](../../beginner/01-personal-research-assistant/) plan-research-synthesize loop, but as a LangGraph state machine instead of a single agent loop.

The reasoning layer runs without checkpointing first. Verify the agent completes a 5-minute research task end-to-end (the Project 01 scope) before adding durability.

**Done when**: a 5-minute research task completes; the final report has citations; the state graph executes the plan → search → fetch → extract → synthesize sequence.

### Milestone 3 — Add checkpointing (4-5 hours)

Wire up the checkpointer. For LangGraph: configure the PostgreSQL or Redis checkpointer; verify checkpoints get written at every super-step.

Test the checkpointing manually:
- Start a research task
- Kill the process (Ctrl+C) mid-task
- Resume from the last checkpoint
- Verify it picks up where it left off

Per [LangGraph April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "Each super-step of graph execution writes a checkpoint to the persistence layer (PostgreSQL)... any run can be retried, replayed, or resumed from the exact point of interruption."

**Done when**: kill-and-resume works correctly across 3+ different kill points; the resumed run produces the same final report as an uninterrupted run.

### Milestone 4 — Cost-budget enforcement (4-5 hours)

Add cost tracking + budget enforcement. Per Path 03 v2 Pattern 4:

- **Per-step cost tracking**: every LLM call + tool call writes its cost to the state
- **Soft cap** (e.g., $1.50 of an expected $2.00 run): warning logged; agent continues but flagged
- **Hard cap** (e.g., $3.00): graceful termination; partial results saved; HITL escalation
- **Per-LLM-call cost cap**: extreme outlier prompts (e.g., 100K-token contexts) get rejected before sending

**Done when**: a budget-overrun simulation triggers the hard cap; the agent terminates gracefully; partial results are saved; the audit trail shows the cap fired.

### Milestone 5 — Retry policies (3-5 hours)

Implement retry-policy discipline per Path 03 v2 Pattern 5. Distinguish:

| Failure class | Treatment |
|---|---|
| **Transient — Network/timeout** | Exponential backoff retry (3 attempts, 1s/2s/4s) |
| **Transient — 429 rate limit** | Respect Retry-After header; backoff and retry (up to 5 attempts) |
| **Transient — 502/503 service unavailable** | Exponential backoff retry (3 attempts, 5s/15s/45s) |
| **Permanent — 401/403 auth** | No retry; escalate to HITL with clear error message |
| **Permanent — 400 bad request** | No retry; log the malformed call; the agent should learn from this |
| **Permanent — quota exceeded** | No retry; escalate to HITL; cost-budget layer should have caught this earlier |

**Done when**: deliberately inject each failure class; verify the right policy fires for each; transient failures don't terminate the run.

### Milestone 6 — HITL approval gates (4-5 hours)

Add 2-3 HITL approval gates at high-stakes decision points. Recommended gate locations:

- **Gate 1 — Scope confirmation**: after the planner agent produces the research plan, pause for user to confirm the plan is on-track before spending the next $X
- **Gate 2 — High-cost source approval**: if the agent wants to fetch from a high-cost source (e.g., paid API with per-query fee), pause for approval
- **Gate 3 — Final delivery review**: before producing the final report, pause for the user to review the synthesis-in-progress

Per [LangGraph April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "LangGraph's runtime pauses execution, saves state, and waits for human input without blocking threads. When the human responds (seconds or hours later), execution resumes from the exact point it paused."

**Done when**: each gate pauses the agent; the agent's state persists during the pause; resumption picks up from the gate; pauses can last from seconds to hours without state loss.

### Milestone 7 — Chaos tests (4-6 hours)

Run deliberate-failure tests to verify the durability layers work together. At least 5 tests:

- **Test 1 — Mid-run server restart**: kill the process during a long-running synthesis; verify resume works
- **Test 2 — Network partition during retrieval**: block the search API mid-task; verify retry policy fires; verify the agent recovers
- **Test 3 — Cost-cap firing**: deliberately misconfigure to trigger the hard cap; verify graceful termination + state preservation
- **Test 4 — HITL pause for 30+ minutes**: trigger an approval gate; let it sit for 30+ minutes; verify resume from the gate produces correct output
- **Test 5 — All-of-the-above**: trigger 3+ of the failure modes in sequence within one research run; verify final output is correct

Document each test's outcome.

**Done when**: at least 4 of 5 chaos tests produce correct final output; the WRITEUP names the failure modes the system handled vs the ones it didn't.

### Milestone 8 — Polish, ADRs, write-up (3-5 hours)

The system works. Now:

- Write 5-7 ADRs (orchestration choice / checkpoint granularity / cost budget thresholds / retry policy per failure class / HITL gate locations / observability stack / deployment shape)
- Build a one-page dashboard: per-run cost distribution, per-failure-class retry counts, HITL pause durations, p95/p99 wall-clock per research task
- Write `WRITEUP.md`
- Record a 3-5 minute screen recording demonstrating: a long-running research run + a deliberate failure + the resume

**Done when**: someone unfamiliar with the project can follow your dashboard + WRITEUP and explain the durability story to a third person.

## Evaluation criteria

The capstone-tier rubric — six dimensions, with durability-discipline specificity:

| Dimension | What it measures | Capstone-tier target |
|---|---|---|
| **Checkpoint integrity** | Does kill-and-resume produce the same final output as an uninterrupted run? | Yes, verified across 3+ kill points; bit-for-bit not required, semantically-equivalent is sufficient |
| **Cost-budget discipline** | Do soft caps and hard caps fire when they should, and not when they shouldn't? | Soft cap fires within 10% of threshold; hard cap fires within 5% of threshold; no false positives on normal runs |
| **Retry-policy correctness** | Are transient vs permanent failures handled with the right policy each? | All 6 failure classes from Milestone 5 produce the documented behavior; verified via deliberate injection |
| **HITL pause-and-resume** | Do approval gates correctly pause, persist state, and resume? | Pauses ≥30 minutes survive without state loss; resumption produces correct downstream output |
| **Chaos test resilience** | How many of the deliberate-failure scenarios produce correct final output? | At least 4 of 5 chaos tests pass; the WRITEUP names which one didn't and why |
| **Wall-clock + cost** | What's the typical end-to-end research run cost and duration? | p50 wall-clock <30 minutes; p50 cost <$3.00 at Sonnet pricing; p95 of each within 2× |

The chaos-test resilience dimension is the load-bearing capstone-tier check specific to this project — converting "I built durability layers" into "I verified the durability layers actually work."

## Stretch goals

Pick at most three.

- **Two-layer architecture (LangGraph + Temporal)** — upgrade from LangGraph-only to the full two-layer pattern. Per [Cordum April 2026](https://cordum.io/blog/temporal-vs-langgraph): "LangGraph for reasoning plus Temporal for orchestration." Demonstrates the production-frontier architecture.
- **Multi-day pause durability** — verify HITL gates survive multi-day pauses. Real production deployments need this; the chaos test in Milestone 7 only verifies 30+ minutes.
- **Cost-tier routing** — route simple queries to Haiku-class; complex multi-needle queries to Opus. Per [Path 05 Module 6](../../../concepts/context/long-context-models.md) framing. Cost optimization at the deployment layer.
- **Concurrent request handling** — multiple research tasks run concurrently with proper isolation; the orchestrator handles N parallel state graphs. Per [LangGraph April 2026](https://www.langchain.com/blog/runtime-behind-production-deep-agents): "Streaming, human-in-the-loop, cron jobs, and concurrent message handling all build on top of [durable execution]."
- **Observability + alerting integration** — the long-running runtime generates OpenTelemetry traces; alerts fire on cost-cap warnings, retry exhaustion, HITL gate timeouts. Production-readiness depth.
- **MCP tool surface** — use MCP per Path 04 for tool integration; demonstrates protocol-level interoperability in long-running contexts.
- **Cron-scheduled research** — the agent runs on a schedule (daily / weekly) with state carrying between runs. Per LangGraph April 2026: "Streaming, human-in-the-loop, cron jobs, and concurrent message handling all build on top of durable execution."

## Anti-scope

What this capstone does NOT need to include:

- **Real production deployment at scale** — local + a small hosted demo is fine; 10K req/sec belongs in a different scope
- **Custom orchestration engine** — use LangGraph / Temporal / Deep Agents runtime; don't build your own
- **Multi-region failover** — single-region deployment is the assumed shape
- **Custom fine-tuned models** — frontier models off the shelf
- **A full evaluation harness with judge ensembles** — that's [Project 07](../07-evaluated-multi-agent-system/); this capstone emphasizes runtime durability, not output evaluation
- **Regulated-domain compliance** — that's [Project 06](../06-financial-research-analyst/); this capstone emphasizes runtime durability, not audit-trail rigor

If you find yourself building any of the above, you're scope-creeping. The runtime-discipline scope is already substantial.

## Resources

**Architecture references**:
- [LangChain (April 2026), The Runtime Behind Production Deep Agents](https://www.langchain.com/blog/runtime-behind-production-deep-agents) — durable execution as foundation; managed task queue; super-step checkpoints
- [AlphaBold (March 2026), LangGraph Agents in Production](https://www.alphabold.com/langgraph-agents-in-production/) — architecture, costs, real-world outcomes; checkpointing at every node execution
- [Clickittech (April 2026), LangChain 1.0 vs LangGraph 1.0](https://www.clickittech.com/ai/langchain-1-0-vs-langgraph-1-0/) — when to pick LangGraph; long-running stateful agents; HITL pattern
- [Cordum (April 2026), Temporal vs LangGraph Durable Agent Architecture](https://cordum.io/blog/temporal-vs-langgraph) — the two-layer architecture pattern; LangGraph for reasoning + Temporal for orchestration
- [AgentMarketCap (April 2026), LangGraph vs Temporal Decision Guide](https://agentmarketcap.ai/blog/2026/04/08/langgraph-vs-temporal-long-running-agent-workflows-2026) — the "checkpoints between nodes not inside nodes" load-bearing limitation
- [Kinde 2026 — Orchestrating Multi-Step Agents](https://www.kinde.com/learn/ai-for-software-engineering/ai-devops/orchestrating-multi-step-agents-temporal-dagster-langgraph-patterns-for-long-running-work/) — Temporal/Dagster/LangGraph comparison

**Tool / library documentation**:
- [LangGraph 1.0 documentation](https://docs.langchain.com/) — the consolidated 1.0 docs (resolves prior fragmentation)
- [Temporal documentation](https://docs.temporal.io/) — event-history-backed durable execution
- [Tavily docs](https://docs.tavily.com/) — recommended search backend (same as Project 01)

**Repo cross-references — load-bearing**:
- [Path 03 v2 Patterns 4 + 5](../../../learning-paths/03-multi-agent-systems/patterns/) — the cost-budget + retry-policy substrate this capstone makes load-bearing
- [Path 07 — Production & Safety](../../../learning-paths/07-production-and-safety/) — deployment + cost engineering modules
- [`production/cost-engineering.md`](../../../production/cost-engineering.md) — the cost discipline this capstone exercises
- [`patterns/10-human-in-the-loop.md`](../../../patterns/10-human-in-the-loop.md) — the HITL pattern this capstone implements at scale
- [Project 01 (Personal research assistant)](../../beginner/01-personal-research-assistant/) — the short-run baseline this capstone scales up
- [Project 07 (Evaluated multi-agent system)](../07-evaluated-multi-agent-system/) — the eval/observability capstone; shares Path 03 v2 substrate

**Repo cross-references — supporting**:
- [Path 02 — Agentic RAG](../../../learning-paths/02-agentic-rag/) — for the retrieval substrate
- [Path 06 v1 Modules 1-3](../../../learning-paths/06-evaluation-observability/) — for the trace instrumentation
- [Path 05 Module 2 — Token budgets](../../../concepts/context/token-budgets.md) — for the per-zone cost budgeting stretch goal
- [Path 04 — Tool Protocols](../../../learning-paths/04-tool-protocols-mcp-a2a/) — for the MCP stretch goal

## Submission guide

When you're done, five artifacts go in your repo:

1. **The system code** — clean directory structure (orchestrator/, agents/, checkpoints/, budgets/, hitl/, dashboards/, runbooks/); README explains setup, dependencies (PostgreSQL / Redis), configuration, running locally
2. **Chaos test results** — `tests/chaos/` directory with one file per chaos test from Milestone 7; each file documents what was injected, what happened, and the resume behavior
3. **Three example research runs** — `examples/run-XX/` each containing the request, the trace, the cost breakdown, the HITL approval interactions, the final report
4. **The dashboard screenshot or recording** — 3-5 minute screen recording demonstrating a long-running run + a chaos injection + the resume + the cost dashboard
5. **`WRITEUP.md`** — a 2,000-3,000 word document covering:
   - The orchestration choice (with ADR: chose / alternatives / why / tradeoffs)
   - The checkpoint granularity decisions (which nodes are atomic; which long operations got decomposed)
   - The cost-budget thresholds and how they were calibrated
   - The retry policy per failure class
   - The HITL gate locations and rationale
   - Chaos test results — which scenarios passed, which didn't, why
   - One thing that surprised you about long-running runtime engineering
   - What you'd do differently with 2× the time

Add yourself to `docs/community/showcase.md` when you submit. Capstone-tier deployment-discipline submissions get highlighted in the project gallery; the chaos-test results make them particularly valuable as community references.

## What this capstone leads to

After Production-Ready Deep Research, the natural progressions:

- **Project 06 (Financial research analyst)** — the regulated-domain capstone; combine runtime durability with audit-trail rigor for the most demanding enterprise surface
- **Project 07 (Evaluated multi-agent system)** — the eval/observability capstone; share the multi-agent substrate with a different emphasis (judge ensembles + drift detection vs runtime durability + HITL)
- **Open-source contribution** — the chaos-test harness you build is non-trivial; consider extracting it as a small framework. The agent-resilience tooling space in 2026 has open problems at exactly this layer.
- **Path 07 v2 (if shipped)** — extends Path 07 v1 with the production-readiness depth this capstone exercises; will likely reference this project as a canonical implementation

This capstone is where Path 03 Patterns 4 + 5 + Path 07 deployment-discipline + the LangGraph/Temporal 2026 architecture compose. Finishing it means you've built one of the highest-skill production patterns in 2026 agentic AI: a long-running agent that completes its work despite the runtime trying to break it.
