# The memory lifecycle

> Concept note. ~8 min. Builds on [memory types](./memory-types.md).

Memory is not a bucket you append to forever. Left to grow unmanaged, it fills with duplicates, contradictions, and stale facts, and retrieving from it gets slower and less accurate. A working memory system runs a **lifecycle** — the same create/read/update/delete operations a database has, plus consolidation — and the hard part is the policy, not the storage.

## The operations

- **Create.** Decide what is worth remembering. Not every message is a durable fact; writing down too much is as harmful as too little, because it dilutes retrieval. A good system extracts the salient fact ("the user is vegetarian") rather than storing the raw turn.
- **Read (retrieve).** Surface the right memories at the right moment, usually by relevance (semantic similarity to the current situation) and recency. This is [retrieval](../rag/) pointed at the memory store, and it is what brings a long-term memory back into the [context window](../llm/context-window.md) when it matters.
- **Update.** Reconcile new information with old. When a user's preference changes, the memory should change — not accumulate a contradiction. This is where naive append-only stores fail: they end up holding both "prefers aisle seats" and "prefers window seats" with no way to choose.
- **Delete (forget).** Remove what is wrong, outdated, or no longer relevant. Forgetting is a feature: a memory that never forgets eventually drowns the signal.

## Consolidation

Beyond per-fact operations, memory needs **consolidation** — periodically summarizing many small entries into compact, higher-level ones, the way a person turns a week of details into a general impression. Consolidation keeps the store small enough to retrieve from quickly and reduces redundancy, at the cost of detail. The judgment, as with [compaction](../context/context-strategies.md) in the context window, is what to keep versus discard: over-summarize and you lose a detail whose importance only becomes clear later.

## Consistency under change

The throughline is consistency. When the world changes, memory must update rather than contradict, and the update should propagate — a changed preference should affect the next decision, not sit alongside the old one. This connects back to [state vs. memory](./state-vs-memory.md): state reacts immediately to the change within the task, and memory records the change durably for every task after. Getting both right is what lets an agent stay coherent across a long relationship instead of slowly accumulating contradictions.

## What to remember

- Memory needs a lifecycle — create, read, update, delete — plus consolidation, and the policy is harder than the storage.
- Write the salient fact, not every turn; reconcile updates instead of appending contradictions; forget what is stale.
- Consolidation keeps memory retrievable; the cost is detail, so choose what survives carefully.

## References

- Chhikara, P., et al. (2025). *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory.* arXiv:2504.19413. See [`../../references/references.md`](../../references/references.md).
