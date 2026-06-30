# Foundations of generative modeling

> Concept note. ~10 min. Math: [`../math/objectives-and-transformations.md`](../math/objectives-and-transformations.md).

A generative model learns the probability distribution $p(x)$ behind a dataset — of images, text, audio — well enough to act on it. The motivation is the one captured in the line often attributed to Feynman, "what I cannot create, I do not understand": a model that can synthesize convincing data has, in some sense, internalized its structure.

## Three objectives

Generative models are asked to do three different things, and a given family may be good at some and not others:

- **Sampling (generation).** Produce new instances that resemble the training data but are not copies — a new image, a coherent paragraph, a fresh audio clip.
- **Density estimation.** Assign a probability $p(x)$ to a given point. Low-probability points are unusual, which makes this directly useful for anomaly detection.
- **Representation learning.** In learning to generate, many models discover a compact latent code that captures the salient factors of the data, useful for downstream classification or clustering without labels.

## Two axes that classify the families

Almost every model family can be placed by answering two questions.

**Explicit or implicit density?** An **explicit** model defines a mathematical form for $p(x; \theta)$ you can evaluate — autoregressive models and normalizing flows do this, with tractable likelihoods. An **implicit** model never writes $p(x)$ down; it defines a sampling process (a network that maps noise to data) and you can draw from it but not score it. The generative adversarial network is the canonical implicit model.

**Likelihood-based or likelihood-free?** **Likelihood-based** models train by maximizing the likelihood of the data, or a tractable bound on it — autoregressive models, flows, and VAEs. **Likelihood-free** models avoid computing likelihood and train by other means: an adversarial loss (GANs), or score matching and contrastive divergence (energy-based models).

## Latent variables

Many families assume the data is generated from an unobserved **latent variable** $z$: draw $z$ from a simple prior $p(z)$ (often a standard Gaussian), then generate $x$ from $p(x \mid z)$. The latent is a compact set of hidden factors — pose, style, content — and recovering it (inferring the posterior $p(z \mid x)$) is what makes representation learning possible. VAEs are built entirely around this idea.

## The training principle: MLE is KL minimization

The default way to fit an explicit model is **maximum likelihood estimation** — choose $\theta$ to maximize the likelihood of the training data under $p(x; \theta)$. This is equivalent to minimizing the KL divergence from the data distribution to the model — so MLE is, precisely, pulling the model toward the data. The [math page](../math/objectives-and-transformations.md) makes the equivalence explicit.

## Three challenges, and the trilemma

The reason there are many families and not one is that high-dimensional $p(x)$ is hard along three axes at once:

- **Representation** — the joint distribution over many variables is astronomically large (every $28\times28$ binary image is one of $2^{784}$ configurations), so you cannot tabulate it. Families impose structure: autoregressive factorization, or a low-dimensional latent manifold.
- **Learning** — you only have a finite sample from the true $p_{\text{data}}$; you must pick a divergence and optimize the model to minimize it.
- **Inference** — for latent-variable models, recovering $p(z \mid x)$ is its own hard, often intractable, problem.

These pressures produce the **generative trilemma**: high sample quality, exact tractable likelihood, and fast stable training/sampling — pick the corner you need, because no family has all three without compromise. The rest of this module is the families, read as different answers to that trilemma.

## What to remember

- Generative models learn $p(x)$ to sample, score, and represent data.
- Classify a family by explicit-vs-implicit density and likelihood-based-vs-free training.
- MLE equals minimizing KL to the data; the generative trilemma (quality, exact likelihood, fast/stable) explains why no single family wins everywhere.

## References

- Goodfellow, I., Bengio, Y., Courville, A. (2016). *Deep Learning*, ch. 20 (generative models). See [`../references/references.md`](../references/references.md).
