# Multi-agent coordination graphs

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/multi-agent/`](../concepts/multi-agent/).

## Why this matters for agentic AI

Multi-agent systems are easy to build and hard to debug. Modeling them as graphs makes the failure surface explicit: who can talk to whom, where the cycles are, what the coordination overhead costs. Most "why is my multi-agent system flaky" questions resolve into "what is the shape of your graph."

## The equation

A multi-agent system is a directed graph $G = (V, E)$:

**Symbols:**

- $V = \{A_1, A_2, \ldots, A_n\}$ - the set of agents (vertices).
- $E \subseteq V \times V$ - communication channels (directed edges). An edge $A_i \to A_j$ means $A_i$ can hand off (or delegate) work to $A_j$.

Each agent $A_i$ has its own policy $\pi_{\theta_i}$, action space $\mathcal{A}_i$ (its tools plus the option to hand off to its successors), and state $s_t^{(i)}$.

A **handoff** from $A_i$ to $A_j$ at step $t$ is an action $a_t^{(i)}$ that transfers control plus a payload:

$$
\text{handoff}_{i \to j}(\text{payload}) \in \mathcal{A}_i.
$$

Standard topologies are constraints on the shape of $G$:

| Topology | Shape of $G$ | Use when |
|---|---|---|
| Single-agent | $\|V\| = 1$ | Task fits in one specialist's action space |
| Supervisor-worker | Star: one central node connected to leaves | Single coordinator; specialists do not need peer-to-peer comms |
| Hierarchical | Tree | Multi-layer delegation; intermediate managers |
| Plan-and-execute | Linear chain (planner $\to$ executor) | Plan-first workloads with no peer communication |
| Swarm | Complete or near-complete graph | Decentralized; peers hand off without central coordination |

## How to read this equation

Think of $V$ as the cast of characters and $E$ as the lines on a who-talks-to-whom diagram. Each agent is a self-contained policy with its own state. A handoff edge $A_i \to A_j$ means: $A_i$ can choose, as one of its actions, to package a payload and transfer control to $A_j$.

The topology constrains what graphs are allowed. A star topology rules out lateral communication between workers. A hierarchical topology rules out skip-level handoffs. A complete graph allows everything but makes the system harder to reason about.

## Mathematical intuition

Three things to internalize.

**The graph shape determines the failure surface.** A star (supervisor-worker) fails when the supervisor fails; the leaves cannot recover independently. A complete graph (swarm) does not have a single point of failure but is harder to debug, since control can be anywhere. Hierarchical sits between: failure of a manager kills the subtree but other branches continue. The graph is an explicit articulation of where things can go wrong.

**Cycles in $G$ enable replan loops but require termination guards.** If $A \to B \to A$ is in $E$, the system can ping-pong indefinitely. Production systems either forbid cycles (the DAG constraint of plan-and-execute) or bound them (each edge fires at most $k$ times per task). Without the guard, a multi-agent system can spend unbounded budget without progress.

**Handoff contracts are the edges of $G$ made explicit.** The handoff is not just "send messages to $A_j$" but "send a typed payload conforming to a schema $A_j$ knows how to consume." Without contracts, $G$ exists implicitly (agents send each other raw chat history) and the system loses every formal property we would want.

## Where this appears in agentic systems

Four practical implications:

1. **Pick the topology that minimizes communication overhead for your workload.** If the task naturally decomposes into independent sub-tasks, supervisor-worker is the cleanest. If the task requires peer collaboration (for example, adversarial generator-critic loops), a small cycle or two is justified. If the task is one specialist's job, *do not use multi-agent at all*. Multi-agent overhead is real; the graph shape sets the floor on coordination cost.
2. **Coordination overhead grows superlinearly with $\|V\|$.** Each agent needs prompt tokens describing the other agents in $G$, plus handoff schemas, plus context about whose turn it is. Doubling the number of agents typically more than doubles per-task cost. The 2026 production sweet spot is 2 to 5 agents per workflow; beyond that, the marginal value drops sharply.
3. **The DAG constraint is the easiest way to bound runtime.** If $G$ is a DAG (no cycles), the system terminates in at most $\|V\|$ steps. This is why plan-and-execute is so attractive operationally: the graph is a linear chain, runtime is bounded, and replanning is the only mechanism that can extend it.
4. **The graph is a deployable artifact.** Production multi-agent frameworks (LangGraph, CrewAI, AutoGen) make $G$ explicit code. The graph definition plus the per-agent prompts plus the handoff schemas constitute the system's executable specification. Versioning the graph is versioning the agent system.

## Code example

A minimal supervisor-worker star topology with typed handoffs.

```python
from dataclasses import dataclass
from typing import Callable
from openai import OpenAI

client = OpenAI()

@dataclass
class HandoffPayload:
    """The typed contract that crosses an edge of G."""
    task: str
    context: dict

@dataclass
class WorkerResult:
    """What flows back along the reverse edge."""
    answer: str
    confidence: float

class Worker:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def handle(self, payload: HandoffPayload) -> WorkerResult:
        """The worker's pi_worker sees only what payload contains."""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Task: {payload.task}\nContext: {payload.context}"},
            ],
            temperature=0,
        )
        return WorkerResult(answer=response.choices[0].message.content, confidence=0.8)

class Supervisor:
    """Star center: routes to one of several workers."""
    def __init__(self, workers: dict[str, Worker]):
        self.workers = workers              # leaves of the star

    def route(self, query: str) -> str:
        """One LLM call decides which worker to invoke."""
        names = list(self.workers.keys())
        prompt = (
            f"Available specialists: {names}\n"
            f"Query: {query}\n"
            "Reply with exactly one specialist name."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        choice = response.choices[0].message.content.strip()
        return choice if choice in names else names[0]

    def run(self, query: str) -> WorkerResult:
        chosen = self.route(query)               # edge: supervisor -> workers[chosen]
        payload = HandoffPayload(task=query, context={"router": "supervisor"})
        return self.workers[chosen].handle(payload)

# Usage.
sup = Supervisor({
    "math":    Worker("math",    "You answer math problems."),
    "history": Worker("history", "You answer history questions."),
})
result = sup.run("What year did the French Revolution begin?")
print(result.answer, result.confidence)
```

The `HandoffPayload` and `WorkerResult` types are the explicit handoff contracts. For DAG-shaped systems with multiple edges and cycles, [LangGraph](https://langchain-ai.github.io/langgraph/) makes the graph first-class with `StateGraph`, `add_node`, `add_edge`, and `add_conditional_edges`.

## Common mistakes

- **Using multi-agent when single-agent would do.** Many tasks fit comfortably in one agent's action space. If the only reason for multi-agent is "to separate concerns," that is what code modules are for. Reach for multi-agent only when the task genuinely requires different specializations or different contexts per agent.
- **Letting raw chat history cross edges.** Without a typed handoff contract, downstream agents end up parsing previous agents' free text. Brittle. Always define `HandoffPayload`-style schemas.
- **Unbounded cycles.** $A \to B \to A$ without a maximum-iterations guard is a foot-gun. Either constrain to a DAG or bound the cycle.
- **Adding agents instead of fixing prompts.** "The agent is confused; let's add a planner and a critic" sometimes solves it; often it just spreads the confusion across more LLM calls and more tokens.

## Repo cross-references

- [`concepts/multi-agent/`](../concepts/multi-agent/) - the conceptual treatment.
- [`concepts/multi-agent/multi-agent-frameworks-deep-dive.md`](../concepts/multi-agent/multi-agent-frameworks-deep-dive.md) - how 9 frameworks represent $G$.
- [`patterns/03-supervisor-workers.md`](../patterns/03-supervisor-workers.md), [`patterns/04-hierarchical-teams.md`](../patterns/04-hierarchical-teams.md), [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md), [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md) - pattern pages for each topology.
- [Lab 10 - Supervisor-worker from scratch](../labs/10-supervisor-worker-from-scratch/), [Lab 11 - Generator-critic from scratch](../labs/11-generator-critic-from-scratch/), [Lab 12 - Plan-execute from scratch](../labs/12-plan-and-execute-from-scratch/) - implementations.

## Related pages

- [04 - Agents as policies](./04-agents-as-policies.md) - each vertex of $G$ is its own policy.
- [07 - Tool selection as function selection](./07-tool-selection.md) - the action space inside each agent.
- [08 - Planning and search](./08-planning-search.md) - the math for the plan-and-execute case.
- [Glossary: Topology, Supervisor-worker, Handoff contract, Swarm](../glossary/terms.md) - short definitions.

## References

- Wu, Q., et al. (2023). [*AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*](https://arxiv.org/abs/2308.08155). Foundational treatment of multi-agent LLM systems as graphs of conversing agents.
- Park, J. S., et al. (2023). [*Generative Agents*](https://arxiv.org/abs/2304.03442). UIST 2023. Demonstrates large-scale multi-agent emergent behavior.
- Russell, S., and Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 17.5. The multi-agent decision-theory foundation.
- Lynch, N. A. (1996). *Distributed Algorithms*. Morgan Kaufmann. The classical reference on impossibility results and design tradeoffs (FLP impossibility, CAP) that apply to multi-agent LLM systems too.
- LangChain. [*LangGraph documentation*](https://langchain-ai.github.io/langgraph/). The most-used framework for graph-structured agent systems in 2025-2026; needs manual verification as the docs change frequently.
