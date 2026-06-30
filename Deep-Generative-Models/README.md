# Deep Generative Models

A self-contained knowledge module on **deep generative models** — the families of models that learn the probability distribution behind a dataset well enough to sample new data from it. It mirrors the structure of the rest of this repository: a landing map, modular concept notes, a math page, a diagram, a glossary, and canonical references.

> Original educational content. The notes are written from scratch and cite the primary papers; no source text is reproduced. See [`STYLE.md`](./STYLE.md).

## What this covers

Generative modeling learns a model of $p(x)$ over data — images, text, audio — so it can do three things: **sample** new instances, **score** the likelihood of a point (density estimation, useful for anomaly detection), and **learn representations** (the latent structure it discovers is useful downstream). The hard part is that the joint distribution over high-dimensional data is intractable to write down directly, and every model family is a different bargain for getting around that.

## Concept notes

| # | Note | Family / topic |
|---|---|---|
| 0 | [Foundations](./concepts/foundations.md) | objectives; explicit vs. implicit; likelihood-based vs. -free; latent variables; MLE↔KL; the generative trilemma |
| 1 | [Autoregressive models](./concepts/autoregressive-models.md) | chain-rule factorization; exact likelihood; PixelCNN, WaveNet, GPT |
| 2 | [Normalizing flows](./concepts/normalizing-flows.md) | invertible maps; change of variables; NICE, RealNVP, Glow |
| 3 | [Variational autoencoders](./concepts/variational-autoencoders.md) | latent variables; the ELBO; the reparameterization trick |
| 4 | [Generative adversarial networks](./concepts/generative-adversarial-networks.md) | implicit density; the minimax game; mode collapse |
| 5 | [Energy-based models](./concepts/energy-based-models.md) | unnormalized densities; the partition function; score matching |
| 6 | [Diffusion and score-based models](./concepts/diffusion-and-score-based-models.md) | forward noising, reverse denoising; the current image SOTA |

## The generative trilemma

A useful lens for the whole field: three properties you want, and the fact that no single family gets all three for free.

1. **High sample quality and expressivity** — samples that are sharp and varied.
2. **Tractable, exact likelihood** — you can compute $p(x)$ and do density estimation.
3. **Fast, stable training and sampling.**

Autoregressive models and flows give exact likelihood; GANs give sharp samples; diffusion gives quality at the cost of slow sampling; VAEs give fast inference and representations at some cost to sharpness. Each family is a different corner of this triangle — the [model-families diagram](./diagrams/model-families.md) lays them out.

## Repository map

```text
Deep-Generative-Models/
├── concepts/      # one note per family, plus shared foundations
├── math/          # the objectives and transformations behind the families
├── diagrams/      # a Mermaid taxonomy of the families
├── glossary/      # shared vocabulary
└── references/    # canonical papers
```

## License

Dual-licensed: code under Apache-2.0, prose and diagrams under CC-BY-4.0. See [`LICENSE`](./LICENSE).
