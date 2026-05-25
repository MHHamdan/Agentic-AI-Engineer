# Lab 11 — Generator-critic from scratch

> ⏱ 110-140 min · 🟡 Intermediate · Prerequisites: Lab 10, Path 01 Labs 01-03

Extend Lab 10's supervisor-worker system with a **critic worker** that reviews the writer's draft against the brief, returning structured `{status, issues}`. Wire the critic into a bounded refinement loop: the supervisor invokes the writer, then the critic; if the critic approves, the draft is final; if not, the writer runs again with the critic's issues injected into its brief. Hard cap of 3 refinement cycles.

No new dependencies. No frameworks. Just one new worker on top of Lab 10's machinery, and a small update to the supervisor's prompt and step cap.

## What you'll build

```
        user task
            │
            ▼
    ┌───────────────┐
    │  supervisor   │  ← Lab 10's supervisor + 1 new tool (call_critic)
    │               │  ← MAX_REFINEMENT_CYCLES = 3
    └───────────────┘
        │   ▲   │   ▲   │   ▲
        │   │   │   │   │   │
        ▼   │   ▼   │   ▼   │
   researcher  writer  critic
                  ▲       │
                  └───────┘
                  (refinement cycle:
                   critic-issues injected
                   into writer's brief
                   on each retry)
```

The critic is a fourth agent, with its own system prompt and a strict structured-output envelope. The supervisor's prompt is updated to describe the refinement loop. Everything else from Lab 10 — the researcher, the writer's prompt, the chat client, action-hash dedup, structured-error envelopes — stays untouched.

## Goal

By the end of the lab you should be able to:

- Implement the generator-critic pattern as an extension of the supervisor-worker pattern, without rewriting the supervisor.
- Apply the four critic-prompt rules (anchor to checklist, default to ok, require evidence, bound the issue list) and explain why each prevents a specific failure mode.
- Run the obvious-bad-draft sycophancy test as a routine diagnostic before deploying any critic.
- Bound refinement with `MAX_REFINEMENT_CYCLES = 3` and handle the cap honestly — surfacing partial results plus unresolved critic issues, rather than forced approvals.
- Read a supervisor trace and distinguish legitimate iteration from runaway disagreement.

## Prerequisites

- **Lab 10** — the supervisor-worker pattern. Lab 11 *extends* Lab 10's supervisor in place. If you haven't built Lab 10, do that first.
- **Lab 02** — tool design. Critic prompts are essentially eval rubrics applied at inference time; same design discipline.
- **Lab 03** — `web_search` + `fetch_page`. Reused verbatim through Lab 10's researcher worker.
- **Concept pages** — at minimum [agent debate and critics](../../concepts/multi-agent/agent-debate-and-critics.md) and [generator-critic pattern](../../concepts/multi-agent/generator-critic-pattern.md). The lab references their failure modes and design rules directly.

## Setup

No new dependencies. Same `.env` setup as Labs 01-10 (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). Lab 10's researcher worker requires `ddgs`, `requests`, `bs4` — already installed if you completed Lab 03.

## Structure

Roughly 30-35 cells, output-stripped, sample-output markdown cells throughout. Each step builds on the prior one; the lab is structured so the deltas from Lab 10 are visible at each turn.

- **Step 0**: Setup — same as Lab 10.
- **Step 1**: Recap of Lab 10's worker functions and supervisor. Compact restatement of `researcher_agent`, `writer_agent`, and the supervisor's tool registry. Not a re-derivation — just enough to make the deltas in this lab clear.
- **Step 2**: The critic worker. `critic_agent(draft, brief) → {status, issues}`. System prompt anchored to a 5-item checklist (the issue `kind` enumeration: `unsupported_claim`, `missing_citation`, `dropped_citation`, `unclear_prose`, `format_violation`). Strict-reviewer framing. `temperature=0`. Issues bounded to ≤3.
- **Step 3**: The sycophancy diagnostic. Construct an obviously-bad draft (made-up facts, missing citations) and feed it to the critic without running the full supervisor. Verify the critic flags it. If your critic returns `ok` here, your prompt is sycophantic — and the lab shows exactly why and how to fix it.
- **Step 4**: Update the supervisor. Add `call_critic` to `SUPERVISOR_TOOLS` with a `CallCriticArgs` schema and a negative-guidance description. Update `SUPERVISOR_SYSTEM_PROMPT` to describe the refinement loop. Raise `SUPERVISOR_MAX_STEPS` from 6 to 10 to accommodate the refinement cycles. Add `MAX_REFINEMENT_CYCLES = 3` as a hard cap the supervisor enforces.
- **Step 5**: Run end-to-end on a real task with a verbose trace showing each agent's invocation and the cycle count.
- **Step 6**: Failure-mode walkthrough — the four debate failure modes with the mitigation each gets in this implementation:
  - Sycophancy → rubric-anchored prompt + strict-reviewer framing + the diagnostic test from Step 3.
  - Infinite agreement → same mitigations as sycophancy plus eval-time spot-checks.
  - Runaway disagreement → `MAX_REFINEMENT_CYCLES = 3` cap + honest surfacing of partial results.
  - Critique drift → stateless critic (receives only the current draft, not the revision history).
- **Step 7** (stretch): Pattern variation — self-critique (the writer reviews its own draft, no separate critic). Demonstrate it works on simple tasks but is more sycophantic on subtle errors. Reinforces why Lab 11 uses separate-critic by default.

## What to watch for

Five practical issues that come up:

1. **Sycophancy on the first run.** If you skip Step 3 and run the full supervisor first, you may not notice the critic is sycophantic until you read the trace carefully (every call returns `ok`, no refinement cycle ever fires). The diagnostic test catches this before it pollutes the trace.

2. **The writer not actually addressing the critic's issues.** Sometimes the writer produces the *same* draft on retry, ignoring the issues. The action-hash dedup catches this — the next critic call has identical arguments and dedup fires. When you see this, the fix is in the writer's revision prompt: explicitly require the writer to address each issue and explain in a comment what changed.

3. **Step-cap interaction.** `WORKER_MAX_STEPS = 8` (per-worker), `SUPERVISOR_MAX_STEPS = 10` (per-supervisor invocation), `MAX_REFINEMENT_CYCLES = 3` (per-task). The three are independent. A worker hitting its step cap returns a `step_cap` envelope; the supervisor reads it and decides. A supervisor hitting its step cap returns its partial result; you'd see this if the supervisor has been routing inefficiently. Refinement cycles only count writer → critic round-trips, not researcher or finalization steps.

4. **Critique drift in long refinement cycles.** If the supervisor's brief grows by accumulating critic-issues across cycles, the critic may eventually flag issues that *new* parts of the brief introduce (rather than draft problems). The fix: the critic sees only the *current draft* and the *original* brief, not the revision history. Lab 11 implements this; resist the urge to "give the critic context."

5. **Cost.** The full pipeline averages 8-12 LLM calls per task (~2x Lab 10). Real-world workloads with this pattern often run 1.5-2x Lab 10's cost; budget accordingly when designing.

## Anti-scope

Deliberately out of scope, scoped for future batches:

- **CrewAI, AutoGen, LangGraph multi-agent helpers** — none of them. The lab is `chat_with_tools` and Python all the way down. Framework bridges come later.
- **Self-consistency / majority voting** — different pattern (parallel sampling + aggregation), different bug profile. Not in this lab.
- **Tree-of-Thoughts** — search over candidate critique paths in parallel. Different shape, different cost. Not in this lab.
- **Multi-agent debate with >2 agents** — generator-critic is the simplest form; >2 agents adds complexity disproportionate to quality gains on most tasks. Out of scope.
- **Adversarial training of the critic** — out of scope for an educational lab; the critic here is a prompted reviewer, not a fine-tuned discriminator.
- **Multi-agent RAG with critique** — composing this with Lab 06-08's retrieval pipeline. A future Path 03 batch.
- **MCP / A2A coverage** — Path 04.
- **Production observability** — Path 06.

## Run-time and cost

Per end-to-end run, roughly 8-12 LLM calls depending on refinement cycles:

- 1-2 supervisor calls (routing + finalization).
- 2-4 researcher calls (Lab 10's researcher; same shape).
- 1-3 writer calls (one per refinement cycle).
- 1-3 critic calls (one per refinement cycle).

At gpt-4o-mini rates, well under $0.10 per full lab run. Wall-clock is dominated by the researcher's live web fetches (1-3 seconds each); the critic and writer are fast.

## Solution

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 17 cells vs the lab's 32 — the sycophancy diagnostic (the "deliberately bad draft" cell), the unbounded-loop walkthrough, and the structured-trace appendix are condensed; the bounded refinement loop reads end-to-end. Two implementation choices flagged there:

- **The critic receives only `(current_draft, original_brief)`** — explicitly *not* the revision history. The stateless critic prevents critique drift; this is a deliberate design choice, not an oversight.
- **The action-hash dedup is unchanged from Lab 10.** It composes naturally: if the writer produces the same draft twice (failing to address critic feedback), the next critic call has identical args and dedup catches it. This is a useful signal that the refinement isn't actually refining.

## Next

- After completing the lab, take the [agent debate and critics quiz](../../quizzes/multi-agent/agent-debate-and-critics.md).
- Path 03 continues with [Lab 12 (plan-and-execute)](../12-plan-and-execute-from-scratch/) and [Lab 13 (multi-agent RAG)](../13-multi-agent-rag-from-scratch/), then Module 5's framework bridge in [Lab 14](../14-langgraph-supervisor-bridge/) + [Lab 15](../15-langgraph-plan-execute-bridge/).
- If you've also done Path 02, [Lab 13](../13-multi-agent-rag-from-scratch/) composes Lab 06-08's retrieval pipeline with the supervisor + critic patterns from Labs 10-11.
