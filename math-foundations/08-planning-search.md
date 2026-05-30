# Planning and search

> Mathematical foundation. About 10 minutes to read. Anchor: [`concepts/agents/`](../concepts/agents/).

## Why this matters for agentic AI

Many real tasks need a sequence of decisions, not a single tool call. Planning gives you a vocabulary for that sequence (states, actions, goals, branching factor) and tells you which approximations are cheap. The result is two concrete production patterns: plan-and-execute and bounded replanning. Both fall out of the math.

## The equation

A **plan** is a sequence of actions that, executed in order, achieves a goal. Given an initial state $s_0$ and a goal predicate $G(s)$:

$$
\text{plan}(s_0, G) = (a_1, a_2, \ldots, a_K) \text{ such that } G(s_K) = \text{True},
$$

where the state evolves via $s_{k+1} = \delta(s_k, a_k)$ for some deterministic or stochastic transition $\delta$.

**Symbols:**

- $s_0$ - the initial state.
- $G(s)$ - goal predicate. True when the state satisfies the goal.
- $a_1, \ldots, a_K$ - the planned sequence of actions.
- $\delta(s, a)$ - the transition function. The new state after taking action $a$ in state $s$.
- $K$ - the plan length (number of steps).

**Search** is the procedure of finding such a plan by exploring a tree of partial plans. Each node is a state; each edge is an action. Three formulations to know:

- **Breadth-first search.** Expand all 1-step plans, then all 2-step plans, etc. Finds the shortest plan. Cost: $O(b^d)$ where $b$ is the branching factor and $d$ is plan depth.
- **A-star search.** Use a heuristic $h(s)$ that estimates remaining cost to goal. Expand the node with lowest $f(s) = g(s) + h(s)$, where $g(s)$ is cost-so-far. Optimal if $h$ is *admissible* (never overestimates).
- **Monte Carlo Tree Search (MCTS).** Stochastic. Sample rollouts from each candidate; backpropagate values. Used in AlphaGo; emerging in LLM-based planning (Tree-of-Thoughts).

For LLM agents, the most-used pattern is **plan-and-execute**: the planner LLM emits the full plan up front (no search), then the executor runs each step. Replanning happens on failure.

## How to read this equation

Read the plan as a recipe: starting from $s_0$, do $a_1$, then $a_2$, then ... and the goal predicate $G$ becomes True at the end. The transition $\delta$ tells you what happens at each step.

In real LLM agents, $\delta$ is "the world plus your tools." Calling a search tool produces a new state where the search results are now in your context. Calling a code interpreter produces a new state where the code has been executed and the output is observed. We rarely write $\delta$ down explicitly; we just observe what happens.

## Mathematical intuition

Three things to internalize.

**Planning is search through state space; search is planning made operational.** They are the same problem viewed from different angles. The thing that varies is *how aggressively you commit*: pure planning generates one sequence and commits; pure search explores many partial sequences; LLM plan-and-execute commits to one plan but with replan loops on failure.

**The branching factor is what makes search hard.** If $|\mathcal{A}| = 20$ and plans are 10 steps deep, BFS enumerates $20^{10} = 10^{13}$ candidate plans. Heuristics (A-star) or pruning (beam search) reduce the effective branching factor. LLM planning sidesteps this entirely: the LLM's policy $\pi_\theta$ is already a heuristic over actions, so we are sampling from a smart distribution rather than enumerating uniformly.

**Replanning is the "search" component of LLM planning.** Pure plan-and-execute has no search; the planner emits one trajectory. But when an executor step fails (tool error, unexpected output, environment shift), the agent replans. The planning plus replanning loop *is* a (cheap) search over plan space, with the LLM as both heuristic and planner. The number of allowed replans bounds the search depth.

## Where this appears in agentic systems

Four practical implications:

1. **Plan-and-execute is the default LLM-planning shape.** A single LLM call produces a plan; a separate executor runs each step. The pattern is in [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md). Reasons to choose it: cheap (one planning call); inspectable (plan is visible before execution); composable with HITL approval gates between plan and execute.
2. **`MAX_PLAN_STEPS` is your branching-factor control.** A plan with 20 steps is harder to validate, more likely to drift, and exposes more failure surface. Bound the plan depth. Standard production cap is 5 to 10 steps; harder than that means decompose into sub-plans.
3. **Replan policies are a design choice with operational consequences.** Two extremes: (a) replan on any failure means expensive; agent loops forever on flaky tools. (b) Never replan means agent fails on the first transient error. Production default: max 2 to 3 replans, with the failed action's error fed to the replanner.
4. **Tree-of-Thoughts is search applied to reasoning, not actions.** ToT (Yao et al. 2023) explores multiple reasoning chains in parallel and picks the best by self-evaluation. The math is the same as search; the "actions" are intermediate reasoning steps rather than tool calls. Useful for puzzle-like problems; rarely worth the cost overhead for typical agentic workflows.

## Code example

A plan-and-execute skeleton with bounded replanning.

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()
MAX_REPLANS = 2

class PlanStep(BaseModel):
    id: int
    description: str
    tool: str
    args: dict

class Plan(BaseModel):
    steps: list[PlanStep]

def make_plan(goal: str, history: list = None) -> Plan:
    """One LLM call emits a full plan."""
    context = (
        f"Goal: {goal}\n"
        f"Prior attempts: {history}\n" if history else f"Goal: {goal}\n"
    )
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Produce a 3 to 7 step plan."},
            {"role": "user", "content": context},
        ],
        response_format=Plan,
        temperature=0,
    )
    return response.choices[0].message.parsed

def execute(plan: Plan, tools: dict) -> tuple[bool, list]:
    """Walk the plan. Returns (success, results)."""
    results = []
    for step in plan.steps:
        try:
            output = tools[step.tool](**step.args)
            results.append({"step": step.id, "ok": True, "output": output})
        except Exception as e:
            results.append({"step": step.id, "ok": False, "error": str(e)})
            return False, results
    return True, results

def run(goal: str, tools: dict) -> list:
    history = []
    for replan_idx in range(MAX_REPLANS + 1):
        plan = make_plan(goal, history)
        ok, results = execute(plan, tools)
        history.append({"plan": plan.model_dump(), "results": results})
        if ok:
            return history
    return history  # exhausted replan budget
```

The `make_plan` function corresponds to the planner; `execute` walks the action sequence. Replanning passes prior failures back into the planner so it can pick a different path. This is the core shape of every plan-execute system in production.

## Common mistakes

- **No upper bound on plan length.** A plan with 30 steps will go wrong somewhere, and recovering is expensive. Cap at 5 to 10.
- **Unbounded replanning.** If the agent can replan forever, a flaky tool will burn your budget. Limit to 2 to 3 replans per task.
- **Replanning without feeding prior failures back to the planner.** If the next plan looks identical to the failed one, you have an infinite loop. Always include the failure context.
- **Reaching for search when plan-and-execute would do.** Production systems rarely need tree search. The LLM's policy is already a strong heuristic; aggressive search is usually a research artifact, not a production need.
- **Skipping the goal predicate.** "Done" needs to be defined precisely. Without an explicit $G$, the agent does not know when to stop.

## Repo cross-references

- [Lab 12 - Plan-and-execute from scratch](../labs/12-plan-and-execute-from-scratch/) - implements this end-to-end.
- [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md) - the production pattern this formalizes.
- [`patterns/09-deep-research.md`](../patterns/09-deep-research.md) - plan-and-execute applied to multi-step research.

## Related pages

- [04 - Agents as policies](./04-agents-as-policies.md) - the per-step policy that drives planning.
- [05 - MDP / POMDP intuition](./05-mdp-pomdp.md) - the environment model planning operates over.
- [10 - Multi-agent coordination graphs](./10-multi-agent-coordination.md) - when planning extends across multiple agents.
- [Glossary: Plan-and-execute, Retry policy](../glossary/terms.md) - short definitions.

## References

- Russell, S., and Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.), Ch. 3 and Ch. 11. The canonical search and planning treatment.
- Yao, S., et al. (2023). [*Tree of Thoughts: Deliberate Problem Solving with Large Language Models*](https://arxiv.org/abs/2305.10601). NeurIPS 2023. Adapts classical search to reasoning chains.
- Wang, L., et al. (2023). [*Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning*](https://arxiv.org/abs/2305.04091). ACL 2023. Established the plan-then-execute pattern for reasoning.
- Hao, S., et al. (2023). [*Reasoning with Language Model is Planning with World Model*](https://arxiv.org/abs/2305.14992). EMNLP 2023. The RAP framework. Formalizes LLM reasoning as planning in a learned world model.
- Hart, P. E., Nilsson, N. J., and Raphael, B. (1968). [*A Formal Basis for the Heuristic Determination of Minimum Cost Paths*](https://ieeexplore.ieee.org/document/4082128). The original A-star paper. Classic reference for heuristic search.
