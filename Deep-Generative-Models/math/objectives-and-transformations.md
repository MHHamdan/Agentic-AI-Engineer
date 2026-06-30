# Objectives and transformations

> Mathematical foundation. ~9 min. Supports the [concept notes](../concepts/).

Four pieces of math recur across the generative families: the MLE–KL equivalence (how almost all of them train), the change-of-variables formula (flows), the ELBO (VAEs), and the score (energy-based and diffusion models). This page states each compactly.

## Maximum likelihood is KL minimization

Given data $x^{(1)}, \dots, x^{(m)}$ drawn from $p_{\text{data}}$, maximum likelihood chooses

$$
\theta^\* = \arg\max_\theta \frac{1}{m}\sum_{i=1}^m \log p_\theta\!\big(x^{(i)}\big).
$$

As $m \to \infty$ the average converges to $\mathbb{E}_{p_{\text{data}}}[\log p_\theta(x)]$, and

$$
\mathrm{KL}\!\big(p_{\text{data}} \,\|\, p_\theta\big) = \mathbb{E}_{p_{\text{data}}}[\log p_{\text{data}}(x)] - \mathbb{E}_{p_{\text{data}}}[\log p_\theta(x)].
$$

The first term does not depend on $\theta$, so maximizing the log-likelihood is exactly minimizing $\mathrm{KL}(p_{\text{data}} \,\|\, p_\theta)$ — fitting by MLE pulls the model toward the data distribution in KL.

## Change of variables (flows)

If $x = f_\theta(z)$ is invertible and differentiable and $z \sim p_Z$, the density of $x$ is

$$
p_X(x) = p_Z\!\big(f_\theta^{-1}(x)\big)\,\Big|\det J_{f_\theta^{-1}}(x)\Big|,
\qquad J_{f_\theta^{-1}}(x) = \frac{\partial f_\theta^{-1}}{\partial x}.
$$

The log-likelihood a flow maximizes is then $\log p_Z(f_\theta^{-1}(x)) + \log|\det J|$. The engineering goal is a map whose $\log|\det J|$ costs $O(n)$, achieved by a triangular Jacobian (coupling layers).

## The ELBO (VAEs)

For a latent-variable model with prior $p(z)$, decoder $p_\theta(x\mid z)$, and approximate posterior $q_\phi(z\mid x)$, the marginal log-likelihood decomposes as

$$
\log p_\theta(x) = \underbrace{\mathbb{E}_{q_\phi}\!\Big[\log \tfrac{p_\theta(x,z)}{q_\phi(z\mid x)}\Big]}_{\text{ELBO}} + \mathrm{KL}\!\big(q_\phi(z\mid x)\,\|\,p_\theta(z\mid x)\big).
$$

The KL term is $\ge 0$ and involves the intractable true posterior, so the ELBO is a lower bound on $\log p_\theta(x)$. Rearranging the ELBO gives the trainable form,

$$
\text{ELBO} = \mathbb{E}_{q_\phi(z\mid x)}\big[\log p_\theta(x\mid z)\big] - \mathrm{KL}\!\big(q_\phi(z\mid x)\,\|\,p(z)\big),
$$

a reconstruction term minus a regularizer. The reparameterization $z = \mu_\phi(x) + \sigma_\phi(x)\odot\epsilon$, $\epsilon\sim\mathcal N(0,I)$, makes the expectation differentiable in $\phi$.

## The score (energy-based and diffusion)

The **score** of a density is the gradient of its log, $s(x) = \nabla_x \log p(x)$. For an energy-based model $p_\theta(x) = e^{-E_\theta(x)}/Z_\theta$,

$$
\nabla_x \log p_\theta(x) = -\nabla_x E_\theta(x),
$$

and the intractable normalizer $Z_\theta$ drops out because it does not depend on $x$ — which is why matching the score avoids the partition function. Diffusion models learn this score at every noise level and sample by following it (Langevin-style: $x \leftarrow x + \tfrac{\epsilon}{2}\nabla_x\log p(x) + \sqrt{\epsilon}\,\eta$), walking noise back to data.

## What to remember

- MLE $\equiv$ minimizing $\mathrm{KL}(p_{\text{data}}\,\|\,p_\theta)$ — the shared training principle.
- Change of variables gives flows an exact likelihood; a triangular Jacobian makes it cheap.
- The ELBO is a tractable lower bound for latent-variable models; the score removes the partition function and underlies diffusion.

## See also

- [`../concepts/`](../concepts/) — the families that use these objectives.
