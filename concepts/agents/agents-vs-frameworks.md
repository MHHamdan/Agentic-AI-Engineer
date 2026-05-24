# Agents vs. frameworks

> 🟢 Stable · ⏱ ~12 min read · 🏷 agents, frameworks, decision-making

## TL;DR

A framework like LangGraph doesn't make your agent *smarter*. It gives you working implementations of state management, conditional routing, checkpointing, and human-in-the-loop — capabilities you'd otherwise have to write yourself. The question isn't *"is the framework good?"* but *"are the things it provides worth the dependency, the indirection, and the learning cost for this particular project?"*

For a one-screen agent that returns an answer in a single user turn, probably not. For a long-running, multi-user, recoverable agent with human approval gates, almost certainly. This page is about how to decide.

---

## What "the framework" actually does for you

Lab 01 hand-rolls an agent loop in about 150 lines. It works. What does a framework like LangGraph add on top?

Five things, concretely:

1. **A graph runtime.** Your agent's control flow is expressed as a graph of nodes and edges, not as Python code. The runtime walks the graph, dispatches each node, and handles routing. This is mostly a notation choice, but it pays off when control flow is non-trivial.
2. **Reducer-based state.** Instead of mutating `state.messages.append(...)`, you return `{"messages": [new_msg]}` from a node, and a reducer (`add_messages`) merges it. This makes parallel updates and replay correct by construction.
3. **Checkpointing.** Every step's state can be persisted automatically. The agent can be paused, the process restarted, and the run resumed exactly where it left off.
4. **Human-in-the-loop primitives.** A first-class `interrupt(...)` function pauses graph execution, surfaces a payload, and waits for a `Command(resume=...)` call — across process boundaries, with the checkpoint backing the wait.
5. **Streaming, observability, and tool plumbing.** Built-in support for streaming intermediate state, structured tracing (e.g., to LangSmith), and prebuilt tool-execution nodes that handle the call/result protocol.

Each of these is also possible to build by hand. The framework's value is that they're already built, tested, and consistent with each other.

---

## A 90-second comparison

The same tool-using agent, expressed two ways. Both work; they have different costs.

### From-scratch (Lab 01 style)

```python
def run_agent(question: str) -> str:
    state = [{"role": "system", "content": SYSTEM_PROMPT},
             {"role": "user", "content": question}]
    for step in range(MAX_STEPS):
        msg = chat_with_tools(state, tools=schemas)
        state.append(msg.to_dict())
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            result = execute_tool(call)
            state.append({"role": "tool",
                          "tool_call_id": call.id,
                          "content": json.dumps(result)})
    return "[step cap reached]"
```

**Pros:** zero hidden behavior. You can read it top to bottom and predict exactly what happens. Debugging is `print(state)`. No dependencies beyond the LLM client.

**Cons:** every cross-cutting concern (persistence, human approval, retries, parallel calls) is a future change to this function. State management is implicit in the `list.append` calls. There's no replay; if the process dies at step 3, you start over.

### LangGraph (Lab 05 style)

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

def call_model(state: MessagesState) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "model")

agent = builder.compile(checkpointer=InMemorySaver())
result = agent.invoke({"messages": [HumanMessage(question)]},
                      config={"configurable": {"thread_id": "1"}})
```

**Pros:** state mutations are explicit and replay-safe. The graph picture (model → tools → model → END) is the architecture; the code mirrors it. Adding a human-approval node, parallel tool branches, or a routing step is a localized change. Persistence comes free.

**Cons:** more vocabulary to learn (`StateGraph`, `MessagesState`, conditional edges, reducers, checkpointers, thread_id). Behavior is partially in the framework, so debugging means reading framework source occasionally. The dependency surface is wider.

Same agent, same behavior on the happy path. Different costs for everything that isn't the happy path.

---

## A decision framework

Eight dimensions where the two approaches differ. None of them is universally "better"; they tilt depending on what you're building.

### 1. Readability

**From-scratch wins for short agents.** A 150-line loop you wrote is easier to read than a 50-line graph definition plus the framework's internals.

**Framework wins as agents grow.** A graph with 6 nodes and conditional edges is far easier to read than a deeply nested `if`/`elif` ladder in a homemade loop.

**Inflection point:** roughly when your agent has more than one decision point that isn't "did the model call a tool?" If you're routing on the *content* of a tool result, branching on user intent, or splitting work to multiple specialists — you've crossed the line where a graph is clearer than a procedure.

### 2. State management

**From-scratch:** state is whatever your code mutates. Easy to reason about in isolation, easy to corrupt with a typo. No invariants enforced.

**Framework:** state is a typed object with reducer-validated mutations. Mutations are commutative by design (returning `{"messages": [m]}` from two nodes in parallel produces the same final state regardless of order, because `add_messages` is a reducer). This is what makes parallel branches and replay correct.

**The killer feature here is replay.** A LangGraph run with a checkpointer can be paused, re-loaded from disk, and continued — and the final state is identical to what you'd get from an uninterrupted run. From-scratch agents either give up that property or reimplement it (poorly).

### 3. Debugging

**From-scratch:** `print(state)`, `breakpoint()`, ordinary Python tooling. Fast feedback loop, no special skills.

**Framework:** structured traces (especially with LangSmith), but you sometimes need to read framework internals to understand why a node fired or didn't. Stack traces include framework frames.

**Practical note:** in our experience, framework debugging is *better than* from-scratch debugging *once you've climbed the learning curve* — because the trace shows you exactly which node ran, what state it saw, and what it returned. But the curve is real, and on a 30-minute toy project it's not worth climbing.

### 4. Reliability

**From-scratch:** as reliable as your control flow. Crashes from un-handled exceptions, partial state, malformed tool results — all on you to prevent.

**Framework:** the runtime handles many failure modes — partial tool calls, node-level retries, replay after crashes. You still have to handle business-logic errors, but the agent loop itself is harder to break.

**For production work, this gap matters.** Tracking down "why did the agent get stuck after a network blip" in a from-scratch loop is *much* more work than configuring `retry_policy` on a graph node.

### 5. Checkpointing

**From-scratch:** you can implement it; nobody does. The amount of code required to do checkpointing correctly (per-step serialization, race-free resume, thread isolation) is comparable to the agent itself.

**Framework:** `checkpointer=InMemorySaver()` or `PostgresSaver(...)`. Persist state at every node boundary. Resume on the next process invocation by referencing the same `thread_id`. This is the single biggest "the framework does something I'd never have written" capability.

**If you need long-running agents** — anything that survives a server restart, anything that pauses for human input over hours, anything multi-user with isolated conversation threads — checkpointing alone usually justifies the framework.

### 6. Human approval

**From-scratch:** ad-hoc. A common shape is: special tool that returns `{"requires_approval": true, ...}`, plus runtime code that detects that shape and pauses. Works, but fragile — every new approval point needs the same plumbing.

**Framework:** `interrupt(payload)` inside any node, `Command(resume=value)` to continue. The interruption point can be conditional, dynamic, and the resumed value flows back through the call site. The state at interrupt time is checkpointed automatically, so the approval can happen days later.

**Pattern matching to needs:** if you have a single, predictable approval gate (e.g., "always confirm before sending email"), from-scratch is fine. If you have *multiple* gates that fire conditionally — risk score above threshold, certain tool combinations, user-specific rules — the framework primitive is materially easier.

### 7. Maintainability

**From-scratch:** code is yours. It rots at the rate you let it. No risk of upstream changes breaking you.

**Framework:** code is theirs. You inherit improvements (and bugs, and migration costs). LangGraph specifically has committed to no breaking changes until 2.0, which reduces risk — but a major version cut will eventually come, and you'll need to migrate.

**Two-year view:** for a project you'll maintain for >12 months, the framework is usually a win even after migration costs, because the per-feature cost of additions stays low. For a project you'll throw away in a sprint, from-scratch is genuinely simpler.

### 8. Learning value

**From-scratch first, framework second.** This is the curriculum's opinion, but it's a strong one.

When you build the loop by hand, you internalize what the agent *is* — a model that picks actions, a state that grows, observations that flow back. When you skip that step and reach for `create_agent(model, tools)`, you can ship an agent without ever understanding why it works. That works fine until something breaks, and then you have nothing to debug against.

After you've built one from scratch, the framework's abstractions become obvious — `StateGraph` is the loop you wrote; `MessagesState` is your `state` list; `ToolNode` is your `execute_tool` helper. The framework is *making explicit* what was implicit in your code.

So our order is: Lab 01 (from scratch) → Lab 02 (better tools, still from scratch) → Lab 05 (same agent, in LangGraph). The framework lab is supposed to feel like an "oh, this is the same thing, organized differently" moment. If it doesn't, go back to Lab 01.

---

## The decision in one table

| If your project... | Lean toward |
|---|---|
| Is a learning exercise or interview project | **From-scratch.** Build the loop. Internalize it. |
| Returns an answer in one user turn, no persistence needed | **From-scratch.** Simpler, fewer deps. |
| Has 1–3 tools, predictable control flow | **From-scratch.** Or `create_agent` if you want fast wiring. |
| Has 4+ tools with non-trivial routing | **Framework.** Conditional edges pay off. |
| Needs to survive process restarts | **Framework.** Checkpointing is hard to roll yourself. |
| Needs human approval gates | **Framework.** `interrupt()` + `Command(resume=...)` is a real win. |
| Has multi-user thread isolation | **Framework.** `thread_id` model is right. |
| Has parallel branches or fan-out/fan-in | **Framework.** Reducers handle it correctly. |
| Will be maintained for >12 months | **Framework.** Per-feature cost stays low. |
| Has unusual control flow the framework doesn't natively support | **Reconsider.** Either the framework can be extended, or you're paying for indirection that buys nothing. |

The honest version of the table: **start from-scratch, switch when a specific framework capability solves a specific problem.** Don't reach for the framework as a default. Don't refuse the framework when persistence becomes the hard part.

---

## What the framework *doesn't* fix

Worth saying plainly: no framework changes the model. If your agent picks the wrong tool, calls it with bad arguments, loops on confusing observations, or hallucinates — those problems live in *tool design, prompting, and selection*, not in the runtime. We covered the design side in [`concepts/tools/`](../tools/); the framework helps you build the runtime that runs the design, not the design itself.

A common pattern we've seen: a team migrates to LangGraph hoping it'll fix the reliability of their agent, and the agent gets *worse* for a while (new framework, new bugs, more indirection) before the long-term wins show up. If the underlying problem is "the model doesn't pick the right tool" or "the descriptions are vague," migrating to LangGraph won't help. Fix the tools first.

---

## See also

- 🧪 [Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/) — the from-scratch reference implementation.
- 🧪 [Lab 05: LangGraph rewrite of Lab 01](../../labs/05-langgraph-rewrite/) — same agent, LangGraph form. Read this page first; do the lab; come back and re-read this page.
- 📖 [What is an agent?](./what-is-an-agent.md) and [Agent loop](./agent-loop.md) — the framework-independent vocabulary.
- 📖 [Tool design](../tools/tool-design.md) and [Tool selection](../tools/tool-selection.md) — the things frameworks *don't* fix.
- ⚙️ [LangGraph tool snapshot](../../tools/langgraph/snapshot-v1.0.md) — pinned versions and APIs.
- 🧠 [LangGraph basics quiz](../../quizzes/foundations/langgraph-basics.md).

## References

- LangChain team (2025). [*LangChain and LangGraph Agent Frameworks Reach v1.0 Milestones*](https://blog.langchain.com/langchain-langgraph-1dot0/). The official 1.0 announcement. Worth reading for the design philosophy section, not just the features.
- LangChain docs. [*LangGraph migration guide*](https://docs.langchain.com/oss/python/migrate/langgraph-v1). What deprecated, what changed.
- Sumers, T. R. et al. (2024). [*Cognitive Architectures for Language Agents*](https://arxiv.org/abs/2309.02427). TMLR 2024. The CoALA framework gives a vocabulary for the kinds of agent control flow frameworks try to support.
- Anthropic (2024). [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents). A good companion read on when *simpler* approaches (single LLM calls, chains, routers) beat full agentic patterns — sister concern to "when does a framework pay off."
