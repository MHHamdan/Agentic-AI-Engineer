# Language model probability

> Mathematical foundation. About 8 minutes to read. Anchor: [`learning-paths/01-foundations/`](../learning-paths/01-foundations/).

## Why this matters for agentic AI

Every action an agent takes is a sample from a probability distribution defined by the language model. Understanding that distribution lets you control reproducibility, debug hallucinations, and choose decoding hyperparameters with intent rather than guesswork. The same equation underlies tool calls, structured outputs, and prose.

## The equation

A language model defines a probability distribution over token sequences by factoring the joint distribution into a product of conditionals:

$$
p(x_{1:T}; \theta) = \prod_{t=1}^{T} p(x_t \mid x_{<t}; \theta).
$$

**Symbols:**

- $x_{1:T}$ - a sequence of $T$ tokens, the full output.
- $x_{<t}$ - every token before position $t$, the context the model conditions on at step $t$.
- $\theta$ - the model parameters (weights).
- $p(x_t \mid x_{<t}; \theta)$ - the next-token distribution at step $t$. The whole vocabulary gets a probability.

## How to read this equation

Read left to right. The joint probability of an entire sequence equals the product of the probabilities of each token conditional on the tokens that came before it. The semicolon separating $x_{<t}$ from $\theta$ is a convention meaning "given the parameters." The parameters are fixed during generation; the random thing is the sequence.

Sampling from this distribution is what every LLM call does. Three common decoding rules:

- **Greedy.** $x_t = \arg\max_x p(x \mid x_{<t}; \theta)$. Take the most-likely token every step. Deterministic but myopic.
- **Temperature sampling.** Reshape the distribution as $p_\tau(x_t) \propto p(x_t)^{1/\tau}$ before sampling. Higher $\tau$ gives more diversity; as $\tau$ approaches $0$, sampling collapses to greedy.
- **Top-p (nucleus).** Restrict sampling to the smallest set of tokens whose cumulative probability exceeds $p$, then renormalize. Cuts the long tail of unlikely tokens while preserving diversity.

## Mathematical intuition

Three things to internalize.

**Everything an LLM does is sampling from this distribution.** Tool calls, structured outputs, long-form essays. All of it is repeated draws from $p(x_t \mid x_{<t}; \theta)$. The mechanism that makes a model emit a JSON tool call instead of plain prose is conditioning: the system prompt and tool schemas put probability mass on the relevant token patterns.

**The conditional is autoregressive, so every token shapes the next.** Once a wrong token appears in $x_{<t}$, the model conditions on that wrong token going forward. This is why error compounding is real in long generations. A hallucinated entity in token 50 reshapes the distribution at token 51 onward. The fix is usually upstream (better conditioning) not downstream (longer outputs).

**Decoding choices are variance controls, not vibes.** Temperature 0 collapses $p(x_t)$ to a point mass; the model becomes deterministic and reproducible. Temperature greater than 0 spreads probability mass and introduces variance. For tool-calling agents, low temperature is the default because deterministic tool selection is a load-bearing engineering property. For creative writing, higher temperature is the default because diversity is the load-bearing property.

## Where this appears in agentic systems

- **Reproducibility.** Setting `temperature=0` and seeding the sampler makes agent runs replayable for debugging, evals, and audit logs. Otherwise the same prompt gives different completions on different calls.
- **Cost.** Each token costs about $O(\text{context length})$ at inference. FLOPs per token grow with $x_{<t}$, which is why long contexts dominate cost.
- **Prompting.** A system prompt is appended tokens; it works because it reshapes $p(x_t \mid x_{<t}; \theta)$ for downstream $t$. Few-shot examples work the same way. There is no magic, only conditioning.
- **Logprobs as diagnostics.** Most APIs expose token-level log-probabilities. A model that is confident (low entropy) at every step behaves differently from one that is uncertain (high entropy). Logging logprobs on critical steps lets you detect when the model is guessing vs answering.

## Code example

Compute token-level log-probabilities and perplexity using the OpenAI Chat Completions API. Perplexity is $\exp(-\frac{1}{T} \sum_t \log p(x_t \mid x_{<t}))$. Lower means more confident.

```python
import math
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Name a primary color."}],
    logprobs=True,
    temperature=0,
    max_tokens=20,
)

# Pull the per-token log-probabilities of the chosen tokens.
tokens = response.choices[0].logprobs.content
logp = [t.logprob for t in tokens]
text = "".join(t.token for t in tokens)

# Perplexity over the generated tokens.
mean_logp = sum(logp) / len(logp)
perplexity = math.exp(-mean_logp)

print(f"Generated: {text!r}")
print(f"Mean log-prob: {mean_logp:.3f}")
print(f"Perplexity:    {perplexity:.3f}")
```

If the model emits "red." you would expect a low perplexity (high confidence). If it emits something hesitant or wordy, perplexity rises. This is the cheapest possible confidence signal you can extract from any modern LLM API.

## Common mistakes

- **Confusing temperature with creativity.** Temperature controls *variance*, not *quality*. Higher temperature does not produce better creative writing automatically; it produces more varied output, some of which may be worse.
- **Assuming temperature 0 is fully deterministic.** It is deterministic at the sampling step, but floating-point non-determinism on the GPU and version drift in the backend can still produce different outputs across runs. Pin the model version when reproducibility matters.
- **Reading raw probabilities instead of log-probabilities.** APIs return log-probabilities because the actual probabilities are often tiny (`1e-15` is not unusual). Always convert with `math.exp(logprob)` only when you need a probability in `[0, 1]`.
- **Computing perplexity on too few tokens.** Perplexity is a mean over tokens. Averaging over fewer than about 20 tokens is noisy; use it as a qualitative signal on short generations.

## Repo cross-references

- [Lab 01 - First agent from scratch](../labs/01-first-agent-from-scratch/) - the ReAct loop that samples from $p(x_t \mid x_{<t}; \theta)$ once per step.
- [`concepts/agents/agent-loop.md`](../concepts/agents/agent-loop.md) - the engineering view of the sampling loop.
- [`patterns/07-reflection.md`](../patterns/07-reflection.md) - where temperature differences between a writer and a critic become an architectural choice.

## Related pages

- [02 - Embeddings and vector similarity](./02-embeddings-vector-similarity.md) - the encoding side of language; this page covered generation.
- [04 - Agents as policies](./04-agents-as-policies.md) - how $p(x_t \mid x_{<t}; \theta)$ becomes $\pi_\theta(a_t \mid s_t)$ when the output space is structured actions.
- [11 - Evaluation metrics](./11-evaluation-metrics.md) - how to score the outputs of this distribution.
- [12 - Uncertainty and safety](./12-uncertainty-safety.md) - entropy of $p(x_t \mid x_{<t})$ as a confidence signal.
- [Glossary: Token, Temperature](../glossary/terms.md) - short definitions.

## References

- Bengio, Y., Ducharme, R., Vincent, P., and Jauvin, C. (2003). [*A Neural Probabilistic Language Model*](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf). JMLR. The first widely cited paper to use the autoregressive conditional factorization with neural parameters.
- Vaswani, A., et al. (2017). [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762). NeurIPS. The Transformer paper. The parameterization $\theta$ that produces the conditional in modern LLMs.
- Hoffmann, J., et al. (2022). [*Training Compute-Optimal Large Language Models*](https://arxiv.org/abs/2203.15556). The Chinchilla scaling laws. How the quality of $p(x_t \mid x_{<t}; \theta)$ improves with parameter count and training data.
- Holtzman, A., Buys, J., Du, L., Forbes, M., and Choi, Y. (2020). [*The Curious Case of Neural Text Degeneration*](https://arxiv.org/abs/1904.09751). ICLR. Origin of nucleus (top-p) sampling; explains why pure max-likelihood decoding produces degenerate text.
- OpenAI. [*Chat Completions API: logprobs*](https://platform.openai.com/docs/api-reference/chat/create#chat-create-logprobs). Documentation for the `logprobs` parameter used in the code example.
