# Notation and conventions

> 🟢 Reference page. Read once. Come back when a symbol is unfamiliar.

Every math page in this folder uses the symbols and conventions listed here. We aim for consistency with the original sources (Sutton & Barto for RL terminology, the ReAct and RAG papers for agent-specific notation) and call out where we deliberately diverge for clarity.

---

## Core symbols

| Symbol | Reads as | Meaning |
|---|---|---|
| $x$ | "x" | A token (or a sequence of tokens, if subscripted as $x_{1:T}$) |
| $x_{1:T}$ | "x one through T" | A sequence of $T$ tokens — $x_1, x_2, \ldots, x_T$ |
| $x_{<t}$ | "x less than t" | All tokens before position $t$ — $x_1, \ldots, x_{t-1}$ |
| $p(\cdot)$ | "probability of" | A probability distribution |
| $p(y \mid x)$ | "p of y given x" | The conditional probability of $y$ given $x$ |
| $\theta$ | "theta" | Model parameters (the LLM's weights) |
| $\pi_\theta$ | "pi sub theta" | A policy parameterized by $\theta$ — the LLM, used as a decision function |
| $s_t$ | "s sub t" | The state at time step $t$ |
| $o_t$ | "o sub t" | The observation at time step $t$ |
| $a_t$ | "a sub t" | The action at time step $t$ |
| $r_t$ | "r sub t" | Reward at step $t$ (used when relevant; LLM agents often don't have one) |
| $b_t$ | "b sub t" | Belief state at step $t$ (POMDP setting) |
| $\mathbf{u}, \mathbf{v}$ | "bold u", "bold v" | Vectors (used for embeddings) |
| $\\|\mathbf{u}\\|$ | "norm of u" | The Euclidean norm of vector $\mathbf{u}$ |
| $\mathbf{u} \cdot \mathbf{v}$ | "u dot v" | Dot product |
| $\mathcal{A}, \mathcal{S}, \mathcal{O}$ | "calligraphic A, S, O" | Sets — action space, state space, observation space |
| $\arg\max_a f(a)$ | "argmax over a of f of a" | The value of $a$ that maximizes $f$ |
| $\mathbb{E}[\cdot]$ | "expectation of" | Expected value (over whatever distribution context implies) |

---

## Agentic AI conventions

Several quantities in agent papers go by different names. We pick one name per concept and stick with it:

| Concept | Our notation | Also seen as | Note |
|---|---|---|---|
| The LLM as a decision function | $\pi_\theta$ | "model", "policy", $M$, $f_\theta$ | We use *policy* whenever decisions are involved, *model* when we mean generation only |
| The conversation so far | $s_t$ | "context", "history", $h_t$, $c_t$ | We treat the full conversation as the agent's state |
| A retrieved document | $z$ | "passage", "context document", $d$ | Following Lewis et al. (RAG) — $z$ for retrieved context |
| Set of available tools | $\mathcal{A}_{\text{tool}}$ | "toolset", $\mathcal{T}$ | Tools live inside the action space |
| Termination action | $a_{\text{stop}}$ or "Final Answer" | "halt", "respond", "$\bot$" | When the agent decides it's done |

If a paper we cite uses different notation, we'll show its symbols on first reference and then translate to ours.

---

## Conditional probability — a refresher

The notation $p(y \mid x)$ shows up in nearly every page. It means "the probability of $y$ given that $x$ is true (or observed, or fixed)." Two things worth re-internalizing:

- $p(y \mid x)$ is *not* the same as $p(y, x)$ (the joint) or $p(x \mid y)$ (the reverse conditional). When in doubt, write out which variable is the random one.
- Bayes' rule: $p(y \mid x) = \frac{p(x \mid y)\, p(y)}{p(x)}$. We rarely apply Bayes directly in agentic AI, but it underlies the RAG marginalization: a generator sees retrieved context and conditions on it.

The autoregressive factorization is just repeated application of the chain rule:

$$p(x_{1:T}) = \prod_{t=1}^{T} p(x_t \mid x_{<t}).$$

This is the bedrock of every LLM. Every other equation in these notes either uses this or generalizes it.

---

## Sequences, indices, and time

- We use $t$ for *time steps in an agent loop* (each LLM call increments $t$).
- We use $i$ or $j$ for indexing items in a collection (e.g., the $i$-th retrieved document $z_i$).
- We use $1{:}T$ for inclusive ranges (1 through $T$ inclusive).

When ambiguity is possible, we annotate. For instance, $x_{1:T}$ inside an autoregressive model refers to tokens within a single generation. $s_t$ inside an agent loop refers to the state at the $t$-th step of the loop, which may itself span many tokens. Different scales, same letter sometimes — we'll be explicit when it matters.

---

## Vectors and embeddings

Embeddings are real-valued vectors, typically in $\mathbb{R}^d$ where $d$ is 384, 768, 1024, 1536, 3072, or whatever the chosen embedding model produces. We write them in bold ($\mathbf{u}$, $\mathbf{v}$) to distinguish them from scalars and discrete tokens.

Two operations dominate:

- **Dot product**: $\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^d u_i v_i$. Used directly when vectors are already normalized.
- **Cosine similarity**: $\text{sim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\\|\mathbf{u}\\|\,\\|\mathbf{v}\\|}$. The angle-only measure, invariant to magnitude.

Both are covered in detail in [`02-embeddings-similarity.md`](./02-embeddings-similarity.md) (forthcoming).

---

## "Roughly equal" and "proportional to"

- $\approx$ — approximately equal. Used when we drop a small term or normalization constant.
- $\propto$ — proportional to. Used when we care about the *shape* of a distribution but not its normalization. $p(y \mid x) \propto p(x \mid y)\, p(y)$ means the same as the full Bayes formula above, with the denominator $p(x)$ absorbed.

These come up often in retrieval scoring and in casual derivations.

---

## Discrete vs continuous

LLM agents live mostly in discrete spaces — tokens, tool names, action labels. Embeddings are the main continuous quantity we work with. When we sum over an action space, we write $\sum_{a \in \mathcal{A}}$; when we integrate over a continuous space (rarely), we write $\int \cdot \, da$. The math pages flag when the underlying space is continuous, since it changes how arguments work (e.g., densities replace probabilities for continuous variables).

---

## What we deliberately don't use

A few notational habits common in academic papers we avoid here:

- **Heavy measure-theoretic notation** ($\mathcal{F}$-measurable, $\sigma$-algebras). Not needed for agentic engineering; would obscure rather than clarify.
- **Information-theoretic shorthand** ($H(X)$, $\text{KL}(p \\| q)$). Used only where it carries its weight (mostly in evaluation pages).
- **Bra-ket notation** ($\langle \cdot, \cdot \rangle$ for inner products). We just write the dot product.

---

## See also

Every math page in this folder will refer back to this one when introducing a new symbol. If you find a symbol used somewhere that isn't listed here, please [open an issue with the `docs` label](https://github.com/MHHamdan/Agentic-AI-Engineer/issues) — it means we owe you a clearer note.

---

## References

The notation is mostly pulled from these sources and adapted for engineering use:

- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. [Free online](http://incompleteideas.net/book/the-book-2nd.html). Source for $\pi$, $s$, $a$, $r$ notation.
- Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer. Source for probability notation.
- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. Source for the $z$-for-retrieved-document convention used in RAG-related pages.
