# Fine-tuning vs. retrieval

> Concept note. ~8 min. Builds on [hallucination and cutoff](./hallucination-and-cutoff.md); leads into [RAG](../rag/).

When a base model is not enough, there are two broad ways to add what is missing, and they solve different problems. Choosing the wrong one is a common and expensive mistake, so it is worth being precise about what each is for.

## What each one changes

**Fine-tuning** continues training the model on your data, adjusting its weights. It changes *behavior*: tone, format, style, adherence to a schema, and skill at a narrow task. It bakes the change into the model, so it costs compute and ML expertise up front and produces a snapshot — the moment your underlying facts change, a fine-tuned model is stale again, because the new facts are not in its weights.

**Retrieval** (RAG) leaves the model's weights alone and instead fetches relevant context at query time, placing it in the prompt. It changes *knowledge*: the model answers from documents you supply, which can be current, private, and citable. Update the documents and the next answer reflects them, with no retraining.

## A decision guide

Reach for **retrieval** when the gap is knowledge:

- the answer depends on facts that change (prices, policies, inventory, news),
- the answer lives in private or proprietary documents,
- you need citations and traceability to a source,
- the corpus is large or updated often.

Reach for **fine-tuning** when the gap is behavior:

- you need a consistent format, tone, or structured output the base model resists,
- you are teaching a narrow skill or domain style rather than facts,
- you want to shorten prompts by internalizing instructions,
- latency or cost rules out sending long instructions every call.

The two are not rivals; production systems often do both — fine-tune for how the model should behave, retrieve for what it should know. And reach for neither first: a clear prompt, good examples, and the right decoding settings solve many problems without either.

## The cost and staleness lens

The cleanest way to decide is to ask what goes stale. Fine-tuning bakes knowledge in, so knowledge that changes makes it stale and forces retraining; retrieval keeps knowledge external, so it stays fresh by editing a store. Behavior, by contrast, is stable — once you want a certain format, you want it indefinitely — which is exactly the kind of thing worth training in. Match the method to whether the thing you are adding is stable (train it) or changing (retrieve it).

## What to remember

- Fine-tuning changes behavior and bakes it in; retrieval changes knowledge and keeps it external and fresh.
- Use retrieval for facts that are current, private, or must be cited; use fine-tuning for stable format, tone, and narrow skills.
- They compose, and neither should be the first move before good prompting.

## References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* arXiv:2005.11401. See [`../../references/references.md`](../../references/references.md).
