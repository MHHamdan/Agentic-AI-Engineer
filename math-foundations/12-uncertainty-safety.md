# Uncertainty and safety

> Mathematical foundation. About 9 minutes to read. Anchor: [`concepts/agents/`](../concepts/agents/).

## Why this matters for agentic AI

Hallucinations are confident wrong answers. Calibration tells you when to trust the model's confidence; abstention turns calibrated confidence into a safety mechanism. Together they form the basis for HITL routing, refusal logic, and any system where being wrong has real cost.

## The equation

The model's uncertainty over its next-token distribution is **entropy**:

$$
H(p(x_t \mid x_{<t})) = -\sum_{x \in \mathcal{V}} p(x \mid x_{<t}) \log p(x \mid x_{<t}).
$$

**Symbols:**

- $H(\cdot)$ - Shannon entropy.
- $p(x_t \mid x_{<t})$ - the next-token distribution (page 01).
- $\mathcal{V}$ - the model's vocabulary.

Low entropy means the model is confident (probability mass concentrated on a few tokens). High entropy means uncertain (probability spread broadly across the vocabulary).

**Calibration** is the property that stated confidence equals actual accuracy. For a model that emits both an answer and a probability $\hat{p}$ of being correct:

$$
\text{Calibrated} \iff \forall c \in [0,1]: \; p(\text{correct} \mid \hat{p} = c) = c.
$$

In words: when the model says "90% confident," it is right 90% of the time. Most LLMs are *miscalibrated*. They tend to be overconfident on plausible-sounding wrong answers and underconfident on counterintuitive correct ones.

**Abstention** is the agent action of declining to answer when confidence is low:

$$
a_t = \begin{cases} \text{respond}(y) & \text{if } \hat{p}(\text{correct}) \geq \tau \\ \text{abstain} & \text{otherwise} \end{cases}
$$

where $\tau$ is the confidence threshold.

## How to read these equations

**Entropy.** Sum over the vocabulary of $-p \log p$. Each token in the vocab contributes its probability times the log of its probability. A model that puts all probability on one token has zero entropy (perfect confidence). A model that spreads probability uniformly has maximum entropy ($\log \|\mathcal{V}\|$).

**Calibration.** Read the "for all $c$" as: for every level of stated confidence, the model's actual accuracy at that confidence level should equal the stated confidence. A reliability diagram plots stated confidence on x-axis and actual accuracy on y-axis. A calibrated model lies on the y = x diagonal.

**Abstention.** A simple gate: if confidence is above threshold $\tau$, respond; otherwise abstain. The threshold is a business decision: how willing are you to refuse vs how willing are you to be wrong?

## Mathematical intuition

Three things to internalize.

**Entropy and accuracy are correlated but not identical.** A low-entropy answer can be confidently wrong (a hallucination: the model is sure of the wrong fact). A high-entropy answer can be approximately right (the model is not sure which phrasing to pick but the gist is correct). For safety-critical applications, entropy is a *signal*, not a guarantee.

**Calibration is a property of the model plus prompt combination, not the model alone.** The same model can be well-calibrated under one prompting style and miscalibrated under another. Asking "Are you sure?" after every answer often *reduces* calibration (the model second-guesses itself). Asking for confidence as a verbalized number ("0 to 100") works for some models, fails for others. This is empirical: measure it for your setup.

**Abstention is a useful safety primitive when calibration is decent.** If $\hat{p}$ tracks true accuracy reasonably well, then "abstain when $\hat{p} < 0.7$" filters out a meaningful slice of would-be wrong answers. But it requires calibration to work; on a badly-miscalibrated model, abstaining at low $\hat{p}$ is equivalent to abstaining randomly.

## Where this appears in agentic systems

Four practical implications:

1. **Hallucinations are confident wrong answers.** They are not noise; they are the model's policy putting concentrated probability on a wrong action. The traditional "lower the temperature" advice can make hallucinations *worse*, not better, because it removes the variance that would otherwise reveal uncertainty. Better defenses: retrieval grounding (page 03), claim-level verification, judge ensembles (page 11).
2. **Verbalized confidence is the practical knob most models support.** Asking the model to emit a confidence score alongside its answer is the closest thing to introspecting $\hat{p}$. Per Kadavath et al. 2022, large models are reasonably calibrated on factual questions when asked to verbalize confidence. Measure ECE on your workload before relying on it.
3. **Safety guardrails should be calibration-aware.** A guardrail that routes "low-confidence answers to humans" works only if the model is calibrated. Without calibration, you are routing a random subset of cases (most are fine; some are subtly wrong). Either calibrate first or use independent verification (judge ensemble per page 11) rather than self-reported confidence.
4. **HITL triggering thresholds need empirical tuning.** Setting $\tau = 0.9$ sounds safe but may abstain on 80% of inputs, making the system unusable. Setting $\tau = 0.5$ catches few errors. The right value depends on the workload's cost structure (false negatives vs unnecessary human review). Tune on validation data; do not pick a round number.

## Code example

Two ways to read out uncertainty: token-level entropy and verbalized confidence.

```python
import math
import numpy as np
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

# 1. Token-level entropy from logprobs.
def token_entropy(message_logprobs) -> list[float]:
    """Entropy at each generated token position."""
    entropies = []
    for tok in message_logprobs.content:
        probs = np.array([math.exp(alt.logprob) for alt in tok.top_logprobs])
        probs = probs / probs.sum()
        h = -float(np.sum(probs * np.log(probs + 1e-12)))
        entropies.append(h)
    return entropies

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Is the sky blue? One-word answer."}],
    logprobs=True,
    top_logprobs=5,
    temperature=0,
)
print("Per-token entropy:", token_entropy(response.choices[0].logprobs))

# 2. Verbalized confidence with structured output.
class AnswerWithConfidence(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1, description="0=guess, 1=certain")
    reasoning: str

def answer_with_confidence(query: str) -> AnswerWithConfidence:
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer with confidence in [0, 1]. Reflect your true uncertainty."},
            {"role": "user", "content": query},
        ],
        response_format=AnswerWithConfidence,
        temperature=0,
    )
    return response.choices[0].message.parsed

HITL_THRESHOLD = 0.7
result = answer_with_confidence("What was the GDP of Estonia in 2024?")
if result.confidence < HITL_THRESHOLD:
    print(f"Abstaining (confidence={result.confidence:.2f}). Route to human.")
else:
    print(f"Answer (confidence={result.confidence:.2f}): {result.answer}")
```

For HITL routing in production, low-confidence outputs get escalated; high-confidence outputs proceed. Measure ECE on a validation set before trusting the threshold.

## Common mistakes

- **Equating low entropy with correctness.** Entropy says "the model is confident," not "the model is right." A confident hallucination has low entropy.
- **Asking for confidence after generating the answer.** The model often justifies whatever it just said. Either ask for confidence as part of the structured output (one call) or use logprobs from the original generation.
- **Picking $\tau$ by gut.** The threshold should come from a validation experiment. Plot accuracy vs abstention rate; choose the point that matches your cost structure.
- **Treating uncalibrated confidence as a probability.** If ECE is 0.2 (meaning the model is, on average, 20 points off its stated confidence), you cannot use the stated number as a probability. Calibrate first (temperature scaling or isotonic regression) or use a different signal.

## Repo cross-references

- [Lab 20 - Drift detection and calibration](../labs/20-drift-detection-and-calibration/) - measures calibration over time.
- [`learning-paths/07-production-and-safety/`](../learning-paths/07-production-and-safety/) - the production-discipline view.
- [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md) - the HITL pattern that abstention enables.
- [Project 06 - Financial research analyst](../projects/capstone/06-financial-research-analyst/) and [Project 08 - Production-ready deep research](../projects/capstone/08-production-ready-deep-research/) - HITL approval gates in production capstones.

## Related pages

- [01 - Language model probability](./01-language-model-probability.md) - the underlying distribution from which entropy is computed.
- [11 - Evaluation metrics](./11-evaluation-metrics.md) - where ECE and calibration measurement live.
- [Glossary: Calibration, HITL, Approval gate, Guardrail](../glossary/terms.md) - short definitions.

## References

- Kadavath, S., et al. (2022). [*Language Models (Mostly) Know What They Know*](https://arxiv.org/abs/2207.05221). Anthropic. Demonstrates that large LMs can produce reasonably-calibrated confidence estimates when asked.
- Guo, C., et al. (2017). [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599). ICML 2017. The ECE definition and canonical empirical analysis.
- Lin, S., Hilton, J., and Evans, O. (2022). [*Teaching Models to Express Their Uncertainty in Words*](https://arxiv.org/abs/2205.14334). The verbalized-confidence methodology this page references.
- Shannon, C. E. (1948). [*A Mathematical Theory of Communication*](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf). The original entropy paper.
- Bommasani, R., et al. (2021). [*On the Opportunities and Risks of Foundation Models*](https://arxiv.org/abs/2108.07258). Stanford. Comprehensive survey of foundation-model safety considerations, including calibration and abstention as risk-mitigation primitives.
