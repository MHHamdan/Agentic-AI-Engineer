---
quiz_id: multi-agent-plan-and-execute
title: "Plan-and-execute: when it beats supervisor-worker and ReAct, the planner-prompt rules, and bounded replanning"
source:
  - concepts/multi-agent/plan-and-execute.md
  - concepts/multi-agent/planner-executor-pattern.md
  - labs/12-plan-and-execute-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Your task is 'find me the answer to this open-ended question' where each step's result determines what makes sense next. You're choosing between plan-and-execute and ReAct. Which framing is most accurate?"
    options:
      A: "Always use plan-and-execute — the plan is auditable, which is strictly better."
      B: "Use ReAct. Plan-and-execute commits to a plan upfront; on tasks where the trajectory can't be known in advance, that commitment produces brittle plans that don't survive contact with reality."
      C: "Use plan-and-execute with `MAX_REPLANS = 10` — frequent replanning compensates for the lack of upfront knowledge."
      D: "Use neither; this task wants a single-agent ReAct loop with no planning."
    answer: B
    explanation: |
      Plan-and-execute optimizes the median run on tasks with clear
      upfront decomposition. For exploratory tasks where each step's
      result determines what makes sense next, the planner is just
      imagining a trajectory the supervisor would have followed
      anyway — and the imagined trajectory often doesn't survive
      execution. ReAct's interleaved think-act-think-act is built for
      exactly this case. Option A ignores when plan-and-execute is
      genuinely the wrong call. Option C is replanning thrash by
      design — frequent replans are a symptom that you've chosen the
      wrong pattern. Option D conflates ReAct with single-agent ReAct;
      ReAct is the pattern, single-agent is one deployment of it.
    review:
      page: concepts/multi-agent/plan-and-execute.md
      section: "When plan-and-execute is the wrong call"

  - id: q2
    difficulty: easy
    question: "Your planner emits a step that says 'fetch the third URL from step_1's results.' At execution time, step_1 returns only two results. What's the failure mode and what's the right fix?"
    options:
      A: "This is execution drift — the executor should pick a different URL. Fix: relax the anti-improvement prompt."
      B: "This is plan brittleness — the planner committed to a structure (a third result) that didn't hold. Fix: planner-prompt rule that step descriptions use role-based references ('fetch URLs from step_1') and let the executor resolve them from actual dependency outputs."
      C: "This is the plan-execution gap — the executor doesn't have a 'fetch the third URL' tool. Fix: add such a tool."
      D: "This is replanning thrash — the planner should produce a fresh plan whenever a step fails."
    answer: B
    explanation: |
      This is the canonical plan brittleness failure mode. The planner
      guessed what step_1's result would look like (3+ URLs) and wrote
      step_2 assuming the guess held. The fix is structural: step
      descriptions should be **role-based** ("fetch URLs from
      step_1's results" or "fetch the most relevant URLs") rather
      than **structural** ("fetch the third URL"). The executor sees
      the actual dependency outputs at runtime and adapts.
      Option A misnames the failure — execution drift is the
      executor deviating from the plan, not the plan being wrong.
      Option C confuses brittleness with the plan-execution gap (the
      executor not having a tool the planner specified). Option D
      treats the symptom; the fix is at the planner-prompt level.
    review:
      page: concepts/multi-agent/plan-and-execute.md
      section: "Plan brittleness"

  - id: q3
    difficulty: medium
    question: "In Lab 12, the executor's tool registry is passed into the planner's system prompt and the `Plan.validate_graph()` method rejects plans referencing unknown tools. Which failure mode does this primarily prevent?"
    options:
      A: "Plan brittleness — by constraining the planner, plans become more robust."
      B: "Replanning thrash — by validating upfront, replans become rarer."
      C: "Plan-execution gap — the planner can't emit steps using tools the executor doesn't have, because the planner is told what tools exist and validation enforces it."
      D: "Sycophancy — the planner can't agree with everything the user wanted."
    answer: C
    explanation: |
      The plan-execution gap is the failure mode where the plan looks
      reasonable to a human reading it but the executor can't actually
      run the steps (tools that don't exist, capabilities the executor
      lacks). Passing the executor's tool registry into the planner's
      system prompt and validating against it at plan-emit time
      closes this gap structurally. Option A is plausible but
      misnamed — constraining tool choice doesn't fix the larger
      brittleness pattern (which is about structural assumptions).
      Option B is downstream — fewer plan-execution-gap failures
      means fewer replans, but the mechanism is the validation, not
      the replan cap. Option D is from Lab 11; sycophancy isn't a
      plan-and-execute failure mode.
    review:
      page: concepts/multi-agent/plan-and-execute.md
      section: "Plan-execution gap"

  - id: q4
    difficulty: medium
    question: "Lab 12 sets `MAX_PARALLEL_EXECUTORS = 3` via `ThreadPoolExecutor(max_workers=3)`. Which framing of pool size is most accurate?"
    options:
      A: "Pool size is a cost lever — 3 concurrent calls cost a third of 3 sequential calls."
      B: "Pool size is a latency lever — 3 concurrent calls cost the same as 3 sequential calls, but finish faster. More workers = more concurrent calls = lower wall-clock; 3 is the empirical sweet spot before rate limits and debugging trace complexity make larger pools costly to operate."
      C: "Pool size is a quality lever — more workers means better answers because more steps run in parallel."
      D: "Pool size should match the number of CPUs."
    answer: B
    explanation: |
      Parallelism is a wall-clock optimization, not a cost or quality
      optimization. Three concurrent LLM calls cost the same as three
      sequential ones — you still pay for each. What changes is
      wall-clock time. Three workers is the empirical sweet spot:
      enough parallelism to matter for tasks with 3-4 independent
      fetches; small enough that shared API rate limits don't fire and
      debugging traces stay readable. Option A inverts the cost
      relationship. Option C is wishful thinking — parallelism doesn't
      change answer quality, only how fast you get there. Option D is
      a category error — these are LLM API calls (network-bound IO),
      not CPU-bound work; threads are fine and CPU count is irrelevant.
    review:
      page: concepts/multi-agent/planner-executor-pattern.md
      section: "Executor pool concurrency"

  - id: q5
    difficulty: medium
    question: "When the supervisor invokes the replanner after a failure, Lab 12 maintains a `seen_plan_sigs` set keyed on the structural plan signature. If the replanner returns an identical plan to one that already failed, Lab 12 escalates to `partial_after_cap` instead of trying it. Why?"
    options:
      A: "To save on LLM calls — the second attempt would cost the same as the first."
      B: "Because running the same plan again produces the same failure; the dedup is the same action-hash discipline from Lab 03/10/11, applied at the plan level. It prevents replanning thrash where the replanner emits a slightly-reworded but structurally identical plan."
      C: "Because Pydantic forbids it."
      D: "Because identical plans violate the parallel-group integrity rule."
    answer: B
    explanation: |
      Plan signatures are computed from structural content (step IDs,
      tools, args, dependencies, parallel groups) — not prose
      descriptions. So a replan that changes only the wording but
      keeps the same steps produces the same signature. If we tried
      it, we'd get the same failure. The escalation is the same
      discipline from prior labs: when you detect a loop, surface it
      honestly rather than letting it run. Option A is true but
      secondary — the real value is avoiding the wasted execution,
      not just the planner call. Option C is unrelated. Option D
      conflates plan dedup with parallel-group validation.
    review:
      page: concepts/multi-agent/plan-and-execute.md
      section: "Replanning thrash"

  - id: q6
    difficulty: medium
    question: "In Lab 12's `Plan` schema, `depends_on` and `parallel_group` are two different fields. Which statement most accurately distinguishes them?"
    options:
      A: "They're synonyms — `parallel_group` is just sugar for empty `depends_on`."
      B: "`depends_on` declares what a step needs (a correctness constraint); `parallel_group` declares which steps the planner claims can run together (a parallelism hint). The dispatcher uses `depends_on` to decide when a step is ready, and `parallel_group` to decide which ready steps to batch together. The graph validator rejects plans where steps in the same `parallel_group` have transitive dependencies — that's a contradiction."
      C: "`depends_on` is for serial execution and `parallel_group` is for parallel execution; they're mutually exclusive."
      D: "`parallel_group` is for steps with the same tool; `depends_on` is for steps with different tools."
    answer: B
    explanation: |
      The two fields encode different concerns. `depends_on` is a
      *correctness* statement: step B needs the output of step A to
      proceed. `parallel_group` is a *parallelism* statement: the
      planner claims these steps can run together. They interact
      logically — a step can be in a parallel group AND have
      dependencies (those dependencies must be outside the group);
      what's forbidden is being in the same group as a step you
      depend on (a contradiction the validator catches).
      Option A erases the distinction. Option C is wrong because a
      step can have both. Option D invents a relationship that
      doesn't exist.
    review:
      page: concepts/multi-agent/planner-executor-pattern.md
      section: "Plan representation"

  - id: q7
    difficulty: hard
    question: "Which of the five planner-prompt rules is most foundational — i.e., violating it produces the worst downstream consequences?"
    options:
      A: "Rule 1 — atomic steps. Multi-tool steps make trace analysis hard but don't break execution."
      B: "Rule 2 — explicit dependencies. Implicit dependencies produce race conditions when the supervisor parallelizes; the executor reads inconsistent state and produces wrong answers, not just slow ones."
      C: "Rule 3 — honest parallel groups. Cosmetic parallelism is wasteful but the validator catches it."
      D: "Rule 5 — bounded plans. Long plans are brittle but a long plan that runs is better than a short plan that doesn't."
    answer: B
    explanation: |
      Rule 2 (explicit dependencies) is foundational because violating
      it produces **wrong answers**, not just slow or brittle ones.
      If step B uses step A's output but doesn't declare
      `depends_on: ["A"]`, the dispatcher may parallelize them, and
      step B will run with stale/missing state from step A. The
      result is a race condition that's correct-looking but factually
      wrong. The other rules produce slower, longer, or harder-to-
      debug plans — but they don't produce wrong answers in the same
      structural way. Rule 3 is close (and is enforced by the
      validator), but Rule 2 is what makes Rule 3 even possible to
      reason about.
    review:
      page: concepts/multi-agent/planner-executor-pattern.md
      section: "The five planner-prompt rules"

  - id: q8
    difficulty: hard
    question: "How does Lab 12 compose with Lab 10 (supervisor-worker) and Lab 11 (generator-critic)?"
    options:
      A: "Lab 12 replaces both Lab 10 and Lab 11 with a unified planner-executor architecture."
      B: "Lab 12 imports Lab 11's critic and adds a critic step before each execution batch."
      C: "Lab 12 reuses Lab 10's `chat_with_tools`, `web_search`, `fetch_page`, `_action_hash`, and `StrictModel` patterns verbatim. It adds new components (Plan schema, planner agent, dependency-resolving dispatcher, ThreadPoolExecutor-based concurrency, replanning hook with plan-signature dedup, synthesizer) without modifying anything from prior labs. It does NOT use Lab 11's critic — composing plan-and-execute with critique is left as a stretch exercise. The patterns are designed to be independently composable."
      D: "Lab 12 requires switching from message-passing to shared state via LangGraph's StateGraph."
    answer: C
    explanation: |
      Lab 12 is a clean extension on Lab 10's machinery, not a
      replacement. The chat client, web tools, action-hash dedup, and
      StrictModel pattern transfer unchanged. What's new: schemas,
      the planner role, the dispatcher, the bounded concurrency, and
      the bounded replanning. Lab 11's critic is deliberately *not*
      part of Lab 12 — the patterns compose, but composing them is
      its own design decision (a critic can review the plan, the
      executor outputs, or the final synthesis; each placement has
      different cost and quality implications). Keeping them separate
      in the headline lab makes the plan-and-execute pattern clear on
      its own. Option A overstates the change. Option B is the future
      stretch composition, not Lab 12 itself. Option D conflates
      coordination patterns with state architecture (Lab 12 still uses
      message-passing — function calls between agents — same as Lab
      10/11).
    review:
      page: concepts/multi-agent/planner-executor-pattern.md
      section: "Composing with Lab 10 and Lab 11"
---

# Quiz: Plan-and-execute

> 🟡 Intermediate · 8 questions · ~10 min · Passing: 6/8

Tests your grasp of when plan-and-execute beats supervisor-worker and ReAct, the four plan-and-execute-specific failure modes, the five planner-prompt rules, bounded replanning, and how the pattern composes with Lab 10/11 machinery.

If you're below 6/8, the answers point at specific sections of the two concept pages — use them as a re-read guide before the lab.

---

## Question 1

Your task is "find me the answer to this open-ended question" where each step's result determines what makes sense next. You're choosing between plan-and-execute and ReAct. Which framing is most accurate?

- A. Always use plan-and-execute — the plan is auditable, which is strictly better.
- B. Use ReAct. Plan-and-execute commits to a plan upfront; on tasks where the trajectory can't be known in advance, that commitment produces brittle plans that don't survive contact with reality.
- C. Use plan-and-execute with `MAX_REPLANS = 10` — frequent replanning compensates for the lack of upfront knowledge.
- D. Use neither; this task wants a single-agent ReAct loop with no planning.

<details>
<summary>Reveal answer</summary>

**B.**

Plan-and-execute optimizes the median run on tasks with clear upfront decomposition. For exploratory tasks where each step's result determines what makes sense next, the planner is just imagining a trajectory the supervisor would have followed anyway — and the imagined trajectory often doesn't survive execution. ReAct's interleaved think-act-think-act is built for exactly this case. Option A ignores when plan-and-execute is genuinely the wrong call. Option C is replanning thrash by design — frequent replans are a symptom that you've chosen the wrong pattern. Option D conflates ReAct with single-agent ReAct; ReAct is the pattern, single-agent is one deployment of it.

Review: [`concepts/multi-agent/plan-and-execute.md`](../../concepts/multi-agent/plan-and-execute.md#when-plan-and-execute-is-the-wrong-call) — "When plan-and-execute is the wrong call".

</details>

---

## Question 2

Your planner emits a step that says "fetch the third URL from step_1's results." At execution time, step_1 returns only two results. What's the failure mode and what's the right fix?

- A. This is execution drift — the executor should pick a different URL. Fix: relax the anti-improvement prompt.
- B. This is plan brittleness — the planner committed to a structure (a third result) that didn't hold. Fix: planner-prompt rule that step descriptions use role-based references ("fetch URLs from step_1") and let the executor resolve them from actual dependency outputs.
- C. This is the plan-execution gap — the executor doesn't have a "fetch the third URL" tool. Fix: add such a tool.
- D. This is replanning thrash — the planner should produce a fresh plan whenever a step fails.

<details>
<summary>Reveal answer</summary>

**B.**

This is the canonical plan brittleness failure mode. The planner guessed what step_1's result would look like (3+ URLs) and wrote step_2 assuming the guess held. The fix is structural: step descriptions should be **role-based** ("fetch URLs from step_1's results" or "fetch the most relevant URLs") rather than **structural** ("fetch the third URL"). The executor sees the actual dependency outputs at runtime and adapts. Option A misnames the failure — execution drift is the executor deviating from the plan, not the plan being wrong. Option C confuses brittleness with the plan-execution gap. Option D treats the symptom; the fix is at the planner-prompt level.

Review: [`concepts/multi-agent/plan-and-execute.md`](../../concepts/multi-agent/plan-and-execute.md#plan-brittleness) — "Plan brittleness".

</details>

---

## Question 3

In Lab 12, the executor's tool registry is passed into the planner's system prompt and the `Plan.validate_graph()` method rejects plans referencing unknown tools. Which failure mode does this primarily prevent?

- A. Plan brittleness — by constraining the planner, plans become more robust.
- B. Replanning thrash — by validating upfront, replans become rarer.
- C. Plan-execution gap — the planner can't emit steps using tools the executor doesn't have, because the planner is told what tools exist and validation enforces it.
- D. Sycophancy — the planner can't agree with everything the user wanted.

<details>
<summary>Reveal answer</summary>

**C.**

The plan-execution gap is the failure mode where the plan looks reasonable to a human reading it but the executor can't actually run the steps (tools that don't exist, capabilities the executor lacks). Passing the executor's tool registry into the planner's system prompt and validating against it at plan-emit time closes this gap structurally. Option A is plausible but misnamed — constraining tool choice doesn't fix the larger brittleness pattern. Option B is downstream — fewer plan-execution-gap failures means fewer replans, but the mechanism is the validation, not the replan cap. Option D is from Lab 11; sycophancy isn't a plan-and-execute failure mode.

Review: [`concepts/multi-agent/plan-and-execute.md`](../../concepts/multi-agent/plan-and-execute.md#plan-execution-gap) — "Plan-execution gap".

</details>

---

## Question 4

Lab 12 sets `MAX_PARALLEL_EXECUTORS = 3` via `ThreadPoolExecutor(max_workers=3)`. Which framing of pool size is most accurate?

- A. Pool size is a cost lever — 3 concurrent calls cost a third of 3 sequential calls.
- B. Pool size is a latency lever — 3 concurrent calls cost the same as 3 sequential calls, but finish faster. More workers = more concurrent calls = lower wall-clock; 3 is the empirical sweet spot before rate limits and debugging trace complexity make larger pools costly to operate.
- C. Pool size is a quality lever — more workers means better answers because more steps run in parallel.
- D. Pool size should match the number of CPUs.

<details>
<summary>Reveal answer</summary>

**B.**

Parallelism is a wall-clock optimization, not a cost or quality optimization. Three concurrent LLM calls cost the same as three sequential ones — you still pay for each. What changes is wall-clock time. Three workers is the empirical sweet spot: enough parallelism to matter for tasks with 3-4 independent fetches; small enough that shared API rate limits don't fire and debugging traces stay readable. Option A inverts the cost relationship. Option C is wishful thinking — parallelism doesn't change answer quality. Option D is a category error — these are network-bound IO calls, not CPU-bound work.

Review: [`concepts/multi-agent/planner-executor-pattern.md`](../../concepts/multi-agent/planner-executor-pattern.md#executor-pool-concurrency) — "Executor pool concurrency".

</details>

---

## Question 5

When the supervisor invokes the replanner after a failure, Lab 12 maintains a `seen_plan_sigs` set keyed on the structural plan signature. If the replanner returns an identical plan to one that already failed, Lab 12 escalates to `partial_after_cap` instead of trying it. Why?

- A. To save on LLM calls — the second attempt would cost the same as the first.
- B. Because running the same plan again produces the same failure; the dedup is the same action-hash discipline from Lab 03/10/11, applied at the plan level. It prevents replanning thrash where the replanner emits a slightly-reworded but structurally identical plan.
- C. Because Pydantic forbids it.
- D. Because identical plans violate the parallel-group integrity rule.

<details>
<summary>Reveal answer</summary>

**B.**

Plan signatures are computed from structural content (step IDs, tools, args, dependencies, parallel groups) — not prose descriptions. So a replan that changes only the wording but keeps the same steps produces the same signature. If we tried it, we'd get the same failure. The escalation is the same discipline from prior labs: when you detect a loop, surface it honestly rather than letting it run. Option A is true but secondary. Option C is unrelated. Option D conflates plan dedup with parallel-group validation.

Review: [`concepts/multi-agent/plan-and-execute.md`](../../concepts/multi-agent/plan-and-execute.md#replanning-thrash) — "Replanning thrash".

</details>

---

## Question 6

In Lab 12's `Plan` schema, `depends_on` and `parallel_group` are two different fields. Which statement most accurately distinguishes them?

- A. They're synonyms — `parallel_group` is just sugar for empty `depends_on`.
- B. `depends_on` declares what a step needs (a correctness constraint); `parallel_group` declares which steps the planner claims can run together (a parallelism hint). The dispatcher uses `depends_on` to decide when a step is ready, and `parallel_group` to decide which ready steps to batch together. The graph validator rejects plans where steps in the same `parallel_group` have transitive dependencies — that's a contradiction.
- C. `depends_on` is for serial execution and `parallel_group` is for parallel execution; they're mutually exclusive.
- D. `parallel_group` is for steps with the same tool; `depends_on` is for steps with different tools.

<details>
<summary>Reveal answer</summary>

**B.**

The two fields encode different concerns. `depends_on` is a *correctness* statement: step B needs the output of step A to proceed. `parallel_group` is a *parallelism* statement: the planner claims these steps can run together. They interact logically — a step can be in a parallel group AND have dependencies (those dependencies must be outside the group); what's forbidden is being in the same group as a step you depend on. Option A erases the distinction. Option C is wrong because a step can have both. Option D invents a relationship that doesn't exist.

Review: [`concepts/multi-agent/planner-executor-pattern.md`](../../concepts/multi-agent/planner-executor-pattern.md#plan-representation) — "Plan representation".

</details>

---

## Question 7

Which of the five planner-prompt rules is most foundational — i.e., violating it produces the worst downstream consequences?

- A. Rule 1 — atomic steps. Multi-tool steps make trace analysis hard but don't break execution.
- B. Rule 2 — explicit dependencies. Implicit dependencies produce race conditions when the supervisor parallelizes; the executor reads inconsistent state and produces wrong answers, not just slow ones.
- C. Rule 3 — honest parallel groups. Cosmetic parallelism is wasteful but the validator catches it.
- D. Rule 5 — bounded plans. Long plans are brittle but a long plan that runs is better than a short plan that doesn't.

<details>
<summary>Reveal answer</summary>

**B.**

Rule 2 (explicit dependencies) is foundational because violating it produces **wrong answers**, not just slow or brittle ones. If step B uses step A's output but doesn't declare `depends_on: ["A"]`, the dispatcher may parallelize them, and step B will run with stale/missing state from step A. The result is a race condition that's correct-looking but factually wrong. The other rules produce slower, longer, or harder-to-debug plans — but they don't produce wrong answers in the same structural way. Rule 3 is close (and is enforced by the validator), but Rule 2 is what makes Rule 3 even possible to reason about.

Review: [`concepts/multi-agent/planner-executor-pattern.md`](../../concepts/multi-agent/planner-executor-pattern.md#the-five-planner-prompt-rules) — "The five planner-prompt rules".

</details>

---

## Question 8

How does Lab 12 compose with Lab 10 (supervisor-worker) and Lab 11 (generator-critic)?

- A. Lab 12 replaces both Lab 10 and Lab 11 with a unified planner-executor architecture.
- B. Lab 12 imports Lab 11's critic and adds a critic step before each execution batch.
- C. Lab 12 reuses Lab 10's `chat_with_tools`, `web_search`, `fetch_page`, `_action_hash`, and `StrictModel` patterns verbatim. It adds new components (Plan schema, planner agent, dependency-resolving dispatcher, ThreadPoolExecutor-based concurrency, replanning hook with plan-signature dedup, synthesizer) without modifying anything from prior labs. It does NOT use Lab 11's critic — composing plan-and-execute with critique is left as a stretch exercise. The patterns are designed to be independently composable.
- D. Lab 12 requires switching from message-passing to shared state via LangGraph's StateGraph.

<details>
<summary>Reveal answer</summary>

**C.**

Lab 12 is a clean extension on Lab 10's machinery, not a replacement. The chat client, web tools, action-hash dedup, and StrictModel pattern transfer unchanged. What's new: schemas, the planner role, the dispatcher, the bounded concurrency, and the bounded replanning. Lab 11's critic is deliberately *not* part of Lab 12 — the patterns compose, but composing them is its own design decision (a critic can review the plan, the executor outputs, or the final synthesis; each placement has different cost and quality implications). Keeping them separate in the headline lab makes the plan-and-execute pattern clear on its own. Option A overstates the change. Option B is the future stretch composition. Option D conflates coordination patterns with state architecture.

Review: [`concepts/multi-agent/planner-executor-pattern.md`](../../concepts/multi-agent/planner-executor-pattern.md#composing-with-lab-10-and-lab-11) — "Composing with Lab 10 and Lab 11".

</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Strong grasp. Move on to Lab 12 (or skip ahead if you've already built it). |
| 6-7/8 | Good. Re-read any concept-page sections flagged in the questions you missed. |
| 4-5/8 | Re-read both concept pages before attempting Lab 12. |
| < 4/8 | Re-do Lab 10 first — plan-and-execute extends Lab 10's machinery, and gaps here often trace back to weak Lab 10 footing. |
