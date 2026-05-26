# Multi-turn (threaded) evaluation

> ⏱ ~14 min · 🔴 Advanced · Prerequisites: [Online evaluator registration](./online-evaluator-registration.md), [Agent-as-judge calibration](./agent-as-judge-calibration.md). Helpful: any prior Path 06 lab.

Path 06's prior modules treated each trace as the evaluation unit — score the spans, attribute the cost, sample by the policy. That works for single-turn requests. It breaks for agents that hold conversations across many turns. This page covers what evaluation looks like when the unit shifts from a single request to a complete conversation.

The most-cited failure of 2026 is a voice-AI insurance team whose single-turn evals passed at 92% — faithfulness, groundedness, citation preservation, all green. The production transcripts complained the bot was "going in circles" and "forgetting what I just said." Every turn passed; the conversation failed. The 2026 framing that's stuck: evaluating each turn in isolation is grading movies by random frames.

## The single-turn trap

Single-turn evaluation evaluates one assistant message in the context of one user message (plus optionally retrieved context). Multi-turn evaluation evaluates the whole sequence as a single unit. The shift matters because the failure modes are different:

**Within-turn failures** — the assistant gives a wrong answer to a question that was asked clearly. Single-turn evals catch these.

**Between-turn failures** — the assistant forgets what the user just said, contradicts itself across turns, or re-asks for information already provided. Single-turn evals cannot catch these because each turn looks fine in isolation. The conversation as a whole fails.

Three shifts moved this from "nice to have" to "must have" between 2024 and 2026:

1. **Agents replaced single-shot prompts.** A modern support agent doesn't answer in one turn. It clarifies, retrieves, calls tools, asks confirmation, then answers. Most failures happen between those turns.
2. **Production traces revealed the gap.** Teams running both single-turn evals and human review found the gap was large — single-turn evals at 0.92 paired with user complaints scoring the same conversations at 0.4.
3. **Thread-level tracing went mainstream.** LangSmith made "threads" a first-party concept in October 2025; LangChain, OpenAI, Anthropic, and others followed. Once the trace data was naturally thread-shaped, conversation-level evaluation became a natural extension rather than separate infrastructure.

## The four canonical conversation-level metrics

Four metrics dominate the 2026 multi-turn evaluation landscape, established largely by DeepEval's `ConversationalTestCase` framework and now widely adopted across observability tools:

**Conversation Completeness** — were the user's requests actually fulfilled across the dialogue? Algorithm: (1) extract user intents from the full turn history (typically via LLM-as-judge), (2) for each intent, check whether it was satisfied somewhere in the conversation. Returns a score in [0, 1] plus a per-intent breakdown.

This is the single most important multi-turn metric. If the task doesn't get done, nothing else matters. A conversation can score perfect on every other metric (knowledge retention, role adherence, turn relevancy) and still fail completeness — the agent acknowledged each intent politely and never delivered.

**Knowledge Retention** — does the assistant remember what the user has already provided? Algorithm: extract user-provided facts from earlier turns; check each assistant question against the fact list; flag re-asks. Returns a score in [0, 1].

This is the "do you have a customer service number" / "what's your account number" / "I gave you that two turns ago" failure pattern. The bot has access to its own conversation history; it just doesn't read it.

**Role Adherence** — does the assistant stay within its assigned scope and persona? Algorithm: define a role specification (system prompt scope, allowed topics, refusal patterns); check each assistant turn against the spec via LLM-as-judge. Returns a per-turn score and an aggregate.

This catches the agent that drifts off-task. A customer-service bot that starts giving general medical advice; a coding assistant that starts speculating about the user's personal life. Role adherence is the failure mode that scales with conversation length — the longer the dialogue, the more drift.

**Turn Relevancy** (also called "Conversation Relevancy" in some tools) — is each response contextually appropriate given the full prior history, not just the current question? Algorithm: for each assistant turn, evaluate relevance against the *full* conversation context up to that point. Differs from single-turn relevance because the context includes everything said before.

This catches the agent that gives technically correct answers to the wrong question — e.g., the user asked about their refund three turns ago and the assistant is still answering shipping questions because that was the literal last user message.

## Conversation-level vs turn-level vs trajectory metrics

Three units of evaluation, often confused:

| Unit | Question answered | Example metrics |
|---|---|---|
| **Turn-level** | Given this user turn, was the assistant's response correct? | Faithfulness, single-turn relevance, citation preservation |
| **Conversation-level** | Across the whole dialogue, did the agent succeed? | Conversation Completeness, Knowledge Retention, Role Adherence, Turn Relevancy |
| **Trajectory** | Did the agent take the right path of decisions and tool calls? | Tool-use precision, trajectory-step correctness, replan rate |

The three are complementary, not interchangeable. A coding agent can have perfect turn-level scores (every individual response is correct), perfect conversation-level scores (the user's task was completed), and still have a poor trajectory (used 15 tool calls when 3 would have sufficed). All three views matter for different operational questions.

The trajectory dimension scales harder. Single-turn evaluation is O(n) in test cases. Trajectory evaluation is O(n × k) where k is the average trajectory length — every tool call is a separate evaluation surface. A coding agent making 15 tool calls per task generates 15 checkpoints to evaluate, each of which can fail differently.

## Thread-as-first-party

LangSmith's October 2025 release made threads a first-party concept in agent observability. The pattern that followed:

```
Thread = ordered sequence of traces sharing a thread_id
       = conversation in the user-facing sense
       
Trace = one user request → assistant response
      = one turn in the conversation
      
Span  = one operation within a trace (LLM call, tool call, retrieval)
```

Once your traces carry a `thread.id` attribute (analogous to the `tenant.id` baggage from Module 6's cost attribution), conversation-level evaluation becomes "run a multi-turn evaluator over all traces with this thread.id." LangSmith's Multi-turn Evals run automatically once a thread is marked complete; the developer defines the LLM-as-judge prompt that scores the dialogue.

The same pattern shows up across the tool landscape:
- **LangSmith** — threads + Multi-turn Evals + Insights Agent (the October 2025 release).
- **DeepEval** — `ConversationalTestCase` with the four metrics natively.
- **Confident AI** — Session-level grouping for multi-turn conversations; runs DeepEval metrics on production traces.
- **MLflow GenAI** — `ConversationSimulator` plus conversation-level scorers (experimental in 3.10).
- **Langfuse** — multi-turn conversation evaluation as part of the standard agent-eval suite.

The infrastructure is now in place across the major tools. The remaining work for teams is defining the rubrics and writing the LLM-as-judge prompts.

## The LangChain Deep Agents five-pattern framework

LangChain's production Deep Agents case study established a five-pattern framework for multi-turn evaluation that's worth knowing:

1. **Bespoke test logic per datapoint** — custom assertions for each test case. Not generic metrics; specific checks for what this case should produce.
2. **Single-step evaluations** — validate specific decision points (did the agent pick the right tool at turn 3?). Trajectory-level.
3. **Full agent turn testing** — end-to-end behavior on a complete turn. Turn-level.
4. **Multi-turn with conditional logic** — simulate realistic interactions with branching paths. Conversation-level + simulator.
5. **Proper environment setup** — clean, reproducible conditions. API mocking, containerized environments, deterministic fixtures.

The point isn't to do all five for every test; it's to know which one fits which question. Patterns 3 and 4 are the conversation-level work; pattern 2 is the trajectory work; patterns 1 and 5 are operational discipline.

## Span-attached scores: same metric, CI and production

One operational detail makes multi-turn evals practical in 2026: span-attached scores. The same metric definition runs in CI (against fixtures) and against production traces (against threads). The score lands as a span attribute in both cases.

```python
# CI run
score = conversation_completeness(test_case.turns, judge_model="gpt-4o-mini")
span.set_attribute("eval.conversation_completeness", score)

# Production thread (same function, different input source)
production_thread = trace_store.get_thread(thread_id)
score = conversation_completeness(production_thread.turns, judge_model="gpt-4o-mini")
span.set_attribute("eval.conversation_completeness", score)
```

Same code, same model, same prompt, same span attribute name. The dashboards that watch `eval.conversation_completeness` over time work for both CI regressions and production drift. This is the operational version of "same eval everywhere" — and it's what makes drift detection (Module 5) work on conversation-level scores.

## What this misses

Out of scope; covered elsewhere or later:

- **Conversation simulation** — generating synthetic multi-turn dialogues with personas. Covered in the [next page](./conversation-simulation.md).
- **Tool-use evaluation deep-dive** — "did the agent pick the right tool with the right args" at scale. Touches Path 02/03 (multi-agent and tool-use patterns).
- **Multi-agent conversation evaluation** — when there are multiple agents talking to each other. Path 03 territory.
- **Long-conversation context-window challenges** — when a 100-turn conversation exceeds the judge's context. Sliding-window pattern covered in conversation-simulation.md; deeper techniques (hierarchical summarization, episodic memory eval) out of scope.
- **Red-teaming as a separate discipline** — adversarial persona testing is touched in conversation-simulation.md; DeepTeam-style red-teaming orchestration is its own topic.

## Related concepts

- [Conversation simulation](./conversation-simulation.md) — synthetic personas to generate test conversations at scale.
- [Online evaluator registration](./online-evaluator-registration.md) — the score-stream production pattern multi-turn evals plug into.
- [Agent-as-judge calibration](./agent-as-judge-calibration.md) — LLM-as-judge calibration applies to multi-turn metrics too.
- [Lab 22 — multi-turn evaluation](../../labs/22-multi-turn-evaluation/) — implements three of the four metrics from scratch with a working conversation simulator.

## References

- Confident AI (March 2026), *Multi-Turn LLM Evaluation in 2026: What You Need to Know* — the four-metric framework, the "grading movies by random frames" framing, the 92% / customer-complaints gap example. [confident-ai.com](https://www.confident-ai.com/blog/multi-turn-llm-evaluation-in-2026).
- FutureAGI (March 2026), *Multi-Turn LLM Evaluation in 2026: A Practical Guide* — the three shifts framing, the conversation-level vs turn-level distinction, the span-attached-scores operational pattern. [futureagi.com/blog](https://futureagi.com/blog/multi-turn-llm-evaluation-2026).
- LangChain blog (October 2025), *Improve agent quality with Insights Agent and Multi-turn Evals* — the threads-as-first-party announcement, semantic intent / semantic outcomes / agent trajectory dimensions. [blog.langchain.com](https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/).
- LangChain Deep Agents production case study (via ZenML LLMOps Database) — the five evaluation patterns for production agents. [zenml.io](https://www.zenml.io/llmops-database/evaluation-patterns-for-deep-agents-in-production).
- DeepEval documentation (April 2026), *LLM Metrics introduction* — the `ConversationalTestCase` pattern and the four named multi-turn metrics. [deepeval.com](https://deepeval.com/docs/metrics-introduction).
- Guan et al. 2025, *Evaluating LLM-based Agents for Multi-Turn Conversations: A Survey* — the systematic survey covering ~350 papers; the task-completion / response-quality / user-experience taxonomy. [arxiv.org/abs/2503.22458](https://arxiv.org/abs/2503.22458).
- Adaline (April 2026), *Complete Guide to LLM & AI Agent Evaluation in 2026* — the trace-level / multi-turn-scenario / tool-use / trajectory / state-tracking layering. [adaline.ai/blog](https://www.adaline.ai/blog/complete-guide-llm-ai-agent-evaluation-2026).
