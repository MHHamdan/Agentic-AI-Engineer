# Variational autoencoders

> Concept note. ~9 min. Builds on [foundations](./foundations.md). Math: [`../math/objectives-and-transformations.md`](../math/objectives-and-transformations.md).

A variational autoencoder (VAE) is the canonical latent-variable generative model. It assumes each data point $x$ is generated from a low-dimensional latent $z$, learns to map between the two with a pair of networks, and trains on a tractable bound on the likelihood.

## The two networks and the intractable posterior

A VAE has a **decoder** $p_\theta(x \mid z)$ that generates data from a latent (with a simple prior $p(z)$, usually a standard Gaussian), and an **encoder** $q_\phi(z \mid x)$ that infers a latent from data. The encoder exists because the true posterior $p_\theta(z \mid x)$ — the right latent for a given $x$ — is intractable to compute. The encoder is an *approximate* posterior, a network trained to stand in for it.

## The objective: the ELBO

Because the exact log-likelihood $\log p_\theta(x)$ is intractable, VAEs maximize a lower bound on it, the **evidence lower bound (ELBO)**:

$$
\log p_\theta(x) \;\ge\; \underbrace{\mathbb{E}_{q_\phi(z\mid x)}\big[\log p_\theta(x \mid z)\big]}_{\text{reconstruction}} \;-\; \underbrace{\mathrm{KL}\!\big(q_\phi(z\mid x)\,\|\,p(z)\big)}_{\text{regularizer}}.
$$

The two terms pull in useful tension. The **reconstruction** term wants latents that let the decoder rebuild the input. The **KL** term keeps the encoder's distribution close to the prior, which keeps the latent space smooth and regular — so you can sample a $z$ from the prior and decode it into something coherent. Maximizing the ELBO trains encoder and decoder together.

## The reparameterization trick

There is a snag: you need gradients to flow back through a *sampling* step ($z \sim q_\phi(z \mid x)$), and sampling is not differentiable. The **reparameterization trick** fixes it by moving the randomness outside the network: instead of sampling $z$ directly, sample noise $\epsilon \sim \mathcal{N}(0, I)$ and compute $z = \mu_\phi(x) + \sigma_\phi(x)\,\epsilon$. Now $z$ is a deterministic, differentiable function of the network outputs and an external noise source, and gradients pass through. This trick is what makes VAEs trainable by ordinary backpropagation.

## The tradeoff

VAEs give fast generation (one decoder pass), an explicit latent space useful for [representation learning](./foundations.md), and principled probabilistic training. Their well-known weakness is **sample sharpness**: samples are often blurrier than a GAN's or a diffusion model's, partly because the bound and the Gaussian assumptions smooth things out. In the [trilemma](./foundations.md), VAEs favor fast, stable training and useful inference over maximal sample fidelity.

## What to remember

- A VAE pairs a decoder $p_\theta(x\mid z)$ with an approximate-posterior encoder $q_\phi(z\mid x)$, because the true posterior is intractable.
- It maximizes the ELBO: a reconstruction term plus a KL regularizer that keeps the latent space smooth.
- The reparameterization trick makes sampling differentiable; the tradeoff is blurrier samples for fast inference and representations.

## References

- Kingma, D. P. & Welling, M. (2013). *Auto-Encoding Variational Bayes.* arXiv:1312.6114.
- Rezende, D. J., Mohamed, S., Wierstra, D. (2014). *Stochastic Backpropagation and Approximate Inference in Deep Generative Models.* arXiv:1401.4082. See [`../references/references.md`](../references/references.md).
