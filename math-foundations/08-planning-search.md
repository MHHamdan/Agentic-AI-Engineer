# Planning and search

> 🧮 Mathematical foundation · ⏱ ~9 min read · Anchor: [`concepts/agents/`](../concepts/agents/)

## The equation

A **plan** is a sequence of actions that, executed in order, achieves a goal. Formally, given an initial state $s_0$ and a goal predicate $G(s)$:

$$
\text{plan}(s_0, G) \;=\; (a_1, a_2, \ldots, a_K) \;\text{ s.t. }\; G(s_K) = \text{True},
$$

where the state evolves via $s_{k+1} = \delta(s_k, a_k)$ for some (deterministic or stochastic) transition $\delta$.

**Search** is the procedure of finding such a plan by exploring a tree of partial plans. Each node is a state; each edge is an action. Three formulations to know:

- **Breadth-first search.** Expand all 1-step plans, then all 2-step plans, etc. Finds the shortest plan. Cost: $O(b^d)$ where $b$ is the branching factor and $d$ is plan depth.
- **A\* search.** Use a heuristic $h(s)$ that estimates remaining cost to goal. Expand the node with lowest $f(s) = g(s) + h(s)$, where $g(s)$ is cost-so-far. Optimal if $h$ is *admissible* (never overestimates).
- **Monte Carlo Tree Search (MCTS).** Stochastic — sample rollouts from each candidate; backpropagate values. Used in AlphaGo; emerging in LLM-based planning (Tree-of-Thoughts).

For LLM agents, the most-used pattern is **plan-and-execute**: the planner LLM emits the full plan up front (no search), then the executor runs each step. Replanning happens on failure.

---

## Mathematical intuition

Three things to internalize.

**Planning is search through state space; search is planning made operational.** They're the same problem viewed from different angles. The thing that varies is *how aggressively you commit*: pure planning generates one sequence and commits; pure search explores many partial sequences; LLM plan-and-execute commits to one plan but with replan loops on failure.

**The branching factor is what makes search hard.** If $|\mathcal{A}| = 20$ and plans are 10 steps deep, BFS enumerates $20^{10} = 10^{13}$ candidate plans. Heuristics ($A^*$) or pruning (beam search) reduce the effective branching factor. LLM planning sidesteps this entirely — the LLM's policy $\pi_\theta$ is already a heuristic over actions, so we're sampling from a smart distribution rather than enumerating uniformly.

**Replanning is the "search" component of LLM planning.** Pure plan-and-execute has no search — the planner emits one trajectory. But when an executor step fails (tool error, unexpected output, environment shift), the agent replans. The planning + replanning loop *is* a (cheap) search over plan space, with the LLM as both heuristic and planner. The number of allowed replans bounds the search depth.

---

## Why it matters for engineers

Four practical implications:

1. **Plan-and-execute is the default LLM-planning shape.** A single LLM call produces a plan; a separate executor runs each step. The pattern is in [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md). Reasons to choose it: cheap (one planning call); inspectable (plan is visible before execution); composable with HITL approval gates between plan and execute.

2. **MAX_PLAN_STEPS is your branching-factor control.** A plan with 20 steps is harder to validate, more likely to drift, and exposes more failure surface. Bound the plan depth. Standard production cap: 5-10 steps; harder than that → decompose into sub-plans.

3. **Replan policies are a design choice with operational consequences.** Two extremes: (a) replan on any failure → expensive; agent loops forever on flaky tools. (b) Never replan → agent fails on the first transient error. Production default: max 2-3 replans, with the failed action's error fed to the replanner. See [Path 03 v2 Pattern 5](../learning-paths/03-multi-agent-systems/patterns/).

4. **Tree-of-Thoughts is search applied to reasoning, not actions.** ToT (Yao et al. 2023) explores multiple reasoning chains in parallel and picks the best by self-evaluation. The math is the same as search; the "actions" are intermediate reasoning steps rather than tool calls. Useful for puzzle-like problems; rarely worth the cost overhead for typical agentic workflows.

---

## Where you'll see it in the code

From [Lab 12 — Plan-and-execute from scratch](../labs/12-plan-and-execute-from-scratch/), the planner emits a `Plan` schema and the dispatcher walks it:

```python
class PlanStep(BaseModel):
    id: int
    description: str
    tool: str
    args: dict
    depends_on: list[int] = []   # plan as DAG

class Plan(BaseModel):
    steps: list[PlanStep]

# Planning: one LLM call → full plan
plan = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "system", "content": PLANNER_PROMPT}, ...],
    response_format=Plan,   # structured output
    temperature=0,
).choices[0].message.parsed

# Execution: walk the DAG, executing in dependency order
results = {}
for step in topological_order(plan.steps):
    if all(results.get(d, {}).get("ok") for d in step.depends_on):
        results[step.id] = execute_step(step, results)
    else:
        # Replan with failure context
        plan = replan(plan, results, failures, budget_remaining)
        break
```

Production extensions: parallel execution of independent steps; bounded replanning (`MAX_REPLANS = 2`); identical-plan dedup to detect infinite-loop replan cycles.

---

## See also

- 📖 [Plan-and-execute pattern](../patterns/06-plan-and-execute.md) — the production pattern this formalizes.
- 🧮 [Multi-agent coordination graphs](./10-multi-agent-coordination.md) — when planning extends across multiple agents.
- 🧪 [Lab 12 — Plan-execute from scratch](../labs/12-plan-and-execute-from-scratch/) — implements this end-to-end.
- 📖 [Glossary — Plan-and-execute, Retry policy](../glossary/terms.md).

---

## Sources

- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 3 + Ch. 11. The canonical search and planning treatment.
- Yao, S., et al. (2023). [*Tree of Thoughts: Deliberate Problem Solving with Large Language Models*](https://arxiv.org/abs/2305.10601). NeurIPS. Adapts classical search to reasoning chains.
- Wang, L., et al. (2023). [*Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning*](https://arxiv.org/abs/2305.04091). ACL. Established the plan-then-execute pattern for reasoning.
- Hao, S., et al. (2023). [*Reasoning with Language Model is Planning with World Model*](https://arxiv.org/abs/2305.14992). EMNLP. The RAP framework — formalizes LLM reasoning as planning in a learned world model.
