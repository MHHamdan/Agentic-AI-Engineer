# Multi-agent coordination graphs

> 🧮 Mathematical foundation · ⏱ ~9 min read · Anchor: [`concepts/multi-agent/`](../concepts/multi-agent/)

## The equation

A multi-agent system is a directed graph $G = (V, E)$:

- $V = \{A_1, A_2, \ldots, A_n\}$ — the set of agents (vertices).
- $E \subseteq V \times V$ — communication channels (directed edges). An edge $A_i \to A_j$ means $A_i$ can hand off (or delegate) work to $A_j$.

Each agent $A_i$ has its own policy $\pi_{\theta_i}$, action space $\mathcal{A}_i$ (its tools + the option to hand off to its successors), and state $s_t^{(i)}$.

A **handoff** from $A_i$ to $A_j$ at step $t$ is an action $a_t^{(i)}$ that transfers control plus a payload:

$$
\text{handoff}_{i \to j}(\text{payload}) \;\in\; \mathcal{A}_i.
$$

Standard topologies are constraints on the shape of $G$:

| Topology | Shape of $G$ | Use when |
|---|---|---|
| Single-agent | $|V| = 1$ | Task fits in one specialist's action space |
| Supervisor-worker | Star: one central node connected to leaves | Single coordinator; specialists don't need to communicate peer-to-peer |
| Hierarchical | Tree | Multi-layer delegation; intermediate managers |
| Plan-and-execute | Linear chain (planner → executor) | Plan-first workloads with no peer communication |
| Swarm | Complete or near-complete graph | Decentralized; peers hand off without central coordination |

---

## Mathematical intuition

Three things to internalize.

**The graph shape determines the failure surface.** A star (supervisor-worker) fails when the supervisor fails; the leaves can't recover independently. A complete graph (swarm) doesn't have a single point of failure but is harder to debug — control can be anywhere. Hierarchical sits between: failure of a manager kills the subtree but other branches continue. The graph is an explicit articulation of where things can go wrong.

**Cycles in $G$ enable replan loops but require termination guards.** If $A \to B \to A$ is in $E$, the system can ping-pong indefinitely. Production systems either forbid cycles (the DAG constraint of plan-and-execute) or bound them (each edge fires at most $k$ times per task). Without the guard, a multi-agent system can spend unbounded budget without progress.

**Handoff contracts are the edges of $G$ made explicit.** Per Path 03 v2 Pattern 1, the handoff isn't just "send messages to $A_j$" — it's "send a typed payload conforming to a schema $A_j$ knows how to consume." Without contracts, $G$ exists implicitly (agents send each other raw chat history) and the system loses every formal property we'd want.

---

## Why it matters for engineers

Four practical implications:

1. **Pick the topology that minimizes communication overhead for your workload.** If the task naturally decomposes into independent sub-tasks, supervisor-worker is the cleanest. If the task requires peer collaboration (e.g., adversarial generator-critic loops), a small cycle or two is justified. If the task is one specialist's job, *don't use multi-agent at all*. Multi-agent overhead is real; the graph shape sets the floor on coordination cost.

2. **Coordination overhead grows superlinearly with $|V|$.** Each agent needs prompt tokens describing the other agents in $G$, plus handoff schemas, plus context about whose turn it is. Doubling the number of agents typically more than doubles per-task cost. The 2026 production sweet spot is 2-5 agents per workflow; beyond that, the marginal value drops sharply.

3. **The DAG constraint is the easiest way to bound runtime.** If $G$ is a DAG (no cycles), the system terminates in at most $|V|$ steps. This is why plan-and-execute is so attractive operationally — the graph is a linear chain, runtime is bounded, and replanning is the only mechanism that can extend it.

4. **The graph is a deployable artifact.** Production multi-agent frameworks (LangGraph, CrewAI, AutoGen) make $G$ explicit code. The graph definition + the per-agent prompts + the handoff schemas constitute the system's executable specification. Versioning the graph is versioning the agent system.

---

## Where you'll see it in the code

From [Lab 10 — Supervisor-worker from scratch](../labs/10-supervisor-worker-from-scratch/), the topology is a small star:

```python
# V = {supervisor, writer, researcher}; E = {supervisor→writer, supervisor→researcher}
class Supervisor:
    def __init__(self, workers: dict[str, Worker]):
        self.workers = workers   # the leaves of the star

    def step(self, state):
        # Sample action from pi_supervisor: either call a worker or respond.
        action = self.policy(state)
        if action.type == "handoff":
            # Edge fires: supervisor → workers[action.target]
            result = self.workers[action.target].handle(action.payload)
            return self.consume_result(result, state)
        else:
            return action  # terminal response

class Worker:
    def handle(self, payload: WorkerInput) -> WorkerOutput:
        # The handoff contract: typed input, typed output.
        # The worker's pi_worker sees only what payload contains.
        ...
```

For graph-shaped systems (DAGs, cycles), [LangGraph](https://docs.langchain.com/) makes the structure first-class:

```python
graph = StateGraph(AgentState)
graph.add_node("planner", planner_fn)
graph.add_node("executor", executor_fn)
graph.add_edge("planner", "executor")          # E: planner → executor
graph.add_conditional_edges(                    # cycle guard
    "executor", should_replan,
    {"replan": "planner", "done": END},
)
runnable = graph.compile()
```

The framework comparison in [Path 03 v3 frameworks page](../concepts/multi-agent/multi-agent-frameworks-deep-dive.md) walks through how each framework represents $G$.

---

## See also

- 📖 [`concepts/multi-agent/`](../concepts/multi-agent/) — the conceptual treatment.
- 📖 [`patterns/03-supervisor-workers.md`](../patterns/03-supervisor-workers.md), [`patterns/04-hierarchical-teams.md`](../patterns/04-hierarchical-teams.md), [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md), [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md) — pattern pages for each topology.
- 🧮 [Planning and search](./08-planning-search.md) — the math for the plan-and-execute case.
- 🧪 [Lab 10](../labs/10-supervisor-worker-from-scratch/), [Lab 11](../labs/11-generator-critic-from-scratch/), [Lab 12](../labs/12-plan-and-execute-from-scratch/) — implementations.
- 📖 [Glossary — Topology, Supervisor-worker, Handoff contract, Swarm](../glossary/terms.md).

---

## Sources

- Wu, Q., et al. (2023). [*AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*](https://arxiv.org/abs/2308.08155). Foundational treatment of multi-agent LLM systems as graphs of conversing agents.
- Park, J. S., et al. (2023). [*Generative Agents*](https://arxiv.org/abs/2304.03442). UIST. Demonstrates large-scale multi-agent emergent behavior.
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 17.5. The multi-agent decision-theory foundation.
- Lynch, N. (1996). *Distributed Algorithms*. Morgan Kaufmann. The classical reference on the impossibility results and design tradeoffs (FLP impossibility, CAP) that apply to multi-agent LLM systems too.
