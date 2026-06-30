# Glossary

Vocabulary for the deep generative models module. Alphabetical; each entry links to where it is used.

**Autoregressive model.** A generative model that factorizes $p(x)$ into a product of conditionals via the chain rule, one variable at a time, giving exact likelihood at the cost of sequential sampling. → `concepts/autoregressive-models.md`.

**Change of variables.** The formula relating the densities of $z$ and $x = f(z)$ for an invertible $f$, via the Jacobian determinant; the basis of normalizing flows. → `concepts/normalizing-flows.md`.

**Contrastive divergence.** A training method for energy-based models that lowers energy on data and raises it on model samples, avoiding the partition function. → `concepts/energy-based-models.md`.

**Diffusion model.** A generative model that learns to reverse a fixed noising process, sampling by denoising from pure noise; current state of the art for images. → `concepts/diffusion-and-score-based-models.md`.

**ELBO (evidence lower bound).** A tractable lower bound on the log-likelihood, maximized by VAEs; a reconstruction term minus a KL regularizer. → `concepts/variational-autoencoders.md`.

**Energy-based model (EBM).** A model defining $p(x) \propto e^{-E_\theta(x)}$ with an unconstrained energy network; flexible but burdened by an intractable partition function. → `concepts/energy-based-models.md`.

**Explicit vs. implicit density.** Explicit models write an evaluable form for $p(x)$; implicit models only define a sampling process (e.g. a GAN). → `concepts/foundations.md`.

**GAN (generative adversarial network).** An implicit, likelihood-free model in which a generator and discriminator compete; sharp samples, unstable training. → `concepts/generative-adversarial-networks.md`.

**Generative trilemma.** The observation that high sample quality, exact tractable likelihood, and fast stable training/sampling cannot all be had at once; each family is a different compromise. → `concepts/foundations.md`.

**Latent variable.** An unobserved variable $z$ assumed to generate the data $x$ via $p(x\mid z)$; recovering $p(z\mid x)$ enables representation learning. → `concepts/foundations.md`.

**Likelihood-based vs. likelihood-free.** Likelihood-based models train on the data likelihood or a bound; likelihood-free models use other signals (adversarial loss, score matching). → `concepts/foundations.md`.

**Maximum likelihood estimation (MLE).** Fitting $\theta$ to maximize the data likelihood; equivalent to minimizing the KL divergence from the data distribution to the model. → `concepts/foundations.md`.

**Mode collapse.** A GAN failure where the generator produces only a few outputs that fool the discriminator, losing the diversity of the data. → `concepts/generative-adversarial-networks.md`.

**Normalizing flow.** A generative model that transforms a simple prior through invertible maps, giving exact likelihood via the change-of-variables formula. → `concepts/normalizing-flows.md`.

**Partition function.** The normalizing constant $Z_\theta = \int e^{-E_\theta(x)}dx$ of an energy-based model; intractable, which is why EBMs are hard to train. → `concepts/energy-based-models.md`.

**Reparameterization trick.** Writing $z = \mu + \sigma\odot\epsilon$ with $\epsilon\sim\mathcal N(0,I)$ so that sampling becomes differentiable and gradients flow through a VAE. → `concepts/variational-autoencoders.md`.

**Score.** The gradient of the log density, $\nabla_x\log p(x)$; independent of the partition function, and the quantity diffusion and score-based models learn. → `concepts/diffusion-and-score-based-models.md`.

**Variational autoencoder (VAE).** A latent-variable model pairing an encoder (approximate posterior) with a decoder, trained by maximizing the ELBO. → `concepts/variational-autoencoders.md`.
