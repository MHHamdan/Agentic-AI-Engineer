# Short-term, long-term, and external memory

> Concept note. ~8 min. Builds on [state vs. memory](./state-vs-memory.md).

Once you accept that an agent needs [memory](./state-vs-memory.md), the next question is where it lives. Production systems use three tiers, distinguished by how long information lasts and whether it sits inside the context window or outside it.

## The three tiers

- **Short-term (working) memory** is the conversation so far — the messages, the tool calls, and the tool results in the current context window. It is immediate and high-resolution, but it is bounded by the window and vanishes when the session ends. This is where the agent's moment-to-moment reasoning happens.
- **Long-term memory** is what persists across sessions: user preferences, project conventions, durable facts, and summaries of past conversations. It outlives any single context window and is what makes an assistant feel like it knows you on the next visit.
- **External memory** is the larger body of reference knowledge the agent can retrieve from but does not hold in context — documents, a knowledge base, a [vector index](../vector-db/). It is effectively unbounded and is reached through [retrieval](../rag/), not kept in the prompt.

## The operating-system analogy

A productive way to think about this is by analogy to a computer's memory hierarchy: the context window is like RAM — fast, in use right now, and small — while long-term and external memory are like disk — large, persistent, and reached on demand. An agent cannot hold everything in "RAM," so it pages information in when needed and writes results back out. The design problem is the same one an operating system solves: decide what belongs in the small fast tier at each moment, and move the rest to the large slow tier. This framing is why some memory systems describe themselves in operating-system terms.

## What goes where

The tiers are not interchangeable. Active task reasoning belongs in short-term memory, where the model can attend to it directly. A user's standing preferences belong in long-term memory, retrieved into context only when relevant. A million documents belong in external memory, with only the few relevant passages pulled in per query. Putting reference knowledge in short-term memory wastes the window and invites [context rot](../context/context-rot-and-failure-modes.md); trying to keep task state in external memory makes the agent slow and forgetful within a single task.

## What to remember

- Short-term memory is the in-context conversation; long-term memory persists across sessions; external memory is retrieved, not held.
- The context window is RAM and the other tiers are disk: page in what the moment needs, write the rest back out.
- Match the tier to the use — task reasoning in-context, preferences in long-term, reference knowledge external.

## References

- Packer, C., et al. (2023). *MemGPT: Towards LLMs as Operating Systems.* arXiv:2310.08560.
- Chhikara, P., et al. (2025). *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory.* arXiv:2504.19413. See [`../../references/references.md`](../../references/references.md).
