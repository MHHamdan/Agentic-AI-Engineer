# Normalizing flows

> Concept note. ~8 min. Builds on [foundations](./foundations.md). Math: [`../math/objectives-and-transformations.md`](../math/objectives-and-transformations.md).

Normalizing flows get an exact likelihood a different way: start from a simple distribution and push it through a sequence of **invertible** transformations until it matches the data.

## The idea: change of variables

Let $z$ come from a simple prior $p_Z(z)$ (a standard Gaussian), and let $x = f_\theta(z)$ for an invertible, differentiable $f_\theta$. The change-of-variables formula gives the data density exactly:

$$
p_X(x) = p_Z\!\big(f_\theta^{-1}(x)\big)\;\Big| \det J_{f_\theta^{-1}}(x) \Big|,
$$

where $J$ is the Jacobian of the inverse map. The determinant accounts for how the transformation stretches or compresses volume, keeping the density normalized. Because the expression is exact, flows train by exact maximum likelihood — like autoregressive models, but with a single invertible map (or a stack of them) instead of a sequential factorization.

## The engineering problem: a cheap Jacobian

The catch is the determinant. For a general $n\times n$ Jacobian it costs $O(n^3)$, which is hopeless at image scale. The whole craft of flows is designing transformations that are both expressive and have a Jacobian determinant you can compute in $O(n)$ — typically by making the Jacobian **triangular**. **Coupling layers**, introduced in NICE, do this elegantly: split the variables in two, leave one half unchanged, and transform the other half using only the first — the Jacobian is triangular and the determinant is trivial. **RealNVP** generalized these to affine coupling for more flexibility; **Glow** added invertible $1\times1$ convolutions to mix channels; **MAF** and **IAF** built autoregressive structure into the flow.

## The tradeoff

Flows give exact likelihood and a meaningful latent space, with parallel sampling (unlike autoregressive models). Their structural constraint is that the latent $z$ must have the **same dimension** as the data $x$ — every transformation is a bijection — so they cannot compress to a lower-dimensional code the way a VAE can, and the invertibility requirement limits the architectures available.

## What to remember

- Flows transform a simple prior through invertible maps; the change-of-variables formula gives exact likelihood.
- The art is a transformation with a cheap (triangular) Jacobian determinant — coupling layers (NICE, RealNVP), $1\times1$ convolutions (Glow).
- Exact likelihood and parallel sampling, but the latent must match the data dimension — no built-in compression.

## References

- Dinh, L., Krueger, D., Bengio, Y. (2014). *NICE: Non-linear Independent Components Estimation.* arXiv:1410.8516.
- Dinh, L., Sohl-Dickstein, J., Bengio, S. (2016). *Density Estimation Using Real NVP.* arXiv:1605.08803.
- Kingma, D. P. & Dhariwal, P. (2018). *Glow.* arXiv:1807.03039.
- Papamakarios, G., et al. (2019). *Normalizing Flows for Probabilistic Modeling and Inference.* arXiv:1912.02762. See [`../references/references.md`](../references/references.md).
