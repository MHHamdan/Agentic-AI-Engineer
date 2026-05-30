# Language model probability

> 🧮 Mathematical foundation · ⏱ ~7 min read · Anchor: [`learning-paths/01-foundations/`](../learning-paths/01-foundations/)

## The equation

A language model defines a probability distribution over token sequences by factoring the joint into a product of conditionals:

$$
p(x_{1:T}; \theta) \;=\; \prod_{t=1}^{T} p(x_t \mid x_{<t};\, \theta).
$$

The symbols:

- $x_{1:T}$ — a sequence of $T$ tokens (the full output).
- $x_{<t}$ — every token before position $t$ (the context the model conditions on at step $t$).
- $\theta$ — the model parameters (weights).
- $p(x_t \mid x_{<t};\, \theta)$ — the next-token distribution at step $t$. The whole vocabulary gets a probability.

Generation is repeated sampling from this conditional. Three common decoding rules:

- **Greedy.** $x_t = \arg\max_{x} p(x \mid x_{<t};\, \theta)$. Take the most-likely token every step. Deterministic but myopic.
- **Temperature sampling.** Reshape the distribution as $p_\tau(x_t) \propto p(x_t)^{1/\tau}$ before sampling. Higher $\tau$ → more diverse; $\tau \to 0$ → greedy.
- **Top-p / nucleus.** Restrict sampling to the smallest set of tokens whose cumulative probability exceeds $p$, then renormalize. Cuts the long tail of unlikely tokens while preserving diversity.

---

## Mathematical intuition

Three things to internalize.

**Everything an LLM does is sampling from this distribution.** Tool calls, structured outputs, long-form essays — all of it is repeated draws from $p(x_t \mid x_{<t};\, \theta)$. The mechanism that makes a model emit a JSON tool call instead of plain prose is conditioning: the system prompt + tool schemas put probability mass on the relevant token patterns.

**The conditional is autoregressive — every token shapes the next.** Once a wrong token appears in $x_{<t}$, the model conditions on that wrong token going forward. This is why error compounding is real in long generations: a hallucinated entity in token 50 reshapes the distribution at token 51 onward. The fix is usually upstream (better conditioning) not downstream (longer outputs).

**Decoding choices are not vibes — they're variance controls.** Temperature 0 collapses $p(x_t)$ to a point mass; the model becomes deterministic and reproducible. Temperature > 0 spreads probability mass and introduces variance. For tool-calling agents, low temperature is the default because deterministic tool selection is a load-bearing engineering property. For creative writing, higher temperature is the default because diversity is the load-bearing property.

---

## Why it matters for engineers

Four practical implications:

1. **Reproducibility is a temperature decision.** If you need bit-exact replay of agent runs (for debugging, evals, audit), set temperature to 0 and seed your sampler. With non-zero temperature, the same prompt yields different completions on different calls — by design.

2. **Cost scales with the product of sequence length and vocabulary computation.** Each token costs roughly $O(\text{context length})$ at inference. This is why long contexts dominate cost; the FLOPs per token grow with $x_{<t}$.

3. **Prompting shapes the conditional.** A system prompt is just appended tokens — it works because it reshapes $p(x_t \mid x_{<t};\, \theta)$ for downstream $t$. Few-shot examples work the same way. There's no magic; it's all conditioning.

4. **Logprobs are diagnostic.** Most APIs expose token-level log-probabilities. A model that's confident (low entropy) at every step behaves differently from one that's uncertain (high entropy). Logging logprobs on critical steps lets you detect when the model is guessing vs answering.

---

## Where you'll see it in the code

Every LLM call is a sample from $p(x_t \mid x_{<t};\, \theta)$. The visible knobs are the decoding hyperparameters:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=conversation,     # this becomes x_{<t}
    temperature=0,             # tau = 0 → greedy decoding
    top_p=1.0,                 # no nucleus filtering
    max_tokens=512,            # bound on T
)
```

For tool-calling agents in [Lab 01](../labs/01-first-agent-from-scratch/), `temperature=0` is the default — deterministic tool selection avoids spurious variance. For [Path 02 RAG](../learning-paths/02-agentic-rag/) generation, you'll see temperature in the 0.0-0.3 range to keep citations grounded. For [Path 03 Reflection](../patterns/07-reflection.md), the critic step often uses slightly higher temperature than the writer to surface diverse critiques.

---

## See also

- 📖 [Path 01 — Foundations](../learning-paths/01-foundations/) — where the LLM call first becomes load-bearing.
- 🧮 [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) — the *encoding* side of language; this page covered *generation*.
- 🧮 [Agents as policies](./04-agents-as-policies.md) — how $p(x_t \mid x_{<t};\, \theta)$ becomes $\pi_\theta(a_t \mid s_t)$ when the output space is structured actions.
- 📖 [Glossary — Temperature, Token](../glossary/terms.md) — short definitions.

---

## Sources

- Bengio, Y., Ducharme, R., Vincent, P., & Jauvin, C. (2003). [*A Neural Probabilistic Language Model*](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf). JMLR. The first widely-cited paper to use the autoregressive conditional factorization with neural parameters.
- Vaswani, A., et al. (2017). [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762). NeurIPS. The Transformer paper — the parameterization $\theta$ that produces the conditional in modern LLMs.
- Hoffmann, J., et al. (2022). [*Training Compute-Optimal Large Language Models*](https://arxiv.org/abs/2203.15556). The Chinchilla scaling laws — how the quality of $p(x_t \mid x_{<t};\, \theta)$ improves with parameter count and training data.
- Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2020). [*The Curious Case of Neural Text Degeneration*](https://arxiv.org/abs/1904.09751). ICLR. Origin of nucleus (top-p) sampling.
