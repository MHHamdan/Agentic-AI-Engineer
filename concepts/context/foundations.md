# Context engineering foundations

> 🟡 Intermediate · ⏱ ~24 min · 🛠 Verified 2026-05-29 · 📍 Module 1 of [Path 05 — Context Engineering](../../learning-paths/05-context-engineering/); pairs with [`token-budgets.md`](./token-budgets.md) for the foundational vocabulary

## What this page is for

Prompt engineering optimizes the single instruction you send the model. Context engineering optimizes *everything else in the context window* — the retrieved documents, the tool results, the conversation history, the system prompt, the structured data — that fills the window before the model generates a single token. For single-turn tasks the two are nearly the same problem. For multi-step agent workflows, they're different problems with different return on engineering effort.

The 2026 production data per [harnessengineering.academy April 2026](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/): "a team that spends three weeks refining a prompt can move task completion from 85% to 88%. A team that redesigns the context pipeline, ensuring the model sees the right information at the right time, can move task completion from 83% to 96%." Both are real gains; the cost-effectiveness isn't.

This page covers:

1. The **prompt-vs-context engineering distinction** and when each dominates
2. The **three context zones** — system prompt, dynamic context, current query
3. The **attention budget framing** — Anthropic's mental model for why context costs scale non-linearly
4. The **100:1 input-to-output ratio** — what it means for cost
5. The **canonical failure modes** — suicide by context, context rot, attention dilution

What this page does **not** cover is in section 6 (Anti-scope). [`token-budgets.md`](./token-budgets.md) follows this page with explicit allocation strategies.

## The prompt-vs-context distinction

A single-turn task — translate this paragraph, classify this ticket, summarize this article — has one model call. The input is what the user said plus a short instruction. The prompt determines quality.

A multi-step agent task — research a topic, debug a codebase, plan a trip, handle a customer ticket end-to-end — has dozens of model calls. Each call sees a different context window: a different selection of conversation history, different retrieved documents, different tool results, different intermediate state. Per [logic.inc April 2026](https://logic.inc/resources/context-engineering-guide-for-ai-teams): "frontier model capability has closed the prompting gap; the failures you see in production today are almost always context failures."

The practical distinction:

| Concern | Prompt engineering dominates | Context engineering dominates |
|---|---|---|
| Task shape | Single turn, one model call | Multi-step, many model calls |
| What you control | Instruction wording | Token allocation across zones |
| Failure mode | Model misunderstands intent | Model loses track / re-derives / runs out of room |
| Ceiling | ~88-92% task completion typical | ~96%+ task completion typical |
| Investment | Days to weeks per prompt | Weeks to months for pipeline redesign |
| ROI scale | Per-prompt improvement | Per-trajectory improvement |

Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): "context engineering failures are often invisible in standard evaluations." A model that scores 0.92 on natural-traffic faithfulness eval can be silently leaking 50% of its context budget to redundant tool outputs that aren't reflected in any aggregate metric.

## The three context zones

Per [harnessengineering.academy April 2026](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/): "every context window has three zones: the system prompt (stable instructions), dynamic context (retrieved documents, tool results, conversation history), and the current query."

### Zone 1 — System prompt

The stable instruction set authored at deploy time. Per [Wire Blog April 2026](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/): "the system prompt is the smallest category but has the strongest influence per token." A 500-token system prompt that defines refusal categories ([`../../security/safety-policy.md`](../../security/safety-policy.md)), tool usage conventions, output format expectations, and escalation paths shapes every subsequent decision the agent makes.

Two properties matter:

- **Stable across turns** — the system prompt doesn't change mid-conversation. This makes it the perfect candidate for prompt caching ([production/cost-engineering.md](../../production/cost-engineering.md) Layer 3a): cached at 1.25× write cost, read at 0.10× cost. Long stable system prompts pay back via cache reads within the conversation.
- **Disproportionate influence per token** — the model treats system-slot content as higher-trust instruction ([`security/prompt-injection.md`](../../security/prompt-injection.md) Defense 2). Authority follows position.

### Zone 2 — Dynamic context

The volatile portion: retrieved documents (RAG), tool results, conversation history, structured state. This zone *grows* across turns. A research agent at turn 1 might see 2K tokens of dynamic context; by turn 20, it could see 80K. The growth is the engineering surface.

Three sub-categories with very different growth dynamics:

| Sub-zone | Typical size | Growth pattern |
|---|---|---|
| **Tool results** | 200-50,000 tokens per call | Unbounded — a single API call can return 50K tokens of JSON unexpectedly. The "suicide by context" failure mode per [TianPan April 2026](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint) |
| **Retrieved documents (RAG)** | 1,000-20,000 tokens per query | Volatile — depends on retrieval policy and chunk size |
| **Conversation history** | 100-500 tokens per turn | Linear in turn count; one long turn can break the pattern |

The dynamic zone is also where Mem0-style memory injection lives. Per [niteagent.com May 2026](https://niteagent.com/blog/ai-agent-cost-optimization-2026/): 24 memory entries inject 594 tokens; 500 entries inject 8,000 tokens. The cost compounds with conversation length.

### Zone 3 — Current query

The user's most recent input. Typically the smallest zone — 50 to 500 tokens for most production traffic. The exception: long documents pasted into a query (10K+ tokens) shift the current-query zone into territory that requires the same allocation discipline as the dynamic zone.

The three-zone model is the vocabulary the rest of Path 05 uses. Modules 2-6 each operate on a specific zone or transition between zones.

## The attention budget framing

Per [Wire Blog April 2026](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/) citing Anthropic's context engineering guide: "every new token introduced depletes this budget by some amount, increasing the need to carefully curate the tokens available." The goal of context engineering is "not to fill the window but to find the smallest set of high-signal tokens that produces the desired result."

The mechanistic basis per [Towards Data Science April 2026](https://towardsdatascience.com/deep-dive-into-context-engineering-for-ai-agents/): "every new token introduced to the LLM depletes this attention budget it has by some amount. The attention scarcity stems from architectural constraints in the transformer, where every token attends to every other token. This leads to an n² interaction pattern for n tokens. As the context grows, the model is forced to spread its attention thinner across more relationships."

Two implications:

1. **More context is not strictly better.** Beyond a per-task optimum, additional tokens dilute attention. The 1M-token context window doesn't mean a 1M-token prompt; it means *headroom*. Module 6 covers when long-context models help and when they don't.
2. **Token *placement* matters as much as token presence.** Per the Maxim research note citing Google DeepMind: "models maintain optimal performance when critical information appears early in context." The retrieved document that contains the answer is more useful at position 2,000 than at position 80,000.

## The 100:1 input-to-output ratio

The production cost framing per [harnessengineering.academy April 2026](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/): "agents have roughly 100:1 input-to-output token ratios. For every token the model generates, it processes 100 tokens of context. This means context costs dominate your API bill. Wasted context is wasted money."

At Anthropic Claude Opus 4.6 pricing ($5.00 / MTok input, $25.00 / MTok output per the [Tokalator paper, arxiv:2604.08290](https://arxiv.org/pdf/2604.08290)): a 100K-token input + 1K-token output costs $0.50 for input + $0.025 for output. Input dominates by 20×. For a 200K input + 2K output: $1.00 input + $0.05 output. Same 20× ratio.

Per the Tokalator paper, the OpenRouter platform data shows "average prompt length grew nearly fourfold between 2024 and 2025 (from approximately 1,500 to >6,000 tokens), driven by agentic workflows and reasoning-intensive tasks." The growth is the cost surface.

The cross-reference to [`production/cost-engineering.md`](../../production/cost-engineering.md) Layer 1 (attribution): the four token layers (prompt / tool / memory / response) are the per-zone attribution version of this page's three zones. Cost engineering attributes; context engineering allocates.

## Canonical failure modes

Three failure modes the production literature has named explicitly.

### Failure 1 — Suicide by context

Per [TianPan April 2026](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint): "an agent reads a file, receives 250K tokens of output, and silently exceeds its context window. The request fails. The agent never understands why. It doesn't crash or throw an exception — it just stops working."

The mechanism: a tool call returns more data than expected; the next agent turn finds itself over the context limit; the API returns a generic error or truncates silently; the agent's reasoning loop falls apart. The fix is structural — tool outputs need explicit length caps ([`security/prompt-injection.md`](../../security/prompt-injection.md) Defense 3) and the agent's planning needs to budget for unbounded returns (Module 2).

### Failure 2 — Context rot

Per [Towards Data Science April 2026](https://towardsdatascience.com/deep-dive-into-context-engineering-for-ai-agents/): the agent's effective working set degrades as context grows. The model is forced to spread attention across more relationships; tokens at the bottom of context (most recent) crowd out tokens at the top (earlier conversation, system prompt) in the model's effective attention. The remediation: context compaction — summarize older content; reinitiate a fresh context window with the summary; resume work with the compacted state. Path 05 Module 3 covers compaction in depth.

### Failure 3 — Re-reading and re-deriving

Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): one of the four context-drift signals — agents re-reading files they already processed; agents re-stating prior decisions; agents gradually reframing the task away from user intent. The pattern appears in step-level traces before it surfaces in output quality.

The mechanism: when the agent's context window doesn't surface the prior work clearly, the agent's planner concludes the work needs to be redone. The fix: structured state representation that the agent's planner can index against, plus explicit "what I already know" sections in the context (Module 5 covers context-drift detection).

## Operational discipline

Five practices that translate the foundations into production behavior:

1. **Treat the context window as a budget, not as storage** per [Wire Blog April 2026](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/). The decision to *add* something to context costs both money (input tokens) and quality (attention dilution). The default is omission; inclusion is a deliberate choice. Module 2 makes this concrete.
2. **Instrument per-zone token counts as first-class metrics**. Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): "tokens mainly go to system prompts and tool outputs. Tool responses — especially search and API results — are often the largest cost." Counting per-zone is the first step toward Module 2's allocation discipline.
3. **Target 60-80% context utilization, not 100%**. Per [machinelearningmastery April 2026](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/): "aim for roughly 60-80% context utilization rather than maxing out capacity." Headroom is required for unexpected tool-output growth (failure 1) and for the planning the model needs to do.
4. **Cache the system-prompt zone aggressively**. The 1.25× write / 0.10× read break-even after 2 reads ([`production/cost-engineering.md`](../../production/cost-engineering.md) Layer 3a) applies. Long stable system prompts compose well with prompt caching; short volatile ones don't.
5. **Trace step-level token counts**, not just final-call counts. The drift signals (Module 5) appear at step level. Aggregate metrics hide the failures that matter.

## Anti-patterns

Three patterns that look like context engineering and aren't:

### Adding more context to fix quality issues

A model gets the wrong answer; the team's first response is to add more retrieved documents, more tool results, more conversation history. The added content often makes things worse (attention dilution per failure 2). The right diagnostic: trace what was in context for the failed turn; identify what was *missing* or what was *misplaced*, not what to add.

### Optimizing prompt wording when the bottleneck is context allocation

Per the 85%→88% vs 83%→96% comparison: prompt-tuning has a ceiling once frontier-model capability is at par with the task. Past that ceiling, more prompt iteration produces diminishing returns. The engineering payoff moves to the context pipeline. Teams that don't notice the regime shift keep iterating on the prompt and wondering why quality plateaus.

### Using prompt caching as the only optimization

Caching helps. It doesn't address attention dilution (the cached prompt still uses attention bandwidth). It doesn't address the dynamic-zone growth pattern. A team that adds prompt caching and declares context engineering "done" misses the larger surface.

## Anti-scope

What this page does not cover:

- **Token allocation per zone** — that's [`token-budgets.md`](./token-budgets.md) (Module 2). This page establishes the vocabulary; Module 2 makes the allocation concrete.
- **Compression and summarization** — that's Module 3 (`compression-and-summarization.md`, planned).
- **Memory tier separation** — short-term / long-term / episodic — that's Module 4 (`memory-tiers.md`, planned).
- **Context drift detection** — that's Module 5 (`context-drift-detection.md`, planned).
- **Long-context model selection** — Module 6 (`long-context-models.md`, planned).
- **Specific framework abstractions** (LangChain `ConversationBufferMemory`, LangGraph `checkpointer`, OpenAI Agents SDK memory APIs). Per the Path 05 README anti-scope: framework wrappers are addressed at the conceptual layer only.
- **Vector database choice and tuning** — that's [`concepts/rag/`](../rag/) and Path 02. Path 05 covers how the agent *uses* retrieved context, not how retrieval is implemented.
- **Prompt engineering for single-turn tasks** — the foundational prompt-engineering literature (OpenAI cookbook, Anthropic prompt-engineering docs) covers this surface.

## References

**Context engineering as a discipline (2026)**:
- [harnessengineering.academy (April 2026), *Context Engineering: The Key Skill Every AI Developer Needs in 2026*](https://harnessengineering.academy/blog/context-engineering-the-key-skill-every-ai-developer-needs-in-2026/) — three-zone model; 83%→96% lift comparison; six core techniques; Manus production techniques
- [logic.inc (April 2026), *Context engineering guide for AI teams 2026*](https://logic.inc/resources/context-engineering-guide-for-ai-teams) — "frontier model capability has closed the prompting gap; failures you see in production today are almost always context failures"
- [machinelearningmastery (April 2026), *Effective Context Engineering for AI Agents: A Developer's Guide*](https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide/) — production metrics (60-80% utilization target); four context-drift signals
- [Towards Data Science (April 2026), *Context Engineering for AI Agents: A Deep Dive*](https://towardsdatascience.com/deep-dive-into-context-engineering-for-ai-agents/) — attention budget mechanistic explanation; n² interaction pattern; context compaction
- [Wire Blog (April 2026), *Context budgets: how to allocate tokens for AI agents*](https://usewire.io/blog/context-budgets-how-to-allocate-tokens-for-ai-agents/) — context-as-budget vs context-as-storage framing; cost framing ($255K → $102K annual customer-service agent)
- [Maxim (October 2025), *Context Engineering for AI Agents: Token Economics and Production Optimization*](https://www.getmaxim.ai/articles/context-engineering-for-ai-agents-production-optimization-strategies/) — Google DeepMind early-position findings; per-zone allocation ranges

**Token economics and growth patterns (2026)**:
- [TianPan (April 2026), *Token Budget as Architecture Constraint*](https://tianpan.co/blog/2026-04-13-token-budget-as-architecture-constraint) — "suicide by context"; 10-cycle reasoning loops at 50x token cost; output tokens 3-8x more expensive than input
- [Tokalator paper (arxiv:2604.08290), *A Context Engineering Toolkit for AI Coding Assistants*](https://arxiv.org/pdf/2604.08290) — 4x growth in average prompt length 2024-2025; Claude Opus 4.6 pricing ($5/MTok input, $25/MTok output)
- [niteagent.com (May 2026), *AI Agent Cost Optimization in 2026*](https://niteagent.com/blog/ai-agent-cost-optimization-2026/) — Mem0 memory-injection scaling (24 entries → 594 tokens; 500 → 8,000 tokens); 80-120K context within 2-3 weeks of deployment

**Repo cross-references**:
- [`token-budgets.md`](./token-budgets.md) — Module 2; concrete allocation strategies that build on this page's three-zone vocabulary
- [`../../production/cost-engineering.md`](../../production/cost-engineering.md) — Layer 1 (attribution) maps to the three-zone counting; Layer 3a (prompt caching) is the Zone-1 optimization referenced here
- [`../../security/prompt-injection.md`](../../security/prompt-injection.md) — Defense 2 (instruction hierarchy) is why the Zone-1 system-prompt position has disproportionate influence; Defense 3 (tool-output sanitization) addresses the suicide-by-context failure mode at the security layer
- [`../../security/safety-policy.md`](../../security/safety-policy.md) — what gets encoded into the Zone-1 system prompt is what this page references
- [Path 03 Pattern 2 — Shared-state boundaries](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) — the 15× token-burn case from full-transcript inlining is the canonical Zone-2 (dynamic context) failure mode
- [Path 03 Pattern 4 — Per-agent cost budgeting](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) — per-agent envelope; Module 2 (token-budgets.md) extends this to per-zone within a single agent's context window
- [`../rag/`](../rag/) — RAG concept pages that determine the shape of Zone 2's retrieved-documents sub-category
