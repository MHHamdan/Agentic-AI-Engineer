# The ReAct loop, formalized

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/agents/react-pattern.md`](../concepts/agents/react-pattern.md).

## Why this matters for agentic AI

ReAct is the architectural ancestor of every modern agent loop. Knowing how it factors the per-step policy into a *thought* plus an *action* gives you three concrete controls that show up in every framework: how to prompt the reasoning step, how to inspect what the agent was thinking, and how to spot specific failure modes by name.

## The equation

ReAct is the policy framing of [page 04](./04-agents-as-policies.md) with the action space partitioned into three components per step: a **thought**, a **tool action**, and a **terminal flag**.

A single ReAct step:

$$
(\tau_t, a_t, \text{stop}_t) \sim \pi_\theta(\cdot \mid s_t),
$$

with state update:

$$
s_{t+1} = s_t \cup \{\tau_t, a_t, o_t\},
$$

terminating when $\text{stop}_t = \text{True}$ or $t = T_{\max}$.

**Symbols:**

- $\tau_t$ - the **thought** emitted at step $t$. A natural-language string appended to the state but never executed.
- $a_t$ - the **action**. Either a tool call (a `(name, args)` pair) or a "respond" action carrying a final answer.
- $o_t$ - the **observation** that results from executing $a_t$. Empty for the terminal response.
- $\text{stop}_t$ - a Boolean flag indicating that this step's action is terminal.
- $T_{\max}$ - the maximum number of steps the runtime will allow.

The full trajectory of a ReAct run is:

$$
(\tau_1, a_1, o_1, \tau_2, a_2, o_2, \ldots, \tau_T, a_T),
$$

where the final $a_T$ is a terminal response and there is no $o_T$.

## How to read this equation

Per-step output is a *triple*: a thought, an action, and a stop flag. All three are sampled together from one LLM call. The model emits tokens that the runtime parses into these three components, usually with the help of function-calling APIs that enforce the action structure.

The state-update equation just says the new state is the old state with the new thought, action, and observation appended. The conversation keeps growing until the model emits a stop flag or the runtime hits its step budget.

## Mathematical intuition

ReAct is a specific factorization of the policy. The same equation $\pi_\theta(a_t \mid s_t)$ from [page 04](./04-agents-as-policies.md) governs both ReAct and non-ReAct agents, but ReAct *splits* the per-step output into a thought plus an action.

Three things this factorization buys you.

**An autoregressive workspace.** The thought $\tau_t$ is generated *first*, then the action conditions on it. Concretely, the model autoregressively produces tokens for the thought before producing the structured tool call, so we can write the joint as:

$$
\pi_\theta(\tau_t, a_t \mid s_t) = \pi_\theta(\tau_t \mid s_t) \cdot \pi_\theta(a_t \mid s_t, \tau_t).
$$

That second factor, *the action distribution conditional on the thought*, is the technical reason ReAct works. The model is choosing an action under a more refined conditioning context than a "no-thought" agent would.

**Free integration of observations.** Because $s_{t+1}$ includes $o_t$, the next thought $\tau_{t+1}$ is conditioned on what just happened. Without the explicit thought, the action might be selected directly from $s_{t+1}$, but the model has no slot in which to reason about $o_t$ before committing to $a_{t+1}$. The thought gives that reasoning a place to live in the state.

**A natural stopping condition.** Termination is just one possible action, not a separate mechanism. The model emits a "respond" action when $s_t$ contains enough information to answer. This is cleaner than external classifiers ("is the agent done?") and matches the empirical behavior of modern function-calling APIs, which expose a "no tool call needed" branch automatically.

## Where this appears in agentic systems

The formal split has three practical implications you will use repeatedly:

1. **You can prompt the thought distribution independently of the action distribution.** A system message like "First state your reasoning in one or two sentences, then call the most appropriate tool" specifically shapes $\pi_\theta(\tau_t \mid s_t)$. A few-shot example showing concise thoughts shapes the *shape* of thoughts the model emits. These are different controls than tool-description prompting, which shapes $\pi_\theta(a_t \mid s_t, \tau_t)$.
2. **You can introspect $\tau_t$ in a way you cannot introspect raw weights.** Thoughts are surface-level natural language. They are the agentic-AI equivalent of `print` debugging: imperfect but real. Logging $\tau_t$ on every step is one of the highest-value observability investments you can make. Frameworks like LangSmith expose this automatically; the Evaluation and Observability path covers it in detail.
3. **Failure modes have explicit names in this formalism**:
    - "Thought-action mismatch" - high $\pi_\theta(\tau_t \mid s_t)$ but inconsistent $\pi_\theta(a_t \mid s_t, \tau_t)$. The model thought one thing and acted another.
    - "Endless reasoning" - $\pi_\theta(\text{stop}_t \mid s_t)$ is near zero for many steps even when the state contains a defensible answer.
    - "Action without observation integration" - $\tau_{t+1}$ does not condition meaningfully on $o_t$ (the model ignored the result of its last action).

Each one suggests a different fix because they affect different factors of the joint distribution.

## Code example

A minimal ReAct loop that surfaces the thought-action split explicitly.

```python
from openai import OpenAI

client = OpenAI()
MAX_STEPS = 5

REACT_SYSTEM = """You are a helpful agent.
At each step, first say one sentence of reasoning starting with "Thought: ".
Then either call a tool or respond. Keep thoughts short.
"""

def step(state, tools):
    """Sample (tau_t, a_t, stop_t) ~ pi_theta(. | s_t) in a single LLM call."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state,
        tools=[t["schema"] for t in tools.values()],
        tool_choice="auto",
        temperature=0,
    )
    msg = response.choices[0].message
    # The thought tau_t lives in msg.content (free text).
    # The action a_t lives in msg.tool_calls (structured) or in msg.content (terminal).
    # stop_t is implicit: True iff no tool_calls.
    return msg

def run_react(query, tools):
    state = [
        {"role": "system", "content": REACT_SYSTEM},
        {"role": "user", "content": query},
    ]
    for t in range(MAX_STEPS):
        msg = step(state, tools)
        state.append(msg.model_dump())
        thought = (msg.content or "").strip()
        print(f"[t={t}] tau_t: {thought[:80]!r}")

        if not msg.tool_calls:
            return msg.content                  # terminal action

        for call in msg.tool_calls:
            obs = tools[call.function.name]["fn"](call.function.arguments)
            print(f"[t={t}] o_t:   {str(obs)[:80]!r}")
            state.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(obs),
            })
    return "max steps exceeded"
```

The `step` function is exactly $(\tau_t, a_t, \text{stop}_t) \sim \pi_\theta(\cdot \mid s_t)$ in one API call. Modern function-calling models do the thought-action split for you; older models needed careful prompting with stop tokens to enforce the structure.

## Common mistakes

- **Treating the thought as an output to the user.** Thoughts are internal scaffolding. Showing them to end users is usually a UX mistake (they look uncertain or weird). Log them for debugging; do not expose them.
- **Letting thoughts grow without bound.** A model that produces five-paragraph thoughts at every step burns context fast. Cap thought length with a system message instruction or a tokens-per-thought soft limit.
- **Forgetting that the thought conditions the action.** If the prompt encourages over-cautious reasoning, the action distribution drifts toward over-cautious behavior (excessive clarification questions, refusals, no-op tool calls). The fix is the thought prompt, not the tool descriptions.
- **Misreading the stopping behavior.** Modern function-calling APIs decide internally whether to call a tool or respond. You cannot force a stop without restricting the action space (`tool_choice="none"`), and even then the model may produce a question instead of an answer.

## Repo cross-references

- [Lab 01 - First agent from scratch](../labs/01-first-agent-from-scratch/) - the inner loop maps directly to the formalism.
- [`concepts/agents/react-pattern.md`](../concepts/agents/react-pattern.md) - the concept this formalizes.
- [`patterns/01-single-agent-tool-use.md`](../patterns/01-single-agent-tool-use.md) - ReAct as a deployable pattern.
- [`patterns/07-reflection.md`](../patterns/07-reflection.md) - what happens when the agent reflects on its own thoughts.

## Related pages

- [04 - Agents as policies](./04-agents-as-policies.md) - the underlying policy formalism this specializes.
- [07 - Tool selection as function selection](./07-tool-selection.md) - what happens inside $a_t$.
- [08 - Planning and search](./08-planning-search.md) - what to do when one ReAct step is not enough.
- [Glossary: ReAct, Reflection, Tool calling](../glossary/terms.md) - short definitions.

## References

- Yao, S., et al. (2022). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023. The original ReAct paper; introduces the interleaved reasoning-and-acting pattern.
- Wei, J., et al. (2022). [*Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*](https://arxiv.org/abs/2201.11903). NeurIPS 2022. The reasoning side of ReAct; pre-dates ReAct and motivates the "Thought:" prefix.
- Shinn, N., et al. (2023). [*Reflexion: Language Agents with Verbal Reinforcement Learning*](https://arxiv.org/abs/2303.11366). NeurIPS 2023. Extends ReAct with self-reflection on failed trajectories.
- OpenAI. [*Function calling guide*](https://platform.openai.com/docs/guides/function-calling). The API surface that implements the thought-action factoring in the code example.
