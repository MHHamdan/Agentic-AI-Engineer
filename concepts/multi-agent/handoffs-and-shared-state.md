# Handoffs and shared state

> ⏱ ~9 min · 🟡 Intermediate · Prerequisites: [what is a multi-agent system?](./what-is-a-multi-agent-system.md), [supervisor-worker pattern](./supervisor-worker-pattern.md)

When two agents need to coordinate, *how* information moves between them is the design choice that determines most of the system's failure modes. There are two architectures: **message-passing** and **shared-state**. They have different ergonomics, different bug profiles, and different production stories. Most teams pick one without realizing they had a choice.

## Two architectures

### Message-passing

The supervisor calls a worker like a function. The supervisor's prompt arguments get serialized into a structured payload; the worker runs; the worker returns a structured result; the supervisor's loop continues.

```
supervisor: call_researcher(question="What is MCP?")
                  │
                  ▼
    researcher: [own loop runs here]
                  │
                  ▼
supervisor: receives {"findings": ..., "citations": [...]}
```

This is what Lab 02's tool-calling contract already gives you. A worker is just a tool whose handler happens to invoke another agent loop. Each handoff is one function call's worth of state transfer — explicit, structured, debuggable.

### Shared-state

The agents read from and write to a common store. The supervisor might write a "current plan" to the store; a worker reads it, does its work, writes the result back; another worker reads both the plan and the result, writes its own contribution.

```
                    ┌─────────────────┐
                    │  shared state   │
                    │  ────────────   │
                    │  task: ...      │
                    │  plan: ...      │
                    │  findings: ...  │
                    └─────────────────┘
                       ▲  ▲  ▲  ▲
                       │  │  │  │
            ┌──────────┘  │  │  └──────────┐
            │             │  │             │
       supervisor    researcher  writer   critic
```

The canonical production implementation is LangGraph's `StateGraph` — agents are nodes; the state is a typed dict; reducers handle concurrent updates. The pattern predates LangGraph; blackboard systems from the 80s used the same idea.

## The trade

**Message-passing wins on:**

- **Simplicity.** No new abstraction; reuses Lab 02's tool-calling contract verbatim.
- **Debuggability.** Each handoff is one function call with one input and one output. The trace reads top-to-bottom.
- **No race conditions.** Sequential by construction. If two workers should produce something interleaved, that's the supervisor's job to orchestrate.
- **Lower coupling.** Workers don't need to agree on a shared schema; each one has its own input/output contract with the supervisor.

**Shared-state wins on:**

- **Efficiency at scale.** If many agents need to read the same large object (e.g., a long conversation history), serializing it through every handoff is expensive. Shared-state stores it once.
- **Parallel execution.** Several workers can write different fields of the state concurrently; reducers handle the merge.
- **Long-running workflows.** Persistent state survives process restarts; LangGraph's checkpointer makes this concrete. Useful when a workflow legitimately spans hours/days.

**Shared-state loses on:**

- **Race conditions.** Two workers writing the same field concurrently is a real bug class; reducers help but they don't eliminate the design burden.
- **Mutation order matters.** Which worker reads which version of the state is part of the program's semantics. Reasoning about that semantics is harder than reasoning about function calls.
- **Coupling.** Every agent that touches the state needs to know the state schema. Adding a field means coordinating across agents.
- **Debuggability surface grows.** A failure could be in any agent that touched the state, in any order. "Where did this field get set?" becomes a real question.

A heuristic: **default to message-passing.** Reach for shared-state when you've felt message-passing genuinely creak under your system's weight (large shared contexts, real parallel execution needs, multi-day workflows). Most teams reach for shared-state too early because the marketing makes it sound sophisticated. It's a real engineering cost.

Lab 10 — and most of Path 03 v1 — uses message-passing. A future framework-bridge module will cover LangGraph's `StateGraph` as the shared-state implementation and discuss when the trade flips.

## The three handoff-hygiene rules

Regardless of architecture, three rules prevent the most common multi-agent bugs:

### Rule 1: Handoffs carry structured payloads, not free text

The handoff envelope is a dict with named fields, not a paragraph of LLM output. Same discipline as Lab 02's tool returns:

```python
# Good — structured, schema-checkable, future-proof
result = {
    "status": "ok",
    "findings": "...",
    "citations": [{"url": "...", "title": "..."}, ...],
}

# Bad — free text the supervisor has to re-parse
result = "I found that MCP is a protocol developed by Anthropic. Here are some sources: ..."
```

The free-text version *works* for simple tasks, but you can't programmatically check that citations are preserved through the next handoff, you can't field-validate the result, and your trace logs are full of prose instead of data. Production multi-agent systems are built on structured envelopes for the same reason production APIs are built on structured payloads.

### Rule 2: The supervisor decides the next step, not the worker

Workers return; they don't unilaterally hand off to other workers. If the researcher worker decides "I should call the writer next" and does so, you've broken the supervisor's mediation property and you're now in peer-to-peer territory with all the debuggability costs that implies.

Concretely, this means:

- A worker's return value is *just* the result, not a directive about what should happen next.
- If a worker thinks it can't complete its task and needs help from a different worker, it returns `{"status": "needs_help", "reason": "..."}` and the *supervisor* decides what to do.
- The supervisor's system prompt explicitly takes ownership of routing decisions.

This rule is the single most important multi-agent discipline. Violating it produces systems that work in demos and fall apart in production.

### Rule 3: Every handoff is logged at the supervisor

The supervisor's trace IS the audit log. For every handoff:

- The supervisor logs *who* it called.
- It logs the *payload* it sent.
- It logs the *result* it received.
- It logs *how long* the worker took.

This is free if you're using the Lab 02 tool-call mechanism — the conversation history already captures all of it. The only addition is timing.

In shared-state systems this is harder: the supervisor isn't the single hub of communication, so "the supervisor's trace" doesn't capture everything. You need explicit instrumentation. This is one of the implicit costs that doesn't show up in tutorials but does show up at 2am during an incident.

## Where things go wrong

The five most common multi-agent bugs, in rough order of how often they bite:

1. **Citation loss across handoffs.** The researcher returns citations as a structured field. The supervisor synthesizes a final answer that drops half of them. Mitigation: the supervisor's system prompt explicitly says "citations must appear verbatim in the final answer," and you check it in eval. (Lab 09's `groundedness` metric still applies; you're just running it at the supervisor level.)

2. **Worker scope creep.** A worker takes on more than its prompt's scope ("I'm a writer, but I noticed the research didn't cover X, so I'll just look it up"). Mitigation: tight worker prompts that say "If you need X, return `{\"status\": \"needs_more_research\", ...}`. Do NOT search yourself."

3. **Supervisor over-calling a worker.** The supervisor calls researcher → reads result → decides it needs "just a bit more" → calls researcher again → again → again. Mitigation: action-hash dedup at the supervisor + a smaller `SUPERVISOR_MAX_STEPS` than you'd give a single agent.

4. **State mutation races** (shared-state only). Two workers write the same field concurrently. Mitigation: explicit reducers per field; or simply don't run conflicting writers in parallel.

5. **Ambiguous handoff conditions.** The supervisor's prompt doesn't make clear when to hand off vs. when to handle directly. The model picks inconsistently. Mitigation: concrete examples in the supervisor's system prompt; negative guidance on which worker is *not* right for ambiguous cases.

## Related concepts

- The pattern that compounds these rules: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The honest framing of when multi-agent earns its complexity: [what is a multi-agent system?](./what-is-a-multi-agent-system.md).
- The single-agent tool-return contract that handoff envelopes extend: [tool design](../tools/tool-design.md).

## References

- LangGraph's [low-level state documentation](https://langchain-ai.github.io/langgraph/concepts/low_level/) — the canonical production-grade shared-state design; reducers, channels, persistence.
- Engelmore & Morgan 1988, "Blackboard Systems" — the architectural pattern that shared-state systems descend from; still useful framing 35+ years later.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — emphasizes the "keep it simple" discipline that motivates defaulting to message-passing.
