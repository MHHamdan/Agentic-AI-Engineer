# Lost in the middle

> Concept note. About 8 minutes to read. Runnable companion: [`labs/58-measuring-lost-in-the-middle/`](../../labs/58-measuring-lost-in-the-middle/).

A RAG system can retrieve the right passage and still answer wrong, because long-context models do not read their input uniformly. Liu et al. (2023), *Lost in the Middle: How Language Models Use Long Contexts*, showed that accuracy on a question whose answer sits in a long context is **U-shaped in the answer's position** — high when the relevant passage is near the start or the end, and markedly lower when it is in the middle. The effect is large enough that a model with a long context window can do worse than the same model with a short one, if the long version buries the evidence in the middle.

This matters because most RAG evaluation stops at retrieval. Recall@k tells you the gold passage was *in* the top-k; it says nothing about *where* in the assembled prompt that passage landed, and position is part of what determines whether the generator uses it. Retrieval recall is necessary but not sufficient.

## Why it happens

Two contributing mechanisms, neither fully settled:

- **Attention and position encodings.** Decoder-only transformers tend to allocate more attention to the beginning of the sequence (a primacy effect partly attributable to position-encoding schemes and to causal attention) and to the most recent tokens (a recency effect from how generation conditions on the end of the prompt). The middle gets the least.
- **Training distribution.** Instruction-tuning and pretraining data put salient content disproportionately at the start (instructions, headings) and the end (conclusions, answers), so models learn to look there.

The practical consequence is an **absolute** edge effect, not a relative one: a model attends to roughly the first and last *n* passages, so the "dead middle" *widens* as the context grows. Doubling the number of retrieved chunks can lower answer accuracy even when recall improves.

## What to do about it

- **Rerank so the strongest evidence is near an edge.** A cross-encoder reranker that lifts the most relevant passage to the top (or, less commonly, the bottom) moves it out of the dead middle. This is the highest-impact fix and is why reranking earns its latency in long-context RAG.
- **Retrieve fewer, better chunks.** More context is not more signal. Tightening k, deduplicating near-identical chunks, and compressing or summarizing retrieved passages all shrink the middle. The right k is an eval decision, not a default.
- **Order deliberately.** If you must include many passages, some systems interleave or place the top results at both ends rather than packing them in rank order at the top.
- **Evaluate by position, not just on average.** Mean answer accuracy hides the bias. Sweep the gold passage across positions and report the curve, so a regression that pushes evidence toward the middle is visible. That sweep is what [Lab 58](../../labs/58-measuring-lost-in-the-middle/) builds.

## How to measure it for your stack

The curve's depth, the size of the edge window, and even whether the end is favored as much as the start are model- and prompt-specific, so measure rather than assume:

1. Take a question set with a single known gold passage each.
2. For each question, build the context by placing the gold passage at every position among a fixed set of distractors.
3. Ask the model and score correctness at each position.
4. Aggregate to a position → accuracy curve, and read off the edge-vs-middle gap.

A model that shows little gap can take a larger k; one with a deep middle needs aggressive reranking or a smaller k. Either way the decision is now grounded in a measurement instead of a guess.

## See also

- 🧪 [Lab 58: Measuring lost-in-the-middle](../../labs/58-measuring-lost-in-the-middle/) — the position-sweep harness.
- 📖 [RAG evaluation framework](../evaluation/rag-evaluation-framework.md) — where position-aware accuracy fits among retrieval and generation metrics.
- Liu et al. (2023), *Lost in the Middle: How Language Models Use Long Contexts* (TACL).
