# Lab 10 · Reference solution

The polished final implementation of [Lab 10: Supervisor-worker from scratch](../README.md).

A supervisor coordinates a researcher worker (web search + fetch with action-hash dedup) and a writer worker (citation-preserving prose composer). Step caps escalate cleanly across agent levels via structured-error envelopes. No frameworks — just `chat_with_tools` + Lab 10's machinery.

> 📖 The concept pages that frame this implementation:
> [`what-is-a-multi-agent-system`](../../../concepts/multi-agent/what-is-a-multi-agent-system.md),
> [`supervisor-worker-pattern`](../../../concepts/multi-agent/supervisor-worker-pattern.md),
> [`handoffs-and-shared-state`](../../../concepts/multi-agent/handoffs-and-shared-state.md).
> 🧠 Calibrate against the [multi-agent fundamentals quiz](../../../quizzes/multi-agent/multi-agent-fundamentals.md).

## What this solution implements

The headline path from the parent lab:

- Provider-agnostic `chat_with_tools` client (works against OpenAI or Anthropic; same interface throughout Path 03).
- Researcher worker: `web_search` + `fetch_page` with action-hash dedup; `WORKER_MAX_STEPS = 8`; returns `{status, findings, citations}` on completion or `{status: "step_cap", ...}` on budget exhaustion.
- Writer worker: takes the researcher's brief (findings + citations), produces ~150 words of cited prose. No tools; one LLM call.
- Supervisor: `chat_with_tools` with two worker-call tools (`call_researcher`, `call_writer`); strict Pydantic arg validation; `SUPERVISOR_MAX_STEPS = 6`; structured-error fallthrough on unknown workers / repeated actions.
- One end-to-end demonstration run.

**Not in this solution** (deliberately): the dedup demonstration cell, the step-cap envelope walkthrough, the unknown-worker fallback demonstration, the critic preview, and the failure-mode walkthroughs from the parent lab. Those are exploratory cells in the learning notebook; the solution is the canonical mechanism.

## Implementation choices

### Five design decisions worth flagging

**1. The supervisor's worker tools take Pydantic models, not raw `dict`s.** `CallResearcherArgs` and `CallWriterArgs` extend `StrictModel(extra="forbid")`. This rejects fields the LLM might invent (e.g., `priority: "high"`) at validation time rather than letting them silently flow through to the worker and confuse its prompt. The validation error becomes a structured failure the supervisor can surface — same discipline as Lab 02.

**2. Action-hash dedup happens at the supervisor level, not inside workers.** The supervisor checks `_action_hash(tool_name, args)` against a `seen_actions: set[str]` before dispatching. If the LLM tries to call `call_researcher` twice with identical args, the second call returns a `repeated_action` envelope without invoking the worker. This is the right layer because (a) workers don't know what previous handoffs the supervisor made; (b) the dedup signature is structural, so reworded-but-identical calls collapse correctly.

**3. The worker is a function, not a class.** No state across calls. Each `researcher_agent(question)` invocation creates a fresh message list, tracks its own dedup set, and returns when done or capped. The researcher's `findings` aren't held across supervisor turns — if the supervisor wants more research, it issues a new question, which produces a new researcher invocation. Stateless workers compose more predictably than stateful ones.

**4. Step caps escalate via structured envelopes, not exceptions.** When `researcher_agent` hits its `WORKER_MAX_STEPS` cap, it returns `{"status": "step_cap", "findings": "...", "citations": [...]}` — *not* an exception, *not* a partial completion silently coerced to success. The supervisor reads `status` and decides what to do (typically: finalize with what's there, or call the writer with the partial brief). The same shape carries through Lab 11/12/13.

**5. The supervisor's system prompt names the worker contract explicitly.** Rather than letting the LLM infer what `call_researcher` returns, the prompt tells it: "the researcher returns `{status, findings, citations}` — read `status` first, then use `findings` and `citations` only if status is `ok`." This shapes the supervisor's reasoning around the envelope. Without this, the supervisor sometimes ignores `step_cap` and proceeds as if research succeeded.

## Common variations that also work

**Different step caps.** `WORKER_MAX_STEPS = 6 or 10`, `SUPERVISOR_MAX_STEPS = 5 or 8`. The exact numbers matter less than the principle: the worker cap should accommodate 2-3 tool calls + 1 finalization; the supervisor cap should accommodate 2-3 worker calls + 1 finalization. Anything tighter clips reasoning; anything looser invites loops.

**Different dedup keys.** Lab 10's `_action_hash` includes both tool name and args. Some implementations only hash args — that's wrong (a `call_researcher` and a `call_writer` with the same args are not the same action). Some implementations canonicalize text fields (lowercase, strip whitespace) before hashing — fine, but make sure the canonicalization is the same on both sides of comparison.

**Different writer interfaces.** The writer in this solution takes `(findings: str, citations: list[dict])`. Some implementations pass the whole researcher envelope through — also fine, but slightly more surface for the writer to ignore parts of. Some pass `findings` only and let the writer hallucinate citations — actively wrong; the canonical bug for multi-agent RAG.

## Bugs to watch for

Five things that pass syntax but fail eval:

**1. The supervisor loops because it doesn't read the worker's `status` field.** If your supervisor calls `call_researcher`, gets `{"status": "step_cap", ...}`, and immediately calls `call_researcher` again with the same question expecting it to "complete this time," the action-hash dedup catches it and you escalate. If you don't have action-hash dedup, the supervisor genuinely loops until it hits its own cap. Symptom: every run uses all `SUPERVISOR_MAX_STEPS` slots.

**2. The writer hallucinates citations the researcher didn't return.** The handoff payload from supervisor to writer must be structured: the writer's args contain the actual `citations: list[dict]`. If the supervisor passes only `findings: str` (a summary string), the writer composes prose that *looks* cited but the citation list is reconstructed from the LLM's guess. Verify: every citation in the writer's output must appear verbatim in the researcher's `citations` list.

**3. The supervisor uses raw `dict` args instead of Pydantic schemas.** The OpenAI/Anthropic tool-call API gives you `arguments: dict` — but if you dispatch this raw to the worker without validation, an LLM-invented field like `urgency: "critical"` silently flows through. Workers don't know what to do with it; some workers accidentally consume it and produce wrong output. Validating with `CallResearcherArgs(**arguments)` raises immediately on the supervisor side.

**4. The step-cap path doesn't return citations.** When the researcher hits its cap mid-research, the natural impulse is to return `{"status": "step_cap", "findings": "incomplete"}` without citations. But if the researcher fetched 1-2 pages before capping, those citations are valid and the writer can use them. Returning `citations: []` on cap loses partial value.

**5. The `_action_hash` includes timestamps or random IDs.** If your hash includes anything non-deterministic (`time.time()`, `uuid.uuid4()`, or worse, the LLM's `tool_call_id`), it never dedups. Symptom: dedup appears to work in isolated tests but never in production. The hash must be a pure function of `(name, args)`.

## Differences from naive implementations

Three things a learner might miss on first pass:

- **The supervisor sees only the worker's return envelope, not its trajectory.** When `researcher_agent` runs 3 tool calls internally, the supervisor sees `{status: "ok", findings: "...", citations: [...]}`. The supervisor has no record of what the researcher's intermediate `web_search` queries were. That's deliberate: information hiding between agent levels.

- **The supervisor's system prompt does *not* include the worker's tools.** The supervisor knows about `call_researcher` and `call_writer`; it does not know that the researcher internally uses `web_search` and `fetch_page`. If the supervisor "knew" about the researcher's tools, it would be tempted to micro-manage ("search for X then fetch result Y"), which defeats the point of delegation.

- **The supervisor's `SUPERVISOR_MAX_STEPS = 6` is independent of the worker's `WORKER_MAX_STEPS = 8`.** They compose multiplicatively in the worst case (1 supervisor step that triggers 1 worker invocation with 8 worker steps = 8 LLM calls minimum per turn), but they're independent budgets. Conflating them — e.g., "the supervisor budget includes the worker's calls" — produces a brittle accounting that fails when the supervisor calls multiple workers.

## Cost and timing

Per end-to-end run:

- 1-2 supervisor calls (routing decisions; one to call researcher, one to call writer, sometimes one to finalize)
- 2-5 researcher tool calls (`web_search` then 1-3 `fetch_page`)
- 1 writer call

Total: 4-8 LLM calls per task, ~$0.02-$0.05 at gpt-4o-mini rates. Wall-clock dominated by `fetch_page` (live web; 1-3 seconds each). Typical end-to-end: 8-15 seconds.

## Next

After completing this lab, move on to [Lab 11 (generator-critic from scratch)](../../11-generator-critic-from-scratch/) — extends this supervisor with a critic worker for iterative refinement. The chat client, action-hash dedup, structured envelopes, and `StrictModel` patterns all carry over.
