---
quiz_id: foundations-agents-basics
title: "Agents — basics"
source:
  - concepts/agents/what-is-an-agent.md
length_minutes: 7
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What is the *defining* property that distinguishes an agent from a one-shot LLM call?"
    options:
      A: "The agent uses a larger model with more parameters."
      B: "The agent has access to external tools."
      C: "The LLM picks the next action in a loop, based on what it observed."
      D: "The agent persists memory across user sessions."
    answer: C
    explanation: |
      Model size is irrelevant — small models can be agents. Tool access is
      *necessary* but not *sufficient*: a one-shot prompt with tool access is
      still one-shot. Cross-session memory is an optional feature, not a
      definition. The property that turns a generation into an agent is the
      loop where the LLM decides what to do next based on observations from
      previous actions.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "TL;DR"

  - id: q2
    difficulty: easy
    question: "Why doesn't a single, very elaborate prompt solve the problems that agents solve?"
    options:
      A: "Single prompts cost more than agent loops."
      B: "Single prompts can't condition on external information observed at runtime."
      C: "Single prompts always exceed the model's context window."
      D: "Single prompts can't be cached."
    answer: B
    explanation: |
      Cost and caching aren't the issue. Context windows accommodate
      reasonable prompts. The real limit: a single prompt has no way to
      observe the result of an action and react to it. The agent loop closes
      that gap — the model emits an action, the world responds, the model
      conditions its next action on what actually happened.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "The problem this solves"

  - id: q3
    difficulty: medium
    question: "Which of the following is **not** one of the four minimal components of an agent?"
    options:
      A: "A language model."
      B: "A set of tools."
      C: "A reward function."
      D: "A loop with state."
    answer: C
    explanation: |
      The four minimal components are: a language model, a set of tools, a
      loop, and a state (usually the conversation history). A reward function
      is part of *reinforcement learning*. LLM agents do not train on a
      reward during inference — they sample from a fixed policy.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "How it works"

  - id: q4
    difficulty: medium
    question: "A task can be expressed as a fixed sequence of LLM calls and code, with no branching that depends on intermediate LLM output. What should you build?"
    options:
      A: "An agent — it's more flexible."
      B: "A pipeline — agents add unnecessary cost and latency."
      C: "A multi-agent system — each step should have its own agent."
      D: "A single very long prompt that does everything."
    answer: B
    explanation: |
      If the control flow is fixed and doesn't depend on the LLM's output to
      decide what runs next, you have a pipeline, not an agent. Pipelines are
      cheaper, more deterministic, easier to test, and easier to reason about.
      Agents are the right answer only when the model's output materially
      determines what executes next.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "When to use it (and when not to)"

  - id: q5
    difficulty: medium
    question: "An agent keeps calling the same web-search tool with slight rewordings, never making progress. Which failure mode is this?"
    options:
      A: "Hallucinated tool calls."
      B: "Looping without progress."
      C: "Lost in the observations."
      D: "Silent failures."
    answer: B
    explanation: |
      The signature here is *repeated, near-identical actions that don't
      change the state of the world*. Hallucinated tool calls would name
      tools that don't exist. "Lost in the observations" describes context
      bloat. Silent failures are about errors being treated as data. The fix
      is step limits, repeated-action detection, and prompting the model to
      summarize and decide whether to give up.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "Common failure modes"

  - id: q6
    difficulty: medium
    question: "Why is the agent loop more useful than a bigger model for tasks like 'browse the web and summarize'?"
    options:
      A: "Bigger models cost too much for everyone."
      B: "The loop provides grounding — the model can see real tool results and react."
      C: "Bigger models are slower at producing tokens."
      D: "The loop reduces the number of tokens needed per response."
    answer: B
    explanation: |
      A larger one-shot model can produce more fluent text but has no access
      to current information from the web — it can only describe what it
      remembers. The loop lets a smaller model call a search tool, see real
      results, and ground its summary in evidence. Grounding, recovery, and
      budgeting are the three things the loop provides that one-shot
      generation can't.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "Why the loop matters"

  - id: q7
    difficulty: hard
    question: "An agent receives a 50KB JSON response from a tool. By step 4, the context is bloated and the agent is confused. Which of the following is **not** an appropriate fix?"
    options:
      A: "Insert a summarization step between the raw tool result and what's appended to state."
      B: "Have the tool return a handle/page token that the agent can selectively dereference."
      C: "Switch to a bigger model with a larger context window."
      D: "Compress the tool's return contract so it only includes fields the model needs."
    answer: C
    explanation: |
      A, B, and D are all real fixes that address the root cause: noise in
      observation context. Throwing a bigger context window at the problem
      kicks the can — bloat still degrades selection quality regardless of
      window size, and the cost grows linearly. *Compression of returns* is
      a tool-design responsibility, not a model-size problem.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "Common failure modes"

  - id: q8
    difficulty: hard
    question: "In the agent-as-policy framing, what mathematical object is the LLM?"
    options:
      A: "A reward function $r(s, a)$."
      B: "A value function $V(s)$."
      C: "A policy $\\pi_\\theta(a_t \\mid s_t)$."
      D: "A transition function $T(s, a, s')$."
    answer: C
    explanation: |
      The LLM is the policy — a function that maps the current state $s_t$
      (the conversation history) to a distribution over next actions $a_t$
      (tool calls or final responses). Reward and value functions belong to
      RL training; transition functions describe how the *world* responds to
      actions (the tools and environment, not the LLM). The policy framing
      gives you vocabulary for debugging without claiming you're doing RL.
    review:
      page: concepts/agents/what-is-an-agent.md
      section: "🧮 Math behind it"
---

# 🧠 Quiz · Agents — basics

> ⏱ ~7 min · 🎯 Pass: 6/8 · 📖 Source: [`concepts/agents/what-is-an-agent.md`](../../concepts/agents/what-is-an-agent.md)

Try each question before expanding its answer. Score yourself at the end.

---

## Question 1 *(easy)*

What is the *defining* property that distinguishes an agent from a one-shot LLM call?

A. The agent uses a larger model with more parameters.  
B. The agent has access to external tools.  
C. The LLM picks the next action in a loop, based on what it observed.  
D. The agent persists memory across user sessions.

<details>
<summary>Show answer</summary>

**Answer: C** — The LLM picks the next action in a loop.

Model size is irrelevant — small models can be agents. Tool access is *necessary* but not *sufficient*: a one-shot prompt with tool access is still one-shot. Cross-session memory is an optional feature, not a definition. The property that turns a generation into an agent is the loop where the LLM decides what to do next based on observations from previous actions.

→ Review: [`what-is-an-agent.md` § "TL;DR"](../../concepts/agents/what-is-an-agent.md#tldr)

</details>

---

## Question 2 *(easy)*

Why doesn't a single, very elaborate prompt solve the problems that agents solve?

A. Single prompts cost more than agent loops.  
B. Single prompts can't condition on external information observed at runtime.  
C. Single prompts always exceed the model's context window.  
D. Single prompts can't be cached.

<details>
<summary>Show answer</summary>

**Answer: B** — Single prompts can't condition on observations.

Cost and caching aren't the issue. Context windows accommodate reasonable prompts. The real limit: a single prompt has no way to observe the result of an action and react to it. The agent loop closes that gap — the model emits an action, the world responds, the model conditions its next action on what actually happened.

→ Review: [`what-is-an-agent.md` § "The problem this solves"](../../concepts/agents/what-is-an-agent.md#the-problem-this-solves)

</details>

---

## Question 3 *(medium)*

Which of the following is **not** one of the four minimal components of an agent?

A. A language model.  
B. A set of tools.  
C. A reward function.  
D. A loop with state.

<details>
<summary>Show answer</summary>

**Answer: C** — A reward function.

The four minimal components are: a language model, a set of tools, a loop, and a state (usually the conversation history). A reward function is part of *reinforcement learning*. LLM agents do not train on a reward during inference — they sample from a fixed policy.

→ Review: [`what-is-an-agent.md` § "How it works"](../../concepts/agents/what-is-an-agent.md#how-it-works)

</details>

---

## Question 4 *(medium)*

A task can be expressed as a fixed sequence of LLM calls and code, with no branching that depends on intermediate LLM output. What should you build?

A. An agent — it's more flexible.  
B. A pipeline — agents add unnecessary cost and latency.  
C. A multi-agent system — each step should have its own agent.  
D. A single very long prompt that does everything.

<details>
<summary>Show answer</summary>

**Answer: B** — A pipeline.

If the control flow is fixed and doesn't depend on the LLM's output to decide what runs next, you have a pipeline, not an agent. Pipelines are cheaper, more deterministic, easier to test, and easier to reason about. Agents are the right answer only when the model's output materially determines what executes next.

→ Review: [`what-is-an-agent.md` § "When to use it (and when not to)"](../../concepts/agents/what-is-an-agent.md#when-to-use-it-and-when-not-to)

</details>

---

## Question 5 *(medium)*

An agent keeps calling the same web-search tool with slight rewordings, never making progress. Which failure mode is this?

A. Hallucinated tool calls.  
B. Looping without progress.  
C. Lost in the observations.  
D. Silent failures.

<details>
<summary>Show answer</summary>

**Answer: B** — Looping without progress.

The signature here is *repeated, near-identical actions that don't change the state of the world*. Hallucinated tool calls would name tools that don't exist. "Lost in the observations" describes context bloat. Silent failures are about errors being treated as data. The fix is step limits, repeated-action detection, and prompting the model to summarize and decide whether to give up.

→ Review: [`what-is-an-agent.md` § "Common failure modes"](../../concepts/agents/what-is-an-agent.md#common-failure-modes)

</details>

---

## Question 6 *(medium)*

Why is the agent loop more useful than a bigger model for tasks like "browse the web and summarize"?

A. Bigger models cost too much for everyone.  
B. The loop provides grounding — the model can see real tool results and react.  
C. Bigger models are slower at producing tokens.  
D. The loop reduces the number of tokens needed per response.

<details>
<summary>Show answer</summary>

**Answer: B** — Grounding from real tool results.

A larger one-shot model can produce more fluent text but has no access to current information from the web — it can only describe what it remembers. The loop lets a smaller model call a search tool, see real results, and ground its summary in evidence. Grounding, recovery, and budgeting are the three things the loop provides that one-shot generation can't.

→ Review: [`what-is-an-agent.md` § "Why the loop matters"](../../concepts/agents/what-is-an-agent.md#why-the-loop-matters)

</details>

---

## Question 7 *(hard)*

An agent receives a 50KB JSON response from a tool. By step 4, the context is bloated and the agent is confused. Which of the following is **not** an appropriate fix?

A. Insert a summarization step between the raw tool result and what's appended to state.  
B. Have the tool return a handle/page token that the agent can selectively dereference.  
C. Switch to a bigger model with a larger context window.  
D. Compress the tool's return contract so it only includes fields the model needs.

<details>
<summary>Show answer</summary>

**Answer: C** — Bigger context window doesn't fix the root cause.

A, B, and D are all real fixes that address the root cause: noise in observation context. Throwing a bigger context window at the problem kicks the can — bloat still degrades selection quality regardless of window size, and the cost grows linearly. *Compression of returns* is a tool-design responsibility, not a model-size problem.

→ Review: [`what-is-an-agent.md` § "Common failure modes"](../../concepts/agents/what-is-an-agent.md#common-failure-modes)

</details>

---

## Question 8 *(hard)*

In the agent-as-policy framing, what mathematical object is the LLM?

A. A reward function $r(s, a)$.  
B. A value function $V(s)$.  
C. A policy $\pi_\theta(a_t \mid s_t)$.  
D. A transition function $T(s, a, s')$.

<details>
<summary>Show answer</summary>

**Answer: C** — A policy $\pi_\theta(a_t \mid s_t)$.

The LLM is the policy — a function that maps the current state $s_t$ (the conversation history) to a distribution over next actions $a_t$ (tool calls or final responses). Reward and value functions belong to RL training; transition functions describe how the *world* responds to actions (the tools and environment, not the LLM). The policy framing gives you vocabulary for debugging without claiming you're doing RL.

→ Review: [`what-is-an-agent.md` § "🧮 Math behind it"](../../concepts/agents/what-is-an-agent.md#-math-behind-it)

</details>

---

## Scoring

Tally your answers:

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the source page sections you missed, then retake. |
| < 4/8 | Slow down. Work through [`what-is-an-agent.md`](../../concepts/agents/what-is-an-agent.md) carefully, then come back. |

When you're at 6+/8, take the next one: 🧠 [The agent loop](./agent-loop.md).
