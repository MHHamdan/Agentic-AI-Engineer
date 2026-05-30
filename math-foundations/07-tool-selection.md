# Tool selection as function selection

> 🧮 Mathematical foundation · ⏱ ~7 min read · Anchor: [`concepts/tools/`](../concepts/tools/)

## The equation

A tool-using agent at step $t$ samples an action from the policy:

$$
a_t \;\sim\; \pi_\theta(\cdot \mid s_t),
$$

where the action space $\mathcal{A}$ partitions into the tool surface plus a terminal response:

$$
\mathcal{A} \;=\; \big\{ \text{respond}(y) \big\} \,\cup\, \bigcup_{i=1}^{N} \big\{ \text{tool}_i(\mathbf{args}) : \mathbf{args} \in \text{Schema}_i \big\}.
$$

In words: the agent either responds with a final answer $y$, or calls one of $N$ tools with arguments conforming to that tool's schema. The act of "choosing a tool" is sampling from $\pi_\theta$ over this structured space.

Modern function-calling APIs implement this through **constrained decoding**: the model's token distribution is restricted to valid (tool name, JSON schema) emissions, so $\pi_\theta(a_t \mid s_t)$ is automatically a distribution over $\mathcal{A}$.

---

## Mathematical intuition

Three things to internalize.

**Tool selection is the same operation as next-token prediction, with extra structure on the output space.** Without tool calling, $\pi_\theta$ produces token sequences. With tool calling, $\pi_\theta$ produces a structured object — a tool name and its arguments. The model is doing the same thing internally; the API surfaces a more useful output.

**The size of $\mathcal{A}$ matters.** Each additional tool widens the action space, and $\pi_\theta$ has to learn (or be prompted) to put probability mass on the right one. Empirically, agent quality degrades with too many tools — past roughly 10-20 tools per agent, the probability of choosing the right tool drops noticeably. This is the canonical reason for **multi-agent decomposition**: each specialist agent sees a smaller, more relevant $\mathcal{A}$.

**Argument selection is a separate distribution.** Given a tool choice, the model still has to fill in arguments — query strings, file paths, parameter values. Formally:

$$
\pi_\theta\big(\text{tool}_i(\mathbf{args}) \mid s_t\big) \;=\; \pi_\theta\big(\text{tool}_i \mid s_t\big) \cdot \pi_\theta\big(\mathbf{args} \mid s_t,\, \text{tool}_i\big).
$$

This factorization is why **tool descriptions** and **argument schemas** are different controls. Descriptions shape $\pi_\theta(\text{tool}_i \mid s_t)$ (which tool to pick). Argument schemas shape $\pi_\theta(\mathbf{args} \mid s_t, \text{tool}_i)$ (how to call it).

---

## Why it matters for engineers

Four practical implications:

1. **Tool description quality is upstream of tool-choice quality.** $\pi_\theta(\text{tool}_i \mid s_t)$ depends almost entirely on (a) the tool name and (b) the tool description. A tool called `search` with description "Searches" gets confused with every other search tool the agent has. A tool called `web_search` with description "Searches the public web for recent news; returns top 5 result snippets" gets chosen correctly. Naming + describing tools is high-impact work.

2. **Schema design constrains argument quality.** Tight JSON schemas (enums for fixed choices, `pattern` constraints on strings, `minimum`/`maximum` on numbers) sharply reduce malformed tool calls. Loose schemas (`string` everywhere) push the burden onto the LLM's training and your error-handling code.

3. **Tool overlap is the canonical multi-tool failure mode.** When two tools could plausibly serve the same query, $\pi_\theta$ may split probability between them, choosing randomly. Defense: either consolidate (one tool with a parameter that distinguishes the variants) or specialize (more distinct names + descriptions). See [`patterns/02-router.md`](../patterns/02-router.md).

4. **Restricting $\mathcal{A}$ is a real control surface.** Forcing `tool_choice="required"` removes the terminal-respond option from $\mathcal{A}$ — the model *must* call a tool. Forcing `tool_choice={"name": "specific_tool"}` collapses $\mathcal{A}$ to one element. These are blunt controls but operationally useful for orchestration code that needs to guarantee certain steps happen.

---

## Where you'll see it in the code

From [Lab 01](../labs/01-first-agent-from-scratch/), tool selection is a single API call with `tools` as a parameter:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=state,
    tools=[                       # The N elements of the tool surface
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the public web. Returns top 5 result snippets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"],
                },
            },
        },
        # ... more tools
    ],
    tool_choice="auto",           # auto | required | {"name": "..."}
    temperature=0,                # deterministic tool selection
)

# The response either contains tool_calls (one or more) or a text response.
# Sampling a_t ~ pi_theta(. | s_t) is exactly the API call above.
```

For [Path 04 MCP](../learning-paths/04-tool-protocols-mcp-a2a/), the tool surface comes from MCP servers — the same equation applies; only the source of the tool definitions changes. See [Project 05 — Multi-server MCP agent](../projects/intermediate/05-multi-server-mcp-agent/) for the tool-collision failure mode in detail.

---

## See also

- 📖 [What's a tool?](../concepts/tools/tool-selection.md) — the concept this formalizes.
- 🧮 [Agents as policies](./04-agents-as-policies.md) — the broader policy framing.
- 🧮 [ReAct formalization](./06-react-formalization.md) — how tool selection fits inside the ReAct loop.
- 🧪 [Lab 01](../labs/01-first-agent-from-scratch/) — implements tool calling directly.
- 📖 [Glossary — Tool, Tool calling, Function calling, Tool collision](../glossary/terms.md).

---

## Sources

- Schick, T., et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS. Established the modern formulation of tools as a sampled action from the LM's distribution.
- Patil, S. G., et al. (2023). [*Gorilla: Large Language Model Connected with Massive APIs*](https://arxiv.org/abs/2305.15334). The first systematic treatment of tool-selection failures with large $|\mathcal{A}|$ and a benchmark for measuring them.
- Qin, Y., et al. (2023). [*ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs*](https://arxiv.org/abs/2307.16789). Explores the scaling problem — what happens when $N$ gets very large.
- OpenAI. (2023+). [*Function Calling Documentation*](https://platform.openai.com/docs/guides/function-calling). The canonical API specification for constrained-decoding tool calls.
