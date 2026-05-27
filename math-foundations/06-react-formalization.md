# The ReAct loop, formalized

> 🧮 Mathematical foundation · ⏱ ~8 min read · Anchor: [`concepts/agents/react-pattern.md`](../concepts/agents/react-pattern.md)

## The equation

ReAct is the policy framing of [`04-agents-as-policies.md`](./04-agents-as-policies.md) with the action space partitioned into three components per step: a **thought**, a **tool action**, and a **terminal flag**.

A single ReAct step:

$$
\big(\tau_t,\, a_t,\, \text{stop}_t\big) \sim \pi_\theta(\cdot \mid s_t),
$$

with state update

$$
s_{t+1} \;=\; s_t \,\cup\, \{\tau_t,\, a_t,\, o_t\},
$$

terminating when $$\text{stop}_t = \text{True}$ or $t = T_{\max}$$.

The symbols, in order:

- $\tau_t$ — the **thought** emitted at step $t$. A natural-language string appended to the state but never executed.
- $a_t$ — the **action**. Either a tool call (a `(name, args)` pair) or a "respond" action carrying a final answer.
- $o_t$ — the **observation** that results from executing $a_t$. Empty for the terminal response.
- $\text{stop}_t$ — a Boolean flag indicating that this step's action is terminal.
- $T_{\max}$ — the maximum number of steps the runtime will allow.

The full trajectory of a ReAct run is:

$$
\big(\tau_1, a_1, o_1,\; \tau_2, a_2, o_2,\; \ldots,\; \tau_T, a_T\big),
$$

where the final $a_T$ is a terminal response and there is no $o_T$.

---

## Mathematical intuition

ReAct is a specific factorization of the policy. The same equation $\pi_\theta(a_t \mid s_t)$ from [`04-agents-as-policies.md`](./04-agents-as-policies.md) governs both ReAct and non-ReAct agents — but ReAct *splits* the per-step output into a thought plus an action.

Three things this factorization buys you:

**An autoregressive workspace.** The thought $\tau_t$ is generated *first*, then the action conditions on it. Concretely, the model autoregressively produces tokens for the thought before producing the structured tool call, so we can write the joint as:

$$
\pi_\theta(\tau_t, a_t \mid s_t) \;=\; \pi_\theta(\tau_t \mid s_t) \cdot \pi_\theta(a_t \mid s_t, \tau_t).
$$

That second factor — *the action distribution conditional on the thought* — is the technical reason ReAct works. The model is choosing an action under a more refined conditioning context than a "no-thought" agent would.

**Free integration of observations.** Because $s_{t+1}$ includes $o_t$, the next thought $\tau_{t+1}$ is conditioned on what just happened. Without the explicit thought, the action might be selected directly from $s_{t+1}$, but the model has no slot in which to reason about $o_t$ before committing to $a_{t+1}$. The thought gives that reasoning a place to live in the state.

**A natural stopping condition.** Termination is just one possible action, not a separate mechanism. The model emits a "respond" action when $s_t$ contains enough information to answer. This is cleaner than external classifiers ("is the agent done?") and matches the empirical behavior of modern function-calling APIs, which expose a "no tool call needed" branch automatically.

---

## Why it matters for engineers

The formal split has three practical implications you'll use repeatedly:

1. **You can prompt the thought distribution independently of the action distribution.** A system message like "First state your reasoning in one or two sentences, then call the most appropriate tool" specifically shapes $\pi_\theta(\tau_t \mid s_t)$. A few-shot example showing concise thoughts specifically shapes the *shape* of thoughts the model emits. These are different controls than tool-description prompting, which shapes $\pi_\theta(a_t \mid s_t, \tau_t)$.

2. **You can introspect $\tau_t$ in a way you can't introspect raw weights.** Thoughts are surface-level natural language. They're the agentic-AI equivalent of `print` debugging: imperfect but real. Logging $\tau_t$ on every step is the highest-leverage observability investment you can make. (Frameworks like LangSmith expose this automatically — that's covered in the Evaluation & Observability path.)

3. **Failure modes have explicit names in this formalism**:
   - "Thought-action mismatch" — high $\pi_\theta(\tau_t \mid s_t)$ but inconsistent $\pi_\theta(a_t \mid s_t, \tau_t)$. The model thought one thing and acted another.
   - "Endless reasoning" — $\pi_\theta(\text{stop}_t \mid s_t) \approx 0$ for many steps even when the state contains a defensible answer.
   - "Action without observation integration" — $\tau_{t+1}$ doesn't condition meaningfully on $o_t$ (the model ignored the result of its last action).

   Each one suggests a different fix, because they affect different factors of the joint distribution.

---

## Where you'll see it in the code

From [Lab 01](../labs/01-first-agent-from-scratch/), the inner loop maps directly to the formalism:

```python
for t in range(MAX_STEPS):
    # Sample (tau_t, a_t, stop_t) ~ pi_theta(. | s_t)
    response = client.chat.completions.create(
        model=MODEL,
        messages=state,                 # s_t
        tools=tool_schemas,
        tool_choice="auto",
    )
    msg = response.choices[0].message

    # tau_t lives in msg.content; a_t in msg.tool_calls; stop_t is implicit
    state.append(msg)                    # appends tau_t and the action choice

    if not msg.tool_calls:
        return msg.content              # stop_t = True; this is the terminal response

    # Execute each tool call and append o_t for each
    for call in msg.tool_calls:
        result = execute_tool(call, tools)
        state.append({                   # appends o_t
            "role": "tool",
            "tool_call_id": call.id,
            "content": format_observation(result),
        })
```

The variable `state` is $s_t$. Each iteration applies $\pi_\theta$, appends the sampled output, executes any tool actions, and appends the resulting observations. The state-update equation $s_{t+1} = s_t \cup \{\tau_t, a_t, o_t\}$ is the `state.append(...)` lines, in order.

A subtle but important detail: modern APIs let a single $a_t$ be a *set* of tool calls executed in parallel. The formalism above shows one tool call per step for clarity; with parallel calls, $a_t$ becomes a set $\{a_t^{(1)}, \ldots, a_t^{(k)}\}$ and the observation becomes a set $\{o_t^{(1)}, \ldots, o_t^{(k)}\}$, joined into the state. The shape of the equation doesn't change.

---

## Caveats worth marking

A few things this formalization elides for clarity:

- **The thought is not always cleanly separable from the action.** In some API designs, the thought tokens and the tool-call tokens are emitted in one stream and you only conceptually distinguish them. In others (Anthropic's "thinking" channel, OpenAI's reasoning models), there's an explicit separate field. The math is the same; the implementation surface differs.
- **Stop is not always a single Boolean.** Real runtimes also stop on step caps, repeated-action detection, and budget caps. We folded those into the "if $t = T_{\max}$" clause, but production-grade stopping is a small state machine.
- **The "state" includes more than the conversation.** Tool schemas, the system prompt, and any retrieved context are all part of $s_t$ for purposes of the policy distribution — they shape $\pi_\theta$'s output. We elide that for notation but it's there.

These caveats matter when you're debugging a real agent and trying to identify which factor of the joint distribution is misbehaving. The clean formalism is the right starting point; the messy reality is what your CI catches.

---

## See also

- 📖 [ReAct pattern](../concepts/agents/react-pattern.md) — the engineering view of this formalism.
- 🧮 [Agents as policies](./04-agents-as-policies.md) — the general framing this specializes.
- 🧮 [Notation reference](./notation.md) — full symbol glossary.
- 🧪 [Lab 01](../labs/01-first-agent-from-scratch/) — the code expression.

---

## Sources

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023. **Primary source.** Equations and trajectory definition in this page follow the paper's framing.
- Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR 2024. Generalizes the thought/action split to a broader class of agent architectures.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. For the policy / state / action vocabulary used throughout.
