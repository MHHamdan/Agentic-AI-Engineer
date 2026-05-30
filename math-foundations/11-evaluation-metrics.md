# Evaluation metrics

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/evaluation/`](../concepts/evaluation/).

## Why this matters for agentic AI

You cannot ship what you cannot measure. Different metrics catch different failure modes: precision catches hallucination, recall catches missed content, faithfulness catches ungrounded claims, calibration catches overconfidence. A single number cannot summarize agent quality. Knowing which metrics to combine is the first step in building a defensible eval pipeline.

## The equation

Evaluation produces a score $\hat{s}$ for an agent output $y$ given an input $x$ (and optionally a reference $y^*$):

$$
\hat{s} = M(y, x, y^*).
$$

**Symbols:**

- $y$ - the agent's output.
- $x$ - the input (query, task, context).
- $y^*$ - an optional reference answer (golden dataset).
- $M$ - the metric function.
- $\hat{s}$ - the resulting score.

Four metric families show up across the repo.

**Classification metrics** (when output can be judged true/false against a ground truth):

$$
\text{Precision} = \frac{TP}{TP + FP}, \qquad \text{Recall} = \frac{TP}{TP + FN}, \qquad F_1 = \frac{2 \cdot P \cdot R}{P + R}.
$$

**RAG-specific metrics** (Es et al. 2023, the RAGAS framework):

$$
\text{Faithfulness} = \frac{|\text{claims}(y) \cap \text{supported}(z)|}{|\text{claims}(y)|}.
$$

In words: of the claims in the generated answer $y$, what fraction are supported by the retrieved evidence $z$?

**LLM-as-judge metrics**:

$$
\hat{s} = \pi_{\text{judge}}(y, x, \text{rubric}).
$$

A separate LLM scores the output against a rubric. Bounded by the judge's calibration.

**Calibration** (when the model emits both an answer and a confidence):

$$
\text{ECE} = \sum_{b=1}^{B} \frac{n_b}{N} \, |\text{accuracy}(b) - \text{confidence}(b)|.
$$

Expected Calibration Error: how far the model's stated confidence is from its actual accuracy, averaged over confidence bins. $B$ is the number of bins, $n_b$ is the count in bin $b$, $N$ is the total count.

## How to read these equations

**Precision and recall** answer different questions. Precision: of the things the system said were positive, how many actually were? Recall: of the things that actually were positive, how many did the system catch? $F_1$ is their harmonic mean, used when you want one number balancing both.

**Faithfulness** is a fraction. Count the atomic claims in the answer, count how many are supported by the retrieved evidence, divide. The trick is "what counts as a claim?" In practice this is done by an LLM-as-judge that decomposes the answer into claims and then checks each against the evidence.

**LLM-as-judge** is a function call. The judge is itself a policy ($\pi_{\text{judge}}$) that takes the answer, input, and a rubric, and returns a score. Calibration of the judge matters; biases of the judge transfer to the metric.

**ECE** measures the gap between stated and actual confidence. Bin predictions by stated confidence (for example, into 10 bins of width 0.1). In each bin, compare the mean stated confidence to the mean actual accuracy. The weighted average of those gaps is ECE. Lower is better; 0 means perfectly calibrated.

## Mathematical intuition

Three things to internalize.

**Different metrics catch different failure modes.** Precision catches "the agent made stuff up"; recall catches "the agent missed important content"; faithfulness catches "the agent's claims are not in the evidence." A single number cannot summarize agent quality. Production evaluation maintains a **metric portfolio** that covers complementary failure modes.

**LLM-as-judge is the practical workhorse, with a calibration caveat.** Hand-labeling is expensive; rule-based metrics miss most quality issues. LLM judges scale and catch nuance, but they have biases (verbose-answer preference, position bias, format preference) that drift over time. Production systems use **judge ensembles** to reduce variance and detect calibration shift.

**Online and offline evaluation answer different questions.** Offline (golden dataset, run on every deploy) answers "did this change break the things we know about?" Online (production traffic, sampled and judged) answers "is the system staying good in the wild?" You need both. Offline is the regression-safety net; online is the drift-detection signal.

## Where this appears in agentic systems

Four practical implications:

1. **Match the metric to the workload.** RAG -> faithfulness + answer relevance + context recall. Tool-using agents -> tool-choice correctness + argument validity + task completion. Multi-agent -> handoff success rate + per-agent contribution + final-output quality. Wrong metric leads to false confidence in a broken system.
2. **Maintain a baseline portfolio plus a regression set.** A fixed baseline (the golden dataset) plus a growing regression set (failures promoted from production). Every deploy runs both. Failures on baseline block release; failures on regression are reviewed.
3. **Track inter-judge agreement when using LLM judges.** A single LLM judge's score is one data point. Three judges with intentionally different biases give you (a) reduced variance via averaging and (b) a disagreement signal that is a separate quality indicator. High disagreement means the case is hard or the rubric is ambiguous.
4. **Calibration is upstream of HITL triggering.** If the agent's confidence is uncorrelated with its actual accuracy (poor calibration), then "route low-confidence outputs to humans" does not filter the right cases. Measuring ECE periodically catches calibration drift before it breaks the HITL pipeline.

## Code example

A simple precision/recall/F1 plus LLM-as-judge scoring loop.

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# Classification metrics.
def precision_recall_f1(predicted: set, actual: set) -> dict:
    tp = len(predicted & actual)
    fp = len(predicted - actual)
    fn = len(actual - predicted)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f1}

# LLM-as-judge.
class JudgeVerdict(BaseModel):
    score: int                    # 1 to 5
    reasoning: str

def judge(output: str, query: str, rubric: str) -> JudgeVerdict:
    """pi_judge(output, query, rubric) -> {score, reasoning}."""
    prompt = (
        f"Rubric:\n{rubric}\n\n"
        f"Query: {query}\n"
        f"Answer: {output}\n\n"
        "Score this answer 1 to 5 against the rubric. Give brief reasoning."
    )
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict but fair grader."},
            {"role": "user", "content": prompt},
        ],
        response_format=JudgeVerdict,
        temperature=0,
    )
    return response.choices[0].message.parsed

# Example.
predicted_entities = {"Paris", "France", "Eiffel Tower"}
actual_entities    = {"Paris", "France", "Seine"}
print(precision_recall_f1(predicted_entities, actual_entities))
# -> {'precision': 0.667, 'recall': 0.667, 'f1': 0.667}

verdict = judge(
    output="Paris is the capital of France.",
    query="What is the capital of France?",
    rubric="Award 5 for a correct, concise, citable answer. Penalize hedging.",
)
print(verdict.score, verdict.reasoning)
```

For judge ensembles, run three judges with different rubrics in parallel; combine via majority vote or weighted average; flag high-disagreement cases for human review.

## Common mistakes

- **Using just accuracy on imbalanced workloads.** If 95% of queries have no tool calls and you classify "no tool call" as the default, you get 95% accuracy with zero useful behavior. Precision/recall/F1 on the positive class is the right framing.
- **Trusting a single judge.** LLM judges have biases (longer answers tend to win; the same model judging its own output tends to be lenient). Use an ensemble or a different model family as judge.
- **Forgetting to version the rubric.** If the rubric changes, scores across time are not comparable. Treat rubrics like code: versioned, tested, deployed.
- **Computing ECE on too few bins or too few samples.** ECE needs hundreds of predictions per bin to be stable. With small samples, use reliability diagrams as a qualitative tool instead of a single ECE number.
- **Evaluating only the final output.** For multi-agent or multi-step systems, per-step metrics (tool-choice correctness, handoff success) catch issues that final-output evals miss.

## Repo cross-references

- [`concepts/evaluation/`](../concepts/evaluation/) - the conceptual treatment.
- [`learning-paths/06-evaluation-observability/`](../learning-paths/06-evaluation-observability/) - the production discipline.
- [`learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md`](../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) - the multi-judge architecture.

## Related pages

- [03 - RAG formulation](./03-rag-formulation.md) - what faithfulness measures.
- [12 - Uncertainty and safety](./12-uncertainty-safety.md) - the calibration material in more depth.
- [Glossary: LLM-as-judge, Judge ensemble, Faithfulness, Golden dataset, Regression set, Calibration](../glossary/terms.md) - short definitions.

## References

- Es, S., et al. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The faithfulness, answer relevance, and context recall metrics this page uses.
- Zheng, L., et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS 2023. Establishes LLM-as-judge as a research-grade methodology and catalogs its biases.
- Guo, C., et al. (2017). [*On Calibration of Modern Neural Networks*](https://arxiv.org/abs/1706.04599). ICML 2017. The ECE definition and the canonical empirical analysis of neural-network calibration.
- TruEra. [*TruLens documentation*](https://www.trulens.org/). Production reference for groundedness, answer relevance, and context relevance evaluation in RAG systems. Needs manual verification as the project evolves.
- Manning, C., Raghavan, P., and Schutze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press. [Free online](https://nlp.stanford.edu/IR-book/). Standard reference for precision, recall, F1, and related IR metrics.
