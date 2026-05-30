# Tool selection as function selection

> Mathematical foundation. About 8 minutes to read. Anchor: [`concepts/tools/`](../concepts/tools/).

## Why this matters for agentic AI

Tool selection is where most agent quality issues live. Wrong tool, wrong arguments, hallucinated tool names. The math shows that tool description quality and argument schema design are *different controls* on different parts of the distribution, which lets you diagnose problems systematically instead of by guesswork.

## The equation

A tool-using agent at step $t$ samples an action from the policy:

$$
a_t \sim \pi_\theta(\cdot \mid s_t),
$$

where the action space $\mathcal{A}$ partitions into the tool surface plus a terminal response:

$$
\mathcal{A} = \{\text{respond}(y)\} \cup \bigcup_{i=1}^{N} \{\text{tool}_i(\mathbf{args}) : \mathbf{args} \in \text{Schema}_i\}.
$$

**Symbols:**

- $\pi_\theta(\cdot \mid s_t)$ - the policy.
- $\mathcal{A}$ - the action space.
- $\text{respond}(y)$ - terminal action carrying a final answer.
- $\text{tool}_i$ - the $i$-th tool (out of $N$).
- $\text{Schema}_i$ - the JSON schema for tool $i$'s arguments.
- $\mathbf{args}$ - a valid arguments object conforming to $\text{Schema}_i$.

The agent either responds with a final answer or calls one of $N$ tools with arguments conforming to that tool's schema. The act of "choosing a tool" is sampling from $\pi_\theta$ over this structured space.

Modern function-calling APIs implement this through **constrained decoding**: the model's token distribution is restricted to valid `(tool name, JSON schema)` emissions, so $\pi_\theta(a_t \mid s_t)$ is automatically a distribution over $\mathcal{A}$.

## How to read this equation

Read $\mathcal{A}$ as a union of disjoint "branches": one for terminal response, and one for each tool. The model picks a branch, then fills in the arguments within that branch. The argument schema controls what valid arguments look like; the tool description influences which branch the model picks in the first place.

We can factor the per-tool selection probability:

$$
\pi_\theta(\text{tool}_i(\mathbf{args}) \mid s_t) = \pi_\theta(\text{tool}_i \mid s_t) \cdot \pi_\theta(\mathbf{args} \mid s_t, \text{tool}_i).
$$

This factorization tells you that "wrong tool" and "wrong arguments" are two separable failure modes with two separate fixes.

## Mathematical intuition

Three things to internalize.

**Tool selection is the same operation as next-token prediction, with extra structure on the output space.** Without tool calling, $\pi_\theta$ produces token sequences. With tool calling, $\pi_\theta$ produces a structured object: a tool name and its arguments. The model is doing the same thing internally; the API surfaces a more useful output.

**The size of $\mathcal{A}$ matters.** Each additional tool widens the action space, and $\pi_\theta$ has to learn (or be prompted) to put probability mass on the right one. Empirically, agent quality degrades with too many tools. Past roughly 10 to 20 tools per agent, the probability of choosing the right tool drops noticeably. This is the canonical reason for **multi-agent decomposition**: each specialist agent sees a smaller, more relevant $\mathcal{A}$.

**Argument selection is a separate distribution.** Given a tool choice, the model still has to fill in arguments: query strings, file paths, parameter values. The factorization above is why **tool descriptions** and **argument schemas** are different controls. Descriptions shape $\pi_\theta(\text{tool}_i \mid s_t)$ (which tool to pick). Argument schemas shape $\pi_\theta(\mathbf{args} \mid s_t, \text{tool}_i)$ (how to call it).

## Where this appears in agentic systems

Four practical implications you will act on:

1. **Tool description quality is upstream of tool-choice quality.** $\pi_\theta(\text{tool}_i \mid s_t)$ depends almost entirely on (a) the tool name and (b) the tool description. A tool called `search` with description "Searches" gets confused with every other search tool the agent has. A tool called `web_search` with description "Searches the public web for recent news; returns top 5 result snippets" gets chosen correctly. Naming and describing tools is high-impact work.
2. **Schema design constrains argument quality.** Tight JSON schemas (enums for fixed choices, `pattern` constraints on strings, `minimum`/`maximum` on numbers) sharply reduce malformed tool calls. Loose schemas (`string` everywhere) push the burden onto the LLM's training and your error-handling code.
3. **Tool overlap is the canonical multi-tool failure mode.** When two tools could plausibly serve the same query, $\pi_\theta$ may split probability between them, choosing randomly. Defense: either consolidate (one tool with a parameter that distinguishes the variants) or specialize (more distinct names and descriptions). See [`patterns/02-router.md`](../patterns/02-router.md).
4. **Restricting $\mathcal{A}$ is a real control surface.** Forcing `tool_choice="required"` removes the terminal-respond option from $\mathcal{A}$. The model must call a tool. Forcing `tool_choice={"name": "specific_tool"}` collapses $\mathcal{A}$ to one element. These are blunt controls but operationally useful for orchestration code that needs to guarantee certain steps happen.

## Code example

Define two tools with deliberately overlapping coverage to see selection in action.

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the public web. Returns top 5 result snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a math expression. Supports +, -, *, /, **, parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr": {
                        "type": "string",
                        "description": "Arithmetic expression.",
                        "pattern": r"^[\d\s\.\+\-\*\/\(\)\*\*]+$",
                    },
                },
                "required": ["expr"],
            },
        },
    },
]

def select(user_query: str):
    """Sample a_t ~ pi_theta(. | s_t) over the union of tools + respond."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_query}],
        tools=tools,
        tool_choice="auto",          # auto | required | {"name": "..."}
        temperature=0,
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        call = msg.tool_calls[0]
        return (call.function.name, call.function.arguments)
    return ("respond", msg.content)

print(select("What is 17 * 23?"))           # -> ("calculator", {"expr": "17 * 23"})
print(select("Who is the president of France today?"))   # -> ("web_search", ...)
print(select("Tell me a joke."))             # -> ("respond", ...)
```

The `pattern` constraint on the `calculator` argument rejects natural-language input. The schema is doing real work: without it, the model often passes `"What is 17 times 23"` as the `expr`, and the calculator fails.

## Common mistakes

- **Naming a tool just `search`.** It collides with everyone's mental model of "the search tool." Prefix with the source: `web_search`, `vector_search`, `arxiv_search`. The model's tool-choice distribution improves immediately.
- **Stuffing all functionality into one mega-tool.** A tool with 12 optional parameters and "do anything with the database" as a description gives the model nothing to disambiguate on. Split into 3 to 5 specific tools instead.
- **Loose schemas everywhere.** Each `string` parameter without constraints is an opportunity for the model to pass natural language where you wanted a structured value. Add `enum`, `pattern`, `minimum`, `maximum`, and `format` (`date-time`, `email`, `uri`) wherever appropriate.
- **Trying to "force" a tool with prompting instead of `tool_choice`.** If the orchestration needs a specific tool to be called, set `tool_choice={"name": "..."}`. Prompt-based forcing is fragile and adds tokens.

## Repo cross-references

- [Lab 02 - Tool design and selection](../labs/02-tool-design-and-selection/) - implements tool calling directly with deliberate failure modes.
- [`concepts/tools/tool-design.md`](../concepts/tools/tool-design.md) - the engineering view.
- [`concepts/tools/tool-selection.md`](../concepts/tools/tool-selection.md) - selection failure modes.
- [`patterns/02-router.md`](../patterns/02-router.md) - the multi-tool routing pattern.
- [Project 05 - Multi-server MCP agent](../projects/intermediate/05-multi-server-mcp-agent/) - tool collision at scale, across multiple MCP servers.

## Related pages

- [04 - Agents as policies](./04-agents-as-policies.md) - the broader policy framing.
- [06 - The ReAct loop, formalized](./06-react-formalization.md) - how tool selection fits inside one ReAct step.
- [10 - Multi-agent coordination graphs](./10-multi-agent-coordination.md) - how to keep $|\mathcal{A}|$ small via decomposition.
- [Glossary: Tool, Tool calling, Function calling, Tool collision](../glossary/terms.md) - short definitions.

## References

- Schick, T., et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS 2023. Established the modern formulation of tools as a sampled action from the LM's distribution.
- Patil, S. G., et al. (2023). [*Gorilla: Large Language Model Connected with Massive APIs*](https://arxiv.org/abs/2305.15334). The first systematic treatment of tool-selection failures with large $|\mathcal{A}|$, plus a benchmark for measuring them.
- Qin, Y., et al. (2023). [*ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs*](https://arxiv.org/abs/2307.16789). Explores the scaling problem: what happens when $N$ gets very large.
- OpenAI. [*Function Calling Guide*](https://platform.openai.com/docs/guides/function-calling). The canonical API specification for constrained-decoding tool calls.
- Anthropic. [*Tool use*](https://docs.anthropic.com/en/docs/build-with-claude/tool-use). Anthropic's equivalent documentation. Useful for cross-checking schema conventions.
