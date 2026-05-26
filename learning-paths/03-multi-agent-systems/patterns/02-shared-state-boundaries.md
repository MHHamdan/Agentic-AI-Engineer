# Pattern 2 — Shared-state boundaries

> 🟢 Stable · ⏱ ~15 min · 📍 Read after [Lab 14 (LangGraph supervisor bridge)](../../../labs/14-langgraph-supervisor-bridge/) and [`concepts/multi-agent/handoffs-and-shared-state.md`](../../../concepts/multi-agent/handoffs-and-shared-state.md)

## Intent

The Module 1 [handoffs-and-shared-state concept page](../../../concepts/multi-agent/handoffs-and-shared-state.md) names the two architectural choices: **message-passing** (workers behave like function calls) and **shared-state** (agents read and write a common store). It also names the trade. This pattern picks up where that page leaves off: assuming you've chosen shared-state for some part of your topology, **what belongs in shared state and what doesn't?**

The decision rule isn't aesthetic. Over-sharing and under-sharing have different production failure modes, with different cost shapes, that show up in traces in different ways.

## When to use this pattern

- **You've chosen shared-state for at least one boundary.** The LangGraph `StateGraph` in Lab 14 is shared-state by construction; the plan-and-execute bridge in Lab 15 is shared-state; most multi-agent RAG implementations use shared state for the evidence store.
- **More than two agents read or write the same logical data.** A single producer-consumer pair can use a message-passing handoff (Pattern 1). Three or more agents on the same data — a planner plus multiple executors plus a critic — make shared state the natural choice; this pattern then governs *what* shape that shared state takes.
- **You're seeing trace bloat or context-window overflows.** This is the canonical symptom of the over-sharing failure mode. The 15× token-burn cost from full-transcript inlining shows up here.
- **You're seeing agents repeat work or contradict prior decisions.** This is the under-sharing failure mode. A worker can't see what was decided two handoffs ago, so it re-derives or contradicts.

## When NOT to use

- **Two-agent pipelines with no fan-out.** A single supervisor → single worker boundary doesn't need shared state. Use Pattern 1's handoff contract; the supervisor passes what the worker needs, the worker returns what the supervisor needs. Shared state adds machinery without buying anything.
- **Stateless transformations.** A pipeline where each stage takes input and emits output with no need to consult prior stages or peer agents (summarize → classify → format) doesn't need shared state. The output of each stage IS the state that flows forward.
- **When you don't have a clear ownership model.** If you can't name which agent owns each field, you'll get last-write-wins races. The fix is to define ownership first (Pattern 1's "ownership of context" field); only then commit to shared state for that field.
- **For agent system prompts or private reasoning.** These belong to each agent privately. Shared state is for task data, not agent internals; see the boundary rule below.

## The mechanism

Shared state contains four kinds of data, each with a different rule:

| Data kind | Goes in shared state? | Why |
|---|---|---|
| **Task state** (objective, plan, current step) | ✅ Yes | Multiple agents need to see it to coordinate; lifetime is the task |
| **Evidence state** (retrieved chunks, tool outputs needed by ≥ 2 agents) | ✅ Yes | Re-fetching is expensive and non-deterministic; durable provenance matters |
| **Decision state** (the planner's DAG, the critic's verdict, the supervisor's routing decisions) | ✅ Yes | Audit trail; later agents may need to reference earlier decisions |
| **Private agent state** (system prompts, hidden reasoning, scratchpads, conversation history with the model) | ❌ No | Not relevant to peer agents; inlining inflates context and pollutes the trace |

### The four-field model

The minimum useful shared state schema for most multi-agent topologies:

```
shared_state:
  task:           # owned by orchestrator
    objective:    str
    plan:         list[Step]
    current_step: int
    status:       Literal["running", "succeeded", "failed", "escalated"]

  evidence:       # appended by retrievers and tool-calling agents
    items:        list[EvidenceItem]   # each with provenance
    budget_used:  int                  # tracks evidence-budget consumption

  decisions:      # append-only log; each entry references the deciding agent
    log:          list[Decision]

  scratchpad:     # NOT shared — each agent has its own, kept private
                  # (intentionally absent from shared_state)
```

The fourth field is deliberately *not there*. Private scratchpads belong to each agent; sharing them inflates the state object by orders of magnitude per the niteagent May 2026 production measurements.

### The two failure modes

**Over-sharing** (the 15× token-burn case):
- Symptom: shared state grows to include full conversation transcripts from each agent; the orchestrator's context window fills before the task completes; eval latency spikes; LLM costs balloon.
- Root cause: agents return their full internal conversations instead of a summarized result; the shared state acts as a transcript dump rather than a coordination surface.
- Fix: enforce summary returns at the handoff boundary (Pattern 1, output schema); restrict shared state to the four fields above.

**Under-sharing** (the planning-drift case):
- Symptom: an executor agent re-asks for evidence that an earlier executor already gathered; the critic disagrees with a decision the planner made because the critic can't see the planner's reasoning; the supervisor mis-routes because it lost track of which steps are done.
- Root cause: shared state is too narrow — decisions or evidence that one agent needed for context are private to whoever produced them.
- Fix: promote decisions and evidence to shared state (the `decisions.log` field above); keep only system-prompt-level and per-model-call-level state private.

### The append-only convention

Most production deployments treat shared state as **append-only for evidence and decisions** and **last-write-wins for task state**. The two rules together:

- New evidence is appended; old evidence is never overwritten. This preserves the audit trail (essential for Module 6 evaluation) and prevents one agent from "deleting" what another agent found.
- The task's `current_step` is overwritten by the orchestrator. Workers don't mutate task state; they propose updates via their `HandoffResponse`, and the orchestrator commits the change.

In LangGraph `StateGraph` terminology: evidence and decisions use `operator.add` (or a custom append-reducer); task state uses no reducer (last-write-wins). Lab 14's `StateGraph` is the reference implementation.

## Implementation sketch

A LangGraph-style `TypedDict` with annotated reducers. The reducer semantics are what enforce the append-only-vs-overwrite distinction at the framework level.

```python
import operator
from typing import Annotated, Literal, Optional, TypedDict
from pydantic import BaseModel


class EvidenceItem(BaseModel):
    fact_id: str
    source_uri: str
    content: str
    fetched_by: str   # which agent fetched it
    timestamp: float


class Decision(BaseModel):
    decision_id: str
    decided_by: str          # which agent made the decision
    summary: str             # one-sentence rationale; NOT the full reasoning
    referenced_evidence: list[str] = []  # fact_ids the decision cites
    timestamp: float


class Step(BaseModel):
    step_id: str
    description: str
    owner: str               # which agent should execute this step
    status: Literal["pending", "running", "succeeded", "failed"]


class SharedState(TypedDict):
    """The four-field minimum useful shared state schema."""
    # Task state: last-write-wins; only the orchestrator updates these
    objective: str
    plan: list[Step]
    current_step: int
    status: Literal["running", "succeeded", "failed", "escalated"]

    # Evidence and decisions: append-only; any agent can contribute
    evidence: Annotated[list[EvidenceItem], operator.add]
    decisions: Annotated[list[Decision], operator.add]

    # Deliberately omitted: scratchpads, per-agent conversation history,
    # system prompts, full LLM-call transcripts. These are private to each agent.
```

Three production conventions this sketch encodes:

- **Reducer semantics map to ownership rules.** Fields with `operator.add` are co-owned; fields without are single-owner. Reading the type signature tells you who's allowed to write what.
- **Decisions carry summaries, not full reasoning.** The `summary` field is a one-sentence rationale; the full chain-of-thought stays private. This is the explicit defense against the 15× token-burn case.
- **Evidence carries provenance.** Every fact has a `source_uri` and a `fetched_by` agent. This makes later auditing (Module 6 evaluation; Path 06 v2 adversarial red-teaming citation-laundering checks) tractable.

For non-LangGraph implementations, the same four-field model works in Redis (with `LPUSH` for the append-only fields), in a relational DB (with row inserts for evidence and decisions, row update for task state), or in a typed Pydantic state object passed by reference through the agent graph.

## How this combines with Path 03 modules

| Path 03 module / lab | Where this pattern applies |
|---|---|
| Module 1 / [handoffs-and-shared-state](../../../concepts/multi-agent/handoffs-and-shared-state.md) | This pattern is the operational complement to Module 1's architectural distinction. Module 1 tells you when to choose shared-state; Pattern 2 tells you what to put in shared state once you've chosen it. |
| Module 3 / Lab 12 (plan-and-execute from scratch) | The planner-state vs executor-state boundary is the canonical case. The plan goes in shared state (multiple executors need it); the executor's tool-call transcripts stay private (an executor's internal loop is not interesting to peer executors). |
| Module 4 / Lab 13 (multi-agent RAG) | The evidence-state pattern is most visible here. Lab 13's retriever produces evidence; the synthesizer reads it. Both agents touch the evidence field; both append, neither overwrites. The provenance dimension (every fact has a `source_uri`) is what makes the citation contract testable. |
| Module 5 / Lab 14 (LangGraph supervisor bridge) | The `StateGraph` reducer semantics in Lab 14 are exactly the append-only-vs-overwrite mechanism this pattern documents. The lab implements the mechanism; the pattern names the decision rule. |
| Module 5 / Lab 15 (plan-and-execute bridge) | The `Send` API in LangGraph fans the plan out to multiple executors; each executor reads the shared plan, writes its own evidence-append. The pattern's append-only rule for evidence is what makes the fan-out safe — concurrent executors don't trample each other's results. |
| Module 6 / Lab 16 (multi-agent evaluation) | The shared state IS the trajectory that Lab 16 evaluates. A clean four-field shape makes trajectory-level metrics (was every fact cited? did the critic see the decisions log?) directly computable. A messy state shape (with private scratchpads inlined) makes evaluation harder than it has to be. |

## Tradeoffs and what this misses

**Tradeoffs**:

- **Append-only memory grows.** Evidence and decisions accumulate over the task lifetime. For long-horizon tasks this can balloon. Production deployments add a **compaction step** between major phases — summarize the evidence collected so far, replace the raw items with the summary, keep the citations. This pays for itself once tasks exceed ~20 handoffs.
- **The four-field model isn't universal.** Some topologies need a fifth field (a shared message-bus for coordination signals; a shared budget tracker for cost-aware execution). Add fields with the same discipline: name the owner, name the reducer, name what's private.
- **LangGraph reducer semantics are a leak in the abstraction.** The `Annotated[..., operator.add]` syntax is LangGraph-specific. Other frameworks (CrewAI, OpenAI Agents SDK, Anthropic Agent SDK) handle shared state differently; the *decision rule* (what goes in, what stays private) transfers, but the implementation idioms don't.

**What this misses**:

- **Cross-task state**. The four-field model is single-task. Long-running agent sessions where a user comes back the next day need persistent state — that's memory architecture, not shared-state architecture. See the LangGraph long-term memory docs and CrewAI's memory module for that.
- **Eventual consistency in distributed deployments**. If shared state is in Redis or a database accessed by agents on different machines, the rules above assume strong consistency. Production deployments at scale make latency-consistency trade-offs explicitly; this pattern doesn't cover them.
- **PII and data classification**. Some evidence carries PII or regulated data; some decisions reference user identity. Pattern 2 names what goes in shared state by structural role; it doesn't name what to redact or encrypt at rest. That's a security architecture concern, not a multi-agent architecture concern.
- **State observability**. The trace shape of shared state — when did each agent read what, when did each write — is a Path 06 observability concern. Pattern 2 makes the trace tractable; the actual instrumentation lives in [Path 06 Module 3 (OpenTelemetry)](../../../concepts/evaluation/opentelemetry-genai-conventions.md).

## References

**Production literature (verified mid-2026)**:

- niteagent (May 2026), *Multi-Agent in Production 2026: 3 Patterns That Survived* — [niteagent.com/blog](https://niteagent.com/blog/multi-agent-production-2026/) — Rule 3 of the production-survival rules ("return a summary string, not a transcript"); inlining full transcripts pollutes context and burns tokens at 15× the rate of summary returns
- AffinityBots (December 2025), *AI Agent Teams in 2026: How Multi-Agent Systems Actually Work* — [affinitybots.com/blog](https://affinitybots.com/blog/ai-agent-teams-in-2026-how-multi-agent-systems-actually-work) — "shared state is another key element"; the five canonical message types that travel through shared state
- clickittech (February 2026), *Multi-Agent System Architecture Guide for 2026* — [clickittech.com/ai](https://www.clickittech.com/ai/multi-agent-system-architecture/) — role-based agent design (Planner, Executor, Verifier, Optimizer) and the state-sharing implications; over-agentization as a cost driver
- Lifetideshub (April 2026), *How to Build Multi-Agent AI Systems with LangGraph productions* — [lifetideshub.com/langgraph-multi-agent-systems](https://www.lifetideshub.com/langgraph-multi-agent-systems/) — "LangGraph is the production standard for agent graphs because it treats state as a first-class citizen"; short-term state (conversation buffer) vs long-term state (Vector DB) split

**LangGraph documentation**:

- LangGraph `StateGraph` API — the `Annotated[..., operator.add]` reducer pattern; the framework's canonical implementation of the append-only-vs-overwrite distinction
- LangGraph long-term memory — for the cross-task-state extension beyond the four-field model
- LangGraph `Send` API — the fan-out primitive that makes the append-only convention essential

**Path 03 internals**:

- [`concepts/multi-agent/handoffs-and-shared-state.md`](../../../concepts/multi-agent/handoffs-and-shared-state.md) — Module 1 concept page; the architectural distinction this pattern operates inside
- [`concepts/multi-agent/plan-and-execute.md`](../../../concepts/multi-agent/plan-and-execute.md) — Module 3 concept page; the planner-state vs executor-state distinction
- [`concepts/multi-agent/multi-agent-rag.md`](../../../concepts/multi-agent/multi-agent-rag.md) — Module 4 concept page; the evidence-state pattern
- [Lab 12](../../../labs/12-plan-and-execute-from-scratch/), [Lab 13](../../../labs/13-multi-agent-rag-from-scratch/), [Lab 14](../../../labs/14-langgraph-supervisor-bridge/), [Lab 15](../../../labs/15-langgraph-plan-execute-bridge/), [Lab 16](../../../labs/16-multi-agent-evaluation-from-scratch/) — the lab implementations this pattern layers onto
- [Pattern 1 — Handoff contracts](./01-handoff-contracts.md) — the boundary-shape pattern; this pattern is what crosses that boundary
- [Pattern 3 — Escalation and fallback](./03-escalation-and-fallback.md) — what runs when the decisions log shows agent disagreement
