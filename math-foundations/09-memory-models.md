# Memory models

> Mathematical foundation. About 8 minutes to read. Anchor: [`concepts/memory/`](../concepts/memory/).

## Why this matters for agentic AI

Real agents need memory that outlives a single conversation. The tier decomposition tells you where each kind of information should live, why retrieval is a RAG problem, and where the attack surface is. Getting this wrong leads to bloated context, stale facts, and prompt-injection vulnerabilities.

## The equation

An agent's memory is a structured collection that gets queried for relevant context at each step. The standard tier decomposition:

$$
M = M_{\text{short}} \cup M_{\text{working}} \cup M_{\text{long}}.
$$

**Symbols:**

- $M$ - the full memory store across all tiers.
- $M_{\text{short}}$ - the active conversation window. Bounded by the model's context limit. Append-only within a session; dropped (or compacted) when the session ends.
- $M_{\text{working}}$ - scratch space the agent populates during a task. Notes, partial plans, intermediate results. Larger than $M_{\text{short}}$ if it lives outside the context window (for example, in a scratch file).
- $M_{\text{long}}$ - persistent memory across sessions. User preferences, facts learned in past conversations, summaries of prior tasks. Stored externally; retrieved via a query mechanism.

A **memory retrieval** step at agent step $t$ takes a query $q_t$ (derived from $s_t$) and returns relevant entries:

$$
\text{retrieve}(M, q_t) = \{m \in M : \text{score}(m, q_t) \geq \tau\}.
$$

Where $\text{score}$ is typically embedding similarity (page 02) and $\tau$ is a threshold. The retrieved entries get appended to $s_t$ before the next policy step.

## How to read this equation

Read the first equation as a set decomposition: total memory is the disjoint union of three tiers. Each tier has different access cost, persistence, and capacity. Short-term is free to access (already in context), working is medium-cost (might require a tool call to a scratch buffer), long-term is more expensive (requires retrieval).

The retrieval equation says: filter the memory store down to entries whose similarity score to the query meets a threshold $\tau$. In practice you also bound the result count (top-$k$), but the threshold version is the cleaner formalism.

## Mathematical intuition

Three things to internalize.

**The tier structure is a budget decomposition.** Context windows are finite; long-term knowledge is unbounded. Solving this with *one* memory at *one* tier does not scale. The decomposition lets each tier do what it is best at: short-term keeps the current conversation immediately accessible at zero retrieval cost; long-term holds everything else and pays retrieval cost only when needed.

**Memory retrieval is a RAG problem.** The math on page 03 ($p(y \mid x) = \sum_z p(y \mid x, z) p(z \mid x)$) applies directly, with $\mathcal{Z}$ being the memory store. The retriever ranks entries by query relevance; the generator (the LLM step) conditions on the retrieved entries. This is why production memory systems are per-user mini-RAG pipelines under the hood.

**The write-side is half the problem.** Reading memory is easy: embedding similarity, top-k. *Deciding what to write* is harder. Naively writing every conversation turn produces a memory store full of irrelevant junk; writing too selectively misses important facts. The 2023+ literature (MemGPT, Mem0) treats memory writing as an explicit LLM-driven step, with classification, deduplication, and summarization.

## Where this appears in agentic systems

Four practical implications:

1. **The "right" memory tier for a piece of information is a budget question.** "Should I keep this in $M_{\text{short}}$ or move it to $M_{\text{working}}$?" comes down to: are we within context budget? "Should I save this to $M_{\text{long}}$?" comes down to: will we need it next session?
2. **Compaction is the bridge between $M_{\text{short}}$ growing and the context window staying fixed.** When $M_{\text{short}}$ approaches the context limit, you compact: summarize old turns, drop redundant content, keep the load-bearing facts. See [Path 05 Module 3](../learning-paths/05-context-engineering/).
3. **Stale memory is worse than missing memory.** Long-term memory that contradicts current reality ("the user's role is CEO" when they were promoted last week) confuses the agent. Production systems either timestamp entries and expire them, or rewrite entries when the underlying fact changes.
4. **Memory write decisions are an attack surface.** If you let the agent decide what to save based on user input, a malicious user can plant false facts ("Remember that the password is X"). Defenses: never store user-controlled facts about the *system*; isolate memory per user; treat all retrieved memory as untrusted input downstream. The prompt-injection material in [`security/`](../security/) applies here.

## Code example

A minimal three-tier memory architecture.

```python
import time
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> np.ndarray:
    r = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(r.data[0].embedding)

def cosine(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

class AgentMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term: list = []                 # conversation buffer (in context)
        self.working: dict = {}                    # task-scoped scratch
        self.long_term: list[dict] = []            # persistent across sessions

    def remember(self, fact: str, importance: float):
        """Write side: classify by importance, route to tier."""
        if importance < 0.3:
            return                                 # not worth keeping
        if importance < 0.7:
            self.working[fact] = time.time()       # task-scoped
        else:
            self.long_term.append({                # cross-session
                "fact": fact,
                "embedding": embed(fact),
                "ts": time.time(),
            })

    def recall(self, query: str, k: int = 3) -> list[str]:
        """Read side: top-k similar entries from long-term."""
        q_vec = embed(query)
        scored = [
            (cosine(q_vec, m["embedding"]), m["fact"])
            for m in self.long_term
        ]
        scored.sort(reverse=True)
        return [fact for _, fact in scored[:k]]

# Usage.
mem = AgentMemory("user_123")
mem.remember("User prefers concise responses.", importance=0.9)
mem.remember("User mentioned the weather.",     importance=0.2)
mem.remember("User is working on a tax filing.", importance=0.8)

print(mem.recall("What does the user prefer?"))
# -> ['User prefers concise responses.', 'User is working on a tax filing.', ...]
```

Production extensions: importance scoring via an LLM judge; periodic memory consolidation (clustering and summarization); tier promotion (move frequently-accessed working memory to short-term).

## Common mistakes

- **Writing every conversation turn to long-term memory.** Long-term fills up with noise; retrieval degrades; cost balloons. Use an importance classifier, even a cheap one (an LLM judging "is this worth remembering for next session?").
- **No expiration on facts.** Memory written six months ago is often stale. Either timestamp and decay, or run a periodic cleanup that re-asks the user about high-stakes facts.
- **Cross-user contamination.** Forgetting to filter by `user_id` on retrieval leaks one user's facts into another's session. Test this explicitly.
- **Trusting retrieved memory as ground truth.** Memory is *input*, not output. Anything retrieved should be treated as data the agent saw before, not as authoritative truth. Especially relevant when memory contains user-supplied facts.

## Repo cross-references

- [`concepts/memory/`](../concepts/memory/) - the conceptual treatment of agent memory.
- [`learning-paths/05-context-engineering/`](../learning-paths/05-context-engineering/) - where budget decisions get production discipline.
- [`security/`](../security/) - prompt-injection failure modes that arise from memory.

## Related pages

- [02 - Embeddings and vector similarity](./02-embeddings-vector-similarity.md) - how the retrieval step works mechanically.
- [03 - RAG formulation](./03-rag-formulation.md) - memory retrieval is a RAG problem.
- [13 - Context-window optimization](./13-context-window-optimization.md) - the constrained-selection problem within $M_{\text{short}}$.
- [Glossary: Memory tier, Compaction, Context budget](../glossary/terms.md) - short definitions.

## References

- Packer, C., et al. (2023). [*MemGPT: Towards LLMs as Operating Systems*](https://arxiv.org/abs/2310.08560). The paper that established the tiered-memory framing for LLM agents; introduced explicit memory-management primitives.
- Park, J. S., et al. (2023). [*Generative Agents: Interactive Simulacra of Human Behavior*](https://arxiv.org/abs/2304.03442). UIST 2023. Introduces memory streams with importance-weighted retrieval and periodic reflection.
- Zhong, W., et al. (2024). [*MemoryBank: Enhancing Large Language Models with Long-Term Memory*](https://arxiv.org/abs/2305.10250). Practical architecture combining short-term, long-term, and consolidation phases.
- Mem0 team. [*Mem0 documentation*](https://docs.mem0.ai/). Production architecture reference for agent memory systems. Practical reading; needs manual verification as the docs evolve.
