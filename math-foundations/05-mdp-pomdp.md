# MDP / POMDP intuition

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/agents/`](../concepts/agents/).

## Why this matters for agentic AI

When an LLM agent goes wrong, the failure usually splits into two categories: "the agent did not have the information it needed" or "the agent had the information and made the wrong call." MDP/POMDP gives you the vocabulary for that split. It also tells you why "state design" (what you put in the agent's context) is a load-bearing engineering decision.

## The equation

A **Markov Decision Process** is a tuple:

$$
\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma).
$$

**Symbols:**

- $\mathcal{S}$ - state space. Every possible situation the agent can be in.
- $\mathcal{A}$ - action space. Every action the agent can take.
- $P(s' \mid s, a)$ - transition dynamics. Probability of landing in $s'$ if you take action $a$ from $s$.
- $R(s, a)$ - reward function. Scalar value of taking $a$ in $s$.
- $\gamma \in [0, 1]$ - discount factor. Future rewards are worth less than immediate ones.

The **Markov property** is the load-bearing assumption: $P(s_{t+1} \mid s_t, a_t)$ depends only on $s_t$ and $a_t$, not on history. The state captures everything that matters.

A **Partially Observable MDP** drops the assumption that the agent sees $s_t$ directly. Instead, the agent gets observations $o_t$ drawn from $O(o_t \mid s_t)$ and maintains a **belief state**, a distribution over what the true state might be:

$$
b_t(s) = p(s_t = s \mid o_{1:t}, a_{1:t-1}).
$$

The POMDP tuple is $(\mathcal{S}, \mathcal{A}, P, R, \gamma, \Omega, O)$. The MDP plus an observation space $\Omega$ and an observation function $O$.

## How to read this equation

The MDP tuple is a contract: if you specify these five things, you have specified a decision-making problem. An algorithm that solves MDPs (value iteration, policy gradient, etc.) takes the tuple as input and returns a policy.

The belief-state equation reads as: at step $t$, after observing $o_1, \ldots, o_t$ and having taken actions $a_1, \ldots, a_{t-1}$, what does the agent think the world looks like? $b_t$ is a probability distribution over the entire state space. In LLM-land we never compute $b_t$ explicitly; the conversation history is the proxy.

## Mathematical intuition

LLM agents are POMDPs in disguise. The agent never sees the "true state of the world." It sees the conversation history (its observations), and it acts on that. The conversation is the belief state, maintained implicitly by the LLM's conditioning.

Three things to internalize:

**The Markov property is what makes the math tractable.** If $P(s_{t+1} \mid s_t, a_t)$ depended on the full history, we would need to enumerate exponentially many histories to plan. The Markov assumption says: pack everything the future needs into $s_t$. For LLM agents, this is approximate: the agent's "state" is the full conversation, and the LLM is conditioned on all of it, so the assumption holds *because we made $\mathcal{S}$ large enough*.

**Partial observability is the rule, not the exception.** Almost no real-world task gives the agent a perfect $s_t$. The agent sees tool outputs, search results, user messages, fragments. It infers the rest. POMDP framing forces this explicit accounting: the agent's behavior depends on what it knows, not on what is true.

**Belief states are computed implicitly by LLMs.** A formal POMDP solver computes $b_t$ via Bayesian filtering. LLM agents do not do this. They just condition on the observation history. The LLM's internal representation, evolved over training on countless conversation histories, approximates the belief-state inference. This is why prompting matters so much: it controls what gets folded into the (implicit) belief.

## Where this appears in agentic systems

- **"State design" is a real engineering decision.** Choosing what to put in the agent's conversation history determines what is in $s_t$ (or more precisely, what the agent can condition on). Common state-design mistakes: dropping tool errors so the agent forgets a failed approach; truncating early messages so the original goal disappears; persisting irrelevant detail that crowds out relevant context.
- **Belief-state failures and policy failures are different bugs.** "The agent did not have the information to decide" means fix the observation pipeline (better tools, better retrieval, longer context). "The agent had the information and decided wrong" means fix the policy (better system prompt, different model, restricted action space). [Page 04](./04-agents-as-policies.md) develops this distinction at length.
- **Discount factors do not usually apply.** $\gamma$ is meaningful when you are optimizing long-horizon return. Standard inference-time agents do not optimize anything; they just sample from a policy. $\gamma$ shows up when you fine-tune via RL (RLHF, DPO).
- **The POMDP framing buys vocabulary for failure analysis.** "The agent's belief state was wrong because $O(o_t \mid s_t)$ was noisy" means noisy tool outputs polluted the observation space. "The agent's belief state was confident but wrong" means a hallucinated observation was added to $s_t$. Different failure modes, different fixes, same formalism.

## Code example

A minimal MDP loop showing the state / action / observation / reward update. We use a toy environment for clarity; the same shape applies to LLM agents.

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class MDPLoop:
    """A simple MDP runner."""
    initial_state: dict
    policy: Callable                       # pi(s) -> a
    transition: Callable                   # P(s, a) -> s'
    reward: Callable                       # R(s, a) -> float
    is_terminal: Callable
    history: list = field(default_factory=list)

    def run(self, max_steps=20):
        s = dict(self.initial_state)
        total_reward = 0.0
        for t in range(max_steps):
            a = self.policy(s)                       # a_t ~ pi(s_t)
            r = self.reward(s, a)                    # R(s_t, a_t)
            s_next = self.transition(s, a)           # s_{t+1} = P(s_t, a_t)
            self.history.append((s, a, r, s_next))
            total_reward += r
            s = s_next
            if self.is_terminal(s):
                break
        return total_reward, self.history

# Toy example: gridworld-style "navigate to goal".
env = MDPLoop(
    initial_state={"pos": 0, "goal": 5},
    policy=lambda s: "right" if s["pos"] < s["goal"] else "stop",
    transition=lambda s, a: {**s, "pos": s["pos"] + (1 if a == "right" else 0)},
    reward=lambda s, a: 1.0 if a == "stop" and s["pos"] == s["goal"] else -0.1,
    is_terminal=lambda s: s["pos"] == s["goal"],
)
total, history = env.run()
print(f"Total reward: {total:.2f}")
print(f"Steps taken:  {len(history)}")
```

For an LLM agent, swap `policy` for an LLM call, `transition` for "append tool output to message history," `reward` for a downstream eval (only used in offline analysis), and the loop is the same. The structure transfers directly.

## Common mistakes

- **Pretending the Markov property holds when it does not.** If your agent needs to remember something from many steps ago and that detail has been compacted out of the conversation, the Markov property has been violated in practice. Either reintroduce the detail or accept the failure mode.
- **Treating LLM agents as fully observed.** Almost nothing about the world is in the conversation. The agent works on observations, not on $s$. Designing systems as if the agent has perfect state knowledge leads to brittle behavior.
- **Adding a discount factor without an objective.** $\gamma$ only matters if you are summing rewards. If you do not have an explicit reward signal at runtime, $\gamma$ is a distraction.
- **Conflating "no observation" with "negative observation."** An agent that does not see a tool error is in a different epistemic state from one that sees "error: connection refused." Always surface error observations rather than swallowing them.

## Repo cross-references

- [`concepts/agents/what-is-an-agent.md`](../concepts/agents/what-is-an-agent.md) - the concept this formalizes.
- [`concepts/memory/`](../concepts/memory/) - how the conversation history (the implicit belief state) gets organized in tiers.
- [Lab 01 - First agent from scratch](../labs/01-first-agent-from-scratch/) - agent loop implementation.

## Related pages

- [04 - Agents as policies](./04-agents-as-policies.md) - the policy $\pi_\theta$ that an agent samples from. Together with this page, the full MDP/POMDP picture.
- [08 - Planning and search](./08-planning-search.md) - what to do when the agent gets to plan a sequence of actions.
- [09 - Memory models](./09-memory-models.md) - how the conversation history (the implicit belief state) gets organized in tiers.
- [12 - Uncertainty and safety](./12-uncertainty-safety.md) - quantifying belief-state uncertainty.
- [Glossary: MDP, POMDP, Belief state, Policy](../glossary/terms.md) - short definitions.

## References

- Sutton, R. S., and Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press, Ch. 3. [Free online](http://incompleteideas.net/book/the-book-2nd.html). The MDP formulation in canonical form.
- Kaelbling, L. P., Littman, M. L., and Cassandra, A. R. (1998). [*Planning and Acting in Partially Observable Stochastic Domains*](https://www.sciencedirect.com/science/article/pii/S000437029800023X). Artificial Intelligence Journal 101(1-2). The canonical POMDP reference.
- Sumers, T. R., Yao, S., Narasimhan, K., and Griffiths, T. L. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR. Argues for the agent-as-POMDP framing in the LLM context.
- Russell, S., and Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 17. The MDP / POMDP material from the AI textbook tradition.
