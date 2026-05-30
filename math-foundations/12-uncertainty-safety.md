# Uncertainty and safety

> 🧮 Mathematical foundation · ⏱ ~8 min read · Anchor: [`concepts/agents/`](../concepts/agents/)

## The equation

The model's uncertainty over its next-token distribution is **entropy**:

$$
H\big(p(x_t \mid x_{<t})\big) \;=\; -\sum_{x \in \mathcal{V}} p(x \mid x_{<t}) \cdot \log p(x \mid x_{<t}).
$$

Low entropy → the model is confident (probability mass concentrated on a few tokens). High entropy → uncertain (probability spread broadly across the vocabulary).

**Calibration** is the property that stated confidence equals actual accuracy. For a model that emits both an answer and a probability $\hat{p}$ of being correct:

$$
\text{Calibrated} \iff \forall c \in [0,1]: \quad P(\text{correct} \mid \hat{p} = c) = c.
$$

In words: when the model says "90% confident," it's right 90% of the time. Most LLMs are *miscalibrated* — they tend to be overconfident on plausible-sounding wrong answers and underconfident on counterintuitive correct ones.

**Abstention** is the agent action of declining to answer when confidence is low:

$$
a_t \;=\; \begin{cases} \text{respond}(y) & \text{if } \hat{p}(\text{correct}) \geq \tau \\ \text{abstain} & \text{otherwise} \end{cases}
$$

where $\tau$ is the confidence threshold.

---

## Mathematical intuition

Three things to internalize.

**Entropy and accuracy are correlated but not identical.** A low-entropy answer can be confidently wrong (a hallucination — the model is sure of the wrong fact). A high-entropy answer can be approximately right (the model isn't sure which phrasing to pick but the gist is correct). For safety-critical applications, entropy is a *signal* — not a guarantee.

**Calibration is a property of the model + prompt combination, not the model alone.** The same model can be well-calibrated under one prompting style and miscalibrated under another. Asking "Are you sure?" after every answer often *reduces* calibration (the model second-guesses itself). Asking for confidence as a verbalized number ("0 to 100") works for some models, fails for others. This is empirical — measure it for your setup.

**Abstention is a useful safety primitive when calibration is decent.** If $\hat{p}$ tracks true accuracy reasonably well, then "abstain when $\hat{p} < 0.7$" filters out a meaningful slice of would-be wrong answers. But it requires calibration to work; on a badly-miscalibrated model, abstaining at low $\hat{p}$ is equivalent to abstaining randomly.

---

## Why it matters for engineers

Four practical implications:

1. **Hallucinations are confident wrong answers.** They're not noise — they're the model's policy putting concentrated probability on a wrong action. The traditional "lower the temperature" advice can make hallucinations *worse*, not better, because it removes the variance that would otherwise reveal uncertainty. Better defenses: retrieval grounding (page 03), claim-level verification, judge ensembles (page 11).

2. **Verbalized confidence is the practical knob most models support.** Asking the model to emit a confidence score alongside its answer is the closest thing to introspecting $\hat{p}$. Per Kadavath et al. 2022, large models are *reasonably calibrated* on factual questions when asked to verbalize confidence. Measure ECE on your workload before relying on it.

3. **Safety guardrails should be calibration-aware.** A guardrail that routes "low-confidence answers to humans" works only if the model is calibrated. Without calibration, you're routing a random subset of cases — most are fine; some are subtly wrong. Either calibrate first or use independent verification (judge ensemble per page 11) rather than self-reported confidence.

4. **HITL triggering thresholds need empirical tuning.** Setting $\tau = 0.9$ sounds safe but may abstain on 80% of inputs, making the system unusable. Setting $\tau = 0.5$ catches few errors. The right value depends on the workload's cost structure (false negatives vs unnecessary human review). Tune on validation data; don't pick a round number.

---

## Where you'll see it in the code

Logprobs expose token-level $p(x_t \mid x_{<t})$ directly. From a Path 06 pattern:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[...],
    logprobs=True,                          # expose log-probs
    top_logprobs=5,                         # top 5 per position
    temperature=0,
)

# Per-token entropy as a confidence proxy
def token_entropies(response) -> list[float]:
    entropies = []
    for tok_lp in response.choices[0].logprobs.content:
        probs = [np.exp(alt.logprob) for alt in tok_lp.top_logprobs]
        probs = np.array(probs) / sum(probs)         # renormalize over top-k
        h = -float(np.sum(probs * np.log(probs + 1e-12)))
        entropies.append(h)
    return entropies

# Verbalized confidence (more common in production)
class AnswerWithConfidence(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1, description="0=guess, 1=certain")
    reasoning: str

# In the agent loop, route low-confidence to HITL
result = generate_structured(...)
if result.confidence < HITL_THRESHOLD:
    return route_to_human(result, original_query)
```

For HITL routing in production, see [Project 06's compliance-review gate](../projects/capstone/06-financial-research-analyst/) and [Project 08's HITL approval gates](../projects/capstone/08-production-ready-deep-research/).

---

## See also

- 🧮 [Evaluation metrics](./11-evaluation-metrics.md) — where ECE and calibration measurement live.
- 🧮 [Language model probability](./01-language-model-probability.md) — the underlying distribution from which entropy is computed.
- 📖 [Path 07 — Production & Safety](../learning-paths/07-production-and-safety/) — the production-discipline view.
- 📖 [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md) — the HITL pattern that abstention enables.
- 📖 [Glossary — Calibration, HITL, Approval gate, Guardrail](../glossary/terms.md).

---

## Sources

- Kadavath, S., et al. (2022). [*Language Models (Mostly) Know What They Know*](https://arxiv.org/abs/2207.05221). Anthropic. Demonstrates that large LMs can produce reasonably-calibrated confidence estimates when asked.
- Guo, C., et al. (2017). [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599). ICML. The ECE definition + canonical empirical analysis.
- Bommasani, R., et al. (2021). [*On the Opportunities and Risks of Foundation Models*](https://arxiv.org/abs/2108.07258). The canonical survey of foundation-model safety considerations, including calibration and abstention as risk-mitigation primitives.
- Lin, S., Hilton, J., & Evans, O. (2022). [*Teaching Models to Express Their Uncertainty in Words*](https://arxiv.org/abs/2205.14334). The verbalized-confidence methodology this page references.
