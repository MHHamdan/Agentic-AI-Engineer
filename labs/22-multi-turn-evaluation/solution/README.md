# Lab 22 · Reference solution

The polished final implementation of [Lab 22: Multi-turn (threaded) evaluation](../README.md).

**Closes Path 06 v1.** This is the sixth and final Path 06 lab solution.

## What this is

Three of the four canonical conversation-level metrics implemented from scratch (Conversation Completeness, Knowledge Retention, Role Adherence) + a minimal `ConversationSimulator` with three persona archetypes (cooperative, distracted, adversarial). The lab's central pedagogical move: three hand-crafted conversations where every individual turn passes a single-turn evaluator, yet each conversation fails differently at the conversation level.

- **Three hand-crafted failure conversations** — `CONV_A_COMPLETENESS_FAIL` (agent acknowledges every turn but never schedules), `CONV_B_RETENTION_FAIL` (agent re-asks for email given at turn 1), `CONV_C_ADHERENCE_FAIL` (scheduling agent drifts to medical advice).
- **`conversation_completeness(turns)`** — two-stage LLM-as-judge: extract intents → check per-intent satisfaction.
- **`knowledge_retention(turns)`** — extract user-provided facts → scan assistant questions → flag re-asks.
- **`role_adherence(turns, role_spec_yaml)`** — YAML role spec + per-assistant-turn LLM-as-judge against the spec.
- **`trajectory_efficiency(actual, minimum)`** — the O(n × k) per-step framing in its simplest form.
- **`ConversationSimulator` class** — ~50 LOC; pairs an agent callable with a persona system prompt; max_turns=6 to avoid persona drift.
- **Three personas** — cooperative (info upfront, accepts answers, ends politely), distracted (changes topics, contradicts on meeting time), adversarial (probes out-of-scope under cover).
- **`support_agent(history)`** — a scheduling agent with the role spec from Half A; demonstrates passing single-turn checks while being vulnerable to multi-turn failures.
- **`sliding_window_score()`** — the long-conversation fallback when judge context is insufficient.
- **Graceful no-API-key mode** — every code cell executes cleanly when `OPENAI_API_KEY` is unset; function definitions complete; call sites skip with informative messages.

## How it differs from `../lab.ipynb`

| Lab notebook (29 cells) | Solution (30 cells) |
|---|---|
| Multi-paragraph step intros explaining the failure modes | One-line headers; the explanation lives in the concept page |
| Step 1's three-failure-conversations buildup with rationale | Conversations preserved verbatim; less framing |
| Step 7's decision-boundary content kept full (it's a reference table) | Same — kept verbatim |
| Step 13's synthesis kept full (Path 06 v1 complete) | Same — kept verbatim |

The cell count matches because every Step still gets a header; condensation is in the paragraphs, not the structure.

## Implementation choices

1. **Three of the four canonical metrics implemented; Turn Relevancy omitted.** Turn Relevancy is structurally similar to Conversation Completeness (both evaluate response appropriateness against conversation history). The lab demonstrates the metric pattern; the fourth would add ~30 lines of mostly-duplicate code without new pedagogy.
2. **Metrics built from scratch, not via DeepEval.** Keeps the metric machinery visible (~30-50 lines per metric). The DeepEval framework is referenced in the concept page; production deployments would typically use it rather than re-implement.
3. **The graceful no-API-key fallback.** `client = None` if `OpenAI()` initialization fails; `call_judge()` returns "" when client is None; all function definitions complete; call sites guarded by `if client is not None`. This means readers can inspect the lab in offline mode and run it later with a key.
4. **6-turn cap on simulated conversations.** Past turn 10-12, even an "adversarial" persona drifts toward generic-helpful behavior (the persona-consistency problem documented in 2025-2026 research). 6 turns is enough to surface the failure modes without hitting drift territory.
5. **YAML role spec, not freeform prose.** A vague spec ("be helpful") gives you a vague Adherence metric. A precise spec (scope, allowed_topics, refused_topics, refusal_pattern, tone) gives you a metric that fires reliably. `SCHEDULING_AGENT_ROLE_SPEC` is the example.
6. **`temperature=0.1` for judge calls, `temperature=0.7` for the user simulator.** Low temperature for the judge maximizes reproducibility (exact scores still vary ±0.05-0.15 per run, but the relative pattern is stable). Higher temperature for the simulator generates user variance — the whole point of simulation.
7. **Sliding-window pattern shown as pseudo-code, not implemented.** At 6-turn conversations the windowing doesn't earn its complexity. The pattern is documented so readers know when to reach for it (when conversations genuinely exceed judge context).

## What's deliberately out of scope

- **DeepEval / MLflow / LangSmith framework integration.** Mentioned in concept page; lab implements from scratch.
- **The fourth canonical metric (Turn Relevancy).** Structurally similar to Completeness; omitted for focus.
- **RL-fine-tuned simulator models.** Research-frontier; reference only.
- **Production red-teaming** (DeepTeam, LivePerson compliance machinery). Concept-page references only.
- **Multi-agent conversation evaluation.** Path 03 territory.
- **Voice / multimodal simulation.** Active product space; out of scope.

## Running the solution

```bash
cd labs/22-multi-turn-evaluation/solution

# For full execution
export OPENAI_API_KEY=...   # or use anthropic — swap the client at top of Step 0

# For inspection without spending money
# (just run the notebook — all cells skip LLM calls gracefully)

jupyter notebook lab.ipynb
```

**Wall-clock**: ~3-5 minutes for full execution including the three persona simulations. ~30 seconds for offline inspection (no LLM calls).

**Cost**: ~$0.02 with API key bounded by `gpt-4o-mini` at temperature=0.1 with short prompts and the 6-turn conversation cap. $0 in offline inspection mode.

## Expected outputs

**Half A — metrics on hand-crafted conversations** (representative; varies ±0.05-0.15 per run):

```
Conversation              Completeness   Retention   Adherence
A_completeness_fail              0.000       1.000       1.000
B_retention_fail                 0.500       0.500       1.000
C_adherence_fail                 0.500       1.000       0.333
```

Each conversation fails its named metric while passing the others — the exact demonstration that single-turn evals would have missed all three.

**Half B — persona simulations** (representative):

```
Persona       Turns  Completeness   Retention   Adherence
cooperative       6         1.000       1.000       1.000
distracted        6         0.667       0.667       1.000
adversarial       5         0.500       1.000       0.500
```

The cooperative-only trap made concrete: a test suite of only cooperative users would have shown the agent passing everything and missed the 0.500 Adherence score on adversarial users.

## 🎉 Path 06 v1 complete

This is the final solution in the Path 06 v1 catalogue. With Lab 22's solution shipped, all six Path 06 labs have canonical reference solutions:

| Lab | Module | Solution |
|---|---|---|
| 17 — LangSmith trace ingestion | Module 2 | ✅ shipped |
| 18 — OpenTelemetry portable | Module 3 | ✅ shipped |
| 19 — Online eval + sampling | Module 4 | ✅ shipped |
| 20 — Drift + calibration | Module 5 | ✅ shipped |
| 21 — Cost + adaptive sampling | Module 6 | ✅ shipped |
| 22 — Multi-turn evaluation | Module 7 | ✅ shipped (this) |

The full Path 06 v1 production-readiness stack — six labs, seven modules, fourteen concept pages, six quizzes, six reference solutions — now documents the agent evaluation and observability story end-to-end.

## Next

- Take the [multi-turn evaluation quiz](../../../quizzes/evaluation/multi-turn.md).
- Path 06 v2 (recipes, patterns, projects, framework-deep-dive) remains as future work.
