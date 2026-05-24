---
quiz_id: foundations-langgraph-basics
title: "LangGraph basics"
source:
  - concepts/agents/agents-vs-frameworks.md
  - tools/langgraph/snapshot-v1.0.md
  - labs/05-langgraph-rewrite/
length_minutes: 8
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What does using LangGraph instead of a from-scratch loop change about the *model* picking actions?"
    options:
      A: "The model picks better tools because LangGraph re-ranks them."
      B: "The model gets fine-tuned on your tool descriptions automatically."
      C: "Nothing. The framework changes the runtime around the agent, not the agent."
      D: "The model becomes deterministic."
    answer: C
    explanation: |
      Frameworks are runtimes, not intelligence. LangGraph changes how state is
      managed, how control flows, how persistence works, and how interrupts are
      handled. None of that changes the LLM, its tool selection quality, its
      sampling, or its understanding. If your agent picks the wrong tool with a
      hand-rolled loop, it will pick the wrong tool in LangGraph too — that's a
      tool-design problem, not a runtime problem.
    review:
      page: concepts/agents/agents-vs-frameworks.md
      section: "What the framework *doesn't* fix"

  - id: q2
    difficulty: easy
    question: "In a LangGraph node, what's the *right* way to add a new message to the state?"
    options:
      A: "`state.messages.append(new_message)` — mutate it directly."
      B: "`return {\"messages\": [new_message]}` — let the reducer merge it."
      C: "Call `state.update(new_message)` and return the new state."
      D: "Save it to a database and reload."
    answer: B
    explanation: |
      LangGraph state mutations are *declarative*. A node returns a dict of
      changes; reducers (like `add_messages`) merge them into the existing state.
      This is what makes parallel branches and replay correct by construction —
      if two nodes ran in parallel and both returned message lists, the reducer
      merges them deterministically. Directly mutating `state.messages.append`
      bypasses the reducer and breaks parallelism and replay.
    review:
      page: labs/05-langgraph-rewrite/README.md
      section: "Steps"

  - id: q3
    difficulty: medium
    question: "Which of the following is **required** for `interrupt()` and `Command(resume=...)` to work?"
    options:
      A: "Two API keys — one for OpenAI and one for LangSmith."
      B: "A checkpointer attached to the compiled graph."
      C: "The `interrupt` middleware enabled in `pyproject.toml`."
      D: "A web server running on port 8000 to receive the resume."
    answer: B
    explanation: |
      Interrupts only work with a checkpointer. The pause is persisted by saving
      the graph state at the interrupt point; the resume replays from that
      saved state. Without persistence there's no way to bridge the gap between
      "graph paused" and "graph continuing later" — especially when the resume
      happens in a different process or hours later. The error message from
      LangGraph when you forget the checkpointer is clear; the snapshot page
      lists this as the most common gotcha.
    review:
      page: tools/langgraph/snapshot-v1.0.md
      section: "What you can rely on (stable APIs)"

  - id: q4
    difficulty: medium
    question: "In LangGraph 1.0+, what is `langchain.agents.create_agent` doing under the hood?"
    options:
      A: "Calling a different, smaller LLM that handles tool selection."
      B: "Building a `StateGraph` with the standard model ↔ tools loop and compiling it."
      C: "Pre-training a small adapter on your tools."
      D: "Replacing your tools with prebuilt LangChain alternatives."
    answer: B
    explanation: |
      `create_agent` is a thin convenience wrapper around `StateGraph` — it
      builds the same graph you'd build by hand (model node + ToolNode + the
      conditional tools_condition edge) and compiles it. The point is to skip
      the boilerplate when you don't need custom routing. You can call
      `.get_graph()` on the result and see the same nodes-and-edges as an
      explicit construction.
    review:
      page: labs/05-langgraph-rewrite/README.md
      section: "Steps"

  - id: q5
    difficulty: medium
    question: "Two `agent.invoke(...)` calls with the same `thread_id` but different inputs. What happens?"
    options:
      A: "The second call is rejected as a duplicate."
      B: "The two calls run in parallel and merge results."
      C: "The second call continues the conversation — it sees the messages from the first call in its state."
      D: "The second call always overwrites the first call's state."
    answer: C
    explanation: |
      `thread_id` identifies a conversation/run. When the checkpointer sees an
      invocation with an existing `thread_id`, it loads that thread's most
      recent state and continues from there. This is how multi-turn
      conversations work in LangGraph: the second call sees the first call's
      messages already in `state["messages"]`. Different `thread_id`s are
      independent runs.
    review:
      page: labs/05-langgraph-rewrite/README.md
      section: "Steps"

  - id: q6
    difficulty: medium
    question: "Which of these is **not** a real advantage of LangGraph over a from-scratch loop?"
    options:
      A: "Replay-safe state via reducers."
      B: "Built-in checkpointing for durable execution."
      C: "Better LLM responses because the framework optimizes prompts."
      D: "First-class `interrupt()` primitive for human-in-the-loop."
    answer: C
    explanation: |
      A, B, and D are real LangGraph wins. C isn't — the framework doesn't
      touch your prompt or change how the LLM responds. The "framework makes
      the model better" claim is exactly the marketing trap the
      framework-vs-from-scratch concept page warns about. Frameworks help you
      build the *runtime around* the model, not the model itself.
    review:
      page: concepts/agents/agents-vs-frameworks.md
      section: "What the framework *doesn't* fix"

  - id: q7
    difficulty: hard
    question: "You're building an agent for a one-off CLI tool — a single user turn that returns an answer. No persistence, no human approval, three simple tools. What's the most honest recommendation?"
    options:
      A: "Use LangGraph — always reach for the framework for new projects."
      B: "Use a from-scratch loop or `create_agent`. LangGraph's main wins (persistence, interrupts) don't apply here."
      C: "Use LangGraph because you'll need it eventually."
      D: "Use a multi-agent system for reliability."
    answer: B
    explanation: |
      The honest answer is that LangGraph's biggest wins (checkpointing,
      interrupts, durable execution) don't apply to a stateless single-turn CLI
      tool. For three tools and no special control flow, a from-scratch loop or
      a one-liner `create_agent` call is the right size. "Always use the
      framework" is the kind of advice that produces over-engineered systems.
      Reach for the framework when a specific capability it provides solves a
      specific problem you have.
    review:
      page: concepts/agents/agents-vs-frameworks.md
      section: "The decision in one table"

  - id: q8
    difficulty: hard
    question: "You're migrating a 2024-era codebase that uses `langgraph.prebuilt.create_react_agent`. What does the 2026 LangGraph documentation recommend?"
    options:
      A: "Stay on `create_react_agent` — it's the recommended high-level helper."
      B: "Use `langchain.agents.create_agent` — `create_react_agent` is deprecated in LangGraph 1.0+."
      C: "Switch to `AgentExecutor`, the modern replacement."
      D: "Manually wire `StateGraph` — there's no high-level helper anymore."
    answer: B
    explanation: |
      Per the LangGraph v1 migration guide, `create_react_agent` is deprecated
      in favor of `create_agent` from `langchain.agents`. `create_agent` runs
      on the same LangGraph runtime and adds middleware support, a cleaner
      state contract, and provider-agnostic tool wiring. `AgentExecutor` is the
      *older* deprecated thing from the pre-LangGraph era (moved to
      `langchain-legacy` in 1.0), not a replacement. Raw `StateGraph` is still
      available but isn't the recommended path for the common case.
    review:
      page: tools/langgraph/snapshot-v1.0.md
      section: "What changed in 1.0 (and what got deprecated)"
---

# 🧠 Quiz · LangGraph basics

> ⏱ ~8 min · 🎯 Pass: 6/8 · 📖 Sources:
>
> - [`concepts/agents/agents-vs-frameworks.md`](../../concepts/agents/agents-vs-frameworks.md)
> - [`tools/langgraph/snapshot-v1.0.md`](../../tools/langgraph/snapshot-v1.0.md)
> - [`labs/05-langgraph-rewrite/`](../../labs/05-langgraph-rewrite/)

The questions test *what LangGraph actually adds*, not its syntax. If you can't yet recite the import paths from memory, that's fine. If you don't understand what reducers buy you, go back and re-do Lab 05.

---

## Question 1 *(easy)*

What does using LangGraph instead of a from-scratch loop change about the *model* picking actions?

A. The model picks better tools because LangGraph re-ranks them.  
B. The model gets fine-tuned on your tool descriptions automatically.  
C. Nothing. The framework changes the runtime around the agent, not the agent.  
D. The model becomes deterministic.

<details>
<summary>Show answer</summary>

**Answer: C** — Frameworks are runtimes, not intelligence.

LangGraph changes how state is managed, how control flows, how persistence works, and how interrupts are handled. None of that changes the LLM, its tool selection quality, its sampling, or its understanding. If your agent picks the wrong tool with a hand-rolled loop, it will pick the wrong tool in LangGraph too — that's a tool-design problem, not a runtime problem.

→ Review: [`agents-vs-frameworks.md` § "What the framework doesn't fix"](../../concepts/agents/agents-vs-frameworks.md#what-the-framework-doesnt-fix)

</details>

---

## Question 2 *(easy)*

In a LangGraph node, what's the *right* way to add a new message to the state?

A. `state.messages.append(new_message)` — mutate it directly.  
B. `return {"messages": [new_message]}` — let the reducer merge it.  
C. Call `state.update(new_message)` and return the new state.  
D. Save it to a database and reload.

<details>
<summary>Show answer</summary>

**Answer: B** — Return a dict; the reducer merges.

LangGraph state mutations are *declarative*. A node returns a dict of changes; reducers (like `add_messages`) merge them into the existing state. This is what makes parallel branches and replay correct by construction — if two nodes ran in parallel and both returned message lists, the reducer merges them deterministically. Directly mutating `state.messages.append` bypasses the reducer and breaks parallelism and replay.

→ Review: [`lab 05 README` § "Steps"](../../labs/05-langgraph-rewrite/README.md#steps)

</details>

---

## Question 3 *(medium)*

Which of the following is **required** for `interrupt()` and `Command(resume=...)` to work?

A. Two API keys — one for OpenAI and one for LangSmith.  
B. A checkpointer attached to the compiled graph.  
C. The `interrupt` middleware enabled in `pyproject.toml`.  
D. A web server running on port 8000 to receive the resume.

<details>
<summary>Show answer</summary>

**Answer: B** — A checkpointer is required.

Interrupts only work with a checkpointer. The pause is persisted by saving the graph state at the interrupt point; the resume replays from that saved state. Without persistence there's no way to bridge the gap between "graph paused" and "graph continuing later" — especially when the resume happens in a different process or hours later. The error message from LangGraph when you forget the checkpointer is clear; the snapshot page lists this as the most common gotcha.

→ Review: [`snapshot-v1.0.md` § "What you can rely on (stable APIs)"](../../tools/langgraph/snapshot-v1.0.md#what-you-can-rely-on-stable-apis)

</details>

---

## Question 4 *(medium)*

In LangGraph 1.0+, what is `langchain.agents.create_agent` doing under the hood?

A. Calling a different, smaller LLM that handles tool selection.  
B. Building a `StateGraph` with the standard model ↔ tools loop and compiling it.  
C. Pre-training a small adapter on your tools.  
D. Replacing your tools with prebuilt LangChain alternatives.

<details>
<summary>Show answer</summary>

**Answer: B** — A `StateGraph` is built and compiled for you.

`create_agent` is a thin convenience wrapper around `StateGraph` — it builds the same graph you'd build by hand (model node + ToolNode + the conditional `tools_condition` edge) and compiles it. The point is to skip the boilerplate when you don't need custom routing. You can call `.get_graph()` on the result and see the same nodes-and-edges as an explicit construction.

→ Review: [`lab 05 README` § "Steps"](../../labs/05-langgraph-rewrite/README.md#steps)

</details>

---

## Question 5 *(medium)*

Two `agent.invoke(...)` calls with the same `thread_id` but different inputs. What happens?

A. The second call is rejected as a duplicate.  
B. The two calls run in parallel and merge results.  
C. The second call continues the conversation — it sees the messages from the first call in its state.  
D. The second call always overwrites the first call's state.

<details>
<summary>Show answer</summary>

**Answer: C** — Same `thread_id` continues the same conversation.

`thread_id` identifies a conversation/run. When the checkpointer sees an invocation with an existing `thread_id`, it loads that thread's most recent state and continues from there. This is how multi-turn conversations work in LangGraph: the second call sees the first call's messages already in `state["messages"]`. Different `thread_id`s are independent runs.

→ Review: [`lab 05 README` § "Steps"](../../labs/05-langgraph-rewrite/README.md#steps)

</details>

---

## Question 6 *(medium)*

Which of these is **not** a real advantage of LangGraph over a from-scratch loop?

A. Replay-safe state via reducers.  
B. Built-in checkpointing for durable execution.  
C. Better LLM responses because the framework optimizes prompts.  
D. First-class `interrupt()` primitive for human-in-the-loop.

<details>
<summary>Show answer</summary>

**Answer: C** — Frameworks don't change the model.

A, B, and D are real LangGraph wins. C isn't — the framework doesn't touch your prompt or change how the LLM responds. The "framework makes the model better" claim is exactly the marketing trap the framework-vs-from-scratch concept page warns about. Frameworks help you build the *runtime around* the model, not the model itself.

→ Review: [`agents-vs-frameworks.md` § "What the framework doesn't fix"](../../concepts/agents/agents-vs-frameworks.md#what-the-framework-doesnt-fix)

</details>

---

## Question 7 *(hard)*

You're building an agent for a one-off CLI tool — a single user turn that returns an answer. No persistence, no human approval, three simple tools. What's the most honest recommendation?

A. Use LangGraph — always reach for the framework for new projects.  
B. Use a from-scratch loop or `create_agent`. LangGraph's main wins (persistence, interrupts) don't apply here.  
C. Use LangGraph because you'll need it eventually.  
D. Use a multi-agent system for reliability.

<details>
<summary>Show answer</summary>

**Answer: B** — From-scratch is the right size for the problem.

The honest answer is that LangGraph's biggest wins (checkpointing, interrupts, durable execution) don't apply to a stateless single-turn CLI tool. For three tools and no special control flow, a from-scratch loop or a one-liner `create_agent` call is the right size. "Always use the framework" is the kind of advice that produces over-engineered systems. Reach for the framework when a specific capability it provides solves a specific problem you have.

→ Review: [`agents-vs-frameworks.md` § "The decision in one table"](../../concepts/agents/agents-vs-frameworks.md#the-decision-in-one-table)

</details>

---

## Question 8 *(hard)*

You're migrating a 2024-era codebase that uses `langgraph.prebuilt.create_react_agent`. What does the 2026 LangGraph documentation recommend?

A. Stay on `create_react_agent` — it's the recommended high-level helper.  
B. Use `langchain.agents.create_agent` — `create_react_agent` is deprecated in LangGraph 1.0+.  
C. Switch to `AgentExecutor`, the modern replacement.  
D. Manually wire `StateGraph` — there's no high-level helper anymore.

<details>
<summary>Show answer</summary>

**Answer: B** — Migrate to `langchain.agents.create_agent`.

Per the LangGraph v1 migration guide, `create_react_agent` is deprecated in favor of `create_agent` from `langchain.agents`. `create_agent` runs on the same LangGraph runtime and adds middleware support, a cleaner state contract, and provider-agnostic tool wiring. `AgentExecutor` is the *older* deprecated thing from the pre-LangGraph era (moved to `langchain-legacy` in 1.0), not a replacement. Raw `StateGraph` is still available but isn't the recommended path for the common case.

→ Review: [`snapshot-v1.0.md` § "What changed in 1.0"](../../tools/langgraph/snapshot-v1.0.md#what-changed-in-10-and-what-got-deprecated)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the framework-comparison page, then retake. |
| < 4/8 | Re-do Lab 05 with the concept page open, then retake. The questions map directly to specific sections. |

You've now finished the **Foundations** path. Continue on to Path 02 (Agentic RAG), Path 03 (Multi-Agent Systems), or wherever your next project takes you.
