# The generator-critic pattern

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [agent debate and critics](./agent-debate-and-critics.md), [supervisor-worker pattern](./supervisor-worker-pattern.md)

The specific pattern Lab 11 implements: a generator agent produces a draft; a critic agent reviews it against an explicit rubric; if the critic approves, the draft is final, otherwise the generator runs again with the critic's issues injected into its brief. The whole loop is bounded by a hard cap on refinement cycles, orchestrated by the same supervisor pattern from Lab 10.

This page is prescriptive. The previous page covered the *why* and *when*; this page covers the *how*.

## The shape

```
        user task
            │
            ▼
    ┌───────────────┐
    │  supervisor   │ ← Lab 10's supervisor, extended with one new worker
    └───────────────┘
        │   ▲   │   ▲   │
        │   │   │   │   │
        ▼   │   ▼   │   ▼
    researcher  writer  critic
                  ▲       │
                  └───────┘
                  (refinement
                   cycle, up to
                   MAX_REFINEMENT_CYCLES = 3)
```

Three properties to internalize:

1. **The supervisor is unchanged in shape.** Same Lab 10 agent loop. The only changes are: one new worker tool (`call_critic`), an updated system prompt that describes the refinement loop, and a slightly larger step cap to accommodate the cycle.

2. **The generator and critic are independent agents.** They have separate system prompts, separate calling contexts. The critic does not see the generator's reasoning; it sees only the draft and the original brief. This is the deliberate-disagreement property.

3. **The refinement loop is bounded.** `MAX_REFINEMENT_CYCLES = 3`. If the critic still wants changes after the third round, the supervisor surfaces the partial result *and* the critic's remaining concerns. The user sees both.

## The critic's structured envelope

The handoff discipline from [handoffs and shared state](./handoffs-and-shared-state.md) applies: structured payloads, not free text.

The critic returns one of two shapes:

```json
{"status": "ok"}
```

or

```json
{
  "status": "needs_revision",
  "issues": [
    {"kind": "unsupported_claim", "detail": "Claim 'X was founded in 2024' has no supporting sentence in the findings."},
    {"kind": "missing_citation", "detail": "The reference to RFC 7159 is uncited."}
  ]
}
```

Issue kinds are enumerated, not free text. A reasonable starter set for prose tasks:

- `unsupported_claim` — a factual claim in the draft can't be traced to the findings
- `missing_citation` — a claim that should cite a source doesn't
- `dropped_citation` — a citation from the findings doesn't appear in the draft
- `unclear_prose` — the prose is structurally hard to follow
- `format_violation` — the draft violates an explicit format rule (e.g., "150 words")

Enumerating the kinds does real work: the generator's revision prompt can branch on kind ("for each `unsupported_claim` issue, either remove the claim or add a supporting citation"), and you can compute eval metrics over issue distributions.

## Critic prompt design — the four rules

The critic's prompt is the single most consequential design surface in the whole pattern. Get it wrong and you get sycophancy. Get it right and you get useful disagreement that improves quality.

### Rule 1: Anchor the critic to a checklist, not a vibe

Bad: *"Review the draft for quality and provide feedback."*
Good: *"Apply each of these checks in order. If all pass, return ok. If any fail, return needs_revision with one issue per failed check."*

The difference is whether the critic is doing concrete pass/fail decisions on enumerable items, or doing a holistic vibes-based assessment. Vibes-based critics either approve everything (sycophancy) or flag arbitrary nits.

### Rule 2: Make "ok" the default for borderline cases

Bad: *"Flag any issues you notice."*
Good: *"Flag only issues that meet the bar in the rubric. When uncertain, default to ok."*

Critics over-flag by default because the model interprets the critique-framing as adversarial. Explicit "default to ok when uncertain" framing pulls the balance back toward useful precision. Borderline calls almost always cost more in noise than they yield in signal.

### Rule 3: Require specific evidence in each issue

Bad: *"The draft has factual issues."*
Good: *"For claim X in the draft, find the supporting sentence in the findings. If you cannot find it, flag as `unsupported_claim` with the specific claim quoted."*

Forces the critic to actually do the lookup, not pattern-match on "looks suspicious." Critics that can't ground their objections in specific evidence usually can't ground them at all.

### Rule 4: Bound the issue list

Bad: *"List all issues."*
Good: *"List up to 3 most important issues. If you find more than 3, that's a signal the draft needs structural revision, not point fixes."*

More than 3 issues per round usually indicates a structural problem with the brief or the generator's approach, not point-fixable details. Bounding the list forces prioritization and prevents the generator from being asked to fix 12 things at once.

## Bounded refinement

The supervisor maintains a `refinement_cycles` counter. Pseudocode for the loop:

```
researcher → findings, citations
writer(brief=findings+citations) → draft_v1
critic(draft_v1, brief) → critic_response

cycles = 0
while critic_response.status == "needs_revision" and cycles < 3:
    cycles += 1
    revised_brief = brief + critic_response.issues
    writer(revised_brief) → draft_vN
    critic(draft_vN, brief) → critic_response

if critic_response.status == "ok":
    return draft_vN
else:
    return draft_vN with status="bounded_by_cap" and unresolved_issues
```

The hard cap matters. Without it, runaway disagreement (one of the four failure modes) produces unbounded refinement. With it, you guarantee termination at the cost of occasionally surfacing partial results.

When the cap fires legitimately — the critic genuinely sees real issues that the generator can't fix — surfacing the partial draft *with* the critic's remaining concerns is the right move. The user gets the best draft the system could produce *and* an honest account of what's still wrong. That honesty is more valuable than a forced approval would be.

## Sycophancy: detection and mitigation

### Detection: the obvious-bad-draft test

Take an obviously-bad draft — made-up facts, missing citations, internally contradictory — and ask the critic to review it. If the critic returns `ok`, your prompt is sycophantic. This is a routine diagnostic; Lab 11 includes it explicitly before running the full pipeline.

If you can't construct an obviously-bad draft to test against, your task probably doesn't have a clear enough quality criterion to support critic-style refinement in the first place.

### Mitigation 1: Different temperature for the critic

Set the critic's temperature to `0.0` while the generator runs at `0.0`-`0.3`. Small effect on its own but compounds with the other mitigations.

### Mitigation 2: Adversarial system-prompt framing

The critic's system prompt should explicitly position the critic as a strict reviewer:

> *"You are a strict reviewer. Your job is to find issues in drafts, not to be agreeable. Default to ok only when the draft genuinely meets the rubric."*

The framing matters because RLHF tunes models toward agreement; the prompt has to push back explicitly.

### Mitigation 3: Concrete rubric anchors

The critic prompt should reference *specific*, *checkable* criteria. "Each claim must be supported by a sentence in the findings" is checkable. "The prose should be high-quality" is not. Replace vague rubrics with checkable ones; sycophancy drops sharply.

### Mitigation 4: Different model

If your budget allows two API costs, use a different model for the critic than for the generator. Different model lineage = different blind spots = stronger disagreement. This is the strongest single mitigation but has cost implications.

Lab 11 stays with one model for clarity but uses mitigations 1-3.

## Self-critique vs separate-critic — the cost-quality trade

Self-critique: the same agent reviews its own work. One additional LLM call per refinement round. Cheaper.

Separate-critic: a distinct agent with its own prompt. Two LLM calls per refinement round (the critic, then potentially the generator's revision). More expensive.

Empirically, separate-critic is the production default for any high-stakes task. Self-critique works fine for catching obvious errors (typos, format violations) but misses subtle errors at a much higher rate. The same context that produced the draft has the same blind spots when reviewing it.

A useful framing: **the prompt difference is what gets you useful disagreement, not the model difference**. The separate critic typically runs on the same model as the generator; what makes the critique useful is that the prompts are different — adversarial-framed vs generative-framed. The "separate model" mitigation above is gravy on top.

## Composing with Lab 10

Lab 11's supervisor is *literally* Lab 10's supervisor with one new tool added. The deltas:

- Add `call_critic` to `SUPERVISOR_TOOLS` with a `CallCriticArgs` schema (draft + brief).
- Update `SUPERVISOR_SYSTEM_PROMPT` to describe the refinement loop and the `MAX_REFINEMENT_CYCLES` cap.
- Raise `SUPERVISOR_MAX_STEPS` modestly (Lab 10's `6` → Lab 11's `10`) to accommodate the refinement cycles.
- Everything else — the agent loop, action-hash dedup, structured-error envelope, the chat client, the researcher and writer workers — stays identical.

The action-hash dedup is worth flagging: it composes naturally. If the writer produces the *same* draft twice (because the critic's issues didn't get incorporated), the next critic call has identical arguments and the dedup catches it — a useful signal that the refinement loop isn't actually refining.

## When this pattern stops working

Two situations where you should reach for a different pattern:

- **The critic and generator agree on everything but the output is still bad.** Either the rubric is wrong (you're checking the wrong things) or the generator is at the model's quality ceiling. More refinement rounds won't help; better data, better tools, or a stronger model will.
- **The critic objections require parallel exploration of alternatives.** "Should this be a list or a paragraph?" — the answer needs trying both and comparing. That's Tree-of-Thoughts territory, not generator-critic. Out of scope here.

## Related concepts

- The general framing this pattern lives within: [agent debate and critics](./agent-debate-and-critics.md).
- The supervisor that orchestrates the loop: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The structured-payload discipline the critic envelope follows: [handoffs and shared state](./handoffs-and-shared-state.md#rule-1-handoffs-carry-structured-payloads-not-free-text).
- The eval-rubric discipline that critic prompts encode: [`concepts/evaluation/answer-quality-metrics.md`](../evaluation/answer-quality-metrics.md).

## References

- Madaan et al. 2023, ["Self-Refine"](https://arxiv.org/abs/2303.17651) — empirical baseline for iterative-critique gains.
- Sharma et al. 2023, ["Towards Understanding Sycophancy in Language Models"](https://arxiv.org/abs/2310.13548) — the mechanism behind sycophancy; required reading for anyone building critics.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the evaluator-optimizer section describes essentially this pattern; engineering-grounded.
- Saunders et al. 2022, ["Self-critiquing models for assisting human evaluators"](https://arxiv.org/abs/2206.05802) — foundational work on critique-quality.
