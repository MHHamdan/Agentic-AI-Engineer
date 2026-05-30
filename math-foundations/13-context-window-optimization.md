# Context-window optimization

> Mathematical foundation. About 9 minutes to read. Anchor: [`learning-paths/05-context-engineering/`](../learning-paths/05-context-engineering/).

## Why this matters for agentic AI

Every agent runs into the context-window cliff: too much candidate information, too few tokens to fit it. The formalism (knapsack) tells you that this is a real combinatorial problem and explains why production systems all converge on similar shapes (greedy top-k, with reordering and per-source caps). Knowing the math also tells you which approximations are cheap and which are dangerous.

## The equation

Context selection is a **0/1 knapsack problem**. Given a set of candidate context items $\mathcal{I}$, each with token-cost $c_i$ and predicted value $v_i$, choose the subset that maximizes total value subject to the token budget:

$$
\max_{x \in \{0,1\}^{|\mathcal{I}|}} \sum_{i \in \mathcal{I}} v_i \, x_i \quad \text{subject to} \quad \sum_{i \in \mathcal{I}} c_i \, x_i \leq B.
$$

**Symbols:**

- $\mathcal{I}$ - the candidate set (retrieved chunks, conversation turns, memory entries, tool outputs).
- $x_i \in \{0, 1\}$ - inclusion indicator. $x_i = 1$ means item $i$ goes into the context.
- $c_i$ - token cost of item $i$.
- $v_i$ - predicted value of item $i$ (typically retrieval similarity score, recency, importance, or a learned ranking).
- $B$ - the token budget. The context window minus reserved tokens for system prompt, conversation tail, and generation buffer.

The exact 0/1 knapsack is NP-hard. In practice we use a **greedy approximation**: sort items by $v_i / c_i$ (value per token), include greedily until the budget is exhausted.

After selection, **order matters**. Models exhibit a **lost-in-the-middle** effect: items in the middle of long contexts are recalled less reliably than items at the start or end (Liu et al. 2023). So after selecting, we reorder:

$$
\text{order}(x) = \text{interleave}(\text{high-value at start and end}, \text{lower-value in middle}).
$$

The selection problem is what to include; the ordering problem is where to put it.

## How to read these equations

The knapsack reads: pick a subset of items maximizing total value while staying under the token budget. Each $x_i$ is a binary choice (include or exclude). The constraint says the sum of token costs of included items cannot exceed $B$.

The ordering equation says: after selection, do not just dump everything in retrieval order. Reorder so high-value items live at positions the model actually attends to. The interleave pattern (high-value at start *and* end, lower-value tucked in the middle) is a practical workaround for lost-in-the-middle.

## Mathematical intuition

Three things to internalize.

**Greedy by value-per-token is the right default approximation.** For 0/1 knapsack, greedy gives a 2-approximation in the worst case but is much closer to optimal on real workloads where the items are diverse in cost. Production systems rarely need anything more sophisticated. Dynamic programming gives the exact solution at $O(\|\mathcal{I}\| \cdot B)$ but is overkill for typical $\|\mathcal{I}\|$ (say, 100 candidates) and $B$ (say, 30k tokens).

**The value function is the hard part.** $v_i$ is not given; you assign it. Common signals: retrieval similarity (page 02), recency (more recent is usually more valuable), importance (some items are pre-marked), source reliability (some sources matter more). The right $v_i$ is workload-dependent. Tuning it is most of the work.

**Lost-in-the-middle is a real and measurable failure mode.** It is not folklore. Long-context models (32k, 128k, 1M tokens) have measurably better recall at the start and end of the context than in the middle. The effect is strongest around the 30% to 70% positional range. Putting load-bearing facts there means losing them.

## Where this appears in agentic systems

Four practical implications:

1. **Selection happens once per turn; ordering happens after every selection.** A production context-engineering pipeline looks like: gather candidates from all sources (retrieval, memory, tools), score them, greedy-select up to budget, reorder, render into the prompt. The shape is the same across most agent frameworks.
2. **Reserve a budget for the generation buffer.** The token budget $B$ is the context window minus (a) the system prompt, (b) the trailing conversation history that the user can see, (c) the expected generation length. Forgetting any of these gives an OOM-style error at inference time.
3. **Per-source caps prevent dominance failures.** Without a cap, a single source (for example, web search returning 20 long chunks) can crowd out memory, conversation history, and other retrievals. Production systems typically allocate fractional budgets per source: 40% for retrieval, 30% for memory, 20% for conversation, 10% for tool outputs. Adjust per workload.
4. **Compaction is amortized selection.** When the active conversation exceeds budget over time, compaction is "select the most valuable previous turns; summarize or drop the rest." It is the same knapsack at the conversation level. See [`patterns/05-context-engineering/`](../learning-paths/05-context-engineering/) for the production version.

## Code example

A minimal greedy selector with reordering.

```python
from dataclasses import dataclass

@dataclass
class ContextItem:
    text: str
    value: float        # retrieval score, importance, etc.
    tokens: int

def greedy_knapsack(items: list[ContextItem], budget: int) -> list[ContextItem]:
    """Greedy by value-per-token. 2-approximation in the worst case."""
    scored = sorted(items, key=lambda x: -x.value / max(x.tokens, 1))
    selected, used = [], 0
    for item in scored:
        if used + item.tokens <= budget:
            selected.append(item)
            used += item.tokens
    return selected

def lost_in_the_middle_reorder(selected: list[ContextItem]) -> list[ContextItem]:
    """High value at start AND end; lower in the middle."""
    by_value = sorted(selected, key=lambda x: -x.value)
    front, back, middle = [], [], []
    for i, item in enumerate(by_value):
        if i % 3 == 0:    front.append(item)
        elif i % 3 == 1:  back.append(item)
        else:             middle.append(item)
    return front + middle + list(reversed(back))

def render_context(items: list[ContextItem]) -> str:
    return "\n\n".join(f"[{i+1}] {item.text}" for i, item in enumerate(items))

# Usage.
candidates = [
    ContextItem(text="Eiffel Tower built 1887-1889.",   value=0.92, tokens=12),
    ContextItem(text="Paris is the capital of France.", value=0.95, tokens=10),
    ContextItem(text="The Seine flows through Paris.",   value=0.61, tokens=11),
    ContextItem(text="France has 18 administrative regions.", value=0.40, tokens=14),
    ContextItem(text="Roast chicken at 425 F for one hour.",   value=0.05, tokens=15),
]
selected = greedy_knapsack(candidates, budget=40)
ordered = lost_in_the_middle_reorder(selected)
print(render_context(ordered))
```

Production extensions: per-source budget caps, learned value functions (cross-encoder reranking), and diversity penalties (maximal marginal relevance) to avoid near-duplicates dominating the selection.

## Common mistakes

- **Stuffing every retrieved chunk into the context.** Cheap and wrong. Past about 10 to 20 chunks, the model's recall on each one drops sharply, and you pay the full token cost for marginal value.
- **Sorting purely by similarity score.** Ignores token cost. A 500-token chunk at similarity 0.85 and a 50-token chunk at 0.80 have very different value-per-token. Greedy on the ratio handles this.
- **No reservation for generation.** Filling the context window to the model's hard limit leaves no room for the response. The model truncates output, or the API errors.
- **Treating the budget as fixed across turns.** Conversation history grows; the budget for retrieval and memory shrinks correspondingly. Re-budget every turn.
- **Skipping the reorder step.** Putting the most-relevant chunk in position 7 of 12 sometimes means the model effectively does not see it. Empirically, reordering improves recall.

## Repo cross-references

- [`learning-paths/05-context-engineering/`](../learning-paths/05-context-engineering/) - the production-discipline view.
- [`concepts/context/foundations.md`](../concepts/context/foundations.md) - the engineering treatment.
- [`concepts/context/compression-and-summarization.md`](../concepts/context/compression-and-summarization.md) - how compaction works in practice. The compression-and-summarization page covers the amortized-selection variant for long-running conversations.
- The lost-in-the-middle phenomenon is covered in the Liu et al. reference below; no dedicated repo page yet (a candidate for continuous improvement).

## Related pages

- [02 - Embeddings and vector similarity](./02-embeddings-vector-similarity.md) - how $v_i$ gets computed for retrieval candidates.
- [03 - RAG formulation](./03-rag-formulation.md) - the upstream problem that produces the candidate set.
- [09 - Memory models](./09-memory-models.md) - memory entries are knapsack candidates too.
- [Glossary: Context window, Compaction, Lost in the middle, Token budget](../glossary/terms.md) - short definitions.

## References

- Liu, N. F., et al. (2023). [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172). TACL 2024. The paper that established the U-shaped recall curve and named the lost-in-the-middle effect.
- Kellerer, H., Pferschy, U., and Pisinger, D. (2004). *Knapsack Problems*. Springer. The canonical reference for knapsack algorithms and their approximations. Useful when you need to go past greedy.
- Anthropic. [*Long context prompting techniques*](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips). Practical guidance on positioning load-bearing content in long contexts. Needs manual verification as the docs evolve.
- OpenAI. [*Best practices for prompt engineering with the OpenAI API*](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api). Useful for context-budget allocation patterns. Needs manual verification as guidance updates.
- Gao, T., et al. (2023). [*Enabling Large Language Models to Generate Text with Citations*](https://arxiv.org/abs/2305.14627). EMNLP 2023. Includes empirical results on how context structure affects citation accuracy in long-context RAG.
