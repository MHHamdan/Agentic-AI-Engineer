# The context window

> Concept note. ~8 min. Builds on [attention](./attention.md). Companion area: [context engineering](../context/).

The **context window** is the maximum number of tokens a model can attend to in a single request. Everything the model "knows" in the moment lives inside it; anything outside it does not exist for that call. Treating the window as a budget — a working set you fill deliberately — is one of the highest-impact skills in building LLM systems, and the reason [context engineering](../context/) is its own discipline.

## What competes for the budget

Every request's window is the sum of several claimants, not just the user's question:

- system and developer instructions,
- the conversation so far,
- retrieved context (documents, search results, memory),
- tool and function schemas,
- tool outputs and API responses,
- the user's current message.

Tool definitions and raw tool outputs are easy to underestimate — a handful of verbose tool schemas can consume more of the window than the model's actual reasoning. A useful mental model, for visibility rather than precision:

```text
window = instructions + history + retrieved context + tool schemas + tool outputs + user input
```

When the total exceeds the limit, something has to give. Naive strategies drop the oldest messages first, which often deletes the original goal and constraints — the very things you most wanted to keep.

## Bigger windows are not a free fix

Context windows have grown to hundreds of thousands and even millions of tokens, which tempts a brute-force approach: put everything in. Three problems push back. It is expensive — you pay per token on every call. It still has a ceiling — no window holds an entire enterprise corpus. And, least obvious, models use long contexts **unevenly**: accuracy is highest when the relevant fact is near the start or end of the window and drops when it is buried in the middle. Adding more context does not guarantee the model will use it, and can bury the part that matters.

The practical response is selectivity: retrieve only what the current step needs, summarize completed work, keep durable knowledge in external [memory](../memory/) rather than the prompt, and place the most important material where the model attends best. Those techniques are the subject of the [context engineering](../context/) and [memory](../memory/) areas; the point here is the constraint they exist to manage.

## What to remember

- The window is a hard, finite budget shared by instructions, history, retrieved context, tool schemas, tool outputs, and the user message.
- A larger window is not a substitute for selectivity: it costs more, still has a ceiling, and is used unevenly.
- Put the important material where attention is strongest, and keep the rest out of the prompt.

## References

- Liu, N. F., et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts.* arXiv:2307.03172. See [`../../references/references.md`](../../references/references.md).
