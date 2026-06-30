# Diffusion and score-based models

> Concept note. ~9 min. Builds on [foundations](./foundations.md) and [energy-based models](./energy-based-models.md).

Diffusion models are the current state of the art for image synthesis, and the engines behind modern text-to-image systems. The idea is disarmingly simple: learn to reverse a process that gradually destroys data with noise.

## The idea: destroy, then learn to rebuild

The **forward process** takes a data point and adds a small amount of Gaussian noise, repeatedly, over many steps, until nothing is left but pure noise. This direction is fixed and requires no learning — it is just progressive corruption. The model learns the **reverse process**: at each step, given a noisier version, predict how to denoise it slightly toward the data. Chain enough learned denoising steps together, start from pure noise, and you walk back to a clean, realistic sample.

Training is stable because it reduces to a simple regression: at a random noise level, predict the noise that was added (equivalently, the **score** $\nabla_x \log p(x)$ — the same quantity from [energy-based models](./energy-based-models.md), which is why these are also called *score-based* models). There is no adversarial game and no intractable partition function — just denoising, which is what makes diffusion training far more stable than a GAN's.

## Why it wins on quality, and what it costs

Diffusion models produce samples that rival or exceed GANs in fidelity *and* diversity, without mode collapse — they cover the data distribution rather than fixating on a few modes. That combination is why they took over image generation. The cost lands squarely in the [trilemma](./foundations.md): **sampling is slow**, because generating one sample means running many sequential denoising steps (originally hundreds or thousands). A large body of recent work is about cutting the number of steps — faster samplers, distillation — to close that gap.

## How it relates to the other families

Diffusion ties the module together. It uses the **score** that energy-based models introduced, it can be cast as a (continuous) transformation of noise into data like a [flow](./normalizing-flows.md), and it shares the sequential-sampling cost of [autoregressive models](./autoregressive-models.md) — but trades exact likelihood for sample quality and training stability. It is the clearest example that the families are not isolated; each new one recombines ideas from the others to move to a different corner of the trilemma.

## What to remember

- Diffusion models learn to reverse a fixed noising process: predict the denoising (the score) at each step, then sample by denoising from pure noise.
- Training is a stable regression — no adversarial game, no partition function — which is why quality and diversity are high.
- The cost is slow, multi-step sampling; reducing the step count is the active frontier.

## References

- Sohl-Dickstein, J., et al. (2015). *Deep Unsupervised Learning Using Nonequilibrium Thermodynamics.* arXiv:1503.03585.
- Ho, J., Jain, A., Abbeel, P. (2020). *Denoising Diffusion Probabilistic Models.* arXiv:2006.11239.
- Song, Y. & Ermon, S. (2019). *Generative Modeling by Estimating Gradients of the Data Distribution.* arXiv:1907.05600.
- Song, Y., et al. (2020). *Score-Based Generative Modeling through Stochastic Differential Equations.* arXiv:2011.13456. See [`../references/references.md`](../references/references.md).
