# Answer quality metrics

> 🟢 Stable · ⏱ ~11 min read · 🏷 rag, evaluation, generation, metrics

## TL;DR

Once retrieval has surfaced chunks, the *generation* step turns them into an answer. Whether that answer is good depends on five separate properties:

- **Faithfulness** — does every claim in the answer follow from the chunks?
- **Groundedness** — does every claim trace to a specific chunk citation?
- **Citation accuracy** — do the cited chunks actually support the cited claim?
- **Answer relevance** — does the answer address the user's actual question?
- **Refusal quality** — when the corpus can't answer, does the system refuse honestly?

These can't usually be checked mechanically (the answer is free text). Two approaches work: **rule-based checks** for narrow cases, and **LLM-as-judge** (Zheng et al. NeurIPS 2023) for the rest. Each has documented failure modes — position bias, verbosity bias, self-enhancement bias — that you need to design around.

This page covers each metric, the rule-based vs LLM-as-judge tradeoff, and which production frameworks (RAGAS, TruLens, DeepEval) wrap what. Path 02 builds from scratch; [Path 06](../../learning-paths/) covers the frameworks.

---

## Why this is harder than retrieval evaluation

Retrieval evaluation is comparatively easy: ranked list vs. set of relevant chunks, compute a number. Generation evaluation has no such structure. The answer is free-form text; the chunks are free-form text; the question of whether one supports the other requires *understanding*.

Three implications:

1. **Pure mechanical scoring is limited.** You can check whether the answer cites *any* chunk, but not whether the citation is accurate. You can check string overlap, but a paraphrase fails string overlap while being correct.
2. **LLM-as-judge is the standard** for everything mechanical scoring misses. A strong LLM compares answer to chunks and scores each property.
3. **All of this is noisy.** Repeated runs of the same judge on the same answer can produce different scores. You have to design around the noise.

## Faithfulness

**Does every claim in the answer follow from the chunks?**

A faithful answer can say only what the chunks support. If the chunks say "the agent loop has four phases" and the answer says "the agent loop has four phases: perceive, reason, act, observe", that's faithful (assuming the chunks list the phases). If the answer adds "this is the same approach used in OpenAI's Swarm framework" and the chunks don't mention Swarm, that's *unfaithful* — the model hallucinated a connection.

This is closely related to **FActScore** (Min et al., EMNLP 2023): decompose the answer into atomic claims; for each claim, check whether the chunks support it; faithfulness = supported / total.

### Rule-based approach

For factoid-style answers where claims are short and copy-from-source:

```python
def faithfulness_substring(answer: str, chunks: list[str]) -> float:
    """Fraction of answer sentences whose key noun phrases appear in some chunk."""
    sentences = split_sentences(answer)
    if not sentences:
        return 0.0
    chunks_joined = " ".join(chunks).lower()
    hits = 0
    for sent in sentences:
        # Extract content words (proper nouns, numbers, technical terms)
        terms = extract_key_terms(sent)
        if all(t.lower() in chunks_joined for t in terms):
            hits += 1
    return hits / len(sentences)
```

This works for narrow domains (technical Q&A, factual lookups) where unfaithful claims tend to introduce unfamiliar terms. It fails on paraphrasing — a faithful sentence in different vocabulary scores 0.

### LLM-as-judge approach

Ask a strong LLM to score each answer against its chunks:

```text
PROMPT:
You are evaluating whether an answer is supported by source chunks.

CHUNKS:
{chunks}

ANSWER:
{answer}

For each claim in the answer, mark whether it is supported by the chunks.
A claim is supported if its substance is stated or directly implied in the chunks.
A claim is unsupported if it adds information not in the chunks, even if true.

Return a number between 0 (no claims supported) and 1 (all claims supported).
```

This handles paraphrasing well, generalizes across domains, and is what RAGAS and TruLens do under the hood. But it has biases (next section) and costs one LLM call per evaluation.

## Groundedness

**Does every claim in the answer have a citation, regardless of whether the citation is correct?**

Distinct from faithfulness:

- **Faithfulness** = "the claim is supported by the chunks."
- **Groundedness** = "the answer explicitly links the claim to a chunk."

An ungrounded answer might be perfectly faithful — every claim *is* supported by the chunks — but doesn't say *which* chunk supports which claim. The reader has to take it on faith.

For agentic RAG systems where the agent reads specific chunks (Lab 06's `read_chunk` pattern), groundedness is straightforward: the agent's citation log records which chunks were read; if a claim doesn't appear in any read chunk, it's ungrounded.

```python
def groundedness(answer: str, citations: list[dict]) -> float:
    """Fraction of answer sentences that overlap with at least one cited chunk."""
    sentences = split_sentences(answer)
    if not sentences:
        return 0.0
    cited_text = " ".join(c["text"] for c in citations).lower()
    grounded = sum(1 for s in sentences if has_overlap(s, cited_text))
    return grounded / len(sentences)
```

The Lab 06/07/08 agent already provides the structure for this — it tracks citations as the loop runs. Groundedness becomes a computable property of the agent's output.

## Citation accuracy

**Do the cited chunks actually support the cited claim?**

A claim might be cited (good for groundedness) but cited *to the wrong chunk* (bad for accuracy). The reader looks at the citation, expects supporting evidence, finds something else.

Citation accuracy is hardest to check mechanically. The rule-based approximation:

```python
def citation_accuracy(claim: str, cited_chunks: list[str]) -> float:
    """Does the claim's content appear in the cited chunks specifically?"""
    claim_terms = extract_key_terms(claim)
    cited_text = " ".join(cited_chunks).lower()
    if not claim_terms:
        return 0.0
    return sum(1 for t in claim_terms if t.lower() in cited_text) / len(claim_terms)
```

For text-overlap-friendly domains this works. For paraphrased domains, LLM-as-judge is the only option.

The serious version of citation accuracy involves *atomic-claim decomposition* (FActScore-style): split the answer into claims, identify the citation attached to each, ask the judge whether the cited chunk supports that specific claim. Expensive but reliable.

## Answer relevance

**Does the answer address the user's actual question?**

Independent of whether the answer is faithful or grounded. A perfectly faithful answer to a question the user *didn't ask* is irrelevant.

Common failure: the user asks "how does the agent handle a tool timeout?" and the answer is a comprehensive overview of the agent loop, faithfully sourced, but never specifically discusses timeouts. Faithfulness = 1.0. Relevance = 0.3.

Rule-based check: lexical overlap between the query and the answer (TF-IDF cosine, sentence-transformer cosine). Crude but catches the worst cases.

LLM-as-judge prompt:

```text
PROMPT:
Did the following answer address the user's question?

QUESTION: {query}
ANSWER: {answer}

Return a number between 0 (answer is unrelated) and 1 (answer fully addresses
the question).
```

RAGAS calls this `answer_relevancy` and computes it with an interesting twist: generate hypothetical questions *that the answer answers*, embed them, compare to the original query's embedding. Strong proxy without needing an LLM judge per query.

## Refusal quality

**When the corpus can't answer, does the system refuse honestly?**

This is the metric that most teams forget to track, and the one [failure mode 8](../rag/retrieval-failure-modes.md#failure-mode-8-the-corpus-doesnt-contain-the-answer) lives or dies on.

For each off-corpus query in your eval set, the system should produce either:
- An explicit refusal ("I can't find information about that in the corpus").
- An empty-status result that the agent loop handles by refusing.
- A clearly-hedged answer that signals low confidence.

What it should *not* produce: a confident-sounding answer with no actual grounding.

```python
def refusal_quality(query: str, answer: str, expected_refusal: bool) -> float:
    """Returns 1.0 if behavior matches expectation, 0.0 otherwise."""
    refused = looks_like_refusal(answer)
    if expected_refusal:
        return 1.0 if refused else 0.0  # FN: should have refused, didn't
    else:
        return 1.0 if not refused else 0.0  # FP: refused when corpus had answer


def looks_like_refusal(answer: str) -> bool:
    """Heuristic: short answer with refusal language."""
    refusal_signals = [
        "i don't have information", "the corpus doesn't",
        "i can't find", "not in the provided", "unable to answer",
    ]
    a = answer.lower()
    return any(s in a for s in refusal_signals) and len(answer) < 300
```

This is a binary metric per query; averaged across off-corpus queries, it's your refusal rate. Worth tracking separately from faithfulness — a system can be 100% faithful on on-corpus queries while *also* being 0% refusal-quality on off-corpus queries because it just makes things up.

## Rule-based vs LLM-as-judge

When to reach for each:

| Rule-based | LLM-as-judge |
|---|---|
| Cheap (no API calls) | Expensive (one call per evaluation, sometimes more) |
| Deterministic, reproducible | Noisy; same input → different scores across runs |
| Limited to surface signals (string overlap, lexical match) | Handles paraphrase, inference, implication |
| Fails on paraphrased answers | Recommended for substance-of-claim checks |
| Good for CI gates (run on every commit) | Good for periodic deeper evaluation |
| Hand-coded; transparent | Black-box; has documented biases |

The pragmatic stance most teams converge on:

1. **Rule-based for everything you can.** Cheap, fast, reproducible.
2. **LLM-as-judge for the substance-of-claim checks** (faithfulness, citation accuracy) where rules fail.
3. **Sample, don't blanket.** Run LLM-as-judge on a sample of queries (10-50) per change, not on every query in CI.

Lab 09 demonstrates both. Most metrics use rule-based scoring; an optional cell shows LLM-as-judge on a subset.

## LLM-as-judge biases (Zheng et al. 2023)

The canonical paper (Zheng et al., NeurIPS 2023) documents three biases that LLM judges exhibit:

1. **Position bias.** When comparing two answers side-by-side, the LLM judge tends to prefer the *first* one. Mitigation: present pairs in both orders and average.
2. **Verbosity bias.** Longer, more detailed answers tend to score higher even when they contain incorrect content. Mitigation: include length in your evaluation criteria explicitly.
3. **Self-enhancement bias.** An LLM judge tends to prefer answers generated by *itself* (or its own family) over answers from other models. Mitigation: use a judge from a different model family than the system being evaluated.

A fourth bias worth knowing about, observed in subsequent work:

4. **Recency bias** in pointwise scoring. When asked to score 10 answers in sequence, the LLM judge's scores often drift over the course of the session. Mitigation: randomize evaluation order; use a fresh context for each evaluation.

Plus the obvious limitation:

- **Limited reasoning ability.** The judge is just an LLM. It can miss subtle errors that careful human evaluation would catch. Don't treat LLM-as-judge scores as ground truth — treat them as a noisy signal that, in aggregate, correlates with ground truth.

The paper's headline finding: GPT-4 as judge agrees with human raters >80% of the time on chatbot quality ratings — the same level of agreement that humans show with each other. For RAG faithfulness specifically, agreement tends to be similar but is dataset-dependent.

## Production frameworks (mention only)

The RAG evaluation framework landscape as of 2026 is mature. The three most commonly used:

- **RAGAS** ([docs.ragas.io](https://docs.ragas.io)) — Reference-free LLM-as-judge framework. Core metrics: `context_precision`, `faithfulness`, `answer_relevancy`, `context_recall`. Strong fast-iteration ergonomics; LangChain integration. The associated paper (Es et al., arXiv:2309.15217) introduced "RAG evaluation" as a structured discipline.
- **TruLens** ([trulens.org](https://www.trulens.org)) — Couples evaluation with tracing/observability; built around the "RAG Triad" of context relevance, groundedness, answer relevance. Now Snowflake-integrated; good production tracing story.
- **DeepEval** ([docs.confident-ai.com](https://docs.confident-ai.com)) — Broadest metric library (~50+ metrics across RAG/agents/multi-turn/MCP/safety/image); native Pytest integration making it the easiest framework to drop into CI/CD.

A reasonable adoption pattern many teams converge on:

- RAGAS during development for fast iteration on RAG-specific metrics.
- DeepEval as a CI gate (because Pytest integration is clean).
- TruLens (or LangSmith / LangFuse / Phoenix) for production observability.

Path 02 deliberately doesn't use any of these — the goal of Lab 09 is to show what they *wrap*, so adopting them later is informed rather than mysterious. [Path 06](../../learning-paths/) is where the framework treatment will live.

## Cost calibration

LLM-as-judge is the big cost. Rough numbers as of 2026 (Claude Sonnet pricing):

- One faithfulness check: ~500 tokens in, ~50 out → ~$0.0025
- One full RAGAS evaluation (4 metrics, one call each): ~$0.01
- A 50-question eval set with full LLM-as-judge: ~$0.50 per evaluation run

This is small per-run but compounds:

- CI on every PR with LLM-as-judge: ~$10-50/month for an active project.
- Production sampling at 1% with hourly evaluation: ~$50-500/month.

Mitigations: cache evaluations of unchanged answers; use a cheaper judge (Haiku is often adequate for narrow metrics); skip LLM-as-judge entirely for queries that pass rule-based checks.

## What evaluation can't measure

Three categories worth flagging:

- **Whether the corpus is correct.** Garbage corpus → garbage faithful answers. Faithfulness is high; the system is still wrong. The fix is content, not evaluation.
- **Whether the user is satisfied.** A faithful, grounded, relevant answer can still feel unhelpful. User satisfaction signals (thumbs up/down, follow-up questions, abandonment) live in product analytics, not in eval sets.
- **Long-term effects.** A system that's faithful but unhelpful gets abandoned. Aggregate retention vs. metrics-on-eval-set is a Path 06 concern.

## See also

- 📖 [What is RAG evaluation?](./what-is-rag-evaluation.md) — the orientation; this page is the second half of that frame.
- 📖 [Eval set construction](./eval-set-construction.md) — where the queries that get scored here come from.
- 📖 [Retrieval metrics](./retrieval-metrics.md) — the other half of "evaluation."
- 📖 [Retrieval failure modes](../rag/retrieval-failure-modes.md) — failure mode 7 (good retrieval, bad synthesis) is what answer-quality metrics catch.
- 🧪 [Lab 09](../../labs/09-evaluating-agentic-rag/) — implements rule-based versions of all these metrics + optional LLM-as-judge.

## References

- Zheng, L. et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track. The canonical LLM-as-judge paper; ~80% agreement with humans; documents position, verbosity, and self-enhancement biases.
- Min, S. et al. (2023). [*FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*](https://arxiv.org/abs/2305.14251). EMNLP 2023. The atomic-claim-decomposition approach to faithfulness; foundational for the RAG-evaluation metrics that came after.
- Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). [*RAGAS: Automated Evaluation of Retrieval Augmented Generation*](https://arxiv.org/abs/2309.15217). The framework paper; introduces `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall` as a standardized metric set.
- Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2023). [*ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*](https://arxiv.org/abs/2311.09476). NAACL 2024. Trains a small classifier for RAG evaluation, calibrated against a human-labeled subset; cheaper than LLM-as-judge with comparable agreement.
- Liu, Y. et al. (2024). [*G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*](https://arxiv.org/abs/2303.16634). EMNLP 2023. The standard LLM-as-judge protocol for text generation; chain-of-thought scoring template that many frameworks adopted.
- Chiang, C.-H., & Lee, H. (2023). [*Can Large Language Models Be an Alternative to Human Evaluations?*](https://arxiv.org/abs/2305.01937). ACL 2023. Empirical comparison; gives the conditions under which LLM evaluation is reliable.
