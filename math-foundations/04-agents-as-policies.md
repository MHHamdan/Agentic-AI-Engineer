# Agents as policies

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/agents/`](../concepts/agents/).

## Why this matters for agentic AI

The single most useful mental model in agentic AI is "an agent is a policy." It gives you the vocabulary to debug bad tool choices, choose decoding hyperparameters, and read RL papers without getting lost. Almost every other math page in this folder specializes this one.

## The equation

An agent is a **policy**: a function that maps states to distributions over actions.

$$
\pi_\theta(a_t \mid s_t).
$$

In an LLM agent, $\pi_\theta$ is the language model (with parameters $\theta$), $s_t$ is the conversation history up to step $t$, and $a_t$ is the next action (either a tool call or a final response).

The agent loop is a sequence of policy evaluations: sample an action from $\pi_\theta$, observe its result, update the state, sample again:

$$
a_t \sim \pi_\theta(\cdot \mid s_t), \qquad s_{t+1} = s_t \cup \{a_t, o_t\}.
$$

**Symbols:**

- $\pi_\theta$ - the policy. The LLM viewed as a decision function.
- $\theta$ - model parameters (weights, system prompt, tool definitions all roll up here).
- $s_t$ - the state at step $t$. The full conversation up to that point.
- $a_t$ - the action at step $t$. A tool call or a final response.
- $o_t$ - the observation at step $t$. The result of executing $a_t$.
- $a_t \sim \pi_\theta(\cdot \mid s_t)$ - sample an action from the distribution.

## How to read this equation

Read $\pi_\theta(a_t \mid s_t)$ as "the probability that the policy chooses action $a_t$ given that the state is $s_t$." It is a distribution over the whole action space, not a single action.

The state-update equation says: after taking action $a_t$ and observing result $o_t$, the new state is the old state with $a_t$ and $o_t$ appended. The state grows over time. Unlike RL, where state is usually fixed-size, the agent's state expands by one tool call and one observation per step.

The whole conceptual framework fits in one line plus its update rule.

## Mathematical intuition

Three pieces worth internalizing.

**The policy is a distribution, not a function to one answer.** $\pi_\theta(\cdot \mid s_t)$ assigns a probability to every possible next action. We sample from it. With temperature 0, sampling collapses to "the most likely action" and the policy becomes deterministic in practice. With temperature greater than 0, the same state can yield different actions on different runs. That is why agent runs are non-reproducible by default.

**Actions live in a structured space.** The action space $\mathcal{A}$ has two kinds of elements:

- A *tool action* is a pair `(tool name, arguments)`. The argument structure is defined by the tool's schema.
- A *terminal action* is a final response that ends the loop.

The LLM emits tokens, but those tokens parse into an element of $\mathcal{A}$. The parsing is usually enforced by structured-output APIs (JSON mode, function calling, grammar-constrained decoding). Without that enforcement, the model's output sometimes does not parse, which is a *malformed action* that the agent runtime has to handle (typically by returning an error observation and asking the model to try again).

**The state grows.** Unlike RL, where state is usually a fixed-size vector or image, the agent's state is the running conversation. It expands by one tool call and one observation per step. This is why context-window budgeting becomes a first-class engineering concern: the policy's input is unbounded in principle, bounded by token limits in practice.

## Partial observability and belief states

LLM agents typically operate in **partial observability**: there is more in the world than the agent's context, and the agent only sees what it has observed so far. Formally this is a POMDP (Partially Observable Markov Decision Process), where the agent maintains a belief state:

$$
b_t(s) = p(s \mid o_{1:t}, a_{1:t-1}).
$$

In words: the belief at step $t$ is the agent's probability distribution over what the true state might be, given everything it has seen and done.

In LLM agents, we do not compute $b_t$ explicitly. The conversation history is an approximation of the belief state, and the LLM's own conditioning on it produces the inference. The technical name for what an LLM agent does is "policy that conditions on observation history as a proxy for belief state." That mouthful is exactly why the simpler $\pi_\theta(a_t \mid s_t)$ formulation, with $s_t$ being the conversation, dominates engineering discussion.

The POMDP framing matters mostly when you are reasoning about how an agent goes wrong. "The agent did not have the information to make this decision" is a belief-state failure: $b_t$ did not concentrate on the true state. "The agent had the information and still chose the wrong action" is a policy failure: $\pi_\theta$ put probability mass on the wrong action even given good $b_t$. Different failures, different fixes.

A full treatment of MDPs and POMDPs comes in [page 05](./05-mdp-pomdp.md).

## Where this appears in agentic systems

The policy framing buys you four practical things:

1. **A vocabulary for thinking about decisions.** "The agent is making bad tool choices" becomes "$\pi_\theta$ is putting probability mass on the wrong actions for these states." That reframing immediately suggests what to do: change $s_t$ (better prompt or clearer tool descriptions), change $\theta$ (fine-tune, switch model), or restrict $\mathcal{A}$ (drop redundant tools).
2. **An explicit place for stochasticity.** Sampling temperature is not a vibe knob. It is the variance of $\pi_\theta(\cdot \mid s_t)$. Lower it when you want consistent behavior; raise it when you want exploration.
3. **A clean handoff to RL when you need it.** If you ever fine-tune an agent with RLHF, RLAIF, or DPO, you are optimizing exactly this object, $\pi_\theta$, under some reward. The framing prepares you for that even if you never do it.
4. **A clear separation between policy failures and observation failures.** Most "the agent did the wrong thing" bugs split cleanly into one of these two categories once you have the framing.

## Code example

The agent loop maps directly to the math.

```python
from openai import OpenAI

client = OpenAI()
MAX_STEPS = 10

def step(state, tools):
    """One application of pi_theta(. | s_t)."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state,
        tools=[t["schema"] for t in tools.values()],
        tool_choice="auto",
        temperature=0,  # makes pi_theta deterministic at the sample step
    )
    return response.choices[0].message

def run(initial_state, tools):
    state = list(initial_state)
    for _ in range(MAX_STEPS):
        action = step(state, tools)            # a_t ~ pi_theta(. | s_t)
        state.append(action.model_dump())

        if not action.tool_calls:
            return action.content              # terminal action: respond

        for call in action.tool_calls:
            o = tools[call.function.name]["fn"](call.function.arguments)
            state.append({                     # s_{t+1} = s_t + a_t + o_t
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(o),
            })
    return "max steps exceeded"
```

The `step` function is exactly $\pi_\theta(\cdot \mid s_t)$ evaluated once. The loop body is the state-update equation. Every agent framework you will use later (LangGraph, CrewAI, Pydantic AI) is sugar over this loop.

## Common mistakes

- **Calling the LLM a "reasoning system" or "autonomous decision-maker."** It is a policy. The policy framing keeps the engineering clear: there is no magic, just a parameterized function from state to action distribution.
- **Confusing temperature with intelligence.** Temperature does not change $\theta$; it changes the *sampling* from $\pi_\theta$. Lower temperature does not make the agent smarter; it makes it more deterministic.
- **Treating the state as opaque.** Anything you can put in the state, you can use to shape behavior. System prompts, tool descriptions, retrieved context, prior thoughts. Choose what goes in deliberately.
- **Conflating policy failures with belief-state failures.** When debugging, ask: was the right information *in the state* at decision time? If yes, fix the policy (prompt or model). If no, fix the observation pipeline (better tools, retrieval, context engineering).

## What this framing is not

To avoid overselling the analogy:

- **We are not doing reinforcement learning.** No gradient updates to $\theta$ during a run. The policy is fixed; the loop just samples from it. RL becomes relevant only if you are fine-tuning the model itself.
- **There is no reward signal in a typical agent run.** Rewards appear when you train (RLHF, DPO) or when you build an evaluator that scores trajectories. Standard inference-time agents have no $r_t$.
- **The "state" is informal.** A real RL state has clean Markov properties. An LLM agent's state is just a list of messages, and the Markov assumption holds approximately because the LLM is conditioned on the whole list. We use the framing for vocabulary, not formal guarantees.

These caveats matter mostly when you are reading RL papers and translating. The engineering framing $\pi_\theta(a_t \mid s_t)$ is useful even when the formal RL machinery does not apply.

## Repo cross-references

- [Lab 01 - First agent from scratch](../labs/01-first-agent-from-scratch/) - the code that implements this directly.
- [`concepts/agents/what-is-an-agent.md`](../concepts/agents/what-is-an-agent.md) - the concept this formalizes.
- [`concepts/agents/agent-loop.md`](../concepts/agents/agent-loop.md) - the cycle this describes.
- [`concepts/agents/react-pattern.md`](../concepts/agents/react-pattern.md) - the specific structure most LLM policies follow.

## Related pages

- [01 - Language model probability](./01-language-model-probability.md) - how $p(x_t \mid x_{<t}; \theta)$ becomes $\pi_\theta(a_t \mid s_t)$ once the output space is structured actions.
- [05 - MDP / POMDP intuition](./05-mdp-pomdp.md) - the formal environment model.
- [06 - The ReAct loop, formalized](./06-react-formalization.md) - how the policy framing specializes to ReAct.
- [07 - Tool selection as function selection](./07-tool-selection.md) - what happens inside the action space.
- [Notation reference](./notation.md) - full symbol glossary.

## References

- Sutton, R. S., and Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press, Ch. 3. [Free online](http://incompleteideas.net/book/the-book-2nd.html). Origin of the policy / state / action vocabulary.
- Kaelbling, L. P., Littman, M. L., and Cassandra, A. R. (1998). [*Planning and Acting in Partially Observable Stochastic Domains*](https://www.sciencedirect.com/science/article/pii/S000437029800023X). Artificial Intelligence Journal 101(1-2). The canonical POMDP reference.
- Sumers, T. R., Yao, S., Narasimhan, K., and Griffiths, T. L. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR. Argues for the agent-as-policy framing in the LLM context specifically.
- Yao, S., et al. (2022). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023. The first popular implementation of the loop in this exact form for LLMs.
