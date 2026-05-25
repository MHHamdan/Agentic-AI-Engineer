# Agent debate and critics

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [supervisor-worker pattern](./supervisor-worker-pattern.md), [handoffs and shared state](./handoffs-and-shared-state.md)

A single-pass agent gets one shot to produce its output. Whatever's wrong with the first draft — unsupported claims, lost citations, weak prose, brittle code — ships unless someone reviews it. Adding a *critic* in the loop is the simplest way to inject that review. It's also where multi-agent systems most often fail in interesting ways.

This page covers the general framing. The next page, [generator-critic pattern](./generator-critic-pattern.md), covers the specific pattern Lab 11 implements.

## The premise

Iterative refinement beats single-pass when the gap between "first draft" and "good draft" is large enough to justify the cost.

That's the whole claim. The cost is concrete: a critic round adds at least one LLM call (the critic itself) plus often one more (the generator's revision). For a task where the first draft is reliably good — factual recall on stable knowledge, simple template fills, mechanical transformations — that cost buys nothing. For a task with a genuine first-draft-quality gap — prose with citations to verify, code that must compile, factual summaries where mistakes propagate — that cost buys real quality.

The discipline is to know which kind of task you have *before* adding a critic. The most common multi-agent failure mode in production isn't the critic doing the wrong thing — it's adding a critic to a task that didn't need one and discovering the costs are real and the gains aren't.

## The pattern family

Three points on a spectrum, from cheapest to most expensive:

- **Self-critique** — the same agent reviews its own draft. One additional LLM call. Cheap, but the agent reviewing its own work tends to approve it (the same context that produced the draft is the same context evaluating it). The degenerate case of the pattern; mostly useful for catching obvious errors, not subtle ones.
- **Generator-critic** — a separate critic agent reviews the generator's draft. Two distinct prompts; typically same model with different temperatures and system prompts; sometimes different models. The default form of the pattern. Lab 11 implements this.
- **Multi-agent debate** — three or more agents argue, propose, critique each other's positions. The generalization. Most papers in the "multi-agent debate" literature describe variants of this; in practice, the marginal gain over generator-critic is small for most tasks and the orchestration complexity is large. Out of scope for Path 03 v1.

Path 03 focuses on generator-critic because it's where most production value lives. If you genuinely need 3+ argued positions, you'll know it — and you'll know it because you tried generator-critic first and found it insufficient.

## When critique earns its place

Tasks where a critic provides real signal the generator lacks:

- **Prose with citations.** The generator writes the prose; the critic checks each claim against the source. This is one of the clearest wins because the critique target (citations) is mechanically verifiable.
- **Code that must compile or pass tests.** The generator writes code; the critic runs it (or reads it carefully) and reports failures. Even better when the critic has access to actual execution.
- **Factual answers where wrong is worse than slow.** Medical, legal, financial summaries where mistakes have consequences. The critic's marginal cost is dwarfed by the cost of a wrong answer.
- **Anything where the eval criterion is clear enough to encode in a critic prompt.** The critic prompt is the operationalization of the eval criterion. If you can't articulate what "good" looks like in the critic prompt, you can't build a useful critic.

## When critique doesn't help

Tasks where the critic doesn't have signal the generator lacks:

- **Stable factual recall.** "What year was the Eiffel Tower built?" — the generator either knows or doesn't; the critic has the same information.
- **Speed-critical workloads.** Real-time chat, completion suggestions. The 2-4x latency multiplier is too expensive.
- **Tasks where the first draft is reliably good.** Mechanical transformations, simple template fills, format conversions. Adding a critic is overhead with no upside.
- **Tasks with no clear quality criterion.** "Write something interesting about X" — the critic has nothing concrete to check against. Without a rubric, the critic falls back on vibes, and vibes-based critics either sycophant ("looks fine to me") or invent objections.

A useful heuristic: if you wouldn't be able to write a useful eval rubric for the task (Lab 09 territory), you probably can't write a useful critic prompt either. The critic prompt *is* an eval rubric, applied at inference time.

## Four failure modes specific to debate

These don't show up in single-agent or supervisor-worker patterns. They're emergent properties of the generator-critic interaction.

### Sycophancy

The critic agrees with whatever the generator produced. Returns `{"status": "ok"}` regardless of draft quality.

This is **the most common multi-agent debate failure mode**, and it's not the model being lazy — it's an artifact of how RLHF tunes models to be agreeable. A critic prompt that says "review this draft" gets a model in agreement mode, and agreement mode says "looks good." Confirmed empirically: Sharma et al. 2023 documented sycophancy as a stable, model-wide tendency in production-grade LLMs.

Diagnostic test: feed the critic an obviously-bad draft (made-up facts, missing citations, contradictions) and see if it gets flagged. If it doesn't, your critic prompt is sycophantic. Lab 11 includes this test explicitly.

Mitigations live in the next page; the short version is rubric anchoring + adversarial framing + (sometimes) a different model.

### Infinite agreement

Generator and critic loop into a stable mediocre state. The critic approves the draft, but the draft isn't good — neither agent has signal the other lacks. The system terminates "successfully" with mediocre output, and nobody complains because both agents are happy.

This is sycophancy's cousin. The fix is the same: bias the critic toward strict review. The diagnostic is harder: you can't catch this in real-time; you catch it in eval.

### Runaway disagreement

The critic always finds issues. The generator can never satisfy. Each revision triggers a new round of objections. The pattern produces an unbounded refinement loop and no final answer.

This is the failure mode the `MAX_REFINEMENT_CYCLES` cap exists for. Set it to 3. If you genuinely need more cycles, you have a task that's not converging — surface that fact to the user instead of looping forever.

Common root cause: the critic prompt doesn't have a clear "ok" threshold. "Review the draft" is open-ended; "verify each claim has a supporting citation; if all do, return ok" has a clear yes/no. Anchored critics terminate; vibe critics don't.

### Critique drift

The critic gradually changes its standards across rounds. Round 1 flags X; the generator fixes X; round 2 flags Y while accepting X; round 3 flags Z while accepting X and Y. The standards aren't stable.

This shows up as the generator producing increasingly weird revisions that try to satisfy successive contradictory critiques. Mitigation: the critic should receive *only* the current draft, not the revision history. Stateless critic, fresh judgment each round.

## Self-critique vs separate-critic

Self-critique: one agent generates, then reviews its own work in a second call. Cheaper (one fewer agent's worth of prompt setup). Faster. But empirically more sycophantic — the same model in the same context has the same blind spots.

Separate-critic: two distinct agents, two distinct prompts, often the same underlying model. The critic's prompt is adversarial-framed ("you are a strict reviewer; flag issues"); the generator's prompt is generative-framed ("produce the best draft you can"). The prompt difference is what gets you useful disagreement; the temperature difference helps a small additional amount.

Lab 11 uses separate-critic. It's the production default. Self-critique is occasionally useful for cost-constrained workloads where you'd rather have *some* review than none, but for any high-stakes task, separate-critic is the right baseline.

## What this pattern is not

Three patterns that get conflated with generator-critic but solve different problems:

- **Tree-of-Thoughts / search over critique paths** — explores multiple candidate drafts in parallel; uses the critic to score them; picks the best. Different shape (parallel + selection), different cost (N× generation calls), different bug profile. Generator-critic is a *sequential* refinement loop, not a search.
- **Self-consistency / majority voting** — generates N independent drafts; takes the most common answer. Useful for factual answers with discrete outcomes; not useful for prose. No critic involved.
- **Constitutional AI / RLHF-time critique** — uses critique during *training* to align model behavior, not during inference. Bai et al. 2022. Different time horizon, different deployment.

If your task wants any of those, generator-critic is the wrong tool.

## Related concepts

- The specific pattern Lab 11 implements: [generator-critic pattern](./generator-critic-pattern.md).
- The supervisor that orchestrates the generator-critic cycle: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The handoff envelopes the critic uses: [handoffs and shared state](./handoffs-and-shared-state.md).
- The eval-rubric discipline that critic prompts encode: [`concepts/evaluation/answer-quality-metrics.md`](../evaluation/answer-quality-metrics.md).

## References

- Madaan et al. 2023, ["Self-Refine: Iterative Refinement with Self-Feedback"](https://arxiv.org/abs/2303.17651) — the canonical paper on iterative-refinement-via-critique. Reports gains across diverse tasks; useful baseline but also useful for understanding when the pattern fails.
- Saunders et al. 2022, ["Self-critiquing models for assisting human evaluators"](https://arxiv.org/abs/2206.05802) — OpenAI's foundational work on critique models. The critic-as-eval-assistant framing.
- Sharma et al. 2023, ["Towards Understanding Sycophancy in Language Models"](https://arxiv.org/abs/2310.13548) — the canonical sycophancy paper. Read this if you're going to build any critic.
- Bai et al. 2022, ["Constitutional AI: Harmlessness from AI Feedback"](https://arxiv.org/abs/2212.08073) — different time horizon (training-time critique) but useful framing for "what makes a critic useful."
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the "evaluator-optimizer" section describes essentially this pattern.
- Du et al. 2023, ["Improving Factuality and Reasoning in Language Models through Multiagent Debate"](https://arxiv.org/abs/2305.14325) — multi-agent (3+) debate variant; useful for understanding why generator-critic captures most of the benefit at lower cost.
