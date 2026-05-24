---
quiz_id: foundations-agent-loop
title: "The agent loop"
source:
  - concepts/agents/agent-loop.md
length_minutes: 8
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What are the four steps of the agent loop, in order?"
    options:
      A: "Plan → execute → log → respond."
      B: "Perceive → reason → act → observe."
      C: "Tokenize → embed → search → generate."
      D: "Receive → validate → process → return."
    answer: B
    explanation: |
      The agent loop is *perceive* (read the state), *reason* (LLM decides
      next move), *act* (execute the move), *observe* (collect the result),
      then back to perceive. Some sources list "plan" or "think" instead of
      "reason"; the underlying cycle is the same. The four-step model is the
      vocabulary the rest of the curriculum uses.
    review:
      page: concepts/agents/agent-loop.md
      section: "The four steps"

  - id: q2
    difficulty: easy
    question: "What is the **state** in a typical LLM agent?"
    options:
      A: "A fixed-size vector of features extracted from the user request."
      B: "The list of messages — system prompt, user request, tool calls, tool results."
      C: "The model's hidden activations from the last forward pass."
      D: "A graph of tools the agent has access to."
    answer: B
    explanation: |
      In LLM agents, the state is the running conversation: the system
      prompt, the user request, every assistant turn, and every tool result.
      Other definitions (feature vectors, activations) are from RL/ML
      generally — they don't apply here. The state grows monotonically with
      each step, which is why context-window budgeting becomes a first-class
      concern.
    review:
      page: concepts/agents/agent-loop.md
      section: "1. Perceive"

  - id: q3
    difficulty: medium
    question: "Which of the following is the **most common** bug in homegrown agent loops?"
    options:
      A: "The tool calls fail intermittently due to API rate limits."
      B: "The model emits malformed JSON for tool arguments."
      C: "The loop has no step cap, so a buggy agent burns through tokens."
      D: "The state is too small to fit the conversation."
    answer: C
    explanation: |
      All four can happen, but the single most common bug in homemade agent
      code is forgetting the step cap. Without it, a buggy loop runs until
      it hits the token budget — expensive and slow to notice. Robust loops
      always have *multiple* termination conditions: final answer detected,
      step cap, repeated-action detection, and budget cap.
    review:
      page: concepts/agents/agent-loop.md
      section: "What stops the loop?"

  - id: q4
    difficulty: medium
    question: "Why is it important to distinguish errors from data in tool observations?"
    options:
      A: "Errors should never reach the model — they should crash the agent."
      B: "Logging frameworks treat them differently."
      C: "The model can only react correctly if 'not found', 'error', and 'empty result' look distinct."
      D: "Errors are larger and cost more tokens than data."
    answer: C
    explanation: |
      The model treats observations as the only signal from reality. If a
      404, a timeout, and a successful empty result all return `"None"`,
      the model has no way to choose a different next action. Distinguishing
      them in the observation lets the model recover gracefully — retry on
      one, broaden the query on another, give up on the third.
    review:
      page: concepts/agents/agent-loop.md
      section: "4. Observe"

  - id: q5
    difficulty: medium
    question: "What does it mean to say the agent operates in *partial observability*?"
    options:
      A: "The agent sometimes can't see the user's input."
      B: "The world contains more state than the agent's context, and the agent acts on what it has observed so far."
      C: "Some tool results are encrypted."
      D: "The model's weights change between calls."
    answer: B
    explanation: |
      Partial observability is the POMDP framing: the world has more state
      than the agent's context window. The agent's "belief" about the world
      is its conversation history (and the LLM's implicit inference over
      it). It's not a bug — it's the normal condition for any LLM agent.
      The full treatment lives in `math-foundations/04-agents-as-policies.md`.
    review:
      page: concepts/agents/agent-loop.md
      section: "State, observation, action: the vocabulary"

  - id: q6
    difficulty: medium
    question: "An agent calls three independent lookup tools in one response (parallel tool calls). How does the loop change?"
    options:
      A: "The four-step model breaks down completely — a new model is needed."
      B: "Same shape: one reason step, one act step (now wider), one observe step. Just executed in parallel."
      C: "Each tool call gets its own loop iteration, sequentially."
      D: "Parallel calls aren't possible in modern LLM APIs."
    answer: B
    explanation: |
      The loop is the same shape. The "act" step just runs $k$ tool calls
      concurrently instead of one; "observe" joins the $k$ results into the
      state; "perceive" then sees them all before the next "reason." Modern
      APIs (OpenAI, Anthropic, Gemini) all support this. The mental model
      doesn't change; the implementation handles the parallelism with
      something like `asyncio.gather`.
    review:
      page: concepts/agents/agent-loop.md
      section: "When this mental model breaks"

  - id: q7
    difficulty: hard
    question: "Which of these is **not** a reason to use a framework like LangGraph instead of a hand-rolled loop?"
    options:
      A: "Durable execution — pausing and resuming runs across crashes."
      B: "Cleaner expression of complex control flow with conditional edges."
      C: "Built-in checkpoint and human-in-the-loop support."
      D: "The framework makes the model itself smarter."
    answer: D
    explanation: |
      Frameworks don't change the model — they don't fine-tune it, they
      don't change how it generates. They reduce boilerplate for state
      management, persistence, branching, and checkpointing. Those wins are
      real and matter at scale. But the model is the same model whether you
      use LangGraph or a `for` loop.
    review:
      page: concepts/agents/agent-loop.md
      section: "1. Perceive"

  - id: q8
    difficulty: hard
    question: "An agent's state has grown so large that observations are getting buried and the model can't see the most recent tool result. Which is the **best** first intervention?"
    options:
      A: "Switch to a model with a larger context window."
      B: "Add summarization between raw tool returns and what gets appended to state."
      C: "Increase `max_steps` to give the agent more chances."
      D: "Restart the agent loop from scratch on each step."
    answer: B
    explanation: |
      The root cause is observation bloat. A bigger window delays the
      problem but doesn't solve it. Increasing `max_steps` makes it worse,
      and restarting throws away progress. The right intervention is to
      compress observations *before* they enter state — either by
      summarizing the tool result, returning a smaller subset of fields,
      or by retrieving only relevant earlier turns. This is the core idea
      of context engineering.
    review:
      page: concepts/agents/agent-loop.md
      section: "1. Perceive"
---

# 🧠 Quiz · The agent loop

> ⏱ ~8 min · 🎯 Pass: 6/8 · 📖 Source: [`concepts/agents/agent-loop.md`](../../concepts/agents/agent-loop.md)

Try each question before expanding its answer. Score yourself at the end.

---

## Question 1 *(easy)*

What are the four steps of the agent loop, in order?

A. Plan → execute → log → respond.  
B. Perceive → reason → act → observe.  
C. Tokenize → embed → search → generate.  
D. Receive → validate → process → return.

<details>
<summary>Show answer</summary>

**Answer: B** — Perceive → reason → act → observe.

The agent loop is *perceive* (read the state), *reason* (LLM decides next move), *act* (execute the move), *observe* (collect the result), then back to perceive. Some sources list "plan" or "think" instead of "reason"; the underlying cycle is the same. The four-step model is the vocabulary the rest of the curriculum uses.

→ Review: [`agent-loop.md` § "The four steps"](../../concepts/agents/agent-loop.md#the-four-steps)

</details>

---

## Question 2 *(easy)*

What is the **state** in a typical LLM agent?

A. A fixed-size vector of features extracted from the user request.  
B. The list of messages — system prompt, user request, tool calls, tool results.  
C. The model's hidden activations from the last forward pass.  
D. A graph of tools the agent has access to.

<details>
<summary>Show answer</summary>

**Answer: B** — The list of messages.

In LLM agents, the state is the running conversation: the system prompt, the user request, every assistant turn, and every tool result. Other definitions (feature vectors, activations) are from RL/ML generally — they don't apply here. The state grows monotonically with each step, which is why context-window budgeting becomes a first-class concern.

→ Review: [`agent-loop.md` § "1. Perceive"](../../concepts/agents/agent-loop.md#1-perceive)

</details>

---

## Question 3 *(medium)*

Which of the following is the **most common** bug in homegrown agent loops?

A. The tool calls fail intermittently due to API rate limits.  
B. The model emits malformed JSON for tool arguments.  
C. The loop has no step cap, so a buggy agent burns through tokens.  
D. The state is too small to fit the conversation.

<details>
<summary>Show answer</summary>

**Answer: C** — No step cap.

All four can happen, but the single most common bug in homemade agent code is forgetting the step cap. Without it, a buggy loop runs until it hits the token budget — expensive and slow to notice. Robust loops always have *multiple* termination conditions: final answer detected, step cap, repeated-action detection, and budget cap.

→ Review: [`agent-loop.md` § "What stops the loop?"](../../concepts/agents/agent-loop.md#what-stops-the-loop)

</details>

---

## Question 4 *(medium)*

Why is it important to distinguish errors from data in tool observations?

A. Errors should never reach the model — they should crash the agent.  
B. Logging frameworks treat them differently.  
C. The model can only react correctly if "not found", "error", and "empty result" look distinct.  
D. Errors are larger and cost more tokens than data.

<details>
<summary>Show answer</summary>

**Answer: C** — The model needs distinct signals to recover.

The model treats observations as the only signal from reality. If a 404, a timeout, and a successful empty result all return `"None"`, the model has no way to choose a different next action. Distinguishing them in the observation lets the model recover gracefully — retry on one, broaden the query on another, give up on the third.

→ Review: [`agent-loop.md` § "4. Observe"](../../concepts/agents/agent-loop.md#4-observe)

</details>

---

## Question 5 *(medium)*

What does it mean to say the agent operates in *partial observability*?

A. The agent sometimes can't see the user's input.  
B. The world contains more state than the agent's context, and the agent acts on what it has observed so far.  
C. Some tool results are encrypted.  
D. The model's weights change between calls.

<details>
<summary>Show answer</summary>

**Answer: B** — More world than context.

Partial observability is the POMDP framing: the world has more state than the agent's context window. The agent's "belief" about the world is its conversation history (and the LLM's implicit inference over it). It's not a bug — it's the normal condition for any LLM agent. The full treatment lives in [`math-foundations/04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md).

→ Review: [`agent-loop.md` § "State, observation, action: the vocabulary"](../../concepts/agents/agent-loop.md#state-observation-action-the-vocabulary)

</details>

---

## Question 6 *(medium)*

An agent calls three independent lookup tools in one response (parallel tool calls). How does the loop change?

A. The four-step model breaks down completely — a new model is needed.  
B. Same shape: one reason step, one act step (now wider), one observe step. Just executed in parallel.  
C. Each tool call gets its own loop iteration, sequentially.  
D. Parallel calls aren't possible in modern LLM APIs.

<details>
<summary>Show answer</summary>

**Answer: B** — Same shape, wider.

The loop is the same shape. The "act" step just runs $k$ tool calls concurrently instead of one; "observe" joins the $k$ results into the state; "perceive" then sees them all before the next "reason." Modern APIs (OpenAI, Anthropic, Gemini) all support this. The mental model doesn't change; the implementation handles the parallelism with something like `asyncio.gather`.

→ Review: [`agent-loop.md` § "When this mental model breaks"](../../concepts/agents/agent-loop.md#when-this-mental-model-breaks)

</details>

---

## Question 7 *(hard)*

Which of these is **not** a reason to use a framework like LangGraph instead of a hand-rolled loop?

A. Durable execution — pausing and resuming runs across crashes.  
B. Cleaner expression of complex control flow with conditional edges.  
C. Built-in checkpoint and human-in-the-loop support.  
D. The framework makes the model itself smarter.

<details>
<summary>Show answer</summary>

**Answer: D** — Frameworks don't change the model.

Frameworks don't change the model — they don't fine-tune it, they don't change how it generates. They reduce boilerplate for state management, persistence, branching, and checkpointing. Those wins are real and matter at scale. But the model is the same model whether you use LangGraph or a `for` loop.

→ Review: [`agent-loop.md` § "1. Perceive"](../../concepts/agents/agent-loop.md#1-perceive)

</details>

---

## Question 8 *(hard)*

An agent's state has grown so large that observations are getting buried and the model can't see the most recent tool result. Which is the **best** first intervention?

A. Switch to a model with a larger context window.  
B. Add summarization between raw tool returns and what gets appended to state.  
C. Increase `max_steps` to give the agent more chances.  
D. Restart the agent loop from scratch on each step.

<details>
<summary>Show answer</summary>

**Answer: B** — Compress at the source.

The root cause is observation bloat. A bigger window delays the problem but doesn't solve it. Increasing `max_steps` makes it worse, and restarting throws away progress. The right intervention is to compress observations *before* they enter state — either by summarizing the tool result, returning a smaller subset of fields, or by retrieving only relevant earlier turns. This is the core idea of context engineering.

→ Review: [`agent-loop.md` § "1. Perceive"](../../concepts/agents/agent-loop.md#1-perceive)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the sections you missed, then retake. |
| < 4/8 | Work through [`agent-loop.md`](../../concepts/agents/agent-loop.md) carefully, then come back. |

Next: 🧠 [The ReAct pattern](./react-pattern.md).
