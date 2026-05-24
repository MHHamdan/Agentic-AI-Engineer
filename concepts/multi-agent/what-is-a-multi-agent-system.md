# What is a multi-agent system?

> ⏱ ~10 min · 🟡 Intermediate · Prerequisite: Path 01 Foundations

A multi-agent system is a setup where two or more LLM-driven agents coordinate to produce an outcome that any single agent would do worse — or not at all. The agents have their own prompts, often their own tools, and they pass information between each other through structured handoffs.

That's the literal definition. The more important question is: *when does this pattern earn its complexity, and when is it expensive theater?*

## The literal mechanics

Strip away the marketing and a multi-agent system is two or more Lab 01-style agent loops, talking. Each agent has:

- Its own system prompt.
- Its own tool set (possibly empty — some agents are prompt-only).
- Its own conversation history.
- A way to receive work from another agent and return a result.

The coordination — *who calls whom, in what order, with what payload* — is what distinguishes the patterns: supervisor-worker, debate, plan-and-execute, swarm. Path 03 v1 covers supervisor-worker because it's the simplest pattern that's genuinely useful in production.

There's nothing new about the machinery. The Lab 02 tool-design principles still apply. The Lab 03 citation-tracking discipline still applies. The Lab 01 agent loop is still the agent loop. What's new is that *some of the "tools" a given agent calls are themselves agent loops*.

## When multi-agent is the right call

Three legitimate motivations:

1. **Specialization.** Different sub-tasks genuinely want different system prompts. A researcher prompt that says "find citations, never invent claims, every fact must come from a fetched page" is the wrong prompt for a writer whose job is to weave the findings into prose. Trying to do both with one prompt produces mediocre versions of each. Splitting the prompts splits the optimization.

2. **Parallelism.** Sub-tasks that are independent can run in parallel, with wall-clock savings proportional to how independent they actually are. (Caveat: production parallel-agent execution is more work than the marketing implies — see the "coordination cost" section below.)

3. **Explicit handoff boundaries that aid debuggability.** When a single 50-step agent trajectory fails, the failure point is somewhere in those 50 steps. When a supervisor → researcher → writer trajectory fails, the failure is in one of three named stages. The audit shape is fundamentally easier to reason about. Many production systems split their agents not for capability reasons but for *debugging* reasons.

If your task has none of these properties, multi-agent is probably the wrong call.

## When multi-agent is the wrong call

Four common mis-motivations to be honest about:

1. **"More agents = better results."** No. Each handoff is an extra LLM call: latency, tokens, and a new failure mode (handoff drops information, supervisor mis-routes, worker over-reaches). Coordination cost is real and it grows with agent count. If you can solve the task with one well-designed agent, you usually should.

2. **"Multi-agent = more autonomous."** No. Autonomy comes from the system prompt + tool design + step cap budget — same as for a single agent. A 5-agent system with weak prompts is *less* autonomous than a 1-agent system with strong ones, because the weakness compounds across handoffs.

3. **"Multi-agent = production-grade."** No. Production-grade comes from clear contracts, structured errors, observability, and graceful degradation. Multi-agent makes all four harder to get right because there are more boundaries to instrument and more handoffs to fail.

4. **"More agents = more parallelism."** Often no. Genuinely independent sub-tasks parallelize; "decompose this task into subtasks and run them concurrently" only helps when the decomposition is real. Many decompositions are sequential in disguise (the writer needs the researcher's output; they can't run in parallel) and you've just added coordination overhead without parallelism gain.

A useful heuristic: if you'd struggle to explain to a colleague *which specific failure mode of the single-agent version is fixed by adding a second agent*, you probably don't need a second agent.

## Coordination cost: the central tradeoff

Every handoff is one round-trip through an LLM. Concretely, for a supervisor calling a worker:

- **Latency:** at least one additional LLM call per handoff (often more — the supervisor needs to read the worker's result and decide next steps).
- **Tokens:** the entire worker context flows back to the supervisor, *and* the supervisor's prompt was already expensive.
- **Failure surface:** the supervisor can mis-route, the worker can mis-interpret the task, the handoff envelope can drop information, the result format can confuse the supervisor.

A rough quantification: if a single-agent trajectory averages 3-4 LLM calls, a supervisor-worker trajectory for the same task averages 6-8. That's a 2x cost for the multi-agent version. The benefit has to clear that bar.

This is why the "decompose your task into 10 specialist agents" demos are usually theater. Each agent multiplies the cost; the marginal benefit often shrinks fast. Production multi-agent systems are typically 2-4 agents, not 10.

## Concrete patterns where multi-agent pays off

Where the cost is genuinely worth paying:

- **Retrieval / synthesis separation.** A researcher agent with web-search tools + a writer agent with no tools. The split lets the researcher prompt be ruthless about grounding ("every claim must come from a fetched page") while the writer prompt focuses on prose quality.
- **Planning / execution separation.** A planner agent emits a structured plan; one or more executor agents carry it out. Plan-and-execute (a later Path 03 module) is the canonical example.
- **Critic / generator separation.** A generator produces; a critic (often a second copy of the model with a different prompt) reviews; the generator revises. This is agent debate.
- **Domain specialization.** A finance specialist + a legal specialist + a coordinator. Each specialist has its own prompt and tool set tuned to its domain.

What unites these: the prompts genuinely differ, and the differences are large enough that trying to fold them into one prompt would produce worse output than splitting them.

## What multi-agent doesn't fix

Multi-agent does **not** fix:

- A weak tool design — apply Lab 02 first, then think about multi-agent.
- A weak system prompt — splitting one weak prompt into three weak prompts gives you three weak agents.
- The absence of retrieval — if you need RAG, you need RAG, in one agent or many.
- Hallucination — agents can hallucinate just as confidently across handoffs. In fact, multi-agent makes hallucination *harder* to detect because the supervisor often can't tell whether the worker's confident output is grounded.
- Lack of evaluation — Lab 09's eval discipline applies the same way; production multi-agent systems need *more* evaluation, not less, because there are more places things can go wrong.

If a problem in your single-agent system is on this list, multi-agent won't solve it. Fix the underlying issue first.

## Related concepts

- The supervisor-worker pattern is covered next: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The mechanics of how agents pass information: [handoffs and shared state](./handoffs-and-shared-state.md).
- The single-agent loop these compose from: [agent loop](../agents/agent-loop.md).
- The tool-design principles that still apply: [tool design](../tools/tool-design.md).

## References

- Wang et al. 2023, "A Survey on Large Language Model based Autonomous Agents" (arXiv:2308.11432) — broad taxonomy of agent architectures.
- Wu et al. 2023, "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (arXiv:2308.08155) — the conversation-driven design philosophy.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — engineering-grounded essay; the most-quoted source for "keep it simple."
- Wang et al. 2024 ([arXiv:2402.05120](https://arxiv.org/abs/2402.05120)) — "Multi-Agent Collaboration Mechanisms: A Survey" — useful taxonomy when you start thinking about pattern selection.
