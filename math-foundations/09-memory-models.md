# Memory models

> 🧮 Mathematical foundation · ⏱ ~7 min read · Anchor: [`concepts/memory/`](../concepts/memory/)

## The equation

An agent's memory is a structured collection that gets queried for relevant context at each step. The standard tier decomposition:

$$
M \;=\; M_{\text{short}} \,\cup\, M_{\text{working}} \,\cup\, M_{\text{long}}.
$$

- $M_{\text{short}}$ — the active conversation window. Bounded by the model's context limit. Append-only within a session; dropped (or compacted) when the session ends.
- $M_{\text{working}}$ — scratch space the agent populates during a task. Notes, partial plans, intermediate results. Larger than $M_{\text{short}}$ if it lives outside the context window (e.g., in a scratch file).
- $M_{\text{long}}$ — persistent memory across sessions. User preferences, facts learned in past conversations, summaries of prior tasks. Stored externally; retrieved via a query mechanism.

A **memory retrieval** step at agent step $t$ takes a query $q_t$ (derived from $s_t$) and returns relevant entries:

$$
\text{retrieve}(M, q_t) \;=\; \{m \in M : \text{score}(m, q_t) \geq \tau\}.
$$

Where `score` is typically embedding similarity (page 02) and $\tau$ is a threshold. The retrieved entries get appended to $s_t$ before the next policy step.

---

## Mathematical intuition

Three things to internalize.

**The tier structure is a budget decomposition.** Context windows are finite; long-term knowledge is unbounded. Solving this *one* memory at *one* tier doesn't scale. The decomposition lets each tier do what it's best at: short-term keeps the current conversation immediately accessible at zero retrieval cost; long-term holds everything else and pays retrieval cost only when needed.

**Memory retrieval is a RAG problem.** The math on page 03 ($p(y \mid x) = \sum_z p(y \mid x, z) p(z \mid x)$) applies directly, with $\mathcal{Z}$ being the memory store. The retriever ranks entries by query relevance; the generator (the LLM step) conditions on the retrieved entries. This is why production memory systems are per-user mini-RAG pipelines under the hood.

**The write-side is half the problem.** Reading memory is easy — embedding similarity, top-k. *Deciding what to write* is harder. Naively writing every conversation turn produces a memory store full of irrelevant junk; writing too selectively misses important facts. The 2023+ literature (MemGPT, Mem0) treats memory *writing* as an explicit LLM-driven step, with classification, deduplication, and summarization.

---

## Why it matters for engineers

Four practical implications:

1. **The "right" memory tier for a piece of information is a budget question.** "Should I keep this in $M_{\text{short}}$ or move it to $M_{\text{working}}$?" → are we within context budget? "Should I save this to $M_{\text{long}}$?" → will we need it next session? The decision tree is at [`concepts/memory/`](../concepts/memory/).

2. **Compaction is the bridge between $M_{\text{short}}$ growing and the context window staying fixed.** When $M_{\text{short}}$ approaches the context limit, you compact: summarize old turns, drop redundant content, keep the load-bearing facts. Modern implementations (Anthropic's `context_compaction_2026-01-15`) automate this; manual implementations are in [Path 05 Module 3](../learning-paths/05-context-engineering/).

3. **Stale memory is worse than missing memory.** Long-term memory that contradicts current reality ("the user's role is CEO" when they were promoted last week) confuses the agent. Production systems either timestamp entries + expire them, or rewrite entries when the underlying fact changes. See [Mem0](https://docs.mem0.ai/) for the canonical production architecture.

4. **Memory write decisions are an attack surface.** If you let the agent decide what to save based on user input, a malicious user can plant false facts ("Remember that the password is X"). Defenses: never store user-controlled facts about the *system*; isolate memory per user; treat all retrieved memory as untrusted input downstream. The prompt-injection material in [`security/`](../security/) applies here.

---

## Where you'll see it in the code

A simple three-tier memory architecture from the concepts directory:

```python
class AgentMemory:
    def __init__(self, vector_store, user_id: str):
        self.short_term: list[Message] = []        # conversation buffer
        self.working: dict[str, Any] = {}           # scratch state
        self.long_term = vector_store               # persistent (e.g., Chroma)
        self.user_id = user_id

    def remember(self, fact: str, importance: float):
        """Write side — decide where to place a new fact."""
        if importance < 0.3:
            return                                  # not worth keeping
        if importance < 0.7:
            self.working[hash(fact)] = fact         # task-scoped
        else:
            self.long_term.add(                     # cross-session
                texts=[fact],
                metadatas=[{"user_id": self.user_id, "ts": now()}],
            )

    def recall(self, query: str, k: int = 5) -> list[str]:
        """Read side — fetch relevant memories given a query."""
        results = self.long_term.query(
            query_texts=[query],
            n_results=k,
            where={"user_id": self.user_id},
        )
        return results["documents"][0]
```

This is the minimal viable memory architecture. Production extensions: importance scoring via an LLM judge; periodic memory consolidation (clustering + summarization); tier promotion (move frequently-accessed working memory to short-term).

---

## See also

- 📖 [`concepts/memory/`](../concepts/memory/) — the conceptual treatment of agent memory.
- 🧮 [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) — how the retrieval step works.
- 🧮 [Context-window optimization](./13-context-window-optimization.md) — the constrained-selection problem within $M_{\text{short}}$.
- 📖 [Path 05 — Context Engineering](../learning-paths/05-context-engineering/) — where the budget decisions get production discipline.
- 📖 [Glossary — Memory tier, Compaction, Context budget](../glossary/terms.md).

---

## Sources

- Packer, C., et al. (2023). [*MemGPT: Towards LLMs as Operating Systems*](https://arxiv.org/abs/2310.08560). The paper that established the tiered-memory framing for LLM agents; introduced explicit memory-management primitives.
- Park, J. S., et al. (2023). [*Generative Agents: Interactive Simulacra of Human Behavior*](https://arxiv.org/abs/2304.03442). UIST. Introduces memory streams with importance-weighted retrieval and periodic reflection.
- Zhong, W., et al. (2024). [*MemoryBank: Enhancing Large Language Models with Long-Term Memory*](https://arxiv.org/abs/2305.10250). Practical architecture combining short-term, long-term, and consolidation phases.
- Mem0 team. (2024+). [*Mem0 documentation*](https://docs.mem0.ai/). Production-architecture reference for agent memory systems.
