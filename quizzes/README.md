# 🧠 Quizzes

> 🟡 Slow-moving · ⏱ 5–10 min per quiz · 🏷 self-assessment, comprehension

Short reading-comprehension quizzes for the concepts and labs in this repo. Each quiz has 6–8 multiple-choice questions, structured YAML front-matter as the source of truth, and `<details>`-block answers underneath so you can self-test directly on GitHub.

The quizzes are **GitHub-first** by design — they work in any Markdown viewer with no JavaScript, no build step, no framework. The YAML front-matter is also designed to be consumed by a future interactive renderer (a React/Next.js sibling app), so quiz content stays version-controlled and reviewable in the main repo while presentation can evolve separately.

---

## How to use a quiz

1. Read the source page (linked at the top of each quiz).
2. Try to answer all questions *before* expanding any `<details>` blocks.
3. For each answer, click the `Show answer` block to reveal the correct choice and a one-paragraph explanation.
4. Each answer ends with a **review link** pointing to the exact section of source material the question maps to. If you got a question wrong, that's where to go.
5. Aim for ≥ 75% (6/8) before considering a topic learned.

---

## Available quizzes

### Foundations

| Quiz | Source | Length | Difficulty |
|---|---|---|---|
| 🧠 [Agents — basics](./foundations/agents-basics.md) | [`concepts/agents/what-is-an-agent.md`](../concepts/agents/what-is-an-agent.md) | 8 questions | mixed |
| 🧠 [The agent loop](./foundations/agent-loop.md) | [`concepts/agents/agent-loop.md`](../concepts/agents/agent-loop.md) | 8 questions | mixed |
| 🧠 [The ReAct pattern](./foundations/react-pattern.md) | [`concepts/agents/react-pattern.md`](../concepts/agents/react-pattern.md) | 8 questions | mixed |
| 🧠 [Tool design and selection](./foundations/tool-design-and-selection.md) | [`concepts/tools/tool-design.md`](../concepts/tools/tool-design.md) + [`tool-selection.md`](../concepts/tools/tool-selection.md) + [Lab 02](../labs/02-tool-design-and-selection/) | 8 questions | mixed |

### Agentic RAG (Path 02)

| Quiz | Source | Length | Difficulty |
|---|---|---|---|
| 🧠 [RAG fundamentals](./agentic-rag/rag-fundamentals.md) | [`concepts/rag/what-is-rag.md`](../concepts/rag/what-is-rag.md) + [`retrieval-as-a-tool.md`](../concepts/rag/retrieval-as-a-tool.md) + [`chunking-and-indexing.md`](../concepts/rag/chunking-and-indexing.md) + [Lab 06](../labs/06-agentic-rag-from-scratch/) | 8 questions | mixed |
| 🧠 [Retrieval strategies, hybrid search, and reranking](./agentic-rag/retrieval-strategies.md) | [`concepts/rag/retrieval-strategies.md`](../concepts/rag/retrieval-strategies.md) + [`hybrid-search.md`](../concepts/rag/hybrid-search.md) + [`reranking.md`](../concepts/rag/reranking.md) + [Lab 07](../labs/07-retrieval-strategies-and-reranking/) | 8 questions | mixed |
| 🧠 [Contextual retrieval, query rewriting, and retrieval failure modes](./agentic-rag/contextual-retrieval-and-query-rewriting.md) | [`concepts/rag/contextual-retrieval.md`](../concepts/rag/contextual-retrieval.md) + [`query-rewriting.md`](../concepts/rag/query-rewriting.md) + [`retrieval-failure-modes.md`](../concepts/rag/retrieval-failure-modes.md) + [Lab 08](../labs/08-contextual-retrieval-and-query-rewriting/) | 8 questions | mixed |
| 🧠 [RAG evaluation: metrics, eval sets, and answer quality](./agentic-rag/rag-evaluation.md) | [`concepts/evaluation/what-is-rag-evaluation.md`](../concepts/evaluation/what-is-rag-evaluation.md) + [`eval-set-construction.md`](../concepts/evaluation/eval-set-construction.md) + [`retrieval-metrics.md`](../concepts/evaluation/retrieval-metrics.md) + [`answer-quality-metrics.md`](../concepts/evaluation/answer-quality-metrics.md) + [Lab 09](../labs/09-evaluating-agentic-rag/) | 8 questions | mixed |

### Multi-Agent Systems (Path 03)

| Quiz | Source | Length | Difficulty |
|---|---|---|---|
| 🧠 [Multi-agent fundamentals: supervisor-worker, handoffs](./multi-agent/multi-agent-fundamentals.md) | [`concepts/multi-agent/what-is-a-multi-agent-system.md`](../concepts/multi-agent/what-is-a-multi-agent-system.md) + [`supervisor-worker-pattern.md`](../concepts/multi-agent/supervisor-worker-pattern.md) + [`handoffs-and-shared-state.md`](../concepts/multi-agent/handoffs-and-shared-state.md) + [Lab 10](../labs/10-supervisor-worker-from-scratch/) | 8 questions | mixed |
| 🧠 [Agent debate and critics](./multi-agent/agent-debate-and-critics.md) | [`concepts/multi-agent/agent-debate-and-critics.md`](../concepts/multi-agent/agent-debate-and-critics.md) + [`generator-critic-pattern.md`](../concepts/multi-agent/generator-critic-pattern.md) + [Lab 11](../labs/11-generator-critic-from-scratch/) | 8 questions | mixed |
| 🧠 [Plan-and-execute](./multi-agent/plan-and-execute.md) | [`concepts/multi-agent/plan-and-execute.md`](../concepts/multi-agent/plan-and-execute.md) + [`planner-executor-pattern.md`](../concepts/multi-agent/planner-executor-pattern.md) + [Lab 12](../labs/12-plan-and-execute-from-scratch/) | 8 questions | mixed |
| 🧠 [Multi-agent RAG](./multi-agent/multi-agent-rag.md) | [`concepts/multi-agent/multi-agent-rag.md`](../concepts/multi-agent/multi-agent-rag.md) + [`retriever-as-worker.md`](../concepts/multi-agent/retriever-as-worker.md) + [Lab 13](../labs/13-multi-agent-rag-from-scratch/) | 8 questions | mixed |
| 🧠 [Framework bridge: LangGraph multi-agent primitives](./multi-agent/framework-bridge.md) | [`concepts/multi-agent/langgraph-multi-agent.md`](../concepts/multi-agent/langgraph-multi-agent.md) + [`when-frameworks-earn-complexity.md`](../concepts/multi-agent/when-frameworks-earn-complexity.md) + [Lab 14](../labs/14-langgraph-supervisor-bridge/) + [Lab 15](../labs/15-langgraph-plan-execute-bridge/) | 8 questions | mixed |
| 🧠 [Multi-agent evaluation](./multi-agent/multi-agent-evaluation.md) | [`learning-paths/03-multi-agent-systems/`](../learning-paths/03-multi-agent-systems/) + [Lab 16](../labs/16-multi-agent-evaluation-from-scratch/) | 8 questions | mixed |

### Evaluation & Observability (Path 06)

| Quiz | Source | Length | Difficulty |
|---|---|---|---|
| 🧠 [LangSmith trace ingestion](./evaluation/langsmith-ingestion.md) | [`langsmith-tracing-shape.md`](../concepts/evaluation/langsmith-tracing-shape.md) + [`online-vs-offline-evaluation.md`](../concepts/evaluation/online-vs-offline-evaluation.md) + [Lab 17](../labs/17-langsmith-trace-ingestion/) | 8 questions | mixed |
| 🧠 [OpenTelemetry portable tracing](./evaluation/opentelemetry-portable.md) | [`opentelemetry-genai-conventions.md`](../concepts/evaluation/opentelemetry-genai-conventions.md) + [`platform-fanout-and-portability.md`](../concepts/evaluation/platform-fanout-and-portability.md) + [Lab 18](../labs/18-opentelemetry-portable-tracing/) | 8 questions | mixed |
| 🧠 [Online evaluation and tail-based sampling](./evaluation/online-evaluation.md) | [`online-evaluator-registration.md`](../concepts/evaluation/online-evaluator-registration.md) + [`tail-based-sampling.md`](../concepts/evaluation/tail-based-sampling.md) + [Lab 19](../labs/19-online-evaluation-and-sampling/) | 8 questions | mixed |
| 🧠 [Drift detection and agent-as-judge calibration](./evaluation/drift-and-calibration.md) | [`drift-detection.md`](../concepts/evaluation/drift-detection.md) + [`agent-as-judge-calibration.md`](../concepts/evaluation/agent-as-judge-calibration.md) + [Lab 20](../labs/20-drift-detection-and-calibration/) | 8 questions | mixed |
| 🧠 [Cost attribution and adaptive sampling](./evaluation/cost-and-sampling.md) | [`cost-attribution.md`](../concepts/evaluation/cost-attribution.md) + [`adaptive-sampling.md`](../concepts/evaluation/adaptive-sampling.md) + [Lab 21](../labs/21-cost-attribution-and-adaptive-sampling/) | 8 questions | mixed |
| 🧠 [Multi-turn (threaded) evaluation](./evaluation/multi-turn.md) | [`multi-turn-evaluation.md`](../concepts/evaluation/multi-turn-evaluation.md) + [`conversation-simulation.md`](../concepts/evaluation/conversation-simulation.md) + [Lab 22](../labs/22-multi-turn-evaluation/) | 8 questions | mixed |

More quizzes will land as new content does. Each new concept page or lab should ship with its quiz in the same batch.

---

## Quiz format

Quizzes are Markdown files with a YAML front-matter header. The front-matter is the source of truth — the body underneath is generated to match it, in a format that renders cleanly on GitHub. A future interactive renderer would parse the YAML and replace the body with a real component.

### Front-matter schema

```yaml
---
quiz_id: foundations-agents-basics      # unique slug across the repo
title: Agents — basics                  # human-readable title
source:                                 # source pages this quiz tests on
  - concepts/agents/what-is-an-agent.md
length_minutes: 7
difficulty: mixed                       # easy | medium | hard | mixed
passing_score: 6                        # questions correct out of total
total_questions: 8

questions:
  - id: q1                              # stable id, never renumbered after publish
    difficulty: easy                    # per-question difficulty
    question: "Question text. Use Markdown if needed."
    options:
      A: "First option"
      B: "Second option"
      C: "Third option"
      D: "Fourth option"
    answer: B                           # the correct option key
    explanation: |
      A short paragraph explaining why B is correct, and (briefly) why
      the others are not. Two or three sentences. Use Markdown.
    review:                             # where to go to review this concept
      page: concepts/agents/what-is-an-agent.md
      section: "The problem this solves"
---
```

### Body rendering convention

Below the front-matter, each question renders as:

```markdown
**Question N** *(difficulty)*

The question text.

A. First option
B. Second option
C. Third option
D. Fourth option

<details>
<summary>Show answer</summary>

**Answer: B** — short restatement.

{explanation paragraph}

→ Review: `[{page} § "{section}"]({page}#{anchor})`
</details>
```

This rendering is deterministic from the YAML, which means a contributor (or a future build step) can regenerate the body from the front-matter without losing fidelity.

---

## Contributing a quiz

Three rules:

1. **Anchor each question to a specific section of a source page.** Every question has a `review.page` and `review.section` field. If you can't point to where the answer comes from, the question doesn't belong.
2. **Distractors should be plausible.** Wrong answers should reflect *common misconceptions* of the topic, not nonsense. The point of a quiz is to surface mental-model errors, not test reading speed.
3. **No "all of the above" or "none of the above".** They reduce signal and aren't compatible with future single-select interactive rendering.

Open a [pull request](https://github.com/MHHamdan/Agentic-AI-Engineer/pulls) and tag it with `content: quiz`. A maintainer will review the question quality, source anchoring, and distractor plausibility.

---

## Why this format

A few decisions worth flagging:

- **YAML front-matter, not embedded JSON.** Easier to read in a PR diff, easier to write by hand, supported natively by every Markdown tooling we care about (GitHub renderer, MkDocs, Docusaurus, Astro, MDX).
- **`<details>` blocks for reveals.** Works in plain GitHub-flavored Markdown. No JavaScript, no plugin.
- **Stable per-question IDs.** Lets a future interactive renderer track which questions a learner has answered, persist scores, or even A/B test rewordings without losing identity.
- **Single-select only, for now.** Multi-select and short-answer types are deliberate omissions — they complicate scoring and don't currently appear often enough in our content to justify the format complexity. We'll add them when a quiz needs them.
- **Per-question difficulty.** Both for self-assessment ("I missed all the hard ones") and for future use (a renderer could spaced-repeat the harder ones).

The format is intentionally boring. Boring formats survive framework rewrites; clever formats don't.
