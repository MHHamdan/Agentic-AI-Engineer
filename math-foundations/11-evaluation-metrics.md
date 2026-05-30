# Evaluation metrics

> 🧮 Mathematical foundation · ⏱ ~9 min read · Anchor: [`concepts/evaluation/`](../concepts/evaluation/)

## The equation

Evaluation produces a score $\hat{s}$ for an agent output $y$ given an input $x$ (and optionally a reference $y^*$):

$$
\hat{s} \;=\; M(y, x, y^*).
$$

Where $M$ is the **metric**. Four metric families that show up across the repo:

**Classification metrics** (when output can be judged true/false against a ground truth):

$$
\text{Precision} \;=\; \frac{TP}{TP + FP}, \qquad \text{Recall} \;=\; \frac{TP}{TP + FN}, \qquad F_1 \;=\; \frac{2 \cdot P \cdot R}{P + R}.
$$

**RAG-specific metrics** (Es et al. 2023, the RAGAS framework):

$$
\text{Faithfulness} \;=\; \frac{|\text{claims}(y) \cap \text{supported}(z)|}{|\text{claims}(y)|}.
$$

In words: of the claims in the generated answer $y$, what fraction are supported by the retrieved evidence $z$?

**LLM-as-judge metrics**: $\hat{s} = \pi_{\text{judge}}(y, x, \text{rubric})$. A separate LLM scores the output against a rubric. Bounded by the judge's calibration.

**Calibration** (when the model emits both an answer and a confidence):

$$
\text{ECE} \;=\; \sum_{b=1}^{B} \frac{n_b}{N} \,\big|\,\text{accuracy}(b) - \text{confidence}(b)\big|.
$$

Expected Calibration Error: how far the model's stated confidence is from its actual accuracy, averaged over confidence bins.

---

## Mathematical intuition

Three things to internalize.

**Different metrics catch different failure modes.** Precision catches "the agent made stuff up"; recall catches "the agent missed important content"; faithfulness catches "the agent's claims aren't in the evidence." A single number can't summarize agent quality — production evaluation maintains a **metric portfolio** that covers complementary failure modes.

**LLM-as-judge is the practical workhorse, with a calibration caveat.** Hand-labeling is expensive; rule-based metrics miss most quality issues. LLM judges scale and catch nuance — but they have biases (verbose-answer preference, position bias, format preference) that drift over time. Production systems use **judge ensembles** (page 11 in [Path 06 patterns](../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md)) to reduce variance and detect calibration shift.

**Online and offline evaluation answer different questions.** Offline (golden dataset, run on every deploy) → "did this change break the things we know about?" Online (production traffic, sampled and judged) → "is the system staying good in the wild?" You need both. Offline is the regression-safety net; online is the drift-detection signal.

---

## Why it matters for engineers

Four practical implications:

1. **Match the metric to the workload.** RAG → faithfulness + answer relevance + context recall. Tool-using agents → tool-choice correctness + argument validity + task completion. Multi-agent → handoff success rate + per-agent contribution + final-output quality. Wrong metric → false confidence in a broken system.

2. **Maintain a baseline portfolio + a regression set.** Per [Project 07](../projects/capstone/07-evaluated-multi-agent-system/) and Path 06 v2: a fixed baseline (the golden dataset) plus a growing regression set (failures promoted from production). Every deploy runs both. Failures on baseline block release; failures on regression are reviewed.

3. **Track inter-judge agreement when using LLM judges.** A single LLM judge's score is one data point. Three judges with intentionally different biases give you (a) reduced variance via averaging and (b) a disagreement signal that's a separate quality indicator — high disagreement means the case is hard or the rubric is ambiguous.

4. **Calibration is upstream of HITL triggering.** If the agent's confidence is uncorrelated with its actual accuracy (poor calibration), then "route low-confidence outputs to humans" doesn't filter the right cases. Measuring ECE periodically catches calibration drift before it breaks the HITL pipeline.

---

## Where you'll see it in the code

From [Path 06 — Judge ensemble pattern](../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md), the scoring function:

```python
def judge(output: str, query: str, evidence: list[str], rubric: dict) -> dict:
    """LLM-as-judge: pi_judge(output, query, evidence, rubric) -> {score, reasoning}."""
    prompt = render_judge_prompt(output, query, evidence, rubric)
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
        response_format=JudgeVerdict,    # Pydantic schema enforces {score: int, reasoning: str}
        temperature=0,
    )
    return response.choices[0].message.parsed.dict()

def faithfulness(output: str, evidence: list[str]) -> float:
    """Es et al. 2023 — fraction of output claims supported by evidence."""
    claims = extract_claims(output)
    supported = sum(1 for c in claims if any(supports(c, e) for e in evidence))
    return supported / max(len(claims), 1)
```

For judge ensembles (Path 06 Pattern 3), three judges with different rubrics run in parallel; their verdicts get combined via majority vote or weighted average; high disagreement triggers human review.

---

## See also

- 📖 [`concepts/evaluation/`](../concepts/evaluation/) — the conceptual treatment.
- 📖 [Path 06 — Evaluation & Observability](../learning-paths/06-evaluation-observability/) — the production discipline.
- 📖 [Judge ensemble pattern](../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) — the multi-judge architecture.
- 🧮 [Uncertainty and safety](./12-uncertainty-safety.md) — the calibration material in more depth.
- 📖 [Glossary — LLM-as-judge, Judge ensemble, Faithfulness, Golden dataset, Regression set, Calibration](../glossary/terms.md).

---

## Sources

- Es, S., et al. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The faithfulness, answer relevance, and context recall metrics this page uses.
- Zheng, L., et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS. Establishes LLM-as-judge as a research-grade methodology and catalogs its biases.
- TruEra. (2023+). [*TruLens documentation*](https://www.trulens.org/). Production reference for groundedness, answer relevance, and context relevance evaluation in RAG systems.
- Guo, C., et al. (2017). [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599). ICML. The ECE definition + the canonical empirical analysis of neural-network calibration.
