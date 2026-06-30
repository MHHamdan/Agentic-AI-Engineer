# Energy-based models

> Concept note. ~8 min. Builds on [foundations](./foundations.md).

Energy-based models (EBMs) are the most flexible explicit family and the most awkward to train. They define a distribution through an **energy function** that scores configurations, without committing to a tractable normalized form.

## The idea: an unnormalized density

An EBM assigns each point an energy $E_\theta(x)$ — low energy for likely data, high for unlikely — and defines

$$
p_\theta(x) = \frac{e^{-E_\theta(x)}}{Z_\theta}, \qquad Z_\theta = \int e^{-E_\theta(x)}\,dx.
$$

The energy can be *any* neural network, with no architectural constraints — no invertibility (as flows need), no ordering (as autoregressive models need). That freedom is the appeal. The problem is the denominator $Z_\theta$, the **partition function**: an integral over all of data space that is intractable to compute, which means you cannot evaluate $p_\theta(x)$ directly or take its gradient the easy way.

## Training around the partition function

The field's techniques are ways to learn $E_\theta$ without ever computing $Z_\theta$:

- **Contrastive divergence** pushes energy down on real data and up on samples drawn from the model (via short-run Markov-chain sampling), so the relative energies come out right even though the normalizer is unknown.
- **Score matching** sidesteps $Z_\theta$ entirely by matching the *gradient* of the log density, $\nabla_x \log p_\theta(x)$ — the **score** — which does not depend on the normalizing constant because the constant vanishes under the gradient. This idea is the bridge to [diffusion and score-based models](./diffusion-and-score-based-models.md).

Sampling is also hard: with no direct sampler, EBMs rely on iterative Markov-chain methods (such as Langevin dynamics, which follows the score plus noise), which can be slow to mix.

## The tradeoff

EBMs are maximally flexible in what they can represent, and the score-matching idea they motivate turned out to be foundational. But the intractable partition function makes both training and sampling difficult and often unstable, which kept them less practical than other families on their own — until score matching re-emerged at the heart of diffusion.

## What to remember

- An EBM defines $p(x) \propto e^{-E_\theta(x)}$ with an unconstrained energy network — very flexible.
- The partition function $Z_\theta$ is intractable; contrastive divergence and score matching train without it.
- Sampling needs iterative MCMC (e.g., Langevin); the score-matching idea leads directly to diffusion models.

## References

- Hinton, G. (2002). *Training Products of Experts by Minimizing Contrastive Divergence.*
- Hyvärinen, A. (2005). *Estimation of Non-Normalized Statistical Models by Score Matching.*
- Song, Y. & Kingma, D. P. (2021). *How to Train Your Energy-Based Models.* arXiv:2101.03288. See [`../references/references.md`](../references/references.md).
