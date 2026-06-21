# Decoding and sampling

> Concept note. ~7 min. Builds on [tokens and embeddings](./tokens-and-embeddings.md).

A model does not output text. At each step it outputs a probability distribution over the entire token vocabulary — a score (logit) for every possible next token, turned into probabilities by a softmax. **Decoding** is the policy that picks the next token from that distribution, and it controls how varied, how safe, and how reproducible the output is. The same model and the same prompt can produce very different text depending only on these settings.

## The main controls

- **Greedy / argmax.** Always take the most probable token. Reproducible and safe, but flat and repetitive; it can also paint itself into a corner by committing early.
- **Temperature.** Scales the logits before the softmax. Below 1 sharpens the distribution (more deterministic, more conservative); above 1 flattens it (more varied, more risk of nonsense); at 0 it reduces to greedy.
- **Top-k.** Restrict sampling to the k highest-probability tokens, then sample among them — a cap on how far down the tail the model can reach.
- **Top-p (nucleus).** Restrict to the smallest set of tokens whose probabilities sum to p, then sample. Unlike top-k, the set size adapts to how confident the model is at that step.

Top-p and temperature are the two you tune most often: temperature sets how adventurous the model is, top-p caps how unlikely a token it may still pick.

## Determinism, and why you rarely get it

Two requests with sampling enabled will differ, by design. Even with temperature 0, exact reproducibility is not guaranteed across hardware, model versions, or batching, because floating-point reductions are not perfectly associative and providers change models underneath you. So treat "deterministic output" as a goal you approach (low or zero temperature, pinned versions, seeds where offered), not a guarantee you can assume — and never build a test that asserts an exact long generation will reproduce byte-for-byte.

## Choosing settings

Match the setting to the task. Factual extraction, structured output, and anything you will parse want low temperature and tight top-p. Brainstorming, drafting, and creative variation want more. When you need several distinct options, sample several times at moderate temperature rather than once — one call cannot give you diversity.

## What to remember

- The model emits a distribution; decoding picks from it, and that choice — not just the model — shapes the output.
- Temperature sets adventurousness; top-p and top-k cap how far into the tail it can reach.
- Exact reproducibility is not free even at temperature 0; design tests and systems accordingly.
