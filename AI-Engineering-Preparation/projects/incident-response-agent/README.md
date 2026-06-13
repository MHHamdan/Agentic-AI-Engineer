# Project: Incident-response agent

Build a tool-using agent for a focused operational task: read signals, decide an action, call tools, observe the result, and escalate to a human when the right move is uncertain.

> Batch 00: specification. The build arrives in a later batch.

## Objectives

- Implement the reason-act-observe loop with real tool calls.
- Ground each step in tool output rather than guesses.
- Add guardrails and a human-in-the-loop stop condition.
- Log a trajectory you can evaluate later.

## Planned deliverables

- A runnable agent with a small tool set.
- A guardrail and escalation policy.
- A trajectory log format for evaluation.

## Concept areas

[`agents`](../../concepts/agents/), [`patterns`](../../concepts/patterns/), [`eval`](../../concepts/eval/)

## References

See [`../../references/references.md`](../../references/references.md). Original work; sources cited, not copied ([`../../STYLE.md`](../../STYLE.md)).
