# Recipe: Corrective RAG (CRAG)

> 🟡 Slow-moving · ⏱ ~7 min · Problem: retrieval sometimes returns irrelevant chunks and the model trusts them anyway.

## Problem

Static RAG has no way to notice that retrieval failed. When the corpus does not contain the answer, or retrieval surfaces tangentially-related junk, the model dutifully grounds its answer in the wrong context and produces a confident, wrong, "cited" response. You need a step that grades retrieval quality before generation and takes corrective action when it is poor.

## Solution

Insert a lightweight retrieval evaluator between retrieval and generation (the core idea of CRAG, Yan et al. 2024). It classifies retrieval as `correct`, `ambiguous`, or `incorrect`, and routes accordingly:

- `correct` -> generate from the retrieved context.
- `incorrect` -> discard it; fall back to a web search (or abstain if no fallback).
- `ambiguous` -> combine retrieved context with the fallback.

```python
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

client = OpenAI()

class RetrievalGrade(BaseModel):
    verdict: Literal["correct", "ambiguous", "incorrect"]
    reasoning: str

def grade_retrieval(query: str, chunks: list[str]) -> RetrievalGrade:
    """The CRAG retrieval evaluator. One cheap model call."""
    evidence = "\n".join(f"- {c}" for c in chunks)
    prompt = (
        f"Does the retrieved evidence contain the information needed to answer "
        f"the query?\n\nQuery: {query}\n\nEvidence:\n{evidence}\n\n"
        f"Verdict: 'correct' if the evidence fully answers it, 'incorrect' if it "
        f"is unrelated or missing the key fact, 'ambiguous' if partial."
    )
    r = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format=RetrievalGrade,
        temperature=0,
    )
    return r.choices[0].message.parsed

def web_search_fallback(query: str) -> list[str]:
    """Stand-in for a real web-search tool. Replace with your search API."""
    # In production: call a search tool and return snippets.
    return [f"(web fallback for: {query}) - replace with real search results"]

def generate(query: str, chunks: list[str]) -> str:
    evidence = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(chunks))
    prompt = (
        f"Answer using only the evidence. Cite as [n]. If the evidence is "
        f"insufficient, say so explicitly.\n\nEvidence:\n{evidence}\n\nQuestion: {query}"
    )
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return r.choices[0].message.content

def corrective_rag(query: str, retrieved: list[str]) -> str:
    grade = grade_retrieval(query, retrieved)

    if grade.verdict == "correct":
        context = retrieved
    elif grade.verdict == "incorrect":
        context = web_search_fallback(query)            # discard + fall back
    else:  # ambiguous
        context = retrieved + web_search_fallback(query)  # combine

    return generate(query, context)

# Example: retrieval missed the answer.
retrieved = ["The office is open Monday to Friday, 9am to 5pm."]
print(corrective_rag("What is the refund policy?", retrieved))
# The grader returns 'incorrect' (office hours do not answer a refund question),
# so the system falls back rather than fabricating a refund policy from hours.
```

## Why each piece is there

- **The grader is one cheap call.** CRAG is among the cheapest SOTA patterns to adopt because it adds a single classification step, not a full extra retrieval loop. Use a small fast model for the grader.
- **Structured output** (`RetrievalGrade`) forces a clean three-way verdict instead of free text you have to parse.
- **The three-way split matters.** A binary correct/incorrect split throws away the common "partially relevant" case where combining sources is better than choosing one.
- **The fallback is pluggable.** Web search is the canonical CRAG fallback, but the corrective action can be anything: a different index, a broader query, or abstention.

## Calibrate the grader

The grader is itself a model call and can be wrong. Two failure directions:

- **Too strict** (flags good retrieval as incorrect) -> unnecessary fallbacks, higher latency and cost.
- **Too lax** (passes bad retrieval as correct) -> the exact failure CRAG is meant to prevent.

Measure grader accuracy against your eval set as its own number. The whole point is moot if the grader is miscalibrated. See [`concepts/evaluation/agent-as-judge-calibration.md`](../../concepts/evaluation/agent-as-judge-calibration.md).

## When to use it

CRAG earns its cost when your corpus is incomplete or goes stale and you have a fallback available. If your corpus is complete and curated, the grader mostly returns `correct` and you are paying for a step that rarely fires. Measure the verdict distribution; if it is 95% `correct`, CRAG is not buying you much.

## References

- Yan, S., et al. (2024). [*Corrective Retrieval Augmented Generation*](https://arxiv.org/abs/2401.15884). The CRAG method.
- [`concepts/rag/sota-rag-patterns.md`](../../concepts/rag/sota-rag-patterns.md) - CRAG in the context of the full pattern landscape.
- [`concepts/rag/retrieval-failure-modes.md`](../../concepts/rag/retrieval-failure-modes.md) - the failure modes CRAG catches.
