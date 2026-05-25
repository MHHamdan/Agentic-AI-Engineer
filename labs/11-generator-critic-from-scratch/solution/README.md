# Lab 11 · Reference solution

The polished final implementation of [Lab 11: Generator-critic from scratch](../README.md).

A supervisor coordinates Lab 10's researcher and writer workers, plus a new critic worker. The supervisor's loop adds a bounded refinement cycle: writer → critic → if-approve-finalize-else-refine-with-issues. `MAX_REFINEMENT_CYCLES = 3` bounds the loop and surfaces plainly at the cap. No frameworks.

> 📖 The concept pages that frame this implementation:
> [`agent-debate-and-critics`](../../../concepts/multi-agent/agent-debate-and-critics.md),
> [`generator-critic-pattern`](../../../concepts/multi-agent/generator-critic-pattern.md).
> 🧠 Calibrate against the [agent-debate-and-critics quiz](../../../quizzes/multi-agent/agent-debate-and-critics.md).
> ⬅️ Builds on [Lab 10's solution](../../10-supervisor-worker-from-scratch/solution/README.md).

## What this solution implements

The headline path from the parent lab:

- All of Lab 10's machinery (chat client, web tools, researcher worker, writer worker) — reused without modification.
- Critic worker: takes `(brief, draft)`, returns `{status: "ok"}` or `{status: "needs_revision", issues: [{kind, detail}]}` with five enumerated `kind` values.
- Updated supervisor (`SUPERVISOR_MAX_STEPS = 10`, raised from Lab 10's 6) with three worker-call tools: `call_researcher`, `call_writer`, `call_critic`.
- Bounded refinement loop inside the supervisor: when critic says `needs_revision`, the supervisor re-calls the writer with the issues attached, up to `MAX_REFINEMENT_CYCLES = 3` times.
- Explicit cap surfacing: when the cycle cap fires, the supervisor returns the last draft with `{status: "ok_with_unresolved_issues", ...}` — not a forced approval.
- One end-to-end demonstration run.

**Not in this solution** (deliberately): the sycophancy diagnostic (the "deliberately bad draft" cell from the parent), the four-failure-mode walkthrough, and the self-critique stretch section. Those are exploratory cells in the learning notebook; the solution is the canonical mechanism.

## Implementation choices

### Six design decisions worth flagging

**1. The critic's issue list is bounded and enumerated.** `CRITIC_ISSUE_KINDS = ["unsupported_claim", "missing_citation", "dropped_citation", "unclear_prose", "format_violation"]` — five well-defined kinds, not free-text. The critic's system prompt requires each issue to specify a `kind` from this list. Free-text issues invite the critic to invent vague complaints ("the writing could be more engaging"); enumerated kinds force the critic to pick a concrete failure mode that has a corresponding fix.

**2. Issues are capped at three per critic call.** The critic's system prompt says "cap at 3 issues. More than 3 → structural problems, not point fixes." This is principled: if a draft has more than 3 issues, the right fix is to start over, not to chase point edits. The cap also prevents the critic from emitting a 20-item list that overwhelms the writer's revision context.

**3. The critic defaults to OK on borderline cases.** The system prompt: "Default to OK on borderline cases. When uncertain, return ok." This is the anti-sycophancy mirror: rather than trying to make the critic perfectly precise, you accept it'll occasionally miss issues in exchange for not generating fake issues to please the supervisor. Sycophancy is the failure mode where the critic agrees with everything; the opposite is the critic *disagreeing* with everything to seem rigorous. The default-OK rule keeps the critic calibrated.

**4. The critic gets the brief, not just the draft.** Critic args are `(findings, citations, draft)` — the full brief plus the writer's output. This is what enables groundedness checks: every claim in the draft must trace to the findings; every citation in the brief must appear in the draft. Passing only the draft would force the critic to fabricate what "good" means.

**5. Refinement uses bounded loop with structural revision context.** When the critic flags issues, the supervisor doesn't ask the writer to "try again, be better." It passes the structured issues list back: `"REVISION REQUESTED — address each of these issues: [{kind: missing_citation, detail: ...}, ...]"`. The writer's prompt is tight enough to respond to each issue individually rather than rewriting everything.

**6. The cap fires plainly, not silently.** When `cycles == MAX_REFINEMENT_CYCLES` and the critic still says `needs_revision`, the supervisor returns the last draft with `status = "ok_with_unresolved_issues"`. This is a distinct status from `ok`. Downstream code (eval harnesses, production gates) can react to it. Silently coercing it to `ok` would be the most dangerous failure mode — the system claims success when it shouldn't.

## Common variations that also work

**Different cycle caps.** `MAX_REFINEMENT_CYCLES = 2 or 4`. The exact number matters less than the principle: it must be finite, and the cap-firing path must distinguish itself from the approval path. Production systems sometimes use 2 (faster convergence) or even 1 (single review pass).

**Different critic temperature.** Lab 11's critic uses `temperature=0`. Some implementations use `temperature=0.5` for the critic specifically — the idea being that a slightly stochastic critic catches issues a deterministic one would miss. This is a defensible tradeoff; it costs reproducibility for a small precision gain.

**Different critic placement.** The critic in this solution reviews the *writer's draft*. An alternative is to have the critic review the *researcher's brief* before the writer ever runs — a "pre-writer critic" that catches bad research before it becomes bad prose. Both are valid; this solution picks post-writer because the failure modes (chunk drift, citation drift) typically surface in prose composition.

## Bugs to watch for

Five things that pass syntax but fail eval:

**1. The critic always returns `needs_revision`.** Symptom of weak default-OK guidance in the system prompt, or temperature being too low (the critic finds the same imperfection every cycle). Check: run the critic on a known-good draft (one you wrote yourself). If it still says `needs_revision`, the critic is over-eager. Fix: tighten the default-OK rule, optionally raise temperature slightly.

**2. The critic always returns `ok` (sycophancy).** Symptom of a critic prompt that frames the role too gently ("offer suggestions"). The critic's prompt should frame the role as STRICT review with enumerated failure modes. Check with the sycophancy diagnostic from the parent lab — give the critic a deliberately bad draft. If it still says `ok`, the critic is sycophantic.

**3. The refinement loop runs but the draft doesn't change.** The writer ignores the revision context. Symptom: every cycle produces nearly-identical prose. Cause: the revision prompt is too soft ("consider these suggestions") rather than directive ("address each of these issues"). Fix: the revision prompt must say "address" not "consider."

**4. The cap fires but the system claims success.** The supervisor returns `{status: "ok"}` even when `cycles == MAX_REFINEMENT_CYCLES`. This is the single most dangerous bug: downstream code sees `ok` and treats unresolved issues as resolved. Verify: print the result envelope after each test run; the cap-fire path must produce `ok_with_unresolved_issues`, *not* `ok`.

**5. The critic sees only the draft, not the brief.** Symptom: critic catches stylistic issues but never catches groundedness violations. Without the brief, the critic has nothing to ground against. Fix: critic args include `findings` and `citations` separately from `draft`.

## Differences from naive implementations

Three things a learner might miss on first pass:

- **The critic is stateless across refinement cycles.** Each critic call receives `(brief, current_draft)` fresh; no memory of previous critiques. This is deliberate: a stateful critic would "remember" issues it raised and either (a) keep raising them even after the writer fixed them, or (b) anchor on those issues and miss new ones the latest revision introduced. Stateless critics compose more predictably.

- **The supervisor doesn't try to interpret critic issues — it forwards them.** When the critic says `{kind: "missing_citation", detail: "the [2] reference is mentioned but not in the citation list"}`, the supervisor passes that text directly into the writer's revision prompt. The supervisor doesn't translate, summarize, or filter. This is the same handoff-hygiene as Lab 10: pass structured payloads, don't paraphrase.

- **`SUPERVISOR_MAX_STEPS` jumped from 6 (Lab 10) to 10.** Lab 10's supervisor needed: 1 call to researcher + 1 to writer + 1 to finalize = 3 minimum, with budget for retries. Lab 11's supervisor needs: 1 researcher + 1 writer + 1 critic + up to 3 × (writer + critic) refinements + 1 finalize = up to 9. Step caps must compose with the patterns they enable.

## Cost and timing

Per end-to-end run:

- 1-2 supervisor calls (initial routing + finalize)
- 2-5 researcher tool calls (web_search + 1-3 fetch_page)
- 1-4 writer calls (initial + 0-3 refinements)
- 1-4 critic calls (one per writer draft)

Total: 5-15 LLM calls per task, ~$0.03-$0.10 at gpt-4o-mini rates. Wall-clock dominated by `fetch_page` for the researcher; the refinement loop is fast (no I/O). Typical end-to-end: 10-20 seconds.

## Next

After completing this lab, move on to [Lab 12 (plan-and-execute from scratch)](../../12-plan-and-execute-from-scratch/) — adds a planner agent emitting a structured Plan, with bounded parallel execution and bounded replanning. The supervisor pattern from Lab 10/11 becomes the dispatcher base; the chat client, action-hash dedup, structured envelopes, and StrictModel patterns carry over.
