# Hallucination and knowledge cutoff

> Concept note. ~8 min. Leads into [fine-tuning vs. retrieval](./fine-tuning-vs-retrieval.md) and [RAG](../rag/).

Two related limits explain a large share of LLM failures in production, and both follow from the same fact: a model's knowledge lives in its parameters, fixed when training ended.

## Knowledge cutoff

Everything a base model "knows" was compressed into its weights during training, up to a cutoff date. After that date it is blind: it does not know about a release from last week, this morning's policy change, or any private document it was never trained on. This is not a bug to be patched in the model — it is structural. A model asked about events past its cutoff, or about data it never saw, has no parameter to retrieve the answer from.

## Hallucination

A **hallucination** is fluent, confident output that is not grounded in fact. It happens because the model is trained to produce probable continuations, not to verify them; when it lacks the knowledge, the most probable continuation is often a plausible-sounding fabrication rather than an admission of ignorance. The model does not represent "I don't know" as readily as it represents a confident guess. Reported rates vary widely by task — low for simple, well-supported summarization, much higher for open-ended questions over unfamiliar material — but the failure mode is always available.

The dangerous property is the mismatch between confidence and correctness: a hallucinated answer reads exactly like a correct one. That is why you cannot rely on the model's tone as a signal, and why systems that matter need an external check.

## Mitigations

No single fix removes the problem, but several reduce it sharply:

- **Retrieval (RAG).** Supply the relevant facts in the prompt at query time so the answer is grounded in current, citable sources rather than parametric memory. This directly addresses both the cutoff (fetch fresh data) and hallucination (ground the claim). See [RAG](../rag/).
- **Grounding in tool results.** Have the model act and observe — call a tool, run code, query a system of record — and condition on real outputs instead of guessing. The authoritative source wins over stored belief.
- **Attribution and verification.** Require citations and check that each claim is supported by what was retrieved; reject or flag unsupported sentences.
- **Abstention.** Make "I don't know" or "I need to look that up" an acceptable, rewarded output, so the model is not forced to fabricate.

The throughline: do not ask a frozen model to be a database. Give it the facts, or let it fetch them, and verify what it writes.

## What to remember

- A model's knowledge is frozen at its cutoff; it cannot know recent or private facts on its own.
- Hallucination is confident, ungrounded output, and it looks identical to a correct answer.
- The fixes are external: retrieve the facts, ground in tool results, require citations, and allow abstention.

## References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* arXiv:2005.11401. See [`../../references/references.md`](../../references/references.md).
