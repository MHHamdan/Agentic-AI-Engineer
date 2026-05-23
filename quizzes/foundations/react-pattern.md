---
quiz_id: foundations-react-pattern
title: "The ReAct pattern"
source:
  - concepts/agents/react-pattern.md
length_minutes: 7
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What does *ReAct* stand for in the context of LLM agents?"
    options:
      A: "Reactive Architecture."
      B: "Reasoning + Acting."
      C: "Recursive Activation."
      D: "Real-time Action."
    answer: B
    explanation: |
      ReAct = Reasoning + Acting. The pattern interleaves natural-language
      thoughts (reasoning) with tool calls (acting). It comes from Yao et al.,
      ICLR 2023, and is the default scaffolding for modern tool-using LLM
      agents.
    review:
      page: concepts/agents/react-pattern.md
      section: "TL;DR"

  - id: q2
    difficulty: easy
    question: "In a ReAct step, what order do thought, action, and observation appear in?"
    options:
      A: "Action → Observation → Thought."
      B: "Thought → Action → Observation."
      C: "Observation → Thought → Action."
      D: "Thought → Observation → Action."
    answer: B
    explanation: |
      Thought first (the model plans), then Action (it commits to a tool
      call), then Observation (the tool's result). The next step's thought
      then conditions on that observation. Reversing the order to "act
      first, explain later" produces post-hoc rationalizations that don't
      constrain the next action.
    review:
      page: concepts/agents/react-pattern.md
      section: "The pattern"

  - id: q3
    difficulty: medium
    question: "Why is *acting only* (no thoughts) less reliable than ReAct on multi-step tasks?"
    options:
      A: "Acting only is slower per step."
      B: "Without a thought slot, the model has no place to reason about the last observation before committing the next action."
      C: "Tool APIs reject responses with no text content."
      D: "Acting only produces malformed JSON."
    answer: B
    explanation: |
      Acting-only is faster and cheaper, but it removes the model's
      'workspace' for integrating new information. The thought before each
      action is where the model conditions on the most recent observation
      and decides what to do next. Without it, errors don't get caught and
      plans don't get adjusted.
    review:
      page: concepts/agents/react-pattern.md
      section: "Why interleave thoughts and actions?"

  - id: q4
    difficulty: medium
    question: "What does the *Thought* in a ReAct step actually do, mechanically?"
    options:
      A: "It is executed by the agent runtime."
      B: "It is appended to the state, conditioning future model outputs, but is never executed."
      C: "It is shown to the user but discarded from state."
      D: "It is sent as a system message on the next turn."
    answer: B
    explanation: |
      Thoughts are appended to the state (the conversation) along with the
      action and observation. They're free in compute terms — same forward
      pass — but they shape every subsequent generation by being part of
      the model's context. They're not executed and not separately treated.
    review:
      page: concepts/agents/react-pattern.md
      section: "The pattern"

  - id: q5
    difficulty: medium
    question: "ReAct's termination condition is..."
    options:
      A: "A hardcoded `max_steps` always set to 5."
      B: "Any non-tool response from the model, plus runtime-enforced step caps."
      C: "An external classifier that decides 'is the agent done?'"
      D: "The model emits a special end-of-stream token."
    answer: B
    explanation: |
      In ReAct, terminating is just one of the available actions — the
      model produces a 'respond' rather than a tool call. The runtime adds
      hard stops (step cap, repeated-action detection, budget cap) as
      safety. There's no external classifier and no special token.
    review:
      page: concepts/agents/react-pattern.md
      section: "How it shows up in practice"

  - id: q6
    difficulty: medium
    question: "A ReAct agent emits a thought that says 'I should check X', but then calls a tool that does Y. What's the most likely cause?"
    options:
      A: "Bug in the LLM provider's API."
      B: "The model has cached an earlier plan and is following it instead of this turn's thought."
      C: "The tool descriptions are too short."
      D: "The temperature is set to 0."
    answer: B
    explanation: |
      Thought-action mismatch is most often caused by the model anchoring
      on an earlier plan in the conversation history. Mitigation: shorter
      thoughts (less anchoring), or a prompt that says 'your action must
      follow from this turn's thought.' Temperature-0 generally *reduces*
      this issue; raising it makes mismatch more likely.
    review:
      page: concepts/agents/react-pattern.md
      section: "Common failure modes"

  - id: q7
    difficulty: hard
    question: "Which of these tasks is ReAct **not** the right pattern for?"
    options:
      A: "Searching the web, reading results, following up with another query."
      B: "Inspecting a dataframe and deciding what to plot."
      C: "Translating a paragraph from English to Spanish."
      D: "A code agent reading a file, running a test, editing on failure."
    answer: C
    explanation: |
      ReAct fits when the next move depends on the last observation. A
      one-shot translation needs no observation loop — the input is the
      input and the output is the output. The other three all benefit from
      ReAct because each step's action genuinely depends on what just
      happened. If your task is fully deterministic, use a pipeline (or no
      framework at all); reach for ReAct when adaptation matters.
    review:
      page: concepts/agents/react-pattern.md
      section: "When it isn't"

  - id: q8
    difficulty: hard
    question: "In the formal factorization $\\pi_\\theta(\\tau_t, a_t \\mid s_t) = \\pi_\\theta(\\tau_t \\mid s_t) \\cdot \\pi_\\theta(a_t \\mid s_t, \\tau_t)$, what does the *second factor* represent?"
    options:
      A: "The probability of generating the thought given the state."
      B: "The probability of the action given the state *and* the thought."
      C: "The transition probability of the world."
      D: "The reward for taking action $a_t$."
    answer: B
    explanation: |
      The second factor is the action distribution *conditioned on the
      thought as well as the state*. This is the technical reason ReAct
      works: the model chooses an action under a more refined context
      (state + thought) than a no-thought agent would have. The first
      factor is the thought distribution alone; reward and transition are
      different objects entirely.
    review:
      page: concepts/agents/react-pattern.md
      section: "🧮 Math behind it"
---

# 🧠 Quiz · The ReAct pattern

> ⏱ ~7 min · 🎯 Pass: 6/8 · 📖 Source: [`concepts/agents/react-pattern.md`](../../concepts/agents/react-pattern.md)

Try each question before expanding its answer. Score yourself at the end.

---

## Question 1 *(easy)*

What does *ReAct* stand for in the context of LLM agents?

A. Reactive Architecture.
B. Reasoning + Acting.
C. Recursive Activation.
D. Real-time Action.

<details>
<summary>Show answer</summary>

**Answer: B** — Reasoning + Acting.

ReAct = Reasoning + Acting. The pattern interleaves natural-language thoughts (reasoning) with tool calls (acting). It comes from Yao et al., ICLR 2023, and is the default scaffolding for modern tool-using LLM agents.

→ Review: [`react-pattern.md` § "TL;DR"](../../concepts/agents/react-pattern.md#tldr)

</details>

---

## Question 2 *(easy)*

In a ReAct step, what order do thought, action, and observation appear in?

A. Action → Observation → Thought.
B. Thought → Action → Observation.
C. Observation → Thought → Action.
D. Thought → Observation → Action.

<details>
<summary>Show answer</summary>

**Answer: B** — Thought → Action → Observation.

Thought first (the model plans), then Action (it commits to a tool call), then Observation (the tool's result). The next step's thought then conditions on that observation. Reversing the order to "act first, explain later" produces post-hoc rationalizations that don't constrain the next action.

→ Review: [`react-pattern.md` § "The pattern"](../../concepts/agents/react-pattern.md#the-pattern)

</details>

---

## Question 3 *(medium)*

Why is *acting only* (no thoughts) less reliable than ReAct on multi-step tasks?

A. Acting only is slower per step.
B. Without a thought slot, the model has no place to reason about the last observation before committing the next action.
C. Tool APIs reject responses with no text content.
D. Acting only produces malformed JSON.

<details>
<summary>Show answer</summary>

**Answer: B** — No workspace for integrating observations.

Acting-only is faster and cheaper, but it removes the model's "workspace" for integrating new information. The thought before each action is where the model conditions on the most recent observation and decides what to do next. Without it, errors don't get caught and plans don't get adjusted.

→ Review: [`react-pattern.md` § "Why interleave thoughts and actions?"](../../concepts/agents/react-pattern.md#why-interleave-thoughts-and-actions)

</details>

---

## Question 4 *(medium)*

What does the *Thought* in a ReAct step actually do, mechanically?

A. It is executed by the agent runtime.
B. It is appended to the state, conditioning future model outputs, but is never executed.
C. It is shown to the user but discarded from state.
D. It is sent as a system message on the next turn.

<details>
<summary>Show answer</summary>

**Answer: B** — Appended to state, never executed.

Thoughts are appended to the state (the conversation) along with the action and observation. They're free in compute terms — same forward pass — but they shape every subsequent generation by being part of the model's context. They're not executed and not separately treated.

→ Review: [`react-pattern.md` § "The pattern"](../../concepts/agents/react-pattern.md#the-pattern)

</details>

---

## Question 5 *(medium)*

ReAct's termination condition is...

A. A hardcoded `max_steps` always set to 5.
B. Any non-tool response from the model, plus runtime-enforced step caps.
C. An external classifier that decides "is the agent done?"
D. The model emits a special end-of-stream token.

<details>
<summary>Show answer</summary>

**Answer: B** — Non-tool response + runtime caps.

In ReAct, terminating is just one of the available actions — the model produces a "respond" rather than a tool call. The runtime adds hard stops (step cap, repeated-action detection, budget cap) as safety. There's no external classifier and no special token.

→ Review: [`react-pattern.md` § "How it shows up in practice"](../../concepts/agents/react-pattern.md#how-it-shows-up-in-practice)

</details>

---

## Question 6 *(medium)*

A ReAct agent emits a thought that says "I should check X", but then calls a tool that does Y. What's the most likely cause?

A. Bug in the LLM provider's API.
B. The model has cached an earlier plan and is following it instead of this turn's thought.
C. The tool descriptions are too short.
D. The temperature is set to 0.

<details>
<summary>Show answer</summary>

**Answer: B** — Anchoring on an earlier plan.

Thought-action mismatch is most often caused by the model anchoring on an earlier plan in the conversation history. Mitigation: shorter thoughts (less anchoring), or a prompt that says "your action must follow from this turn's thought." Temperature-0 generally *reduces* this issue; raising it makes mismatch more likely.

→ Review: [`react-pattern.md` § "Common failure modes"](../../concepts/agents/react-pattern.md#common-failure-modes)

</details>

---

## Question 7 *(hard)*

Which of these tasks is ReAct **not** the right pattern for?

A. Searching the web, reading results, following up with another query.
B. Inspecting a dataframe and deciding what to plot.
C. Translating a paragraph from English to Spanish.
D. A code agent reading a file, running a test, editing on failure.

<details>
<summary>Show answer</summary>

**Answer: C** — A one-shot translation.

ReAct fits when the next move depends on the last observation. A one-shot translation needs no observation loop — the input is the input and the output is the output. The other three all benefit from ReAct because each step's action genuinely depends on what just happened. If your task is fully deterministic, use a pipeline (or no framework at all); reach for ReAct when adaptation matters.

→ Review: [`react-pattern.md` § "When it isn't"](../../concepts/agents/react-pattern.md#when-it-isnt)

</details>

---

## Question 8 *(hard)*

In the formal factorization $\pi_\theta(\tau_t, a_t \mid s_t) = \pi_\theta(\tau_t \mid s_t) \cdot \pi_\theta(a_t \mid s_t, \tau_t)$, what does the *second factor* represent?

A. The probability of generating the thought given the state.
B. The probability of the action given the state *and* the thought.
C. The transition probability of the world.
D. The reward for taking action $a_t$.

<details>
<summary>Show answer</summary>

**Answer: B** — Action conditional on state and thought.

The second factor is the action distribution *conditioned on the thought as well as the state*. This is the technical reason ReAct works: the model chooses an action under a more refined context (state + thought) than a no-thought agent would have. The first factor is the thought distribution alone; reward and transition are different objects entirely.

→ Review: [`react-pattern.md` § "🧮 Math behind it"](../../concepts/agents/react-pattern.md#-math-behind-it)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the sections you missed, then retake. |
| < 4/8 | Work through [`react-pattern.md`](../../concepts/agents/react-pattern.md) carefully, then come back. |

Next: 🧠 [Tool design and selection](./tool-design-and-selection.md).
