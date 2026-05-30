# Context-window optimization

> 🧮 Mathematical foundation · ⏱ ~8 min read · Anchor: [`concepts/context/`](../concepts/context/)

## The equation

Context-window optimization is a **constrained selection** problem. Given a set of candidate items $I = \{i_1, i_2, \ldots, i_n\}$ each with token cost $c_i$ and value $v_i$ to the task, pick a subset $S \subseteq I$ that maximizes total value within the budget $B$:

$$
\max_{S} \;\sum_{i \in S} v_i \quad \text{ subject to } \quad \sum_{i \in S} c_i \;\leq\; B.
$$

This is the **0/1 knapsack** problem. It's NP-hard in general; in practice, agent systems use greedy approximations because the items are ranked by a similarity score (page 02) that's already a value proxy.

The standard production approximation:

$$
S \;=\; \big\{ \text{top-}k\,(v_i, c_i) : \sum_{i \in S} c_i \leq B \big\},
$$

implemented as: sort by value, fill until the budget is reached, stop.

Once $S$ is selected, **ordering within the context** matters too. Empirically (Liu et al. 2023, "lost in the middle"), LLMs attend more to the start and end of the context than the middle. So the items in $S$ should be ordered with the most important items at the boundaries.

---

## Mathematical intuition

Three things to internalize.

**The budget $B$ is the model's context window minus everything else.** The total context window is a hard ceiling. The system prompt, tool definitions, conversation history, and reserved generation space all consume budget. What's left over is what you can spend on retrieved context. Per-zone budgets ([`concepts/context/token-budgets.md`](../concepts/context/token-budgets.md)) make this allocation explicit.

**The value $v_i$ is what your retriever's score function approximates.** A perfect retriever would give $v_i$ exactly — the marginal information gain of including item $i$ given everything else in $S$. Real retrievers give cosine similarity to the query, which is a *unconditional* relevance signal that ignores the rest of $S$. That gap (conditional vs unconditional value) is why retrieval often returns near-duplicates: each duplicate has high $v_i$ on its own, but adding the second one barely improves $S$.

**"Lost in the middle" makes ordering load-bearing.** If you have $k = 10$ documents in $S$, putting the 3 most-relevant at positions 1, 9, 10 (start + end) outperforms putting them at positions 4, 5, 6. The math doesn't change — the value $v_i$ is the same — but the model's *effective* use of $v_i$ depends on position. The fix is to reorder $S$ after selection.

---

## Why it matters for engineers

Four practical implications:

1. **Per-zone budgets prevent runaway growth.** Without per-zone tiers, conversation history alone can fill the window before retrieval gets to contribute. Production systems allocate explicitly: 5% system prompt, 10% tool definitions, 20% conversation, 50% retrieval, 15% reserved for generation. [Path 05 Module 2](../learning-paths/05-context-engineering/) walks through tuning this for different workloads.

2. **Greedy top-k is almost always the right approximation.** Real knapsack solving for context selection isn't worth the engineering cost — the rank ordering from the retriever is already a strong heuristic. Where greedy fails: when items are near-duplicates (fix: deduplication before selection) or when the query needs multi-perspective coverage (fix: maximal marginal relevance, which penalizes redundancy).

3. **Reorder after selection.** After choosing $S$ via greedy top-k, reorder so the most relevant items sit at positions 1 and $|S|$. This is the cheapest possible quality improvement — no extra retrieval cost, no extra generation cost, just a few lines of Python.

4. **Long-context models change the math but don't eliminate it.** A 1M-token model has a much larger $B$, so the constraint binds less often. But cost still scales with context length, and "lost in the middle" persists (in fact, gets worse at extreme contexts). Long contexts are an option for the budget, not a replacement for budget discipline. See [`concepts/context/long-context-models.md`](../concepts/context/long-context-models.md).

---

## Where you'll see it in the code

A canonical "greedy fill + reorder" selector:

```python
def select_context(
    candidates: list[Item],
    budget_tokens: int,
    tokenizer,
) -> list[Item]:
    """Greedy top-k subject to budget, reordered for position effects."""
    # Pre-sorted by retriever score (descending).
    selected, used = [], 0
    for item in candidates:
        item_cost = len(tokenizer.encode(item.text))
        if used + item_cost <= budget_tokens:
            selected.append(item)
            used += item_cost
        else:
            continue   # skip oversized; could also truncate

    # Reorder: best at boundaries, weakest in the middle.
    if len(selected) >= 3:
        # selected[0] is most relevant; selected[-1] second-most; etc.
        reordered = []
        left, right = [], []
        for i, item in enumerate(selected):
            (left if i % 2 == 0 else right).append(item)
        reordered = left + list(reversed(right))
        return reordered
    return selected
```

Production extensions: maximal marginal relevance (penalize items too similar to already-selected ones), per-source quotas (don't let one source dominate), and explicit deduplication of near-identical chunks before this function runs.

---

## See also

- 📖 [Token budgets](../concepts/context/token-budgets.md) — the per-zone allocation discipline.
- 📖 [Context drift detection](../concepts/context/context-drift-detection.md) — what goes wrong over long-running conversations.
- 📖 [Long-context models](../concepts/context/long-context-models.md) — the option of just using a bigger window.
- 🧮 [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) — where the value $v_i$ comes from.
- 🧮 [Memory models](./09-memory-models.md) — the tier structure that determines what's in $I$.
- 📖 [Glossary — Context window, Context budget, Long-context model, Compaction](../glossary/terms.md).

---

## Sources

- Liu, N. F., et al. (2023). [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172). TACL 2024. The canonical paper on position-dependent attention in long contexts; motivates the reorder step.
- Carbonell, J., & Goldstein, J. (1998). [*The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries*](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf). SIGIR. The MMR algorithm referenced above.
- Levy, M., et al. (2024). [*Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models*](https://arxiv.org/abs/2402.14848). ACL 2024. Empirical demonstration that performance degrades with input length even when relevant info is preserved — strengthens the budget-discipline argument.
- Hsieh, C.-P., et al. (2024). [*RULER: What's the Real Context Size of Your Long-Context Language Models?*](https://arxiv.org/abs/2404.06654). The benchmark methodology for measuring effective context use as a function of position and length.
