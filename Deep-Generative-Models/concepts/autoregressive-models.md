# Autoregressive models

> Concept note. ~8 min. Builds on [foundations](./foundations.md).

Autoregressive models take the most direct route to an exact likelihood: apply the chain rule of probability and model the joint distribution as a product of conditionals, one variable at a time.

## The idea: factorize by the chain rule

For a data vector $x = (x_1, \dots, x_n)$, the chain rule gives, exactly and without approximation,

$$
p(x) = \prod_{i=1}^{n} p(x_i \mid x_{<i}),
$$

where $x_{<i}$ is everything before $x_i$ in a chosen ordering. Each conditional is a neural network that reads the previous variables and outputs the distribution of the next — a categorical for discrete data (pixels, tokens), a mixture for continuous. Because the factorization is exact, the model computes exact likelihoods and trains by plain maximum likelihood, which not every family can do.

The one imposition is an **ordering**: raster scan (top-to-bottom, left-to-right) for image pixels, time order for audio and text. The model's conditioning is strict — each variable depends only on those before it.

## The line of milestones

The principle is old; the architectures made it work at scale. Fully Visible Sigmoid Belief Networks expressed the conditionals with simple sigmoids; the Neural Autoregressive Density Estimator (NADE) added weight sharing for efficiency. The breakthrough for images was **PixelRNN** and **PixelCNN**, which modeled pixel dependencies — the recurrent version sequentially, the convolutional version with **masked convolutions** that preserve causality while training in parallel. **WaveNet** brought the idea to raw audio with dilated causal convolutions that reach far back in time. Then **Transformers** with masked self-attention — the architecture behind **GPT** — made autoregressive language modeling the dominant paradigm in NLP.

## The tradeoff

Autoregressive models sit firmly in the "exact likelihood" corner of the [trilemma](./foundations.md), and they produce high-quality samples. The price is **sequential sampling**: generating $n$ variables takes $n$ forward passes, because each depends on the last. Training parallelizes (all conditionals are known from the data), but sampling does not, which makes generation slow for long sequences or high-resolution images.

## What to remember

- Autoregressive models factorize $p(x)$ into a product of conditionals via the chain rule — exact, MLE-trainable.
- Masked convolutions (PixelCNN), dilated convolutions (WaveNet), and masked self-attention (GPT) are how the conditionals scale.
- Exact likelihood and strong samples, but sampling is inherently sequential and slow.

## References

- Larochelle, H. & Murray, I. (2011). *The Neural Autoregressive Distribution Estimator (NADE).*
- van den Oord, A., et al. (2016). *Pixel Recurrent Neural Networks.* arXiv:1601.06759.
- van den Oord, A., et al. (2016). *WaveNet.* arXiv:1609.03499.
- Vaswani, A., et al. (2017). *Attention Is All You Need.* arXiv:1706.03762. See [`../references/references.md`](../references/references.md).
