# The ReAct pattern

> 🟢 Stable · ⏱ ~10 min read · 🏷 agents, reasoning, tool-use

## TL;DR

**ReAct** — *Reasoning + Acting* — is a prompting pattern where the model interleaves natural-language **thoughts** with **tool calls** and **observations**. The shape is `Thought → Action → Observation → Thought → Action → …` until a final answer. It comes from Yao et al. (ICLR 2023) and has become the default scaffolding for tool-using LLM agents. Most modern frameworks (LangGraph's `create_react_agent`, ADK, CrewAI) implement a variant of it whether they label it that way or not.

The point of writing thoughts isn't to log the model's "reasoning" for the human reader — it's to give the model a place to plan, self-correct, and stay grounded as the context grows.

---

## The pattern

A single ReAct step looks like:

```
Thought: I need to check whether the user's library is on PyPI before recommending it.
Action: web_search
Action Input: {"query": "pypi pkg-name"}
Observation: Found pypi.org/project/pkg-name — version 1.4.2, last updated 2 days ago.
Thought: The package exists and is recent. I can recommend it.
Final Answer: Yes, `pkg-name` is published on PyPI at version 1.4.2.
```

In a modern function-calling API, the "Action / Action Input" lines get replaced by the API's native tool-call schema (JSON or protobuf), and the framework handles the dispatch. The *thought* either stays in the message content alongside the structured tool call, or rides as part of a "reasoning" channel that the model exposes.

Three things distinguish ReAct from a plain function-calling loop:

1. **The thought is emitted before the action**, not after. The model commits to a plan, then acts on it. Reversing the order tends to produce post-hoc rationalizations that don't constrain the action.
2. **The observation is part of the same conversation**, not hidden. The model sees the actual result and reasons about it explicitly in the next thought.
3. **The loop is open-ended** in step count. The pattern itself doesn't say "stop after 5 steps"; it says "keep going until the answer is final." Hard stops are the agent runtime's job, not the prompt's.

---

## Why interleave thoughts and actions?

You could imagine three simpler designs:

- **Just acting.** The model emits tool calls with no commentary. Faster, cheaper, but the model has no inner workspace. It can't say "wait, that didn't work, let me try a different angle" — it just emits the next call. Reliability collapses on tasks longer than a few steps.
- **Just reasoning, then one big action.** The model writes a plan, then a single tool sequence. Loses the ability to *adapt to observations*. If step 2 returns nothing useful, the model still tries to execute step 3 because the plan was committed.
- **Acting, then reasoning post-hoc.** The model takes an action, then explains it. The explanation has no effect on future actions because it came after them. Useful for logging, useless for steering behavior.

The ReAct ordering — think, then act, then observe, then think again — is the smallest design that makes the model *responsive to what actually happens*. The thought before the next action is the place where the model integrates the latest observation into its plan.

The Yao et al. paper showed this empirically: on HotpotQA, ReAct cut hallucination versus reasoning-only chains, and it outperformed acting-only baselines on ALFWorld and WebShop, in many cases approaching task-completion rates that pure-action methods couldn't reach. The mechanism is intuitive once you've seen the loop: thoughts give the model error-recovery affordance.

---

## How it shows up in practice

In a real codebase, a ReAct agent has three moving parts beyond what the basic [agent loop](./agent-loop.md) requires:

### 1. A prompt that elicits thoughts

The classic ReAct prompt has explicit `Thought:` / `Action:` / `Observation:` markers and few-shot examples. Modern function-calling APIs make most of this implicit — you just include "Think step by step before calling a tool" in the system prompt and the model produces thoughts in the `content` channel alongside its structured tool calls. The few-shot scaffolding from the original paper is rarely necessary with GPT-4-class models.

A useful system prompt is short and behavioral:

```
You are a tool-using assistant. For every step, first state your reasoning in
one or two sentences, then call the most appropriate tool. After observing the
result, decide whether to call another tool or give a final answer. Be concise
in both thoughts and final answers.
```

That's it. The model knows the pattern from training; the prompt just permits it.

### 2. A loop that surfaces observations cleanly

When the tool returns, you append a clearly-labeled observation to the conversation. The exact format matters less than the consistency:

```python
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": format_observation(result),
})
```

`format_observation` is where you compress, redact, or summarize. A raw 50KB JSON response is observation noise; a five-line extracted summary is observation signal. We come back to this in [Context Engineering](../context/token-budgets.md).

### 3. Termination conditions

ReAct's spec doesn't define them; the runtime does. The minimum set, in this order of precedence:

1. **Step cap.** Always. `max_steps=8` is a sane default for tutorials; production agents typically run 10–50 depending on task class.
2. **Final answer detected.** If the model emits a non-tool response, return it.
3. **Repeated action detection.** If the model calls the same tool with the same arguments twice in a row, the agent is stuck. Either inject a "you've tried this; try a different approach" message or terminate.
4. **Budget cap.** Token or dollar limit per run.

We implement all four in [Lab 01](../../labs/01-first-agent-from-scratch/).

---

## When ReAct is the right pattern

ReAct shines on tasks that need *multiple tool calls whose interpretations depend on each other*:

- **Open-domain Q&A.** Find a fact, use it to query the next thing, synthesize.
- **Web research.** Search, read, follow up, cite. (Today's "deep research" features are elaborate ReAct loops.)
- **Data analysis.** Inspect a dataframe, decide what to plot, plot, decide what to summarize.
- **Code agents.** Read a file, run a test, see what fails, edit, repeat.

A useful generalization: *ReAct is the right pattern whenever the agent's next move materially depends on the previous observation.* If your task is a fixed sequence of "search → format → return," you don't need ReAct — you need a pipeline.

---

## When it isn't

ReAct underperforms or wastes resources when:

- **The task is deterministic.** Use a pipeline. ReAct adds latency and cost with no benefit.
- **Tools are expensive and the task is simple.** Every "Thought" is a forward pass. For one-tool, one-step tasks, function calling without explicit thought scaffolding is fine.
- **You need a guaranteed plan structure.** ReAct decides what to do *one step at a time*. If you need an auditable plan up front, use [plan-and-execute](../../patterns/06-plan-and-execute.md) instead.
- **The tool returns a huge artifact you need to reason over.** Loading a 200KB blob into the next thought is wasteful. Add a retrieval or summarization step between tool and observation.

---

## Common failure modes

- **Thought-action mismatch.** The model writes "I should now check X" and then calls a tool that does Y. Cause: the model has cached an earlier plan and is following it instead of the current thought. Fix: shorter thoughts, or prompt that explicitly says "your action must follow from this turn's thought."
- **Endless reasoning, no action.** The model writes paragraphs of thought and never calls a tool. Cause: temperature too high, or the model is unsure which tool fits. Fix: lower temperature, force tool choice with the API's `tool_choice="required"` parameter for the first step.
- **Action without reading the last observation.** The model calls a tool whose result was already returned. Cause: observation got buried in context, or the observation format isn't distinctive enough. Fix: clearer observation labels, summarization, or pinning the last observation at the top of the next prompt.
- **Premature finalization.** The model gives a final answer before it has enough information. Cause: prompt rewards completeness over caution. Fix: explicit "if you're not confident, call a tool to verify" guidance.

---

## 🧮 Math behind it

A ReAct loop can be written as a sequence of policy invocations $\pi_\theta(a_t \mid s_t)$ where the action space includes both *tool calls* and *terminal responses*, and the state at step $t+1$ is the previous state augmented with the latest thought, action, and observation. The formal version, with state transitions and termination, lives in the math-foundations page below.

→ Full treatment: [`math-foundations/06-react-formalization.md`](../../math-foundations/06-react-formalization.md)

---

## See also

- 📖 [What is an agent?](./what-is-an-agent.md) — the broader framing.
- 📖 [Agent loop](./agent-loop.md) — the four-step cycle ReAct specializes.
- 📖 [Plan-and-execute](../../patterns/06-plan-and-execute.md) — the alternative when you need an auditable plan first.
- 🧪 [Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/) — build a ReAct loop end-to-end with no framework.
- 🏛 [Single-agent tool-use pattern](../../patterns/01-single-agent-tool-use.md) — the architectural pattern this concept sits inside.
- 🧮 [ReAct formalization](../../math-foundations/06-react-formalization.md) — the mathematical version.

---

## References

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR 2023. **The** paper. Read it.
- Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., & Zhou, D. (2022). [*Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*](https://arxiv.org/abs/2201.11903). NeurIPS 2022. ReAct's reasoning component generalizes CoT to interactive settings.
- Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., & Yao, S. (2023). [*Reflexion: Language Agents with Verbal Reinforcement Learning*](https://arxiv.org/abs/2303.11366). NeurIPS 2023. An important refinement: agents that critique their own outputs and retry.
- UC Berkeley CS294/194-196 *LLM Agents*, Fall 2024 — Shunyu Yao's lecture *LLM agents: brief history and overview*. [Course page](https://rdi.berkeley.edu/llm-agents/f24).
