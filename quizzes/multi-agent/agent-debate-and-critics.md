---
quiz_id: multi-agent-agent-debate-and-critics
title: "Agent debate and critics: when generator-critic earns its place, sycophancy, and critic-prompt design"
source:
  - concepts/multi-agent/agent-debate-and-critics.md
  - concepts/multi-agent/generator-critic-pattern.md
  - labs/11-generator-critic-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "You're deciding whether to add a critic to your single-agent system. The system already produces ~95% correct outputs on its task. The remaining 5% of failures are subtle factual errors. Which framing is most accurate?"
    options:
      A: "Always add a critic — it can only improve quality."
      B: "Don't add a critic — 95% is already high; the marginal gain doesn't clear the 2x cost."
      C: "Adding a critic earns its place if the cost of the remaining 5% errors is high (e.g., legal/medical) AND if you can write a rubric concrete enough that the critic has signal the generator lacks."
      D: "Critics only work for generation tasks — don't add one to a verification task."
    answer: C
    explanation: |
      Critics earn their place when the cost-benefit trade clears the
      ~2x latency/token bar. A 95%-correct system with high-stakes
      errors is exactly the case where a critic can pay off — but only
      if you can articulate the eval criterion concretely enough to
      encode in a critic prompt. The concept page's "critic prompt is
      an eval rubric applied at inference time" framing matters: if
      you can't write a useful eval rubric for the task (Lab 09
      territory), you can't write a useful critic prompt either.
      Option A ignores cost. Option B ignores stakes. Option D
      misunderstands the pattern.
    review:
      page: concepts/multi-agent/agent-debate-and-critics.md
      section: "When critique earns its place"

  - id: q2
    difficulty: easy
    question: "Your critic returns {\"status\": \"ok\"} every time you call it, regardless of draft quality. Most likely root cause?"
    options:
      A: "The critic is doing its job correctly — your drafts are simply good."
      B: "Sycophancy — the critic prompt isn't anchored to a strict rubric, and RLHF-trained models default toward agreement when reviewing."
      C: "The supervisor isn't passing the draft correctly."
      D: "The critic's temperature is too low."
    answer: B
    explanation: |
      Sycophancy is the most common multi-agent debate failure mode
      (Sharma et al. 2023 documented this as a stable, model-wide
      tendency in production-grade LLMs). The fix isn't a code bug —
      it's the prompt. The diagnostic test in Step 3 of Lab 11 is
      designed to catch exactly this: feed the critic an obviously-bad
      draft and verify it gets flagged. If your critic returns "ok"
      there, your prompt needs the four rules (anchor to checklist,
      default to ok on borderline, require evidence, bound issue list).
      Option A is the trap — "looks fine to me" is what sycophancy
      sounds like. Option D is reversed: temperature=0 actually helps,
      not hurts, sycophancy.
    review:
      page: concepts/multi-agent/generator-critic-pattern.md
      section: "Sycophancy: detection and mitigation"

  - id: q3
    difficulty: medium
    question: "In Lab 11, the critic receives `(draft, original_brief)`. The supervisor's prompt explicitly instructs it to pass the ORIGINAL findings and citations, never the revised/accumulated brief. Why?"
    options:
      A: "It saves tokens."
      B: "To prevent critique drift — if the critic's judgment depended on previous critic results or revised briefs, its standards would shift across rounds, making the refinement loop path-dependent."
      C: "Because the writer needs the original brief separately."
      D: "Because the critic API doesn't accept the revision history."
    answer: B
    explanation: |
      The critic is deliberately stateless. Each critique is a fresh
      judgment against the same original rubric. If you "gave the critic
      context" — past results, accumulated briefs — the critic's
      judgments would become path-dependent, which is the opposite of
      what you want for a refinement loop. This is one of the four
      debate failure modes (critique drift) and the mitigation is
      structural: the API shape forbids passing revision history to
      the critic. Option A is true but secondary. Option C is unrelated
      (the writer's brief shape is a different design question). Option
      D inverts the cause — the API doesn't accept it because of the
      design choice, not the other way around.
    review:
      page: concepts/multi-agent/agent-debate-and-critics.md
      section: "Critique drift"

  - id: q4
    difficulty: medium
    question: "Lab 11 caps refinement at `MAX_REFINEMENT_CYCLES = 3`. If the critic still flags issues after the 3rd cycle, the supervisor's prompt instructs it to finalize the last draft AND surface the remaining critic issues in the final answer. Why is this honest-surfacing approach preferred over forcing the critic to approve?"
    options:
      A: "Forcing approval would violate the action-hash dedup."
      B: "The user gets the best draft the system can produce plus an honest account of what's still wrong; this is more valuable than a forced approval would be, and it makes runaway disagreement debuggable rather than silent."
      C: "It saves on critic API calls."
      D: "It's required by LangChain best practices."
    answer: B
    explanation: |
      The honest-surfacing approach is a deliberate design choice with
      two payoffs. First, the user gets transparency — they can decide
      whether the unresolved issues matter for their use case rather
      than being told everything is fine. Second, runaway disagreement
      becomes observable as data: you can count tasks that hit the cap
      and use that as a signal for prompt/rubric improvement. A forced
      approval ("the critic approves whatever the writer last produced
      after 3 rounds") would silently mask the failure mode. Option A
      conflates mechanisms (dedup is a different lever). Option C is
      false (the cap saves cycles, but the question is about what
      happens AT the cap). Option D is irrelevant.
    review:
      page: concepts/multi-agent/generator-critic-pattern.md
      section: "Bounded refinement"

  - id: q5
    difficulty: medium
    question: "Compared to using a separate critic agent, the self-critique variation (same agent reviews its own draft) has which property?"
    options:
      A: "Catches subtle errors at a higher rate because the agent knows what it intended."
      B: "Cheaper and faster, but empirically more sycophantic — the same context that produced the draft has the same blind spots when reviewing it."
      C: "Strictly better for high-stakes tasks because there's no information loss across handoffs."
      D: "Identical in quality; the cost saving is pure upside."
    answer: B
    explanation: |
      The cost-quality trade is real and reproducible. Self-critique
      saves one prompt setup and the round-trip latency of a separate
      agent, but the same model in the same context tends to approve
      its own work. For high-stakes tasks separate-critic is the
      production default. Self-critique works fine for catching obvious
      errors (typos, format violations) but misses subtle errors more
      often than separate-critic does. A useful intermediate is to use
      self-critique as a cheap first pass and separate-critic only on
      drafts that pass it. Option A is backwards — "knows what it
      intended" is a recipe for confirmation bias. Option C ignores
      the empirical evidence. Option D is the misconception the lab
      explicitly counters in Step 7.
    review:
      page: concepts/multi-agent/agent-debate-and-critics.md
      section: "Self-critique vs separate-critic"

  - id: q6
    difficulty: medium
    question: "Which critic-prompt-design rule most directly prevents 'vibe-based' critics that either approve everything or invent arbitrary nits?"
    options:
      A: "Rule 1 — anchor the critic to a checklist, not a vibe."
      B: "Rule 2 — make 'ok' the default for borderline cases."
      C: "Rule 3 — require specific evidence in each issue."
      D: "Rule 4 — bound the issue list to ≤3."
    answer: A
    explanation: |
      Rule 1 is the foundational rule because it changes the critic's
      task from "holistic assessment" (which collapses to sycophancy or
      arbitrary nitpicking) to "apply each item in this checklist." It
      forces concrete pass/fail decisions on enumerable criteria. The
      other three rules compose on top of this:
      Rule 2 (default to ok) mostly affects how borderline cases are
      resolved within the checklist;
      Rule 3 (require evidence) makes each flagged issue grounded;
      Rule 4 (bound the list) prevents the critic from drowning the
      generator in revisions.
      But without Rule 1 — without a checklist — the other rules don't
      have a structure to apply to.
    review:
      page: concepts/multi-agent/generator-critic-pattern.md
      section: "Critic prompt design — the four rules"

  - id: q7
    difficulty: hard
    question: "Reading a Lab 11 trace: supervisor calls writer (cycle 0), critic flags 3 issues; writer (cycle 1), critic flags 3 different issues; writer (cycle 2), critic flags 3 different issues again. Which interpretation is most accurate?"
    options:
      A: "The pattern is working — each cycle catches different issues."
      B: "This is likely runaway disagreement and/or critique drift; the rubric is too loose and the critic is finding new things to flag each round rather than converging."
      C: "The writer is broken — it should produce the same draft each time."
      D: "This is normal; convergence in refinement loops typically takes 5-7 rounds."
    answer: B
    explanation: |
      A healthy refinement loop converges: cycle 0 finds N issues;
      after revision, cycle 1 finds at most a subset of N (because some
      were fixed); cycle 2 either finds zero or a smaller subset. If
      each cycle finds 3 *different* issues, either the rubric is too
      open-ended (the critic is shifting standards — critique drift) or
      the critic is finding new things to be unhappy about (runaway
      disagreement). Both failure modes have the same fix: tighten the
      rubric. Make the checklist explicit and finite; require evidence;
      ensure the critic is stateless. Option A romanticizes the
      symptom. Option C confuses cause and effect — the writer should
      produce DIFFERENT drafts each time (addressing the issues), just
      not different-with-new-issues. Option D is fiction — production
      refinement loops are designed to converge in 1-2 rounds, with 3
      being a hard cap.
    review:
      page: concepts/multi-agent/agent-debate-and-critics.md
      section: "Runaway disagreement"

  - id: q8
    difficulty: hard
    question: "How does Lab 11 compose with Lab 10's machinery? Pick the most accurate statement."
    options:
      A: "Lab 11 replaces Lab 10's supervisor with a new debate-specific orchestrator."
      B: "Lab 11 keeps Lab 10's agent loop verbatim and adds one new worker tool (`call_critic`), updates the supervisor's prompt to describe the refinement loop, and raises `SUPERVISOR_MAX_STEPS` from 6 to 10. Nothing else changes."
      C: "Lab 11 wraps Lab 10's supervisor in a higher-level loop that re-invokes the supervisor on critique."
      D: "Lab 11 requires switching from message-passing to shared-state."
    answer: B
    explanation: |
      The composition is deliberately minimal. Lab 11 demonstrates that
      iterative refinement is NOT a new framework or new abstraction —
      it's the same supervisor-worker pattern with one more worker and
      an updated prompt. The refinement "loop" is emergent from the
      supervisor's standard agent loop calling tools in sequence,
      guided by the system prompt and bounded by the hard cap. The
      researcher and writer workers from Lab 10 are unchanged (the
      writer's brief shape was extended backward-compatibly to accept
      optional revision_issues). The chat client, action-hash dedup,
      and structured-error envelope all transfer verbatim. This is the
      payoff of the Path 03 "from scratch first" discipline: extending
      the system is a 100-line delta, not a rewrite.
    review:
      page: concepts/multi-agent/generator-critic-pattern.md
      section: "Composing with Lab 10"
---

# Quiz: Agent debate and critics

> 🟡 Intermediate · 8 questions · ~10 min · Passing: 6/8

Tests your grasp of when generator-critic earns its place, the four debate-specific failure modes (especially sycophancy), the critic-prompt design rules, and how the pattern composes with Lab 10's supervisor-worker machinery.

If you're below 6/8, the answers point at specific sections of the two concept pages — use them as a re-read guide before the lab.

---

## Question 1

You're deciding whether to add a critic to your single-agent system. The system already produces ~95% correct outputs on its task. The remaining 5% of failures are subtle factual errors. Which framing is most accurate?

- A. Always add a critic — it can only improve quality.
- B. Don't add a critic — 95% is already high; the marginal gain doesn't clear the 2x cost.
- C. Adding a critic earns its place if the cost of the remaining 5% errors is high (e.g., legal/medical) AND if you can write a rubric concrete enough that the critic has signal the generator lacks.
- D. Critics only work for generation tasks — don't add one to a verification task.

<details>
<summary>Reveal answer</summary>

**C.**

Critics earn their place when the cost-benefit trade clears the ~2x latency/token bar. A 95%-correct system with high-stakes errors is exactly the case where a critic can pay off — but only if you can articulate the eval criterion concretely enough to encode in a critic prompt. The concept page's "critic prompt is an eval rubric applied at inference time" framing matters: if you can't write a useful eval rubric for the task (Lab 09 territory), you can't write a useful critic prompt either. Option A ignores cost. Option B ignores stakes. Option D misunderstands the pattern.

Review: [`concepts/multi-agent/agent-debate-and-critics.md`](../../concepts/multi-agent/agent-debate-and-critics.md#when-critique-earns-its-place) — "When critique earns its place".

</details>

---

## Question 2

Your critic returns `{"status": "ok"}` every time you call it, regardless of draft quality. Most likely root cause?

- A. The critic is doing its job correctly — your drafts are simply good.
- B. Sycophancy — the critic prompt isn't anchored to a strict rubric, and RLHF-trained models default toward agreement when reviewing.
- C. The supervisor isn't passing the draft correctly.
- D. The critic's temperature is too low.

<details>
<summary>Reveal answer</summary>

**B.**

Sycophancy is the most common multi-agent debate failure mode (Sharma et al. 2023 documented this as a stable, model-wide tendency in production-grade LLMs). The fix isn't a code bug — it's the prompt. The diagnostic test in Step 3 of Lab 11 is designed to catch exactly this: feed the critic an obviously-bad draft and verify it gets flagged. If your critic returns "ok" there, your prompt needs the four rules (anchor to checklist, default to ok on borderline, require evidence, bound issue list). Option A is the trap — "looks fine to me" is what sycophancy sounds like. Option D is reversed: `temperature=0` actually helps, not hurts, sycophancy.

Review: [`concepts/multi-agent/generator-critic-pattern.md`](../../concepts/multi-agent/generator-critic-pattern.md#sycophancy-detection-and-mitigation) — "Sycophancy: detection and mitigation".

</details>

---

## Question 3

In Lab 11, the critic receives `(draft, original_brief)`. The supervisor's prompt explicitly instructs it to pass the ORIGINAL findings and citations, never the revised/accumulated brief. Why?

- A. It saves tokens.
- B. To prevent critique drift — if the critic's judgment depended on previous critic results or revised briefs, its standards would shift across rounds, making the refinement loop path-dependent.
- C. Because the writer needs the original brief separately.
- D. Because the critic API doesn't accept the revision history.

<details>
<summary>Reveal answer</summary>

**B.**

The critic is deliberately stateless. Each critique is a fresh judgment against the same original rubric. If you "gave the critic context" — past results, accumulated briefs — the critic's judgments would become path-dependent, which is the opposite of what you want for a refinement loop. This is one of the four debate failure modes (critique drift) and the mitigation is structural: the API shape forbids passing revision history to the critic. Option A is true but secondary. Option C is unrelated. Option D inverts the cause.

Review: [`concepts/multi-agent/agent-debate-and-critics.md`](../../concepts/multi-agent/agent-debate-and-critics.md#critique-drift) — "Critique drift".

</details>

---

## Question 4

Lab 11 caps refinement at `MAX_REFINEMENT_CYCLES = 3`. If the critic still flags issues after the 3rd cycle, the supervisor's prompt instructs it to finalize the last draft AND surface the remaining critic issues in the final answer. Why is this honest-surfacing approach preferred over forcing the critic to approve?

- A. Forcing approval would violate the action-hash dedup.
- B. The user gets the best draft the system can produce plus an honest account of what's still wrong; this is more valuable than a forced approval would be, and it makes runaway disagreement debuggable rather than silent.
- C. It saves on critic API calls.
- D. It's required by LangChain best practices.

<details>
<summary>Reveal answer</summary>

**B.**

The honest-surfacing approach is a deliberate design choice with two payoffs. First, the user gets transparency — they can decide whether the unresolved issues matter for their use case rather than being told everything is fine. Second, runaway disagreement becomes observable as data: you can count tasks that hit the cap and use that as a signal for prompt/rubric improvement. A forced approval would silently mask the failure mode. Option A conflates mechanisms. Option C is false. Option D is irrelevant.

Review: [`concepts/multi-agent/generator-critic-pattern.md`](../../concepts/multi-agent/generator-critic-pattern.md#bounded-refinement) — "Bounded refinement".

</details>

---

## Question 5

Compared to using a separate critic agent, the self-critique variation (same agent reviews its own draft) has which property?

- A. Catches subtle errors at a higher rate because the agent knows what it intended.
- B. Cheaper and faster, but empirically more sycophantic — the same context that produced the draft has the same blind spots when reviewing it.
- C. Strictly better for high-stakes tasks because there's no information loss across handoffs.
- D. Identical in quality; the cost saving is pure upside.

<details>
<summary>Reveal answer</summary>

**B.**

The cost-quality trade is real and reproducible. Self-critique saves one prompt setup and the round-trip latency of a separate agent, but the same model in the same context tends to approve its own work. For high-stakes tasks separate-critic is the production default. Self-critique works fine for catching obvious errors but misses subtle errors more often than separate-critic does. A useful intermediate is to use self-critique as a cheap first pass and separate-critic only on drafts that pass it. Option A is backwards. Option C ignores the empirical evidence. Option D is the misconception Lab 11 Step 7 counters.

Review: [`concepts/multi-agent/agent-debate-and-critics.md`](../../concepts/multi-agent/agent-debate-and-critics.md#self-critique-vs-separate-critic) — "Self-critique vs separate-critic".

</details>

---

## Question 6

Which critic-prompt-design rule most directly prevents "vibe-based" critics that either approve everything or invent arbitrary nits?

- A. Rule 1 — anchor the critic to a checklist, not a vibe.
- B. Rule 2 — make "ok" the default for borderline cases.
- C. Rule 3 — require specific evidence in each issue.
- D. Rule 4 — bound the issue list to ≤3.

<details>
<summary>Reveal answer</summary>

**A.**

Rule 1 is the foundational rule because it changes the critic's task from "holistic assessment" (which collapses to sycophancy or arbitrary nitpicking) to "apply each item in this checklist." It forces concrete pass/fail decisions on enumerable criteria. The other three rules compose on top of this — Rule 2 affects how borderline cases are resolved within the checklist; Rule 3 makes each flagged issue grounded; Rule 4 prevents the critic from drowning the generator in revisions. But without Rule 1, the other rules don't have a structure to apply to.

Review: [`concepts/multi-agent/generator-critic-pattern.md`](../../concepts/multi-agent/generator-critic-pattern.md#critic-prompt-design--the-four-rules) — "Critic prompt design — the four rules".

</details>

---

## Question 7

Reading a Lab 11 trace: supervisor calls writer (cycle 0), critic flags 3 issues; writer (cycle 1), critic flags 3 different issues; writer (cycle 2), critic flags 3 different issues again. Which interpretation is most accurate?

- A. The pattern is working — each cycle catches different issues.
- B. This is likely runaway disagreement and/or critique drift; the rubric is too loose and the critic is finding new things to flag each round rather than converging.
- C. The writer is broken — it should produce the same draft each time.
- D. This is normal; convergence in refinement loops typically takes 5-7 rounds.

<details>
<summary>Reveal answer</summary>

**B.**

A healthy refinement loop converges: cycle 0 finds N issues; after revision, cycle 1 finds at most a subset of N (because some were fixed); cycle 2 either finds zero or a smaller subset. If each cycle finds 3 *different* issues, either the rubric is too open-ended (critique drift) or the critic is finding new things to be unhappy about (runaway disagreement). Both failure modes have the same fix: tighten the rubric — make the checklist explicit and finite, require evidence, ensure the critic is stateless. Option A romanticizes the symptom. Option C confuses cause and effect. Option D is fiction — production refinement loops are designed to converge in 1-2 rounds, with 3 being a hard cap.

Review: [`concepts/multi-agent/agent-debate-and-critics.md`](../../concepts/multi-agent/agent-debate-and-critics.md#runaway-disagreement) — "Runaway disagreement".

</details>

---

## Question 8

How does Lab 11 compose with Lab 10's machinery? Pick the most accurate statement.

- A. Lab 11 replaces Lab 10's supervisor with a new debate-specific orchestrator.
- B. Lab 11 keeps Lab 10's agent loop verbatim and adds one new worker tool (`call_critic`), updates the supervisor's prompt to describe the refinement loop, and raises `SUPERVISOR_MAX_STEPS` from 6 to 10. Nothing else changes.
- C. Lab 11 wraps Lab 10's supervisor in a higher-level loop that re-invokes the supervisor on critique.
- D. Lab 11 requires switching from message-passing to shared-state.

<details>
<summary>Reveal answer</summary>

**B.**

The composition is deliberately minimal. Lab 11 demonstrates that iterative refinement is NOT a new framework or new abstraction — it's the same supervisor-worker pattern with one more worker and an updated prompt. The refinement "loop" is emergent from the supervisor's standard agent loop calling tools in sequence, guided by the system prompt and bounded by the hard cap. The researcher and writer workers from Lab 10 are unchanged (the writer's brief shape was extended backward-compatibly). The chat client, action-hash dedup, and structured-error envelope all transfer verbatim. This is the payoff of the Path 03 "from scratch first" discipline: extending the system is a 100-line delta, not a rewrite.

Review: [`concepts/multi-agent/generator-critic-pattern.md`](../../concepts/multi-agent/generator-critic-pattern.md#composing-with-lab-10) — "Composing with Lab 10".

</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Strong grasp. Move on to Lab 11 (or jump ahead if you've already built it). |
| 6-7/8 | Good. Re-read any concept-page sections flagged in the questions you missed. |
| 4-5/8 | Re-read both concept pages before attempting Lab 11. |
| < 4/8 | Re-do Lab 10 first — the generator-critic pattern is a thin extension of supervisor-worker, and gaps here usually trace back to weak Lab 10 footing. |
