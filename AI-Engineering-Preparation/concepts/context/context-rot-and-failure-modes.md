# Context rot and failure modes

> Concept note. ~8 min. Builds on [context engineering](./context-engineering.md); revisits [the context window](../llm/context-window.md).

The reason context engineering exists is that long contexts fail in measurable ways. Understanding *how* they fail is what justifies the effort of keeping a window small and clean rather than just making it bigger.

## Context rot

A natural assumption is that a model treats its 100,000th token as reliably as its 100th. It does not. **Context rot** is the measured degradation in output quality as input length grows — and it shows up even when the window is nowhere near full, and even on simple tasks. Controlled evaluation across many frontier models found that performance becomes less reliable as inputs lengthen, for every model tested. The practical lesson is blunt: "the window is big enough" is not the same as "the model will use it well." More tokens in can mean worse output out.

## The mechanisms

Three compounding effects drive context rot:

- **Lost in the middle.** Models attend best to the start and end of the context and worst to the material in between, so a fact buried in the middle of a long context is often missed even though it is present. Accuracy can drop sharply for mid-context information.
- **Attention dilution.** [Attention](../llm/attention.md) compares every token with every other, so the relationships to track grow with the square of the length. As the window fills, the signal for any one relevant token is spread thinner.
- **Distractor interference.** Content that is semantically similar to the query but irrelevant does not just take up space — it actively misleads, pulling the model toward plausible-but-wrong material.

## What this means for design

These failure modes turn "add more context" from a safe default into a risk. The responses are exactly the [strategies](./context-strategies.md) of the previous note: retrieve only what the step needs so distractors never enter; compact and summarize so the window stays short; place the most important material where attention is strongest (near the start or end), not buried in the middle; and isolate subtasks so their clutter does not dilute the main thread. The unifying aim is to keep the signal-to-noise ratio high, because the model's effective use of context — not the window's advertised size — is what bounds performance.

## What to remember

- Context rot is the measured drop in quality as input grows, present even below the window limit and on simple tasks.
- It is driven by lost-in-the-middle positioning, attention dilution, and distractor interference.
- The fix is selection and compression, and placing key material where the model attends best — not a bigger window.

## References

- Hong, K., Troynikov, A., Huber, J. (2025). *Context Rot: How Increasing Input Tokens Impacts LLM Performance.* Chroma technical report.
- Liu, N. F., et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts.* arXiv:2307.03172. See [`../../references/references.md`](../../references/references.md).
