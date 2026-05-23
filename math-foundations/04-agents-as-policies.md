# Agents as policies

> 🧮 Mathematical foundation · ⏱ ~10 min read · Anchor: [`concepts/agents/`](../concepts/agents/)

## The equation

An agent is a **policy** — a function that maps states to distributions over actions:

$$\pi_\theta(a_t \mid s_t).$$

In an LLM agent, $\pi_\theta$ is the language model (with parameters $\theta$), $s_t$ is the conversation history up to step $t$, and $a_t$ is the next action — either a tool call or a final response.

The agent loop is then a sequence of policy evaluations: sample an action from $\pi_\theta$, observe its result, update the state, and sample again.

$$s_{t+1} = s_t \cup \{a_t,\, o_t\}, \qquad a_t \sim \pi_\theta(\cdot \mid s_t).$$

That's it. The whole conceptual framework fits on one line.

---

## Mathematical intuition

Three pieces worth internalizing:

**The policy is a distribution, not a function to one answer.** $\pi_\theta(\cdot \mid s_t)$ assigns a probability to every possible next action. We *sample* from it. With temperature 0, sampling collapses to "the most likely action" and the policy becomes deterministic in practice. With temperature > 0, the same state can yield different actions on different runs — which is why agent runs are non-reproducible by default.

**Actions live in a structured space.** The action space $\mathcal{A}$ has two kinds of elements:

- A *tool action* is a pair (tool name, arguments). The argument structure is defined by the tool's schema.
- A *terminal action* is a final response that ends the loop.

The LLM emits tokens, but those tokens parse into an element of $\mathcal{A}$. The parsing is usually enforced by structured-output APIs (JSON mode, function calling, grammar-constrained decoding). Without that enforcement, the model's output sometimes doesn't parse — that's a *malformed action*, which the agent runtime has to handle (typically by returning an error observation and asking the model to try again).

**The state grows.** Unlike RL, where state is usually a fixed-size vector or image, the agent's state is the running conversation — it expands by one tool call and one observation per step. This is why context-window budgeting becomes a first-class engineering concern: the policy's input is unbounded in principle, bounded by token limits in practice.

---

## Why it matters for engineers

The policy framing buys you four practical things:

1. **A vocabulary for thinking about decisions.** "The agent is making bad tool choices" becomes "$\pi_\theta$ is putting probability mass on the wrong actions for these states." That reframing immediately suggests what to do: change $s_t$ (better prompt / clearer tool descriptions), change $\theta$ (fine-tune, switch model), or restrict $\mathcal{A}$ (drop redundant tools).

2. **An explicit place for stochasticity.** Sampling temperature is not a vibe knob — it's the variance of $\pi_\theta(\cdot \mid s_t)$. Lower it when you want consistent behavior; raise it when you want exploration. Knowing *which* you want is now a clear question.

3. **A clean handoff to RL when you need it.** If you ever fine-tune an agent with RLHF, RLAIF, or DPO, you'll be optimizing exactly this object — $\pi_\theta$ — under some reward. The framing prepares you for that even if you never do it.

4. **Honesty about what an "agent" is.** It's a policy, period. Calling it a "reasoning system" or "autonomous decision-maker" oversells it. The policy framing keeps the engineering clear: there's no magic, just a parameterized function from state to action distribution.

---

## Where you'll see it in the code

The policy framing maps directly onto agent code. From [Lab 01](../labs/01-first-agent-from-scratch/lab.ipynb):

```python
def step(state: list[Message], tools: dict[str, Tool]) -> Action:
    """One application of pi_theta(. | s_t)."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=state,
        tools=[t.schema for t in tools.values()],
        tool_choice="auto",
        temperature=0,
    )
    return parse_action(response)
```

This function *is* $\pi_\theta(\cdot \mid s_t)$, sampled once. The full loop applies it repeatedly:

```python
while not done and steps < MAX_STEPS:
    action = step(state, tools)            # sample a_t ~ pi_theta(. | s_t)
    if action.is_final:
        return action.content
    observation = execute(action, tools)   # run the tool, get o_t
    state = state + [action, observation]  # s_{t+1} = s_t ∪ {a_t, o_t}
    steps += 1
```

The math and the code are the same shape. The state list is $s_t$. The `step` call is $\pi_\theta$. The append at the end is the state-update equation. Every framework you'll use later is sugar over this loop.

---

## Partial observability and belief states

LLM agents typically operate in **partial observability**: there's more in the world than the agent's context, and the agent only sees what it has observed so far. Formally this is a **POMDP** (Partially Observable Markov Decision Process), where the agent maintains a **belief state**:

$$b_t(s) = p(s \mid o_{1:t},\, a_{1:t-1}).$$

In words: the belief at step $t$ is the agent's probability distribution over what the true state might be, given everything it has seen and done.

In LLM agents, we don't compute $b_t$ explicitly — the conversation history *is* an approximation of the belief state, and the LLM's own conditioning on it produces the inference. The technical name for what an LLM agent does is "policy that conditions on observation history as a proxy for belief state." That mouthful is exactly why the simpler $\pi_\theta(a_t \mid s_t)$ formulation, with $s_t$ being the conversation, dominates engineering discussion.

The POMDP framing matters mostly when you're reasoning about *how* an agent goes wrong. "The agent didn't have the information to make this decision" is a belief-state failure: $b_t$ didn't concentrate on the true state. "The agent had the information and still chose the wrong action" is a policy failure: $\pi_\theta$ put probability mass on the wrong action even given good $b_t$. Different failures, different fixes.

A full treatment of MDPs and POMDPs comes in [`05-mdp-pomdp.md`](./05-mdp-pomdp.md) (forthcoming, after we have multi-agent examples to motivate the abstraction).

---

## What this framing is not

To avoid overselling the analogy:

- **We are not doing reinforcement learning.** No gradient updates to $\theta$ during a run. The policy is fixed; the loop just samples from it. RL becomes relevant only if you're fine-tuning the model itself.
- **There is no reward signal in a typical agent run.** Rewards appear when you train (RLHF, DPO) or when you build an evaluator that scores trajectories. Standard inference-time agents have no $r_t$.
- **The "state" is informal.** A real RL state has clean Markov properties. An LLM agent's state is just a list of messages, and the Markov assumption holds approximately because the LLM is conditioned on the whole list. We use the framing for vocabulary, not formal guarantees.

These caveats matter mostly when you're reading RL papers and translating. The engineering framing — $\pi_\theta(a_t \mid s_t)$, sample, observe, repeat — is honest and useful even when the formal RL machinery doesn't apply.

---

## See also

- 📖 [What is an agent?](../concepts/agents/what-is-an-agent.md) — the concept this formalizes.
- 📖 [Agent loop](../concepts/agents/agent-loop.md) — the cycle this describes.
- 📖 [ReAct pattern](../concepts/agents/react-pattern.md) — the specific structure most LLM policies follow.
- 🧪 [Lab 01](../labs/01-first-agent-from-scratch/) — the code that implements this directly.
- 🧮 [Notation reference](./notation.md) — full symbol glossary.
- 🧮 [ReAct formalization](./06-react-formalization.md) — how the policy framing specializes to ReAct.

---

## Sources

- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press, Ch. 3. [Free online](http://incompleteideas.net/book/the-book-2nd.html). Origin of the policy / state / action vocabulary.
- Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). [*Planning and Acting in Partially Observable Stochastic Domains*](https://www.cs.cmu.edu/~ggordon/780-fall07/readings/aima.pdf). Artificial Intelligence Journal, 101(1–2). The canonical POMDP reference.
- Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR 2024. Argues for the agent-as-policy framing in the LLM context specifically.
