# Glossary

A-Z index of terms used across the Agentic AI Engineer repo and the broader agentic AI ecosystem. Each entry is a one or two sentence working definition with a link to where the term is canonically discussed.

Glossary entries are **not** a substitute for concept pages. If a term needs more than two sentences to define, it gets its own page in [`concepts/`](../concepts/) or [`math-foundations/`](../math-foundations/) and the glossary entry links to it.

When a term has multiple meanings across communities (e.g., *agent*, *context*, *retrieval*), the glossary picks **one** working definition for this repo. The convention is documented in [`README.md`](./README.md).

Where a term has no dedicated repo page yet, the entry links to a canonical external source (official docs, the originating paper, or the project homepage). Entries marked *needs manual verification* point at fast-moving documentation that may have shifted since the entry was written.

---

## A

**A2A (Agent2Agent Protocol).** Open standard for inter-agent communication across organizational and codebase boundaries — the cross-system counterpart to MCP. → [Path 04 — Tool Protocols (MCP + A2A)](../learning-paths/04-tool-protocols-mcp-a2a/).

**Abstention.** Agent action of declining to answer when confidence is below a threshold. Useful safety primitive when calibration is decent; useless when it is not. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**ACL (Access Control List).** Per-resource set of permissions controlling which agents, users, or tools can read or write. Underpins tenant isolation in multi-tenant agent platforms. → [`security/`](../security/).

**Action.** In agentic systems, one step the agent takes in the environment — usually a tool call. In RL terminology, $a_t$ in a policy $\pi_\theta(a_t \mid s_t)$. → [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**Action space.** The set of all actions an agent can take at a given step — tool calls plus a terminal-response action. Size of this set drives selection accuracy. → [`math-foundations/07-tool-selection.md`](../math-foundations/07-tool-selection.md).

**Adaptive sampling.** Evaluation strategy where harder or higher-stakes inputs get more eval coverage than easy ones — keeps eval cost bounded as production traffic grows. → Path 06 v2.

**Adversarial red-teaming.** Systematic probing of an agent system with attacks designed to elicit unsafe, off-policy, or low-quality outputs. The harness runs continuously in mature production systems. → Path 06 v2 + Path 07 security material.

**Agent.** A system that takes goals, plans actions, calls tools, observes results, and iterates toward an outcome — distinguished from a stateless LLM call by the *loop* and the *autonomy over tool selection*. → [`concepts/agents/`](../concepts/agents/).

**Agent loop.** The iterative reasoning-acting-observing cycle that defines an agent. Common formulations: ReAct (think → act → observe), plan-and-execute (plan once → execute each step). → [`patterns/01-single-agent-tool-use.md`](../patterns/01-single-agent-tool-use.md) + [`math-foundations/06-react-formalization.md`](../math-foundations/06-react-formalization.md).

**Agent runtime.** The orchestration layer that executes the agent loop — parses tool calls, dispatches them, returns results, manages state. Examples: LangGraph runtime, OpenAI Agents SDK runtime, custom Python loops. → Path 01.

**AgentDojo.** Benchmark of tool-using agent attacks with paired tasks and injections — a source for generating red-team trajectories. → [`labs/52-red-teaming-trajectories/`](../labs/52-red-teaming-trajectories/).

**Agentic RAG.** RAG where retrieval is a tool the agent can choose to call (rather than a pre-pended context block), allowing query reformulation, multi-step retrieval, and reflexive critique. → [`patterns/08-agentic-rag.md`](../patterns/08-agentic-rag.md) + Path 02.

**Agentic workflow.** A multi-step process executed by one or more agents, distinguished from a fully scripted workflow by the agent's autonomy over tool selection and step ordering. → [`patterns/`](../patterns/).

**AGI (Artificial General Intelligence).** Hypothetical AI system with human-level competence across most cognitive tasks. Tangential to engineering work; mentioned here because the term shows up in product positioning. → [Wikipedia](https://en.wikipedia.org/wiki/Artificial_general_intelligence).

**AI alignment.** Research and engineering effort to make AI systems behave according to human intent and values. Practical agentic touchpoints: HITL, guardrails, evaluation, refusal behavior. → [Anthropic research](https://www.anthropic.com/research).

**Anthropic.** AI safety company that builds the Claude model family and authored the MCP protocol and Constitutional AI methodology. → [anthropic.com](https://www.anthropic.com/).

**Approval gate.** Pause point in an agent workflow where execution waits for explicit human approval before continuing — the operational primitive of HITL. → [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md).

**Argument schema.** JSON Schema defining valid arguments for a tool call. Tight schemas (enums, patterns, ranges) sharply reduce malformed calls. → Path 04 + [`math-foundations/07-tool-selection.md`](../math-foundations/07-tool-selection.md).

**Async tool call.** Tool invocation that does not block the agent loop — useful for long-running operations (web fetch, large file processing) where the agent can do other work meanwhile. → [`production/`](../production/).

**Attention.** The Transformer mechanism where each token's representation is computed as a weighted sum over all other tokens' representations. The mathematical substrate underneath every LLM. → [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762).

**Audit trail.** Append-only log capturing every decision, source citation, and model action for compliance reconstruction. The minimum schema (timestamp_UTC, audit_id, user_id, model_version, prompt_version, tool_calls, sources_cited, verdict) is the load-bearing artifact for regulated-domain deployments. → [Project 06 — Financial research analyst](../projects/capstone/06-financial-research-analyst/).

**Autoregressive.** Generation process where each next token is sampled conditional on all previous tokens. The factorization $p(x_{1:T}) = \prod_t p(x_t \mid x_{<t})$. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**AutoGen.** Multi-agent orchestration framework from Microsoft Research; first popular treatment of multi-agent LLM systems as conversing agents with structured roles. → [microsoft.github.io/autogen](https://microsoft.github.io/autogen/) (needs manual verification).

**AutoGPT.** Early (2023) demonstration of a recursive, self-prompting agent that decomposes goals into sub-goals. Historical importance; superseded by better-engineered patterns. → [GitHub](https://github.com/Significant-Gravitas/AutoGPT).

## B

**Backoff.** Exponentially increasing wait time between retries on transient failures. Standard in retry policies for rate-limited APIs. → Path 03 v2 Pattern 5.

**BabyAGI.** Early (2023) agent demonstration using a task queue plus an LLM planner. Historical reference point for the plan-and-execute pattern. → [GitHub](https://github.com/yoheinakajima/babyagi).

**Beam search.** Decoding strategy that maintains the top-$k$ partial sequences at each step. Used in older NLP work; mostly replaced by sampling for LLM generation. → [Wikipedia](https://en.wikipedia.org/wiki/Beam_search).

**Belief state.** In a POMDP, the agent's probability distribution over hidden states — what the agent *thinks* the world looks like given partial observations. → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md).

**Benchmark.** Standardized evaluation suite for comparing models on a fixed task. Examples: MMLU (general knowledge), HumanEval (code), MTEB (embeddings), AgentBench (agentic tasks). → Path 06.

**BERT.** Bidirectional encoder Transformer (Devlin et al. 2018). Foundation of many production embedding models. → [Original paper](https://arxiv.org/abs/1810.04805).

**Bias (model bias).** Systematic skew in model outputs traceable to training data composition. Distinct from variance; mitigated through fine-tuning, prompt design, and post-hoc filtering. → [`security/`](../security/).

**BM25.** A sparse keyword-based retrieval scoring function used in hybrid search alongside dense vector retrieval. Strong for exact-match technical terms where embeddings underperform. → Path 02.

**Braintrust.** Commercial evaluation and observability platform for LLM applications; OpenTelemetry-compatible. → [braintrust.dev](https://www.braintrust.dev/) (needs manual verification).

**Browser-use.** Pattern (and library) where an agent drives a real browser to perform tasks that lack APIs — fill forms, click buttons, scrape modern web apps. Related to "computer use." → [browser-use.com](https://browser-use.com/) (needs manual verification).

## C

**Cache-Augmented Generation (CAG).** Variant of RAG that pre-loads documents into the model's KV cache so retrieval becomes a cache lookup rather than a runtime vector search. Trades flexibility for latency. → [Chan et al. 2024](https://arxiv.org/abs/2412.15605).

**Calibration.** The property that a model's stated confidence matches its actual accuracy — a 70%-confident answer should be right 70% of the time. Drifts can be detected via reliability diagrams. → Path 06 v2 + Lab 20 + [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Canonical RAG.** The seven-stage pipeline (ingest / chunk / embed / index / retrieve / generate / cite) — the production-RAG starting point before agentic extensions. → Path 02 + [Project 02 — PDF Q&A bot](../projects/beginner/02-pdf-qa-bot/).

**Capstone (project).** Full-stack agentic system spanning at least four paths with evaluation, observability, deployment, and a written architecture defense. → [`projects/capstone/`](../projects/capstone/).

**Chain (LangChain primitive).** Sequence of LLM calls and transformations composed as a pipeline. The original LangChain abstraction; mostly superseded by LangGraph for agentic workflows. → [LangChain docs](https://docs.langchain.com/) (needs manual verification).

**Chain-of-Thought (CoT).** Prompting technique where the model is induced to produce intermediate reasoning steps before its final answer. Empirically lifts reasoning task accuracy. → [Wei et al. 2022](https://arxiv.org/abs/2201.11903).

**ChatGPT.** OpenAI's consumer chat interface to the GPT model family. Distinct from the Chat Completions API used in code. → [chat.openai.com](https://chat.openai.com/).

**Checkpoint.** Persisted state at a known point in a long-running agent execution. Enables resume after crash/restart. LangGraph saves checkpoints *between nodes*, not inside nodes. → [Project 08 — Production-ready deep research](../projects/capstone/08-production-ready-deep-research/).

**ChromaDB.** Open-source vector database with local-first deployment. Common choice for prototyping and small-to-medium production. → [trychroma.com](https://www.trychroma.com/) (needs manual verification).

**Chunking.** Splitting documents into retrieval units with chosen size + overlap + boundary policy. Production failure modes: split sentences mid-word, lost table contents, header/footer pollution. → Path 02 + [`concepts/rag/`](../concepts/rag/).

**Citation.** Inline reference linking each claim in an agent's output back to the source that supports it. Load-bearing for faithfulness eval and audit trails. → [Project 06](../projects/capstone/06-financial-research-analyst/).

**Claude.** Anthropic's frontier model family (Haiku, Sonnet, Opus tiers). Native tool calling, structured outputs, computer use, MCP support. → [anthropic.com/claude](https://www.anthropic.com/claude).

**Code interpreter.** Tool that lets the model write and execute code in a sandbox, observing output and iterating. Available as a first-class tool in OpenAI and Anthropic APIs. → [OpenAI docs](https://platform.openai.com/docs/assistants/tools/code-interpreter) + [Anthropic docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use).

**Cohere.** AI platform with strong embedding (`embed-v3`) and reranking (`rerank-3`) models used widely in RAG. → [cohere.com](https://cohere.com/).

**Compaction.** Compressing long-running conversation context into a shorter summary so subsequent turns stay within the token budget. Modern implementations: Anthropic's `tools=[{'type': 'context_compaction_2026-01-15'}]`. → Path 05 Module 3.

**Compliance review.** Automated first-pass review of agent outputs against domain-specific policies (citation completeness, contradiction detection, scope boundary). Implemented as a judge ensemble per [Project 06](../projects/capstone/06-financial-research-analyst/).

**Computer use.** Anthropic capability (Oct 2024+) where the model takes screenshots, moves the mouse, types text, and clicks — operates a real desktop. Adjacent to browser-use but at the OS level. → [Anthropic docs](https://docs.anthropic.com/en/docs/build-with-claude/computer-use) (needs manual verification).

**Confidence.** Numeric estimate of an answer's correctness, either token-level (from logprobs and entropy) or verbalized (the model emits a confidence number). → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Conjunctive gate.** Release rule that passes only if *every* dimension clears its floor — contrast with a weighted gate. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

**Constitutional AI.** Anthropic methodology for aligning a model to a written set of principles, using AI-generated critique rather than only human labels. → [Bai et al. 2022](https://arxiv.org/abs/2212.08073).

**Context budget.** The token allocation per zone of an agent's context (system prompt / tool definitions / conversation / retrieval / scratchpad). Per-zone tiers + soft/hard caps prevent runaway growth. → Path 05 Module 2 + [`concepts/context/token-budgets.md`](../concepts/context/token-budgets.md).

**Context drift.** Multi-turn degradation pattern where the agent's behavior loses coherence over time (re-reading the same content, re-deciding the same question, task reframing, retrieval-precision collapse). → Path 05 Module 5 + [`concepts/context/context-drift-detection.md`](../concepts/context/context-drift-detection.md).

**Context engineering.** The discipline of allocating, ordering, and managing the agent's context window — the engineering layer between "more tokens" and "the right tokens." → Path 05.

**Context window.** The maximum input length a model can process in one call. Frontier models in 2026 range from ~200K to 1M+ tokens. The engineering decision: use long-context or build tiered architecture? → Path 05 Module 6 + [`concepts/context/long-context-models.md`](../concepts/context/long-context-models.md).

**Cost engineering.** Practice of measuring, attributing, and bounding LLM call costs across an agent system. Soft caps trigger warnings; hard caps trigger graceful termination. → [`production/cost-engineering.md`](../production/cost-engineering.md) + Path 03 v2 Pattern 4.

**Cosine similarity.** $\cos(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} / (\lVert \mathbf{u} \rVert \lVert \mathbf{v} \rVert)$. The angle-only similarity used in nearly every vector search. → [`math-foundations/02-embeddings-vector-similarity.md`](../math-foundations/02-embeddings-vector-similarity.md).

**CrewAI.** Agent framework emphasizing role-based crews — specialist agents with assigned roles, goals, and backstories — coordinated through tasks. → [crewai.com](https://www.crewai.com/) (needs manual verification).

**Critic agent.** Second-pass agent that reviews another agent's output and provides structured feedback. Core to generator-critic patterns and reflection. → [`patterns/07-reflection.md`](../patterns/07-reflection.md).

**Cross-agent provenance.** Tracking which agent produced which output, from which inputs, in which step, across a multi-agent system. Load-bearing for audit trails. → Path 03 v2 Pattern 6.

**Cross-encoder.** Model that scores a query-document *pair* directly, rather than embedding each independently. Used for reranking: slower than dual-encoder retrieval, more accurate. → Path 02.

## D

**DAG (Directed Acyclic Graph).** Graph with directed edges and no cycles. The natural shape for plan-and-execute workflows, since acyclicity bounds runtime to at most $\|V\|$ steps. → [`math-foundations/10-multi-agent-coordination.md`](../math-foundations/10-multi-agent-coordination.md).

**Data leakage.** Eval pathology where information from the test set bleeds into training or prompt design, inflating measured performance. Especially common with synthetic golden datasets. → Path 06.

**Dead-letter queue (DLQ).** Holding area for messages that failed past a max-delivery count, kept for inspection instead of looping forever. → [`labs/54-production-durable-backends/`](../labs/54-production-durable-backends/).

**DeepEval.** Open-source evaluation framework for LLM applications with built-in faithfulness, answer relevance, and contextual precision metrics. → [github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval) (needs manual verification).

**DeepSeek.** Chinese frontier-model lab whose open-weights R1 reasoning model (Jan 2025) demonstrated chain-of-thought-style reasoning could be trained with smaller compute budgets. → [deepseek.com](https://www.deepseek.com/).

**Deep research.** Agent pattern that decomposes a topic into sub-questions, iteratively browses + verifies sources, and synthesizes a citation-grounded report. The architectural template for both [Project 01](../projects/beginner/01-personal-research-assistant/) (light) and [Project 08](../projects/capstone/08-production-ready-deep-research/) (long-running). → [`patterns/09-deep-research.md`](../patterns/09-deep-research.md).

**Delegation.** Pattern where one agent assigns a sub-task to another agent. The verb form of "handoff." → Path 03.

**Dense retrieval.** Retrieval method using dense vector embeddings (vs sparse term frequencies in BM25). The default for semantic search. → Path 02 + [`math-foundations/02-embeddings-vector-similarity.md`](../math-foundations/02-embeddings-vector-similarity.md).

**Distillation.** Training a smaller model to imitate a larger one. Relevant to agentic AI when shipping cheaper specialist models distilled from frontier teachers. → [Hinton et al. 2015](https://arxiv.org/abs/1503.02531).

**Document loader.** Component (in LangChain and similar frameworks) that ingests raw files (PDF, DOCX, HTML, Markdown) into a unified Document representation. → [LangChain docs](https://docs.langchain.com/) (needs manual verification).

**DPO (Direct Preference Optimization).** Fine-tuning method that aligns a model to preference pairs without an explicit reward model. Used as a simpler alternative to RLHF. → [Rafailov et al. 2023](https://arxiv.org/abs/2305.18290).

**Drift detection.** Monitoring agent quality over time via score drift (judge scores), embedding drift (query/result distribution), or context drift (multi-turn signals). → Path 06 v2 Lab 20 + Lab 23.

**DSPy.** Stanford framework for programming (rather than prompting) LLMs — modular pipelines with optimizable prompts and weights. → [dspy.ai](https://dspy.ai/) (needs manual verification).

**Dual encoder.** Retrieval architecture where query and document are embedded independently, then compared by inner product. Fast to index; the standard for vector search. Contrast with cross-encoder. → Path 02.

**Durable execution.** Orchestration property where a workflow survives infrastructure failures and resumes from the exact point of interruption. The 2026 production frontier — Temporal, LangGraph 1.0, Deep Agents runtime. → [Project 08](../projects/capstone/08-production-ready-deep-research/).

## E

**ECE (Expected Calibration Error).** Metric for calibration: average absolute gap between stated and actual accuracy, weighted across confidence bins. Lower is better; 0 is perfectly calibrated. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Embedding.** Dense vector representation of text (or other modality) where semantic similarity maps to cosine or dot-product distance. Production models: OpenAI text-embedding-3, Cohere embed-v3, sentence-transformers. → [`math-foundations/02-embeddings-vector-similarity.md`](../math-foundations/02-embeddings-vector-similarity.md).

**Embedding model.** Neural network that maps text to a fixed-dimensional vector. Choice of model matters more than dimension; production options live in [MTEB](https://huggingface.co/spaces/mteb/leaderboard). → Path 02.

**Embedding-space drift.** Distribution shift in query or retrieval-result embeddings over time, detected via clustering or distance-from-centroid metrics. Catches retrieval degradation before quality drops. → Lab 23.

**Entity extraction.** Identifying and classifying named entities (people, places, organizations) in text. Useful pre-processing for knowledge-graph RAG. → [`concepts/rag/`](../concepts/rag/).

**Entropy.** $H(p) = -\sum_x p(x) \log p(x)$. Measure of uncertainty in a probability distribution. Low entropy on next-token prediction means the model is confident. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Environment.** In RL, everything outside the agent — the world the agent acts on and observes from. For LLM agents, the environment includes the conversation, tools, and external systems they reach. → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md).

**Episodic memory.** Memory tier holding records of specific past events or interactions, indexed by time or context. Distinct from semantic memory (facts) and procedural memory (skills). → [`concepts/memory/`](../concepts/memory/) + [`math-foundations/09-memory-models.md`](../math-foundations/09-memory-models.md).

**Escalation.** When an agent recognizes a failure mode it can't handle and routes to a different agent (multi-agent) or a human (HITL). Defined per failure class in retry policies. → Path 03 v2 Pattern 3.

**Evaluation.** Measuring agent output quality through golden datasets, LLM-as-judge, judge ensembles, online evaluators, or human review. → Path 06 v1 + v2.

**Evaluator.** A function or LLM call that scores an agent output. Online evaluators run on production traffic; offline evaluators run on golden datasets. → Path 06.

**Event sourcing.** Storing a system's state as an ordered log of events rather than mutable state. Useful pattern for agent audit trails. → [Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html).

**Exfiltration.** Data-theft attack where the agent is tricked into emitting sensitive information to a third party (often through a tool's URL parameter). One canonical agent security failure mode. → [`security/`](../security/) + Path 07 Module 5.

## F

**Failure mode.** A specific way an agent system goes wrong. Naming failure modes is half of debugging them. → Path 03 v2 + Path 06.

**Faithfulness.** Eval metric measuring whether a generated answer is supported by its cited sources — the canonical RAG failure mode the metric catches. → Path 06 v1 + [`concepts/evaluation/`](../concepts/evaluation/) + [`math-foundations/11-evaluation-metrics.md`](../math-foundations/11-evaluation-metrics.md).

**Fallback.** When the agent's preferred approach fails, the policy that chooses the simpler/safer alternative. Sister concept to escalation. → Path 03 v2 Pattern 3.

**FAISS.** Facebook AI Similarity Search. Open-source library for efficient nearest-neighbor search over dense vectors. Default for self-hosted in-process vector indices. → [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss).

**Few-shot prompting.** Including examples of input-output pairs in the prompt to teach the model the task without weight updates. Often the simplest fix for under-performing classification or extraction tasks. → Path 01.

**Fine-tuning.** Updating model weights on a task-specific dataset. For agentic AI, usually post-pretraining with SFT then DPO or RLHF. → [OpenAI fine-tuning](https://platform.openai.com/docs/guides/fine-tuning) (needs manual verification).

**Foundation model.** Large pre-trained model serving as the substrate for many downstream tasks. GPT, Claude, Gemini, Llama families are foundation models. → [Bommasani et al. 2021](https://arxiv.org/abs/2108.07258).

**Function calling.** The OpenAI/Anthropic API mechanism by which an LLM can invoke a developer-defined function with structured arguments. Also called tool calling; the protocol substrate underneath both terms. → Path 01.

## G

**garak.** NVIDIA's LLM vulnerability scanner — probes for prompt injection, jailbreaks, and leakage; its runs export into red-team trajectories. → [`labs/52-red-teaming-trajectories/`](../labs/52-red-teaming-trajectories/).

**Gemini.** Google's frontier multimodal model family with native long context, image/video understanding, and tool calling. → [deepmind.google/technologies/gemini/](https://deepmind.google/technologies/gemini/).

**GenAI semantic conventions.** OpenTelemetry's standard attribute names for model calls (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`) so any tool can read agent spans. → [`labs/56-production-traces-routing/`](../labs/56-production-traces-routing/).

**Generator-critic.** Two-agent pattern where one agent produces output, another critiques it, and revision loops until a quality bar is met. → [`patterns/07-reflection.md`](../patterns/07-reflection.md).

**Goal decomposition.** Breaking a high-level goal into smaller sub-goals an agent can tackle independently. Core to plan-and-execute and hierarchical agents. → [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md).

**Golden dataset.** Hand-curated set of input-output examples used as ground truth for offline evaluation. Maintained and versioned alongside the agent code. → Path 06 v1.

**Google ADK (Agent Development Kit).** Google's open-source framework for building agents with the Gemini API. → [google.github.io/adk-docs/](https://google.github.io/adk-docs/) (needs manual verification).

**GPT (Generative Pre-trained Transformer).** OpenAI's foundational model family (GPT-3.5, GPT-4, GPT-4o, GPT-5). The architectural template for modern LLMs. → [openai.com](https://openai.com/).

**GraphRAG.** RAG variant that builds a knowledge graph from documents and traverses it to retrieve evidence — strong for multi-hop reasoning. Coming in Path 02 v3. → [Microsoft GraphRAG](https://github.com/microsoft/graphrag) (needs manual verification).

**Greedy decoding.** Decoding rule that always picks the highest-probability next token. Deterministic but myopic; produces repetitive text without sampling diversity. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Groq.** Custom-silicon inference provider offering very low time-to-first-token for popular open models. → [groq.com](https://groq.com/) (needs manual verification).

**Groundedness.** Whether a model's claims are supported by the provided context. RAGAS metric; close cousin of faithfulness. → [RAGAS docs](https://docs.ragas.io/) (needs manual verification).

**Guardrail.** Runtime check that blocks unsafe or off-policy agent outputs. Input guardrails screen the request; output guardrails screen the response. → [`security/`](../security/) + Path 07.

**Guardrails AI.** Python library for validating LLM outputs against schemas and policies, with declarative "rail" specifications. → [guardrailsai.com](https://www.guardrailsai.com/) (needs manual verification).

## H

**Hallucination.** Confidently generated false content, traceable to the model's policy putting concentrated probability on a wrong action. Mitigations: retrieval grounding, claim-level verification, judge ensembles, abstention. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Handoff.** Control transfer between agents in a multi-agent system. The agent receiving the handoff inherits state and continues the task. → Path 03 v1 + [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md).

**Handoff contract.** The typed data structure that defines what crosses an agent boundary — load-bearing for clean multi-agent systems. Per Path 03 v2 Pattern 1: only structured data crosses, never raw chat history.

**Helicone.** Open-source LLM observability platform with logging, caching, and rate-limiting features. → [helicone.ai](https://helicone.ai/) (needs manual verification).

**Hierarchical (multi-agent).** Topology where agents form a tree: top-level coordinator delegates to mid-level managers who delegate to leaf-level specialists. → [`patterns/04-hierarchical-teams.md`](../patterns/04-hierarchical-teams.md).

**HITL (Human-in-the-loop).** Agent workflow that pauses at designated decision points for explicit human approval before continuing. State persists across the pause. → [`patterns/10-human-in-the-loop.md`](../patterns/10-human-in-the-loop.md).

**Host (MCP).** The application that maintains MCP client connections to one or more MCP servers — Claude Desktop, Cursor, your custom agent. → Path 04.

**Hugging Face.** Hub for open-weight models, datasets, and inference. Standard place to find Llama, Mistral, sentence-transformers, and the MTEB embedding leaderboard. → [huggingface.co](https://huggingface.co/).

**Human feedback.** Labels provided by humans on model outputs, used for fine-tuning (RLHF), evaluation (golden datasets), or HITL approval. → Path 06.

**Hybrid search.** Combining dense vector retrieval with sparse keyword retrieval (BM25) and re-ranking. Stronger than either alone, particularly for queries mixing technical terms with semantic concepts. → Path 02.

**HyDE (Hypothetical Document Embeddings).** RAG variant where the LLM generates a hypothetical answer first; the embedding of the *hypothetical answer* (not the question) drives retrieval. Coming in Path 02 v3. → [Gao et al. 2022](https://arxiv.org/abs/2212.10496).

## I

**Idempotent (tool).** Tool whose effect on the world is the same whether called once or multiple times. Property that makes retry-on-failure safe. → [`concepts/tools/`](../concepts/tools/).

**Indirect prompt injection.** Attack where the malicious instruction lives inside content the agent retrieves (a web page, a PDF, a tool result) rather than in the user's message. Harder to defend than direct injection. → [`security/`](../security/) + Path 07 Module 4.

**Inference.** Running a trained model to produce output. Distinct from training. The unit of cost in production. → [`production/`](../production/).

**Information retrieval (IR).** Field of computer science covering search systems, ranking algorithms, and the precision/recall framework. The intellectual ancestor of RAG. → [Manning, Raghavan, Schutze 2008](https://nlp.stanford.edu/IR-book/).

**Instruction tuning.** Fine-tuning a base model on instruction-response pairs to make it follow user directives. The step between base GPT and ChatGPT. → [Ouyang et al. 2022](https://arxiv.org/abs/2203.02155).

**Intent classification.** Determining what the user is trying to do as a discrete category. Useful for routing to specialist agents or tools. → Path 03.

**Isotonic regression.** Monotone (non-decreasing) least-squares fit that calibrates a scorer whose bias is monotone but not a constant offset; computed by pool-adjacent-violators. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

## J

**Jailbreak.** Adversarial prompt designed to bypass a model's safety filters or override its system prompt. Active research area; standard production defenses are layered (input filter + model alignment + output filter). → [`security/`](../security/) + Path 07.

**JSON mode.** API feature (OpenAI, Anthropic) constraining output to valid JSON. Distinct from structured outputs (which constrain to a specific schema). → [OpenAI docs](https://platform.openai.com/docs/guides/structured-outputs) (needs manual verification).

**JSON Schema.** Declarative specification of the structure of JSON data. The substrate for tool argument validation and structured output. → [json-schema.org](https://json-schema.org/).

**Judge.** Single LLM-as-judge instance scoring an output. Subject to bias; ensembles reduce variance. → Path 06.

**Judge ensemble.** Multiple LLM-as-judge instances scoring the same output with intentionally different biases. Disagreement structure routes to human review or regression promotion. → Path 06 Pattern 3.

## K

**Knowledge base.** Structured or semi-structured collection of facts used as an agent's reference source. Implementations range from a vector index over Markdown files to a graph database. → [`concepts/rag/`](../concepts/rag/).

**Knowledge cutoff.** The date past which a model's training data does not extend. Anything after the cutoff requires retrieval or tool calls. Cutoff dates are model-specific; consult the model card. → [`concepts/agents/`](../concepts/agents/).

**Knowledge graph.** Structured representation of entities and relationships as nodes and edges. Used in GraphRAG and for multi-hop reasoning. → Path 02 v3 (planned).

**KV cache (Key-Value cache).** Internal cache of attention key-value pairs that speeds up autoregressive generation. Prompt caching APIs surface this to developers as a cost-reduction primitive. → [Anthropic prompt caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) (needs manual verification).

## L

**LangChain.** Open-source framework for composing LLM applications. Provides primitives for chains, agents, retrieval, and tool integration. LangChain 1.0 (Oct 2025) introduced the `create_agent` abstraction. → [docs.langchain.com](https://docs.langchain.com/) (needs manual verification).

**Langfuse.** Open-source LLM observability platform with tracing, evaluation, and prompt management. OpenTelemetry-compatible. → [langfuse.com](https://langfuse.com/) (needs manual verification).

**LangGraph.** Open-source orchestration library for stateful, multi-actor agent applications. Built-in checkpointing; HITL pause-and-resume; integrates with the broader LangChain ecosystem. → Path 03 v3 frameworks page + [Project 08](../projects/capstone/08-production-ready-deep-research/).

**LangSmith.** LangChain's hosted observability and evaluation platform. Standard integration target for LangChain/LangGraph applications. → [smith.langchain.com](https://smith.langchain.com/) (needs manual verification).

**Latency.** Time from request to response. For agents, end-to-end latency includes all tool calls and model invocations. Bounded by retry budgets and timeouts. → [`production/`](../production/).

**LATS (Language Agent Tree Search).** Agent pattern combining ReAct with Monte Carlo Tree Search over the action space. Stronger on reasoning tasks; more expensive per turn. → [Zhou et al. 2023](https://arxiv.org/abs/2310.04406).

**LCEL (LangChain Expression Language).** LangChain's compositional syntax for chaining components. Replaced by LangGraph for agentic workflows. → [LangChain docs](https://docs.langchain.com/) (needs manual verification).

**Llama.** Meta's open-weight LLM family (Llama 2, 3, 3.1, etc.). Used for self-hosted deployment and fine-tuning. → [llama.com](https://www.llama.com/) (needs manual verification).

**LlamaIndex.** Open-source framework for building LLM applications over private data. Strong RAG primitives; agent and multi-agent abstractions added in 2024. → [llamaindex.ai](https://www.llamaindex.ai/) (needs manual verification).

**LLM (Large Language Model).** Foundation model trained on next-token prediction over large text corpora. The substrate of every agentic system in this repo. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**LLM-as-judge.** Using an LLM to score the quality of another LLM's output against a rubric — the operational foundation of modern eval pipelines. Failure modes: bias toward verbose answers, calibration drift. → Path 06 Modules 4-5 + [`math-foundations/11-evaluation-metrics.md`](../math-foundations/11-evaluation-metrics.md).

**LLM-as-judge.** Using a model with a rubric to grade outputs or trajectories that rule-based detectors miss — e.g. catching paraphrased leaks a keyword detector slips past. → [`labs/52-red-teaming-trajectories/`](../labs/52-red-teaming-trajectories/).

**Long-context model.** Frontier model with context windows of 200K to 1M+ tokens. The engineering decision: absorb the cost of larger contexts or build tiered retrieval architecture? → [`concepts/context/long-context-models.md`](../concepts/context/long-context-models.md).

**Loop detection.** Runtime guard that detects when an agent is repeating the same action without progress and halts execution. → Path 07.

**Lost in the middle.** Empirical finding that long-context models have weaker recall on content positioned in the middle of the context window. Defense: place load-bearing content at the start and end. → [Liu et al. 2023](https://arxiv.org/abs/2307.03172) + [`math-foundations/13-context-window-optimization.md`](../math-foundations/13-context-window-optimization.md).

## M

**Markov property.** In an MDP, the assumption that the next state depends only on the current state and action, not on history. Approximate for LLM agents because the "state" is the whole conversation. → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md).

**MCP (Model Context Protocol).** Anthropic's open standard for connecting AI agents to external tools and data sources through a uniform protocol. JSON-RPC over stdio or Streamable HTTP. → Path 04 + [modelcontextprotocol.io](https://modelcontextprotocol.io/).

**MCP client.** The per-server connection instance spawned by an MCP host. One host can run multiple clients concurrently — one per consumed server. → Path 04 + [Project 05](../projects/intermediate/05-multi-server-mcp-agent/).

**MCP server.** A service that exposes tools, resources, and prompts to AI agents via the MCP protocol. Built once, consumed everywhere. → Path 04.

**MDP (Markov Decision Process).** Mathematical framework for sequential decision-making under uncertainty: states, actions, transition probabilities, rewards. Agents formalize as MDP policies. → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md) + [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**Mem0.** Open-source memory layer for AI agents with importance-weighted writes, vector retrieval, and per-user isolation. → [mem0.ai](https://mem0.ai/) (needs manual verification).

**MemGPT.** Architecture from Packer et al. 2023 introducing OS-style memory management for LLM agents — explicit primitives for moving content between working memory and external storage. → [Packer et al. 2023](https://arxiv.org/abs/2310.08560).

**Memory tier.** Layer in an agent's memory architecture (short-term scratch / working memory / long-term retrieval). Tier-specific budgets prevent unbounded growth. → Path 05 Module 4 + [`concepts/memory/`](../concepts/memory/) + [`math-foundations/09-memory-models.md`](../math-foundations/09-memory-models.md).

**Middleware.** LangChain 1.0 abstraction for cross-cutting concerns (logging, rate limiting, guardrails) inserted between agent steps. → [LangChain docs](https://docs.langchain.com/) (needs manual verification).

**Mistral.** French AI lab with open-weight (Mistral 7B, Mixtral) and proprietary (Mistral Large, Codestral) models. → [mistral.ai](https://mistral.ai/) (needs manual verification).

**MMR (Maximal Marginal Relevance).** Reranking strategy that balances similarity to the query with diversity among results, preventing near-duplicates from dominating top-k. → Path 02.

**Modal.** Serverless cloud platform popular for hosting LLM applications and GPU workloads with code-deployed-as-Python. → [modal.com](https://modal.com/) (needs manual verification).

**Model card.** Standardized document describing a model's intended use, training data, evaluation results, and known limitations. → [Mitchell et al. 2019](https://arxiv.org/abs/1810.03993).

**MTEB (Massive Text Embedding Benchmark).** Standard benchmark for comparing embedding models across retrieval, clustering, and classification tasks. The de facto leaderboard for picking embedding models. → [Muennighoff et al. 2023](https://arxiv.org/abs/2210.07316).

**Multi-agent system.** System with two or more agents that communicate, delegate, or collaborate. Topologies include supervisor-worker, hierarchical, plan-and-execute, swarm. → Path 03 + [`math-foundations/10-multi-agent-coordination.md`](../math-foundations/10-multi-agent-coordination.md).

**Multi-hop reasoning.** Task that requires connecting multiple pieces of evidence to answer. The motivating use case for GraphRAG, agentic RAG with iteration, and ReAct. → Path 02.

**Multimodal agent.** Agent that processes inputs across modalities (text, image, audio, video) and/or produces multimodal outputs. → Path 03.

## N

**Namespacing (tools).** Prefixing tool names with their source (e.g., `github__search` vs `filesystem__search`) to prevent collisions across MCP servers. → [Project 05](../projects/intermediate/05-multi-server-mcp-agent/).

**Nearest-neighbor search.** Finding the $k$ vectors in an index closest to a query vector. The retrieval primitive underneath every vector store. → Path 02.

**Negative example.** Input the system should *not* match or respond to in a certain way. Used in eval datasets to catch over-eager retrieval or refusal-failure modes. → Path 06.

**Nucleus sampling (top-p).** Sampling strategy restricting selection to the smallest set of tokens whose cumulative probability exceeds $p$. Truncates the long tail of unlikely tokens. → [Holtzman et al. 2020](https://arxiv.org/abs/1904.09751) + [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

## O

**Observability.** The ability to inspect what an agent is doing in production — traces, spans, metrics, alerts. 2026 production discipline: OpenTelemetry-first posture. → Path 06.

**Observation.** Output of a tool call that the agent integrates into its state for the next step. The $o_t$ in the agent loop. → [`math-foundations/06-react-formalization.md`](../math-foundations/06-react-formalization.md).

**OAuth.** Authorization framework used to grant agents access to user resources (Gmail, GitHub, etc.) without sharing passwords. Standard MCP-server authentication mechanism. → [oauth.net](https://oauth.net/).

**Off-policy.** RL term: evaluating or learning about a policy different from the one generating the data. Mostly tangential to inference-time agents; relevant when fine-tuning. → [Sutton and Barto 2018](http://incompleteideas.net/book/the-book-2nd.html).

**Ollama.** Local LLM runtime that makes running open-weight models on a laptop feel like running `docker pull`. Useful for development without API costs. → [ollama.com](https://ollama.com/).

**Online evaluation.** Running evaluators against live production traffic (sampled) to detect quality drift. Complements offline eval on golden datasets. → Path 06 v2.

**OpenAI.** AI lab that builds the GPT model family, the Assistants API, the Agents SDK, and the o-series reasoning models. → [openai.com](https://openai.com/).

**OpenAI Agents SDK.** Python SDK for building agents with the OpenAI API, including handoffs, guardrails, tracing, and parallel tool execution. → [openai.com/index/new-tools-for-building-agents/](https://openai.com/index/new-tools-for-building-agents/) (needs manual verification).

**OpenRouter.** API gateway that exposes many model providers (OpenAI, Anthropic, Google, Mistral, open-weights) behind a unified API. Useful for A/B testing models. → [openrouter.ai](https://openrouter.ai/) (needs manual verification).

**OpenTelemetry (OTel).** Open standard for distributed tracing, metrics, and logs. Production AI observability platforms (Langfuse, Phoenix, Braintrust, Latitude) standardize on OTel as the wire format. → Path 06 v1 + v2.

**Orchestration.** The layer that decides which agent or tool runs next and routes data between them. Examples: LangGraph, AutoGen, CrewAI, custom Python. → Path 03.

## P

**Parallel tool calls.** Agent capability to invoke multiple tools simultaneously in one step, with the model emitting all calls together and the runtime executing them concurrently. Major latency win when tools are independent. → [OpenAI docs](https://platform.openai.com/docs/guides/function-calling) (needs manual verification).

**Pending Entries List (PEL).** In a Redis Streams consumer group, the set of delivered-but-unacked entries with their delivery counts — the lease and give-up bookkeeping. → [`labs/54-production-durable-backends/`](../labs/54-production-durable-backends/).

**Perplexity (metric).** $\exp(-\frac{1}{T} \sum_t \log p(x_t \mid x_{<t}))$. Inverse-confidence measure for a generated sequence. Lower means more confident. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Phoenix (Arize).** Open-source LLM observability platform with OpenTelemetry support, evaluation framework, and notebook integration. → [phoenix.arize.com](https://phoenix.arize.com/) (needs manual verification).

**Pinecone.** Managed vector database with strong production tooling (replicas, auto-scaling, hybrid search). Common choice for medium-to-large RAG deployments. → [pinecone.io](https://www.pinecone.io/) (needs manual verification).

**Plan-and-execute.** Agent topology where a planner agent decomposes the task once, then an executor agent runs each step. Replanning happens on failure. → [`patterns/06-plan-and-execute.md`](../patterns/06-plan-and-execute.md) + [`math-foundations/08-planning-search.md`](../math-foundations/08-planning-search.md).

**Policy.** The function $\pi_\theta(a_t \mid s_t)$ that maps states to actions. Agent system prompts and tool definitions together parameterize the policy. → [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**POMDP (Partially Observable MDP).** MDP variant where the agent doesn't see the full state — it sees observations and maintains a belief state. The natural framework for agents working with imperfect information. → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md).

**Pool adjacent violators (PAVA).** Linear-time algorithm that computes the isotonic (monotone) least-squares fit by merging adjacent blocks that violate monotonicity. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

**Pre-training.** First training stage where a base model learns next-token prediction on a large corpus. Subsequent stages: SFT, DPO/RLHF. → [Foundation models survey](https://arxiv.org/abs/2108.07258).

**Precision (metric).** Of the things the system flagged as positive, how many actually are. $TP / (TP + FP)$. → [`math-foundations/11-evaluation-metrics.md`](../math-foundations/11-evaluation-metrics.md).

**Prompt.** Input given to a model. Includes system prompt, user message, tool definitions, prior conversation, retrieved context — anything that conditions the model's next output. → Path 01.

**Prompt caching.** API feature (Anthropic, OpenAI) that caches frequently-reused prompt prefixes (system prompts, document context) for cheaper subsequent calls. Major cost saver at scale. → [Anthropic docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) (needs manual verification).

**Prompt engineering.** Designing prompts to elicit better model behavior. Distinct from prompt *programming* (DSPy style) which treats prompts as optimizable artifacts. → [Anthropic prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) (needs manual verification).

**Prompt injection.** Attack where untrusted input (a document, a tool result, a search snippet) contains instructions that hijack the agent's behavior. The canonical agent security failure mode. → [`security/`](../security/) + Path 07 Module 4.

**Prompt template.** Parameterized prompt with placeholders for runtime values. Versioned alongside agent code. → Path 01.

**Provenance.** Tracing each output back to the inputs and sources that produced it. Load-bearing for audit trails, citation verification, and debugging. → Path 03 v2 Pattern 6 + [Project 06](../projects/capstone/06-financial-research-analyst/).

**Pydantic.** Python library for data validation using type hints. The standard schema layer in modern Python LLM applications. → [docs.pydantic.dev](https://docs.pydantic.dev/).

**Pydantic AI.** Agent framework from the Pydantic team emphasizing type-safe agents, structured outputs, and minimal abstraction overhead. → [ai.pydantic.dev](https://ai.pydantic.dev/) (needs manual verification).

**PyRIT.** Microsoft's Python Risk Identification Toolkit for orchestrating multi-turn adversarial conversations against AI systems. → [`labs/52-red-teaming-trajectories/`](../labs/52-red-teaming-trajectories/).

## Q

**Qdrant.** Open-source vector database with strong filtering and quantization features. Available self-hosted or managed. → [qdrant.tech](https://qdrant.tech/) (needs manual verification).

**Quantization.** Compressing model weights to lower-precision representations (8-bit, 4-bit) to fit larger models on smaller hardware. Trade-off: small accuracy hit, big memory savings. → [GPTQ paper](https://arxiv.org/abs/2210.17323).

**Query expansion.** Rewriting or augmenting the user's query with additional terms before retrieval, to improve recall. Cousin of query rewriting. → Path 02.

**Query rewriting.** Reformulating an ambiguous or conversational query into a cleaner search query before retrieval. Often an LLM call. → Path 02.

**Query routing.** Deciding which retrieval source (vector store, SQL database, web search, knowledge graph) to query for a given input. The router is itself an agent action. → Path 02.

## R

**RAG (Retrieval-Augmented Generation).** Pattern where the model retrieves context from an external store before generating an answer. The canonical formulation: $p(y \mid x) = \sum_z p(y \mid x, z) \, p(z \mid x)$. → Path 02 + [`math-foundations/03-rag-formulation.md`](../math-foundations/03-rag-formulation.md).

**RAG-Fusion.** RAG variant where the original query is rewritten into multiple sub-queries; retrieval results from each are fused with reciprocal rank fusion. Coming in Path 02 v3.

**RAGAS.** Framework for automated RAG evaluation with faithfulness, answer relevance, context recall, and context precision metrics. → [docs.ragas.io](https://docs.ragas.io/) (needs manual verification).

**Rate limit.** Per-time-window cap on requests or tokens enforced by a model provider. Triggers 429 errors when exceeded; defense is retry with backoff. → [`production/`](../production/).

**Reasoning model.** Model trained or prompted to produce extended internal reasoning before its final answer (OpenAI o1/o3, DeepSeek R1, Claude with extended thinking). Higher accuracy on hard tasks; higher latency and cost. → [OpenAI o1 system card](https://openai.com/index/openai-o1-system-card/) (needs manual verification).

**ReAct.** Foundational agent pattern: think (reasoning trace) → act (tool call) → observe (tool result) → repeat. The architectural ancestor of every modern agent loop. → [`math-foundations/06-react-formalization.md`](../math-foundations/06-react-formalization.md) + [`patterns/01-single-agent-tool-use.md`](../patterns/01-single-agent-tool-use.md).

**Recall (metric).** Of the items that actually are positive, how many did the system catch. $TP / (TP + FN)$. → [`math-foundations/11-evaluation-metrics.md`](../math-foundations/11-evaluation-metrics.md).

**Reciprocal rank fusion (RRF).** Method for combining ranked lists from multiple retrievers by summing $1/(k + r_i)$ where $r_i$ is each document's rank in each list. Used in RAG-Fusion. → Path 02 v3.

**Redis Streams consumer group.** Redis primitive giving at-least-once delivery with per-consumer leases (the PEL) and reclaim of idle entries via `XAUTOCLAIM` — one production backend for the failure loop. → [`labs/54-production-durable-backends/`](../labs/54-production-durable-backends/).

**Reflection.** Agent pattern where the agent critiques its own output and revises before producing the final answer. Strong for tasks where the first answer is usually wrong. → [`patterns/07-reflection.md`](../patterns/07-reflection.md).

**Reflexion.** Self-improvement pattern (Shinn et al. 2023) where the agent generates verbal reflection on past failures and stores it for future attempts. → [Shinn et al. 2023](https://arxiv.org/abs/2303.11366).

**Regression set.** Versioned collection of failed conversations promoted from production. Runs on every deploy; failures block the deploy. → Path 06 v2 + [Project 07](../projects/capstone/07-evaluated-multi-agent-system/).

**Reranking.** Second-stage scoring of retrieved chunks using a cross-encoder model. Slower than vector retrieval, more accurate. → Path 02.

**Resource (MCP).** MCP primitive for read-only data exposed to clients (files, database rows, web pages). Distinct from tools (which can have side effects). → Path 04.

**Retry policy.** Per-failure-class behavior: transient failures (timeout / 429 / 502) retry with backoff; permanent failures (auth / quota / bad request) escalate to HITL. → Path 03 v2 Pattern 5.

**Reward.** In RL, scalar feedback indicating action quality. For inference-time LLM agents, reward typically does not appear; it surfaces during fine-tuning (RLHF, DPO). → [`math-foundations/05-mdp-pomdp.md`](../math-foundations/05-mdp-pomdp.md).

**Reward hacking.** Failure mode where an agent or model maximizes a proxy reward at the expense of the underlying goal. Why eval metric design matters. → Path 06.

**RLAIF (Reinforcement Learning from AI Feedback).** Variant of RLHF where AI-generated preferences replace some human labels. Used in Constitutional AI. → [Lee et al. 2023](https://arxiv.org/abs/2309.00267).

**RLHF (Reinforcement Learning from Human Feedback).** Fine-tuning method using human preference labels to train a reward model, then optimizing the policy with PPO or similar. The training stage that turned base GPT into ChatGPT. → [Ouyang et al. 2022](https://arxiv.org/abs/2203.02155).

**ROC curve.** Plot of true-positive rate against false-positive rate across all thresholds; Youden's J picks the operating point that maximizes their gap. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

**Router.** Agent or component that routes inputs to specialist tools or sub-agents. → [`patterns/02-router.md`](../patterns/02-router.md).

**Rubric.** Versioned scoring criteria used by an LLM-as-judge. Treat like code: tested, deployed, monitored. → Path 06.

## S

**Sampling.** Random selection of next tokens from the model's distribution. Controlled by temperature, top-p, top-k. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Scratchpad.** Working-memory area where an agent records intermediate thoughts and partial results. Distinct from context that is shown to the user. → [`concepts/memory/`](../concepts/memory/).

**SEC EDGAR.** The U.S. Securities and Exchange Commission's free public filing repository. Primary verifiable data source for financial research agents. → [Project 06](../projects/capstone/06-financial-research-analyst/).

**Self-consistency.** Decoding strategy that samples multiple reasoning paths and picks the majority answer. Improves accuracy on reasoning tasks at the cost of more API calls. → [Wang et al. 2022](https://arxiv.org/abs/2203.11171).

**Self-RAG.** Pattern (Asai et al. 2023) where the agent decides when to retrieve and self-evaluates whether retrieved context is useful. The adaptive variant of RAG. → [Asai et al. 2023](https://arxiv.org/abs/2310.11511).

**Semantic search.** Retrieval using meaning-based similarity (vector embeddings) rather than keyword overlap. Default for modern RAG. → Path 02.

**Sentence Transformers.** Python library for sentence and text embeddings via fine-tuned BERT-family models. The most-used open-weight embedding stack. → [sbert.net](https://www.sbert.net/) (needs manual verification).

**SFT (Supervised Fine-Tuning).** Fine-tuning a base model on input-output pairs to teach a specific task. The step before RLHF or DPO in modern alignment pipelines. → Path 06.

**SKILL.md.** Convention (Anthropic Claude Code, Claude.ai) where a folder contains a SKILL.md file teaching the agent how to perform a category of tasks. Used by Claude's file-creation and document-editing skills. → [Anthropic docs](https://docs.claude.com/en/docs/claude-code/skills) (needs manual verification).

**smolagents.** Hugging Face's compact agent framework emphasizing code-as-action (the agent emits Python rather than JSON tool calls). → [github.com/huggingface/smolagents](https://github.com/huggingface/smolagents) (needs manual verification).

**Span.** A single timed unit of work in a trace (one agent step, one model call) carrying attributes; spans nest to form a trace. → [`labs/56-production-traces-routing/`](../labs/56-production-traces-routing/).

**Span (OTel).** A timed unit of work in a distributed trace — one tool call, one model invocation, one retrieval. Spans nest to form trace trees. → Path 06 Modules 1-3.

**Sparse retrieval.** Retrieval using term-frequency-based scoring (BM25, TF-IDF) rather than dense vectors. Strong for exact-match technical queries. → Path 02.

**SQS visibility timeout.** Amazon SQS mechanism that hides a received message for a fixed window; if it isn't deleted (acked) in time it becomes visible again — the lease primitive behind SQS-backed redelivery. → [`labs/54-production-durable-backends/`](../labs/54-production-durable-backends/).

**SSE (Server-Sent Events).** HTTP-based one-way streaming protocol. Originally used by MCP; replaced by Streamable HTTP in the current spec. → Path 04.

**Stateful.** Agent or workflow that retains memory across invocations. Required for HITL pause-and-resume, durable execution, and conversational agents. → [`patterns/`](../patterns/).

**State.** The conversation history plus retrieved context plus scratchpad — everything the agent's policy conditions on at step $t$. → [`math-foundations/04-agents-as-policies.md`](../math-foundations/04-agents-as-policies.md).

**STDIO (MCP transport).** Standard input/output transport for MCP — runs the server as a local subprocess passing JSON-RPC over stdin/stdout. Default for desktop AI agents and local tooling. → Path 04.

**Stop sequence.** Token or string that, when emitted, terminates generation. Used to enforce structured output boundaries. → Path 01.

**Streamable HTTP (MCP transport).** HTTP-based transport for MCP that replaced the earlier SSE-based variant. Default for remote servers, cloud deployments, multi-client scenarios. → Path 04.

**Streaming.** Server-sent token-by-token output so users see progress in real-time. An agent that takes 30 seconds to respond feels broken unless streaming shows it working. → [`production/`](../production/).

**Structured output.** API feature constraining the model's output to a specific JSON Schema. Distinct from JSON mode (which only enforces valid JSON, not a specific shape). → [OpenAI structured outputs docs](https://platform.openai.com/docs/guides/structured-outputs) (needs manual verification).

**Sub-agent.** Specialized agent invoked by a parent agent for a specific sub-task. The leaf nodes of supervisor-worker and hierarchical topologies. → Path 03.

**Supervisor-worker.** Multi-agent topology where a central supervisor decomposes tasks and delegates to worker specialists. The most-defended starting topology for production multi-agent systems. → [`patterns/03-supervisor-workers.md`](../patterns/03-supervisor-workers.md).

**Swarm.** Multi-agent topology where peers hand off control without a central coordinator. Hardest topology to defend in writing; easiest to lose track of. → [`patterns/05-swarm-handoff.md`](../patterns/05-swarm-handoff.md).

**Synthetic data.** Model-generated training or evaluation data. Useful for bootstrapping; subject to feedback-loop pathologies (the model learning its own biases). → Path 06.

**System prompt.** Per-conversation instructions setting the agent's role, constraints, and tool-usage guidance. The first message the model sees on every call. → Path 01.

## T

**Task decomposition.** Breaking a high-level task into smaller sub-tasks. Performed by a planner agent in plan-and-execute or implicitly by the supervisor in supervisor-worker. → Path 03 + [`math-foundations/08-planning-search.md`](../math-foundations/08-planning-search.md).

**Telemetry.** Runtime data emitted by an agent system — traces, metrics, logs. Substrate for observability. → Path 06.

**Temperature (sampling).** Hyperparameter controlling randomness in next-token sampling. Higher → more diverse; lower → more deterministic. Tool-calling typically uses low temperature. → Path 01 + [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Temporal.** Open-source workflow orchestration platform with durable execution semantics. Used for long-running agent workflows that must survive infrastructure failures. → [temporal.io](https://temporal.io/) (needs manual verification).

**TF-IDF (Term Frequency-Inverse Document Frequency).** Classic information-retrieval scoring function. Predecessor to BM25; rarely used directly in modern RAG. → [Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf).

**Throughput.** Requests or tokens processed per unit time. Latency-vs-throughput tradeoffs shape production deployment topology. → [`production/`](../production/).

**Time-to-first-token (TTFT).** Latency from request submission to the first output token arriving. The metric users actually feel when streaming is on. → [`production/`](../production/).

**Token.** The basic unit of model processing — roughly 0.75 words in English. Costs are quoted per million tokens; budgets are tracked per token. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Token budget.** Allocated tokens per context zone (system / tools / conversation / retrieval). Per-zone tiers + caps prevent runaway costs and context degradation. → [`concepts/context/token-budgets.md`](../concepts/context/token-budgets.md).

**Tokenizer.** Component that splits text into tokens for model processing. Different model families use different tokenizers (BPE, SentencePiece, tiktoken). Token counts vary across tokenizers for the same text. → [tiktoken (OpenAI)](https://github.com/openai/tiktoken).

**Tool.** A function the agent can invoke to interact with the world — search, fetch, write file, call API. Defined by name, description, and JSON schema for arguments. → Path 01 + [`concepts/tools/`](../concepts/tools/).

**Tool calling.** The mechanism by which an LLM generates a structured tool invocation that an orchestration layer executes. Also called function calling. → Path 01.

**Tool collision.** When two MCP servers expose tools with the same name; agent can't disambiguate. Defense: namespace tools at the host layer (e.g., `github__search` vs `filesystem__search`). → [Project 05](../projects/intermediate/05-multi-server-mcp-agent/).

**Tool description.** Natural-language description of what a tool does, used by the model to pick which tool to call. The largest controllable lever on tool-selection accuracy. → [`math-foundations/07-tool-selection.md`](../math-foundations/07-tool-selection.md).

**Toolformer.** Schick et al. 2023 paper formalizing self-supervised tool-use training. Origin of the modern "model decides when to call a tool" framing. → [Schick et al. 2023](https://arxiv.org/abs/2302.04761).

**Top-k sampling.** Sampling strategy restricting selection to the $k$ highest-probability tokens, then renormalizing. Less used than top-p in modern deployments. → [`math-foundations/01-language-model-probability.md`](../math-foundations/01-language-model-probability.md).

**Top-p sampling.** See *Nucleus sampling*.

**Topology.** The shape of an agent system — single-agent, supervisor-worker, plan-and-execute, hierarchical, swarm, handoff. The architectural decision that defines failure modes. → Path 03 + [`patterns/`](../patterns/).

**TPM (Tokens Per Minute).** Provider-side rate-limit unit. Often the binding constraint before request-per-minute (RPM). Watch when deploying agents that batch large prompts. → [`production/`](../production/).

**Trace.** A complete causal record of one agent execution — the tree of spans showing every model call, tool call, and decision. The unit of debugging for agents. → Path 06 Modules 1-3.

**Trace ID.** Unique identifier for one trace, propagated through the agent system so logs and spans can be correlated. → Path 06.

**Transient failure.** A failure that resolves on retry — network timeout, 429 rate limit, 502 service unavailable. Distinguished from permanent failures (auth, quota, bad request). → Path 03 v2 Pattern 5.

**Transformer.** The neural-network architecture (Vaswani et al. 2017) underneath modern LLMs. Multi-head self-attention is the load-bearing component. → [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762).

**Tree-of-Thoughts (ToT).** Yao et al. 2023 pattern that searches over multiple reasoning branches and picks the best by self-evaluation. Strong on puzzle-like tasks; rarely worth the cost for typical agentic workflows. → [Yao et al. 2023](https://arxiv.org/abs/2305.10601).

**TruLens.** Open-source framework for evaluating and tracking RAG and agent applications with built-in groundedness, answer relevance, and context relevance metrics. → [trulens.org](https://www.trulens.org/) (needs manual verification).

## U

**Uncertainty quantification.** Estimating how uncertain a model is about its output. Methods: token entropy, verbalized confidence, ensemble disagreement. Calibration measures whether the estimate is trustworthy. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Unstructured data.** Data without a predefined schema — free text, PDFs, images. The natural input to RAG and the typical agent observation type. → Path 02.

## V

**Variance (in agent runs).** Run-to-run differences in agent behavior on the same input. Caused by sampling temperature, ordering of parallel tool results, and floating-point non-determinism. Reduced by temperature=0 + seeding + pinning model version. → Path 06.

**Vector database / Vector store.** Specialized database for storing embeddings and serving nearest-neighbor queries. Production options: FAISS (local), ChromaDB (local), Pinecone, Weaviate, Qdrant (managed/self-hosted). → Path 02.

**Vector index.** Data structure inside a vector database that accelerates nearest-neighbor search (HNSW, IVF, PQ). The internal cousin of a database index. → [pgvector docs](https://github.com/pgvector/pgvector).

**Verbalized confidence.** Asking the model to emit a confidence score alongside its answer. Per Kadavath et al. 2022, large models can be reasonably calibrated on factual questions when asked this way. → [`math-foundations/12-uncertainty-safety.md`](../math-foundations/12-uncertainty-safety.md).

**Vertex AI.** Google Cloud's managed platform for ML workflows, including hosted access to Gemini and PaLM models. → [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai) (needs manual verification).

**Voyager.** Wang et al. 2023 pattern where an agent in Minecraft accumulates a library of learned skills (executable code) across episodes. Early demonstration of compounding-knowledge agents. → [Wang et al. 2023](https://arxiv.org/abs/2305.16291).

## W

**Weaviate.** Open-source vector database with built-in hybrid search and modular vectorization. Self-hosted or managed. → [weaviate.io](https://weaviate.io/) (needs manual verification).

**Weighted gate.** Release rule that passes when a weighted sum of dimension scores clears a threshold, letting a strong dimension offset a weaker one — contrast with a conjunctive gate. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

**Workflow.** A defined sequence of steps with conditional branches. Distinct from an agent: a workflow has the steps pre-specified; an agent decides the steps at runtime. The distinction matters for cost, predictability, and debugging. → [`patterns/`](../patterns/).

**Working memory.** Mid-tier memory holding task-scoped scratch (notes, plans, intermediate results). Larger than short-term context but more transient than long-term storage. → [`concepts/memory/`](../concepts/memory/) + [`math-foundations/09-memory-models.md`](../math-foundations/09-memory-models.md).

## X

**XML tags (in prompts).** Anthropic-recommended pattern of structuring prompts with `<example>`, `<context>`, `<task>` tags rather than free-form sections. Improves Claude's adherence to structure. → [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) (needs manual verification).

## Y

**YAML.** Human-readable serialization format used widely for prompt templates, agent configurations, and quiz files in this repo. → [yaml.org](https://yaml.org/).

**Youden's J.** Threshold-selection objective $J = \text{TPR} - \text{FPR}$; the cutoff maximizing it best separates two classes without assuming their relative cost. → [`math-foundations/15-calibration-threshold-selection.md`](../math-foundations/15-calibration-threshold-selection.md).

## Z

**Zero-shot.** Asking a model to perform a task without providing any examples in the prompt. Contrasts with few-shot. Strong on simple tasks; weakens as task complexity grows. → Path 01.

**Zero-trust (security).** Architectural principle: never trust input or context by default, verify everything. Applied to agent systems: treat retrieved memory, tool outputs, and user inputs all as untrusted. → [`security/`](../security/).

---

## How to add a term

The glossary is one of the lowest-friction contributions:

- See a term used in the repo with no glossary entry? Add one (follow the format above).
- See an entry that's vague or wrong? Improve it.
- See two terms used inconsistently across pages? Open an issue.

Each entry: bold the term + one or two sentence definition + arrow link to canonical source. Keep under 60 words. See [`README.md`](./README.md) for the full convention.

### When to flag an entry "needs manual verification"

External documentation links to fast-moving projects (frameworks, observability platforms, model providers) get the *needs manual verification* tag. The tag signals that the link was correct at the time of writing but the docs may have shifted. Refresh during routine maintenance sweeps; remove the tag once verified current.

## Related references

- [`README.md`](./README.md) — the glossary convention and contribution guide
- [`concepts/`](../concepts/) — the canonical source for most terms here
- [`math-foundations/`](../math-foundations/) — the canonical source for mathematical terms
- [`patterns/`](../patterns/) — for architectural-pattern terms
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — repo-wide contribution rules

> 🟢 The glossary is classified **stable**. Definitions change rarely; new entries land continuously.
