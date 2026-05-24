# The Agent Loop: A Brief Introduction

The agent loop is the core control flow of a tool-using AI system. It consists of four phases that repeat until a stopping condition is met: perceive, reason, act, and observe.

## The four phases

In the **perceive** phase, the agent receives input from its environment. This is the user's question, the previous turn's output, or the result of a recent tool call. Perception in modern agents is straightforward — the model reads its context window, which contains the conversation history and any system instructions.

In the **reason** phase, the language model decides what to do next. It produces either a final answer (terminating the loop) or a tool call (continuing it). This decision happens in a single model call. The reasoning isn't visible by default; the popular ReAct pattern makes it visible by asking the model to emit explicit thought traces before its action.

In the **act** phase, the agent executes the chosen tool. This is a deterministic step controlled by your code, not the model. The tool returns a structured result — success with data, or an error with a typed failure reason.

In the **observe** phase, the tool's result gets appended to the conversation history and fed back into the next perceive step. The loop continues from there.

## Stopping conditions

Every loop needs an exit. Three exit conditions are common in practice:

1. The model emits a final answer with no tool call. This is the happy path.
2. A step cap is reached. Most agents cap at 5-15 steps to prevent infinite loops.
3. A repeated-action detector fires. If the agent calls the same tool with the same arguments twice in a row, something has gone wrong; the safer behavior is to refuse the duplicate and surface a signal that the agent should try something different.

The third condition matters more than people expect. Research agents in particular tend to retry failed queries with the same wording, expecting different results — a classic infinite-loop bug.

## State and history

The agent's memory across the loop is its conversation history: a list of messages with roles (system, user, assistant, tool). Each tool call appends a new message; each model reply appends another. The list grows on every iteration.

For short conversations this works without modification. For longer ones, the list eventually exceeds the model's context window. Production agents handle this with summarization, with state reducers, or by maintaining structured state alongside the message list. The trade-offs are covered in the framework concept page.

## Why the loop is the agent

Without the loop, you have a language model that calls one tool and produces one answer. With the loop, the model can plan, retry, refine, and synthesize across multiple actions. The loop is what makes an agent an agent.
