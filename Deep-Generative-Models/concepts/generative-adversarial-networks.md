# Generative adversarial networks

> Concept note. ~8 min. Builds on [foundations](./foundations.md).

Generative adversarial networks (GANs) take the implicit, likelihood-free route. They never write $p(x)$ down. Instead, two networks compete, and the competition itself drives one of them to produce realistic data.

## The idea: a two-player game

A **generator** $G$ maps noise $z$ to data; a **discriminator** $D$ tries to tell real data from the generator's fakes. They train against each other in a minimax game: $D$ learns to classify real vs. fake, while $G$ learns to fool $D$. As $D$ gets sharper, $G$ is pushed to make its samples more realistic, and at the ideal equilibrium the generator's distribution matches the data and the discriminator can do no better than chance. $G$ never sees the data directly — it is trained only through $D$'s gradient signal, with no likelihood anywhere in the loop, which is what makes GANs **likelihood-free**.

## Why they were a leap, and why they are hard

GANs produce strikingly **sharp** samples — sharper than VAEs — which made them the image-synthesis workhorse for years (DCGAN for stable convolutional training, StyleGAN for high-fidelity faces). But the adversarial setup is **unstable**: you are looking for an equilibrium of two moving networks, not minimizing a single loss, so training can oscillate or diverge if the two sides fall out of balance. The signature failure is **mode collapse** — the generator finds a few outputs that reliably fool the discriminator and produces only those, abandoning the diversity of the data. Much of the GAN literature (alternative losses like Wasserstein GAN, regularizers, careful architectures) is about taming this instability.

## The tradeoff

In the [trilemma](./foundations.md), GANs buy sample quality at the cost of the other two corners: no tractable likelihood (you cannot score a point), and fragile training. They sample fast — one generator pass — but you give up density estimation entirely.

## What to remember

- A GAN pits a generator against a discriminator; the generator learns only through the discriminator's signal — no likelihood.
- They produce sharp samples (DCGAN, StyleGAN) but train unstably and can suffer mode collapse.
- The tradeoff: high sample quality and fast sampling, but no density estimate and fragile optimization.

## References

- Goodfellow, I., et al. (2014). *Generative Adversarial Nets.* arXiv:1406.2661.
- Radford, A., Metz, L., Chintala, S. (2015). *Unsupervised Representation Learning with Deep Convolutional GANs (DCGAN).* arXiv:1511.06434.
- Arjovsky, M., Chintala, S., Bottou, L. (2017). *Wasserstein GAN.* arXiv:1701.07875. See [`../references/references.md`](../references/references.md).
