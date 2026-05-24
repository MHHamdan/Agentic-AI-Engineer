---
quiz_id: multi-agent-multi-agent-fundamentals
title: "Multi-agent fundamentals: when to reach for it, the supervisor-worker pattern, and handoff hygiene"
source:
  - concepts/multi-agent/what-is-a-multi-agent-system.md
  - concepts/multi-agent/supervisor-worker-pattern.md
  - concepts/multi-agent/handoffs-and-shared-state.md
  - labs/10-supervisor-worker-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "A team is considering splitting their working single-agent customer-support bot into a 5-agent system (triage, lookup, billing, escalation, summarizer). The single-agent version works but they want it to feel 'more production-grade.' Which framing is most accurate?"
    options:
      A: "Splitting will help — more agents always produce more reliable systems."
      B: "Splitting is the right move because production systems are inherently multi-agent."
      C: "Splitting is likely premature: 'production-grade' comes from contracts, errors, observability, and graceful degradation — multi-agent makes all four harder."
      D: "Splitting is fine as long as they keep all five agents on the same model."
    answer: C
    explanation: |
      Multi-agent doesn't fix the things that actually make systems
      production-grade. Adding agents adds handoff boundaries (each one
      a new failure surface), multiplies the trace shape (each handoff
      is a new place to instrument), and increases coordination cost
      (latency and tokens). If the single-agent version works, splitting
      should be motivated by a specific reason — usually specialization
      where the sub-prompts genuinely differ, or explicit handoff
      boundaries that aid debuggability. "Feel more production-grade"
      isn't a reason; it's the marketing-driven intuition the concept
      page warns against.
    review:
      page: concepts/multi-agent/what-is-a-multi-agent-system.md
      section: "When multi-agent is the wrong call"

  - id: q2
    difficulty: easy
    question: "You're estimating cost for a supervisor-worker version of a task that the single-agent version solves in ~3 LLM calls. Which estimate is closest to typical?"
    options:
      A: "About the same — handoffs are cheap."
      B: "About 2x — every handoff adds at least one extra LLM call (often more, since the supervisor must read the worker's result and decide next steps)."
      C: "About 0.5x — multi-agent is more efficient because agents specialize."
      D: "About 10x — multi-agent always blows up costs by an order of magnitude."
    answer: B
    explanation: |
      Coordination cost is real and roughly multiplicative per handoff,
      not free. A supervisor-worker trajectory for a task the single
      agent solves in 3-4 calls typically runs 6-8 calls: the supervisor
      makes a routing call, the worker makes its own internal calls,
      the supervisor reads the result and either synthesizes or routes
      again. 2x is the typical estimate. This is why production
      multi-agent systems are usually 2-4 agents, not 10 — the marginal
      benefit of each added agent has to clear the cost-multiplier bar.
    review:
      page: concepts/multi-agent/what-is-a-multi-agent-system.md
      section: "Coordination cost: the central tradeoff"

  - id: q3
    difficulty: easy
    question: "In the supervisor-worker pattern, the supervisor's 'tools' are calls to the worker agents. Which Lab 02 design principle is most important for ensuring the supervisor routes correctly?"
    options:
      A: "Tool count — keeping tool count above 10 forces better routing."
      B: "Tool name length — short names route better."
      C: "Negative-guidance descriptions on each worker tool ('Use this when X; do NOT use it when Y, use Z instead')."
      D: "Letting the worker decide whether to accept the work."
    answer: C
    explanation: |
      The supervisor's view of each worker is determined entirely by
      the worker's tool description. Negative guidance — 'Do NOT use
      the researcher if the answer is already in this conversation;
      call the writer directly' — is the single most reliable fix for
      selection drift between overlapping workers. It's the same Lab 02
      principle, lifted to the supervisor-worker boundary. Tool count
      (A) is a red herring; production multi-agent systems typically
      have 2-5 workers. Worker-side accept-or-reject (D) violates the
      mediation property — workers don't choose; the supervisor decides.
    review:
      page: concepts/multi-agent/supervisor-worker-pattern.md
      section: "Failure modes and mitigations"

  - id: q4
    difficulty: medium
    question: "A researcher worker returns its findings to the supervisor. The supervisor synthesizes a final answer for the user — but the citations the researcher carefully tracked never appear in the final answer. What's the most likely root cause, and what's the right fix?"
    options:
      A: "The researcher's tool didn't actually track citations; fix it in the researcher."
      B: "The supervisor synthesized free text from the structured payload and the LLM dropped the citation list — fix it with rule 1 (structured payloads, not free text) plus an explicit instruction in the supervisor's prompt to preserve citations."
      C: "The user's task didn't ask for citations, so the supervisor was right to drop them."
      D: "LangGraph's StateGraph would have prevented this — switch to shared-state architecture."
    answer: B
    explanation: |
      This is the canonical citation-loss bug, and the fix is in two
      places. First, the handoff is a structured envelope (`{findings,
      citations}` as a dict, not a paragraph), so the supervisor never
      has to re-serialize the citations from free text. Second, the
      supervisor's prompt explicitly says 'citations must be preserved
      in the final answer.' Option A blames the wrong layer (Lab 03's
      by-the-loop tracking is correct). Option C is wrong because
      citations being grounding-evidence aren't optional even when
      unrequested. Option D is overkill — shared-state doesn't fix
      this; structured envelopes do, and they work in message-passing.
    review:
      page: concepts/multi-agent/handoffs-and-shared-state.md
      section: "Rule 1: Handoffs carry structured payloads, not free text"

  - id: q5
    difficulty: medium
    question: "In Lab 10, the supervisor has SUPERVISOR_MAX_STEPS = 6 and the workers have WORKER_MAX_STEPS = 8. A user's task triggers the researcher worker, which exhausts all 8 of its steps without producing findings. What happens?"
    options:
      A: "The supervisor's step counter immediately jumps to 6, terminating the supervisor."
      B: "The supervisor crashes — worker step-cap raises an exception."
      C: "The worker returns {status: 'step_cap', findings: '...partial...', citations: [...]}; the supervisor receives this as a normal tool result and decides what to do next (re-route, surface to user, or call another worker)."
      D: "The supervisor automatically retries the worker until it succeeds."
    answer: C
    explanation: |
      Step caps compose by escalation through the structured-error
      envelope, not by exceptions or shared counters. When the
      researcher hits its step cap it returns a partial-result payload
      with status='step_cap'. The supervisor's loop receives this as a
      normal tool result (the same envelope shape as a successful
      result), and the supervisor's system prompt — which says 'do not
      silently ignore worker errors' — guides the LLM to surface the
      limitation or change approach. The supervisor's own step counter
      is independent; it only increments when the supervisor itself
      makes an LLM call. Option D is wrong because automatic retry
      would loop; dedup catches the repeat.
    review:
      page: labs/10-supervisor-worker-from-scratch/
      section: "Step 5: Failure-mode walkthrough"

  - id: q6
    difficulty: medium
    question: "Your supervisor-worker system is getting harder to debug. The supervisor calls researcher → writer → researcher again → critic → writer → final. Each handoff is logged. Which architecture/discipline change would help most?"
    options:
      A: "Switch to shared-state — having all agents read/write a common state object simplifies debugging."
      B: "Re-examine whether all those handoffs are necessary; the trajectory complexity may indicate the supervisor's prompt isn't routing decisively, not that the architecture is wrong."
      C: "Add more workers — specialization will reduce the back-and-forth."
      D: "Remove the action-hash dedup so the supervisor can retry workers freely."
    answer: B
    explanation: |
      A 5-handoff trajectory for a single user task is a signal — usually
      that the supervisor's prompt isn't decisive about routing, or that
      the workers' tool descriptions don't give enough negative guidance
      ('do NOT call researcher if X'). Adding more workers (C) usually
      makes routing harder, not easier. Removing dedup (D) makes loops
      worse. Shared-state (A) doesn't reduce the number of handoffs —
      it changes their mechanism but not their count, and it adds
      race-condition surface. The discipline is: minimize handoffs, then
      log the ones you have well. Lab 10's verbose trace is the
      diagnostic surface.
    review:
      page: concepts/multi-agent/supervisor-worker-pattern.md
      section: "What the supervisor does"

  - id: q7
    difficulty: medium
    question: "Compared to message-passing, when does shared-state architecture (LangGraph's StateGraph) become genuinely worth the added complexity?"
    options:
      A: "Always — shared-state is strictly better; message-passing is the legacy approach."
      B: "Never — message-passing is always sufficient."
      C: "When several agents need to read the same large object (long conversation history) and/or when long-running workflows must persist across process restarts and/or when genuinely parallel execution is required."
      D: "Only when using LangGraph's create_supervisor helper — manual StateGraph is too brittle."
    answer: C
    explanation: |
      Shared-state pays off in three specific situations: efficiency
      when a large shared object would otherwise be serialized through
      every handoff; persistence across process restarts (LangGraph's
      checkpointer makes this concrete); and real parallel execution
      where reducers merge concurrent writes. Outside those cases,
      message-passing is simpler, more debuggable, and has no race
      conditions. The general advice is to default to message-passing
      and reach for shared-state only when message-passing has been felt
      to genuinely creak. Marketing-driven adoption of shared-state in
      tutorial-scale systems is the most common mistake new
      multi-agent teams make.
    review:
      page: concepts/multi-agent/handoffs-and-shared-state.md
      section: "The trade"

  - id: q8
    difficulty: hard
    question: "Your supervisor is calling the same worker (call_researcher) repeatedly with slightly different question wording, never converging. Action-hash dedup catches exact repeats, but the supervisor just rephrases. Which is the most reliable fix?"
    options:
      A: "Make the action-hash fuzzy so it catches near-duplicates too."
      B: "Increase SUPERVISOR_MAX_STEPS so the supervisor has more room to find the answer."
      C: "Tighten the supervisor's system prompt to explicitly state 'after one successful researcher call, do not call the researcher again unless the user's task fundamentally changes' — and reduce SUPERVISOR_MAX_STEPS so a wandering supervisor terminates sooner."
      D: "Switch from supervisor-worker to plan-and-execute."
    answer: C
    explanation: |
      Fuzzy action-hashing (A) sounds clean but is brittle — semantically
      different questions can have similar wording, and you'd start
      blocking legitimate re-calls. Increasing the step cap (B) makes
      the problem worse, not better — the supervisor has more rope to
      keep looping. Switching patterns (D) is over-engineering for a
      prompt-level problem. The right fix is at the supervisor's system
      prompt level: explicit guidance about when re-calling the researcher
      is appropriate vs. not, paired with a *smaller* step cap so the
      supervisor terminates before drifting. This is the same lesson
      from Lab 02: prompts and tool descriptions are the highest-leverage
      surface for changing agent behavior; mechanism changes are a
      heavier hammer with their own tradeoffs.
    review:
      page: concepts/multi-agent/supervisor-worker-pattern.md
      section: "Failure modes and mitigations"
---

# Quiz: Multi-agent fundamentals

> 🟡 Intermediate · 8 questions · ~10 min · Passing: 6/8

Tests your grasp of when multi-agent is the right call, how the supervisor-worker pattern earns its place in production, and how handoff hygiene composes with the Lab 01-03 patterns you already know.

If you're below 6/8, the answers point at specific sections of the three concept pages — use them as a re-read guide.

---

## Question 1

A team is considering splitting their working single-agent customer-support bot into a 5-agent system (triage, lookup, billing, escalation, summarizer). The single-agent version works but they want it to feel "more production-grade." Which framing is most accurate?

- A. Splitting will help — more agents always produce more reliable systems.
- B. Splitting is the right move because production systems are inherently multi-agent.
- C. Splitting is likely premature: "production-grade" comes from contracts, errors, observability, and graceful degradation — multi-agent makes all four harder.
- D. Splitting is fine as long as they keep all five agents on the same model.

<details>
<summary>Reveal answer</summary>

**C.**

Multi-agent doesn't fix the things that actually make systems production-grade. Adding agents adds handoff boundaries (each one a new failure surface), multiplies the trace shape (each handoff is a new place to instrument), and increases coordination cost (latency and tokens). If the single-agent version works, splitting should be motivated by a specific reason — usually specialization where the sub-prompts genuinely differ, or explicit handoff boundaries that aid debuggability. "Feel more production-grade" isn't a reason; it's the marketing-driven intuition the concept page warns against.

Review: [`concepts/multi-agent/what-is-a-multi-agent-system.md`](../../concepts/multi-agent/what-is-a-multi-agent-system.md#when-multi-agent-is-the-wrong-call) — "When multi-agent is the wrong call".

</details>

---

## Question 2

You're estimating cost for a supervisor-worker version of a task that the single-agent version solves in ~3 LLM calls. Which estimate is closest to typical?

- A. About the same — handoffs are cheap.
- B. About 2x — every handoff adds at least one extra LLM call (often more, since the supervisor must read the worker's result and decide next steps).
- C. About 0.5x — multi-agent is more efficient because agents specialize.
- D. About 10x — multi-agent always blows up costs by an order of magnitude.

<details>
<summary>Reveal answer</summary>

**B.**

Coordination cost is real and roughly multiplicative per handoff, not free. A supervisor-worker trajectory for a task the single agent solves in 3-4 calls typically runs 6-8 calls: the supervisor makes a routing call, the worker makes its own internal calls, the supervisor reads the result and either synthesizes or routes again. 2x is the typical estimate. This is why production multi-agent systems are usually 2-4 agents, not 10 — the marginal benefit of each added agent has to clear the cost-multiplier bar.

Review: [`concepts/multi-agent/what-is-a-multi-agent-system.md`](../../concepts/multi-agent/what-is-a-multi-agent-system.md#coordination-cost-the-central-tradeoff) — "Coordination cost: the central tradeoff".

</details>

---

## Question 3

In the supervisor-worker pattern, the supervisor's "tools" are calls to the worker agents. Which Lab 02 design principle is most important for ensuring the supervisor routes correctly?

- A. Tool count — keeping tool count above 10 forces better routing.
- B. Tool name length — short names route better.
- C. Negative-guidance descriptions on each worker tool ("Use this when X; do NOT use it when Y, use Z instead").
- D. Letting the worker decide whether to accept the work.

<details>
<summary>Reveal answer</summary>

**C.**

The supervisor's view of each worker is determined entirely by the worker's tool description. Negative guidance — "Do NOT use the researcher if the answer is already in this conversation; call the writer directly" — is the single most reliable fix for selection drift between overlapping workers. It's the same Lab 02 principle, lifted to the supervisor-worker boundary. Tool count (A) is a red herring; production multi-agent systems typically have 2-5 workers. Worker-side accept-or-reject (D) violates the mediation property — workers don't choose; the supervisor decides.

Review: [`concepts/multi-agent/supervisor-worker-pattern.md`](../../concepts/multi-agent/supervisor-worker-pattern.md#failure-modes-and-mitigations) — "Failure modes and mitigations".

</details>

---

## Question 4

A researcher worker returns its findings to the supervisor. The supervisor synthesizes a final answer for the user — but the citations the researcher carefully tracked never appear in the final answer. What's the most likely root cause, and what's the right fix?

- A. The researcher's tool didn't actually track citations; fix it in the researcher.
- B. The supervisor synthesized free text from the structured payload and the LLM dropped the citation list — fix it with rule 1 (structured payloads, not free text) plus an explicit instruction in the supervisor's prompt to preserve citations.
- C. The user's task didn't ask for citations, so the supervisor was right to drop them.
- D. LangGraph's StateGraph would have prevented this — switch to shared-state architecture.

<details>
<summary>Reveal answer</summary>

**B.**

This is the canonical citation-loss bug, and the fix is in two places. First, the handoff is a structured envelope (`{findings, citations}` as a dict, not a paragraph), so the supervisor never has to re-serialize the citations from free text. Second, the supervisor's prompt explicitly says "citations must be preserved in the final answer." Option A blames the wrong layer (Lab 03's by-the-loop tracking is correct). Option C is wrong because citations being grounding-evidence aren't optional even when unrequested. Option D is overkill — shared-state doesn't fix this; structured envelopes do, and they work in message-passing.

Review: [`concepts/multi-agent/handoffs-and-shared-state.md`](../../concepts/multi-agent/handoffs-and-shared-state.md#rule-1-handoffs-carry-structured-payloads-not-free-text) — "Rule 1: Handoffs carry structured payloads, not free text".

</details>

---

## Question 5

In Lab 10, the supervisor has `SUPERVISOR_MAX_STEPS = 6` and the workers have `WORKER_MAX_STEPS = 8`. A user's task triggers the researcher worker, which exhausts all 8 of its steps without producing findings. What happens?

- A. The supervisor's step counter immediately jumps to 6, terminating the supervisor.
- B. The supervisor crashes — worker step-cap raises an exception.
- C. The worker returns `{status: 'step_cap', findings: '...partial...', citations: [...]}`; the supervisor receives this as a normal tool result and decides what to do next (re-route, surface to user, or call another worker).
- D. The supervisor automatically retries the worker until it succeeds.

<details>
<summary>Reveal answer</summary>

**C.**

Step caps compose by escalation through the structured-error envelope, not by exceptions or shared counters. When the researcher hits its step cap it returns a partial-result payload with `status='step_cap'`. The supervisor's loop receives this as a normal tool result (the same envelope shape as a successful result), and the supervisor's system prompt — which says "do not silently ignore worker errors" — guides the LLM to surface the limitation or change approach. The supervisor's own step counter is independent; it only increments when the supervisor itself makes an LLM call. Option D is wrong because automatic retry would loop; dedup catches the repeat.

Review: [`labs/10-supervisor-worker-from-scratch/README.md`](../../labs/10-supervisor-worker-from-scratch/README.md) — Lab 10 structure, Step 5.

</details>

---

## Question 6

Your supervisor-worker system is getting harder to debug. The supervisor calls researcher → writer → researcher again → critic → writer → final. Each handoff is logged. Which architecture/discipline change would help most?

- A. Switch to shared-state — having all agents read/write a common state object simplifies debugging.
- B. Re-examine whether all those handoffs are necessary; the trajectory complexity may indicate the supervisor's prompt isn't routing decisively, not that the architecture is wrong.
- C. Add more workers — specialization will reduce the back-and-forth.
- D. Remove the action-hash dedup so the supervisor can retry workers freely.

<details>
<summary>Reveal answer</summary>

**B.**

A 5-handoff trajectory for a single user task is a signal — usually that the supervisor's prompt isn't decisive about routing, or that the workers' tool descriptions don't give enough negative guidance ("do NOT call researcher if X"). Adding more workers (C) usually makes routing harder, not easier. Removing dedup (D) makes loops worse. Shared-state (A) doesn't reduce the number of handoffs — it changes their mechanism but not their count, and it adds race-condition surface. The discipline is: minimize handoffs, then log the ones you have well. Lab 10's verbose trace is the diagnostic surface.

Review: [`concepts/multi-agent/supervisor-worker-pattern.md`](../../concepts/multi-agent/supervisor-worker-pattern.md#what-the-supervisor-does) — "What the supervisor does".

</details>

---

## Question 7

Compared to message-passing, when does shared-state architecture (LangGraph's `StateGraph`) become genuinely worth the added complexity?

- A. Always — shared-state is strictly better; message-passing is the legacy approach.
- B. Never — message-passing is always sufficient.
- C. When several agents need to read the same large object (long conversation history) and/or when long-running workflows must persist across process restarts and/or when genuinely parallel execution is required.
- D. Only when using LangGraph's `create_supervisor` helper — manual StateGraph is too brittle.

<details>
<summary>Reveal answer</summary>

**C.**

Shared-state pays off in three specific situations: efficiency when a large shared object would otherwise be serialized through every handoff; persistence across process restarts (LangGraph's checkpointer makes this concrete); and real parallel execution where reducers merge concurrent writes. Outside those cases, message-passing is simpler, more debuggable, and has no race conditions. The general advice is to default to message-passing and reach for shared-state only when message-passing has been felt to genuinely creak. Marketing-driven adoption of shared-state in tutorial-scale systems is the most common mistake new multi-agent teams make.

Review: [`concepts/multi-agent/handoffs-and-shared-state.md`](../../concepts/multi-agent/handoffs-and-shared-state.md#the-trade) — "The trade".

</details>

---

## Question 8

Your supervisor is calling the same worker (`call_researcher`) repeatedly with slightly different question wording, never converging. Action-hash dedup catches exact repeats, but the supervisor just rephrases. Which is the most reliable fix?

- A. Make the action-hash fuzzy so it catches near-duplicates too.
- B. Increase `SUPERVISOR_MAX_STEPS` so the supervisor has more room to find the answer.
- C. Tighten the supervisor's system prompt to explicitly state "after one successful researcher call, do not call the researcher again unless the user's task fundamentally changes" — and reduce `SUPERVISOR_MAX_STEPS` so a wandering supervisor terminates sooner.
- D. Switch from supervisor-worker to plan-and-execute.

<details>
<summary>Reveal answer</summary>

**C.**

Fuzzy action-hashing (A) sounds clean but is brittle — semantically different questions can have similar wording, and you'd start blocking legitimate re-calls. Increasing the step cap (B) makes the problem worse, not better — the supervisor has more rope to keep looping. Switching patterns (D) is over-engineering for a prompt-level problem. The right fix is at the supervisor's system prompt level: explicit guidance about when re-calling the researcher is appropriate vs. not, paired with a *smaller* step cap so the supervisor terminates before drifting. This is the same lesson from Lab 02: prompts and tool descriptions are the highest-leverage surface for changing agent behavior; mechanism changes are a heavier hammer with their own tradeoffs.

Review: [`concepts/multi-agent/supervisor-worker-pattern.md`](../../concepts/multi-agent/supervisor-worker-pattern.md#failure-modes-and-mitigations) — "Failure modes and mitigations".

</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Strong grasp. Move on to Lab 10 (or jump ahead if you've already built it). |
| 6-7/8 | Good. Re-read any concept-page sections flagged in the questions you missed. |
| 4-5/8 | Re-read all three concept pages before attempting Lab 10. |
| < 4/8 | Re-do Path 01 Labs 01-03 first — the multi-agent patterns compose from those foundations and the gap is most likely upstream. |
