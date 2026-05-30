# Glossary

A-Z index of terms used across the Agentic AI Engineer repo. Each entry is a one or two sentence working definition with a link to where the term is canonically discussed.

Glossary entries are **not** a substitute for concept pages. If a term needs more than two sentences to define, it gets its own page in [`concepts/`](../concepts/) or [`math-foundations/`](../math-foundations/) and the glossary entry links to it.

When a term has multiple meanings across communities (e.g., *agent*, *context*, *retrieval*), the glossary picks **one** working definition for this repo. The convention is documented in [`README.md`](./README.md).

---

## A

**A2A (Agent2Agent Protocol).** Open standard for inter-agent communication across organizational and codebase boundaries — the cross-system counterpart to MCP. → [Path 04 — Tool Protocols (MCP + A2A)](../learning-paths/04-tool-protocols-mcp-a2a/).

**Action.** In agentic systems, one step the agent takes in the environment — usually a tool call. In RL terminology, $a_t$ in a policy $\pi_\theta(a_t \mid s_t)$. → [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**Adaptive sampling.** Evaluation strategy where harder or higher-stakes inputs get more eval coverage than easy ones — keeps eval cost bounded as production traffic grows. → Path 06 v2.

**Adversarial red-teaming.** Systematic probing of an agent system with attacks designed to elicit unsafe, off-policy, or low-quality outputs. The harness runs continuously in mature production systems. → Path 06 v2 + Path 07 security material.

**Agent.** A system that takes goals, plans actions, calls tools, observes results, and iterates toward an outcome — distinguished from a stateless LLM call by the *loop* and the *autonomy over tool selection*. → [`concepts/agents/`](../concepts/agents/).

**Agent loop.** The iterative reasoning-acting-observing cycle that defines an agent. Common formulations: ReAct (think → act → observe), plan-and-execute (plan once → execute each step). → [`patterns/01-single-agent-tool-use.md`](../patterns/01-single-agent-tool-use.md) + [`math-foundations/06-react-formalization.md`](../math-foundations/06-react-formalization.md).

**Agentic RAG.** RAG where retrieval is a tool the agent can choose to call (rather than a pre-pended context block), allowing query reformulation, multi-step retrieval, and reflexive critique. → [`patterns/08-agentic-rag.md`](../patterns/08-agentic-rag.md) + Path 02.

**Approval gate.** Pause point in an agent workflow where execution waits for explicit human approval before continuing — the operational primitive of HITL. → [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md).

**Audit trail.** Append-only log capturing every decision, source citation, and model action for compliance reconstruction. The minimum schema (timestamp_UTC, audit_id, user_id, model_version, prompt_version, tool_calls, sources_cited, verdict) is the load-bearing artifact for regulated-domain deployments. → [Project 06 — Financial research analyst](../projects/capstone/06-financial-research-analyst/).

## B

**Belief state.** In a POMDP, the agent's probability distribution over hidden states — what the agent *thinks* the world looks like given partial observations. → [`math-foundations/`](../math-foundations/) Page 05 (planned).

**BM25.** A sparse keyword-based retrieval scoring function used in hybrid search alongside dense vector retrieval. Strong for exact-match technical terms where embeddings underperform. → Path 02.

## C

**Calibration.** The property that a model's stated confidence matches its actual accuracy — a 70%-confident answer should be right 70% of the time. Drifts can be detected via reliability diagrams. → Path 06 v2 + Lab 20.

**Canonical RAG.** The seven-stage pipeline (ingest / chunk / embed / index / retrieve / generate / cite) — the production-RAG starting point before agentic extensions. → Path 02 + [Project 02 — PDF Q&A bot](../projects/beginner/02-pdf-qa-bot/).

**Capstone (project).** Full-stack agentic system spanning at least four paths with evaluation, observability, deployment, and a written architecture defense. → [`projects/capstone/`](../projects/capstone/).

**Checkpoint.** Persisted state at a known point in a long-running agent execution. Enables resume after crash/restart. LangGraph saves checkpoints *between nodes*, not inside nodes. → [Project 08 — Production-ready deep research](../projects/capstone/08-production-ready-deep-research/).

**Chunking.** Splitting documents into retrieval units with chosen size + overlap + boundary policy. Production failure modes: split sentences mid-word, lost table contents, header/footer pollution. → Path 02 + [`concepts/rag/`](../concepts/rag/).

**Compaction.** Compressing long-running conversation context into a shorter summary so subsequent turns stay within the token budget. Modern implementations: Anthropic's `tools=[{'type': 'context_compaction_2026-01-15'}]`. → Path 05 Module 3.

**Compliance review.** Automated first-pass review of agent outputs against domain-specific policies (citation completeness, contradiction detection, scope boundary). Implemented as a judge ensemble per [Project 06](../projects/capstone/06-financial-research-analyst/).

**Context budget.** The token allocation per zone of an agent's context (system prompt / tool definitions / conversation / retrieval / scratchpad). Per-zone tiers + soft/hard caps prevent runaway growth. → Path 05 Module 2 + [`concepts/context/token-budgets.md`](../concepts/context/token-budgets.md).

**Context drift.** Multi-turn degradation pattern where the agent's behavior loses coherence over time (re-reading the same content, re-deciding the same question, task reframing, retrieval-precision collapse). → Path 05 Module 5 + [`concepts/context/context-drift-detection.md`](../concepts/context/context-drift-detection.md).

**Context engineering.** The discipline of allocating, ordering, and managing the agent's context window — the engineering layer between "more tokens" and "the right tokens." → Path 05.

**Context window.** The maximum input length a model can process in one call. Frontier models in 2026 range from ~200K to 1M+ tokens. The engineering decision: use long-context or build tiered architecture? → Path 05 Module 6 + [`concepts/context/long-context-models.md`](../concepts/context/long-context-models.md).

**Cost engineering.** Practice of measuring, attributing, and bounding LLM call costs across an agent system. Soft caps trigger warnings; hard caps trigger graceful termination. → [`production/cost-engineering.md`](../production/cost-engineering.md) + Path 03 v2 Pattern 4.

**Cross-agent provenance.** Tracking which agent produced which output, from which inputs, in which step, across a multi-agent system. Load-bearing for audit trails. → Path 03 v2 Pattern 6.

## D

**Deep research.** Agent pattern that decomposes a topic into sub-questions, iteratively browses + verifies sources, and synthesizes a citation-grounded report. The architectural template for both [Project 01](../projects/beginner/01-personal-research-assistant/) (light) and [Project 08](../projects/capstone/08-production-ready-deep-research/) (long-running). → [`patterns/09-deep-research.md`](../patterns/09-deep-research.md).

**Drift detection.** Monitoring agent quality over time via score drift (judge scores), embedding drift (query/result distribution), or context drift (multi-turn signals). → Path 06 v2 Lab 20 + Lab 23.

**Durable execution.** Orchestration property where a workflow survives infrastructure failures and resumes from the exact point of interruption. The 2026 production frontier — Temporal, LangGraph 1.0, Deep Agents runtime. → [Project 08](../projects/capstone/08-production-ready-deep-research/).

## E

**Embedding.** Dense vector representation of text (or other modality) where semantic similarity maps to cosine or dot-product distance. Production models: OpenAI text-embedding-3, Cohere embed-v3, sentence-transformers. → [`math-foundations/`](../math-foundations/) Page 02 (planned).

**Embedding-space drift.** Distribution shift in query or retrieval-result embeddings over time, detected via clustering or distance-from-centroid metrics. Catches retrieval degradation before quality drops. → Lab 23.

**Escalation.** When an agent recognizes a failure mode it can't handle and routes to a different agent (multi-agent) or a human (HITL). Defined per failure class in retry policies. → Path 03 v2 Pattern 3.

**Evaluation.** Measuring agent output quality through golden datasets, LLM-as-judge, judge ensembles, online evaluators, or human review. → Path 06 v1 + v2.

## F

**Faithfulness.** Eval metric measuring whether a generated answer is supported by its cited sources — the canonical RAG failure mode the metric catches. → Path 06 v1 + [`concepts/evaluation/`](../concepts/evaluation/).

**Fallback.** When the agent's preferred approach fails, the policy that chooses the simpler/safer alternative. Sister concept to escalation. → Path 03 v2 Pattern 3.

**Function calling.** The OpenAI/Anthropic API mechanism by which an LLM can invoke a developer-defined function with structured arguments. Also called tool calling; the protocol substrate underneath both terms. → Path 01.

## G

**Golden dataset.** Hand-curated set of input-output examples used as ground truth for offline evaluation. Maintained and versioned alongside the agent code. → Path 06 v1.

**GraphRAG.** RAG variant that builds a knowledge graph from documents and traverses it to retrieve evidence — strong for multi-hop reasoning. Coming in Path 02 v3.

**Guardrail.** Runtime check that blocks unsafe or off-policy agent outputs. Input guardrails screen the request; output guardrails screen the response. → [`security/`](../security/) + Path 07.

## H

**Handoff.** Control transfer between agents in a multi-agent system. The agent receiving the handoff inherits state and continues the task. → Path 03 v1 + [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md).

**Handoff contract.** The typed data structure that defines what crosses an agent boundary — load-bearing for clean multi-agent systems. Per Path 03 v2 Pattern 1: only structured data crosses, never raw chat history.

**Hierarchical (multi-agent).** Topology where agents form a tree: top-level coordinator delegates to mid-level managers who delegate to leaf-level specialists. → [`patterns/04-hierarchical-teams.md`](../patterns/04-hierarchical-teams.md).

**HITL (Human-in-the-loop).** Agent workflow that pauses at designated decision points for explicit human approval before continuing. State persists across the pause. → [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md).

**Host (MCP).** The application that maintains MCP client connections to one or more MCP servers — Claude Desktop, Cursor, your custom agent. → Path 04.

**Hybrid search.** Combining dense vector retrieval with sparse keyword retrieval (BM25) and re-ranking. Stronger than either alone, particularly for queries mixing technical terms with semantic concepts. → Path 02.

**HyDE (Hypothetical Document Embeddings).** RAG variant where the LLM generates a hypothetical answer first; the embedding of the *hypothetical answer* (not the question) drives retrieval. Coming in Path 02 v3.

## J

**Judge ensemble.** Multiple LLM-as-judge instances scoring the same output with intentionally different biases. Disagreement structure routes to human review or regression promotion. → Path 06 Pattern 3.

## L

**LangGraph.** Open-source orchestration library for stateful, multi-actor agent applications. Built-in checkpointing; HITL pause-and-resume; integrates with the broader LangChain ecosystem. → Path 03 v3 frameworks page + [Project 08](../projects/capstone/08-production-ready-deep-research/).

**LLM-as-judge.** Using an LLM to score the quality of another LLM's output against a rubric — the operational foundation of modern eval pipelines. Failure modes: bias toward verbose answers, calibration drift. → Path 06 Modules 4-5.

**Long-context model.** Frontier model with context windows of 200K to 1M+ tokens. The engineering decision: absorb the cost of larger contexts or build tiered retrieval architecture? → [`concepts/context/long-context-models.md`](../concepts/context/long-context-models.md).

## M

**MCP (Model Context Protocol).** Anthropic's open standard for connecting AI agents to external tools and data sources through a uniform protocol. JSON-RPC over stdio or Streamable HTTP. → Path 04 + [modelcontextprotocol.io](https://modelcontextprotocol.io/).

**MCP client.** The per-server connection instance spawned by an MCP host. One host can run multiple clients concurrently — one per consumed server. → Path 04 + [Project 05](../projects/intermediate/05-multi-server-mcp-agent/).

**MCP server.** A service that exposes tools, resources, and prompts to AI agents via the MCP protocol. Built once, consumed everywhere. → Path 04.

**MDP (Markov Decision Process).** Mathematical framework for sequential decision-making under uncertainty: states, actions, transition probabilities, rewards. Agents formalize as MDP policies. → [`math-foundations/`](../math-foundations/) Page 05 (planned) + [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**Memory tier.** Layer in an agent's memory architecture (short-term scratch / working memory / long-term retrieval). Tier-specific budgets prevent unbounded growth. → Path 05 Module 4 + [`concepts/memory/`](../concepts/memory/).

## O

**Observability.** The ability to inspect what an agent is doing in production — traces, spans, metrics, alerts. 2026 production discipline: OpenTelemetry-first posture. → Path 06.

**OpenTelemetry (OTel).** Open standard for distributed tracing, metrics, and logs. Production AI observability platforms (Langfuse, Phoenix, Braintrust, Latitude) standardize on OTel as the wire format. → Path 06 v1 + v2.

## P

**Plan-and-execute.** Agent topology where a planner agent decomposes the task once, then an executor agent runs each step. Replanning happens on failure. → [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md).

**POMDP (Partially Observable MDP).** MDP variant where the agent doesn't see the full state — it sees observations and maintains a belief state. The natural framework for agents working with imperfect information. → [`math-foundations/`](../math-foundations/) Page 05 (planned).

**Policy.** The function $\pi_\theta(a_t \mid s_t)$ that maps states to actions. Agent system prompts and tool definitions together parameterize the policy. → [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**Prompt injection.** Attack where untrusted input (a document, a tool result, a search snippet) contains instructions that hijack the agent's behavior. The canonical agent security failure mode. → [`security/`](../security/) + Path 07 Module 4.

**Provenance.** Tracing each output back to the inputs and sources that produced it. Load-bearing for audit trails, citation verification, and debugging. → Path 03 v2 Pattern 6 + [Project 06](../projects/capstone/06-financial-research-analyst/).

## R

**RAG (Retrieval-Augmented Generation).** Pattern where the model retrieves context from an external store before generating an answer. The canonical formulation: $p(y \mid x) = \sum_z p(y \mid x, z)\, p(z \mid x)$. → Path 02 + [`math-foundations/`](../math-foundations/) Page 03 (planned).

**RAG-Fusion.** RAG variant where the original query is rewritten into multiple sub-queries; retrieval results from each are fused with reciprocal rank fusion. Coming in Path 02 v3.

**ReAct.** Foundational agent pattern: think (reasoning trace) → act (tool call) → observe (tool result) → repeat. The architectural ancestor of every modern agent loop. → [`math-foundations/06-react-formalization.md`](../math-foundations/06-react-formalization.md) + [`patterns/01-single-agent-tool-use.md`](../patterns/01-single-agent-tool-use.md).

**Reflection.** Agent pattern where the agent critiques its own output and revises before producing the final answer. Strong for tasks where the first answer is usually wrong. → [`patterns/07-reflection.md`](../patterns/07-reflection.md).

**Regression set.** Versioned collection of failed conversations promoted from production. Runs on every deploy; failures block the deploy. → Path 06 v2 + [Project 07](../projects/capstone/07-evaluated-multi-agent-system/).

**Reranking.** Second-stage scoring of retrieved chunks using a cross-encoder model. Slower than vector retrieval, more accurate. → Path 02.

**Retry policy.** Per-failure-class behavior: transient failures (timeout / 429 / 502) retry with backoff; permanent failures (auth / quota / bad request) escalate to HITL. → Path 03 v2 Pattern 5.

## S

**SEC EDGAR.** The U.S. Securities and Exchange Commission's free public filing repository. Primary verifiable data source for financial research agents. → [Project 06](../projects/capstone/06-financial-research-analyst/).

**Span (OTel).** A timed unit of work in a distributed trace — one tool call, one model invocation, one retrieval. Spans nest to form trace trees. → Path 06 Modules 1-3.

**STDIO (MCP transport).** Standard input/output transport for MCP — runs the server as a local subprocess passing JSON-RPC over stdin/stdout. Default for desktop AI agents and local tooling. → Path 04.

**Streamable HTTP (MCP transport).** HTTP-based transport for MCP that replaced the earlier SSE-based variant. Default for remote servers, cloud deployments, multi-client scenarios. → Path 04.

**Streaming.** Server-sent token-by-token output so users see progress in real-time. An agent that takes 30 seconds to respond feels broken unless streaming shows it working. → [`production/`](../production/).

**Supervisor-worker.** Multi-agent topology where a central supervisor decomposes tasks and delegates to worker specialists. The most-defended starting topology for production multi-agent systems. → [`patterns/03-supervisor-workers.md`](../patterns/03-supervisor-workers.md).

**Swarm.** Multi-agent topology where peers hand off control without a central coordinator. Hardest topology to defend in writing; easiest to lose track of. → [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md).

**System prompt.** Per-conversation instructions setting the agent's role, constraints, and tool-usage guidance. The first message the model sees on every call. → Path 01.

## T

**Temperature (sampling).** Hyperparameter controlling randomness in next-token sampling. Higher → more diverse; lower → more deterministic. Tool-calling typically uses low temperature. → Path 01 + [`math-foundations/`](../math-foundations/) Page 01 (planned).

**Token.** The basic unit of model processing — roughly 0.75 words in English. Costs are quoted per million tokens; budgets are tracked per token. → [`math-foundations/`](../math-foundations/) Page 01 (planned).

**Token budget.** Allocated tokens per context zone (system / tools / conversation / retrieval). Per-zone tiers + caps prevent runaway costs and context degradation. → [`concepts/context/token-budgets.md`](../concepts/context/token-budgets.md).

**Tool.** A function the agent can invoke to interact with the world — search, fetch, write file, call API. Defined by name, description, and JSON schema for arguments. → Path 01 + [`concepts/tools/`](../concepts/tools/).

**Tool calling.** The mechanism by which an LLM generates a structured tool invocation that an orchestration layer executes. Also called function calling. → Path 01.

**Tool collision.** When two MCP servers expose tools with the same name; agent can't disambiguate. Defense: namespace tools at the host layer (e.g., `github__search` vs `filesystem__search`). → [Project 05](../projects/intermediate/05-multi-server-mcp-agent/).

**Topology.** The shape of an agent system — single-agent, supervisor-worker, plan-and-execute, hierarchical, swarm, handoff. The architectural decision that defines failure modes. → Path 03 + [`patterns/`](../patterns/).

**Trace.** A complete causal record of one agent execution — the tree of spans showing every model call, tool call, and decision. The unit of debugging for agents. → Path 06 Modules 1-3.

**Transient failure.** A failure that resolves on retry — network timeout, 429 rate limit, 502 service unavailable. Distinguished from permanent failures (auth, quota, bad request). → Path 03 v2 Pattern 5.

## V

**Vector store / Vector database.** Specialized database for storing embeddings and serving nearest-neighbor queries. Production options: FAISS (local), ChromaDB (local), Pinecone, Weaviate, Qdrant (managed/self-hosted). → Path 02.

---

## How to add a term

The glossary is one of the lowest-friction contributions:

- See a term used in the repo with no glossary entry? Add one (follow the format above).
- See an entry that's vague or wrong? Improve it.
- See two terms used inconsistently across pages? Open an issue.

Each entry: bold the term + one or two sentence definition + arrow link to canonical source. Keep under 60 words. See [`README.md`](./README.md) for the full convention.

## Related references

- [`README.md`](./README.md) — the glossary convention and contribution guide
- [`concepts/`](../concepts/) — the canonical source for most terms here
- [`math-foundations/`](../math-foundations/) — the canonical source for mathematical terms
- [`patterns/`](../patterns/) — for architectural-pattern terms
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — repo-wide contribution rules

> 🟢 The glossary is classified **stable**. Definitions change rarely; new entries land continuously.
