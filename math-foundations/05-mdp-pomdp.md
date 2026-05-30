# MDP / POMDP intuition

> 🧮 Mathematical foundation · ⏱ ~9 min read · Anchor: [`concepts/agents/`](../concepts/agents/)

## The equation

A **Markov Decision Process** is a tuple:

$$
\mathcal{M} \;=\; (\mathcal{S},\, \mathcal{A},\, P,\, R,\, \gamma).
$$

- $\mathcal{S}$ — state space (every possible situation the agent can be in).
- $\mathcal{A}$ — action space (every action the agent can take).
- $P(s' \mid s, a)$ — transition dynamics. Probability of landing in $s'$ if you take action $a$ from $s$.
- $R(s, a)$ — reward function. Scalar value of taking $a$ in $s$.
- $\gamma \in [0, 1]$ — discount factor. Future rewards are worth less than immediate ones.

The **Markov property** is the load-bearing assumption: $P(s_{t+1} \mid s_t, a_t)$ depends only on $s_t$ and $a_t$, not on history. The state captures everything that matters.

A **Partially Observable MDP** drops the assumption that the agent sees $s_t$ directly. Instead, the agent gets observations $o_t$ drawn from $O(o_t \mid s_t)$ and maintains a **belief state** — a distribution over what the true state might be:

$$
b_t(s) \;=\; p\big(s_t = s \mid o_{1:t},\, a_{1:t-1}\big).
$$

The POMDP tuple is $(\mathcal{S}, \mathcal{A}, P, R, \gamma, \Omega, O)$ — the MDP plus an observation space $\Omega$ and an observation function $O$.

---

## Mathematical intuition

LLM agents are POMDPs in disguise. The agent never sees the "true state of the world" — it sees the conversation history (its observations), and it acts on that. The conversation *is* the belief state, implicitly maintained by the LLM's conditioning.

Three things to internalize:

**The Markov property is what makes the math tractable.** If $P(s_{t+1} \mid s_t, a_t)$ depended on the full history $(s_0, a_0, s_1, a_1, \ldots, s_t, a_t)$, we'd need to enumerate exponentially many histories to plan. The Markov assumption says: pack everything the future needs into $s_t$. For LLM agents, this is approximate — the agent's "state" is the full conversation, and the LLM is conditioned on all of it, so the assumption holds *because we made $\mathcal{S}$ large enough*.

**Partial observability is the rule, not the exception.** Almost no real-world task gives the agent a perfect $s_t$. The agent sees tool outputs, search results, user messages — fragments. It infers the rest. POMDP framing forces this explicit accounting: the agent's behavior depends on *what it knows*, not on what's true.

**Belief states are computed implicitly by LLMs.** A formal POMDP solver computes $b_t$ via Bayesian filtering. LLM agents don't do this — they just condition on the observation history. The LLM's internal representation, evolved over training on countless conversation histories, *approximates* the belief-state inference. This is why prompting matters so much: it controls what gets folded into the (implicit) belief.

---

## Why it matters for engineers

Four practical implications:

1. **"State design" is a real engineering decision.** Choosing what to put in the agent's conversation history determines what's in $s_t$ (or, more precisely, what the agent can condition on). Common state-design mistakes: dropping tool errors so the agent forgets a failed approach; truncating early messages so the original goal disappears; persisting irrelevant detail that crowds out relevant context.

2. **Belief-state failures and policy failures are different bugs.** "The agent didn't have the information to decide" → fix the observation pipeline (better tools, better retrieval, longer context). "The agent had the information and decided wrong" → fix the policy (better system prompt, different model, restricted action space). [Page 04](./04-agents-as-policies.md) develops this distinction at length.

3. **Discount factors don't usually apply.** $\gamma$ is meaningful when you're optimizing long-horizon return. Standard inference-time agents don't optimize anything — they just sample from a policy. $\gamma$ shows up when you fine-tune via RL (RLHF, DPO).

4. **The POMDP framing buys you vocabulary for failure analysis.** "The agent's belief state was wrong because $O(o_t \mid s_t)$ was noisy" → noisy tool outputs polluted the observation space. "The agent's belief state was confident but wrong" → a hallucinated observation was added to $s_t$. Different failure modes; different fixes; same formalism.

---

## Where you'll see it in the code

The "state" of an LLM agent is the conversation history. From [Lab 01](../labs/01-first-agent-from-scratch/):

```python
state: list[Message] = [
    {"role": "system", "content": SYSTEM_PROMPT},   # initial conditioning
    {"role": "user", "content": user_goal},          # the task
]

while not done and len(state) < MAX_STATE:
    action = step(state, tools)                      # sample a_t ~ pi(. | s_t)
    if action.is_final:
        return action.content
    observation = execute(action, tools)             # o_t from environment
    state.append(action)                             # s_{t+1} = s_t + a_t + o_t
    state.append(observation)
```

The `state` list is $s_t$ in MDP terms, and $b_t$ in POMDP terms (the agent's belief about the world is exactly what's in this list). The agent's design choices — what goes in `SYSTEM_PROMPT`, how `observation` gets formatted, when to truncate `state` — are all state-design choices.

For more elaborate stat schemas (with explicit slots for retrieved context, scratchpad memory, etc.), see [Path 05 concepts on memory tiers](../concepts/memory/).

---

## See also

- 🧮 [Agents as policies](./04-agents-as-policies.md) — the policy $\pi_\theta$ that an agent samples from. Together with this page, the full MDP/POMDP picture.
- 🧮 [Memory models](./09-memory-models.md) — how the conversation history (the implicit belief state) gets organized in tiers.
- 📖 [What is an agent?](../concepts/agents/what-is-an-agent.md) — the concept this formalizes.
- 📖 [Glossary — MDP, POMDP, Belief state, Policy](../glossary/terms.md).

---

## Sources

- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press, Ch. 3. [Free online](http://incompleteideas.net/book/the-book-2nd.html). The MDP formulation in canonical form.
- Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). [*Planning and Acting in Partially Observable Stochastic Domains*](https://www.cs.cmu.edu/~ggordon/780-fall07/readings/aima.pdf). Artificial Intelligence Journal, 101(1-2). The canonical POMDP reference.
- Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR. Argues for the agent-as-POMDP framing in the LLM context.
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 17. The MDP / POMDP material from the AI textbook tradition.
