# The ReAct Pattern

ReAct — Reasoning and Acting — is the specific structure modern tool-using agents use to make the language model's decisions auditable. It was introduced by Yao et al. in the 2023 paper of the same name. The pattern is now so embedded in agent frameworks that most people use it without realizing it has a name.

## The structure

In a ReAct agent, every loop iteration interleaves three elements:

A **thought** is a free-form reasoning trace the model emits before deciding what to do. It's natural-language prose explaining the model's current understanding of the problem and what it plans to do next.

An **action** is the tool call the model issues. It's structured — a tool name and arguments — and gets executed by the system.

An **observation** is the structured result returned by the tool. The model reads this in the next iteration's thought.

Each iteration produces one thought, one action, and one observation, in that order. The loop terminates when the model emits a thought without an action — at which point its final answer follows.

## Why the thought matters

Without the thought, the model produces a tool call directly from the conversation history. The reasoning is hidden inside the model's forward pass.

With the thought, the model produces explicit prose first. The prose tends to improve the action that follows: research on chain-of-thought prompting consistently shows that asking the model to think before acting improves the action's quality. The mechanism is not fully understood, but the effect is robust enough to design around.

The thought also makes debugging tractable. When an agent makes a confusing choice, you can read its thought to see what it was reasoning about. Without the thought, you have a tool call and no insight into why.

## ReAct in modern function-calling APIs

The OpenAI and Anthropic function-calling APIs encode ReAct implicitly. The assistant message contains both a `content` field (free-form text — the thought) and a `tool_calls` field (the action). The model emits both in one call.

You don't always see this because the content is sometimes empty when the model decides to act without reasoning out loud. But the structure is there: thought (possibly empty), action (possibly empty), observation (from the previous tool result). One iteration per assistant message.

## Variants

Several variants extend ReAct. **Reflexion** adds a self-critique step where the model reviews its own trajectory and proposes corrections. **Plan-and-Execute** separates a planning phase from execution, where the model first emits a multi-step plan and then executes each step. **Tree-of-Thought** considers multiple alternative reasoning paths in parallel.

In practice, plain ReAct covers the majority of agent use cases. The variants are worth knowing about, but reaching for them prematurely is a common pattern that doesn't usually improve agent quality.

## What ReAct doesn't do

ReAct is a prompting and structuring pattern. It doesn't change what the model can do — it just makes the model's decisions more legible and slightly more careful. ReAct doesn't fix bad tools, doesn't fix missing context, doesn't fix model size limitations, and doesn't fix poorly-defined tasks. The pattern works best when those other things are already adequate.
