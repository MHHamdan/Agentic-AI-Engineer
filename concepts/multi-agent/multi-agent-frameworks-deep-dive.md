# Multi-agent frameworks deep dive — LangGraph, CrewAI, OpenAI Agents SDK, Claude Agent SDK, Pydantic AI, Google ADK, Microsoft Agent Framework, LlamaIndex Workflows, AutoGen/AG2

> 🔴 Advanced · ⏱ ~28 min · 🛠 Verified 2026-05-29 · 📍 Read after Path 03 v1 Modules 1-5 + Path 03 v2 patterns

## What this page is for

A practical selection guide for production multi-agent frameworks. It is **not a vendor ranking** and it does not pick a "best" framework. The point is to help a team pick the framework that fits their constraints — stack commitments, deployment shape, observability needs, model provider, type-safety preferences, ecosystem lock-in tolerance — without reading nine vendor blog posts.

Each framework covered below is in active production use in mid-2026. They differ in what they're optimized for, not in whether they work. Path 03 v1 already covers the **multi-agent patterns** (supervisor-worker, generator-critic, plan-and-execute, multi-agent RAG). Path 03 v2 covers the **production mechanisms** (handoff contracts, retries, escalation, cost budgeting, provenance). Path 03 v3 covers the **capstone deployment shapes** (chat-speed, async, cross-org). This page covers **which framework implements which patterns well** — and where each leaves gaps you'll need to fill.

Three audiences for this page:

1. **Teams picking a framework from scratch** — section 4 (Decision guide) is the entry point.
2. **Teams already on a framework, considering a migration** — section 6 (Migration paths) is the entry point.
3. **Teams running hybrid stacks across A2A boundaries** — section 5 (Path 03 module mapping) plus the integration table in [Project 3](../../learning-paths/03-multi-agent-systems/projects/03-a2a-federated-multi-agent.md) are the entry points. A2A makes cross-framework multi-agent deployments practical; the decision becomes "which framework per agent" rather than "which framework for the whole system."

What the page does **not** do is in section 7 (Anti-scope).

## Comparison table

Nine frameworks, eleven dimensions. Sources for each row are in the references section at the bottom; each claim is dated and cited.

| Framework | Best fit | Orchestration model | Strongest feature | Limiting factor | Checkpointing | Streaming | Observability | MCP + A2A | License | Path 03 module connection |
|---|---|---|---|---|---|---|---|---|---|---|
| **LangGraph** | Stateful production multi-agent in regulated industries; teams wanting explicit graph control + durable execution | Directed graph (`StateGraph`) with typed state + conditional edges | Time-travel debugging; durable execution that resumes after crash; first-class HITL via `interrupt()`; verified enterprise deployments (Klarna, Uber, LinkedIn, JPMorgan, BlackRock) | Steep learning curve (graph + state schemas + reducer semantics); LangSmith pricing pulls some teams off the platform | Native via `PostgresSaver` / `SqliteSaver` | Native per-node token streaming + state streaming | Native LangSmith integration; full OTel via OpenLLMetry/OpenInference | MCP via [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters); A2A via `langgraph-a2a` adapter (March 2026) | MIT (open source) | Module 5 (LangGraph framework bridge) |
| **CrewAI** | Role-based multi-agent prototypes where the workflow maps cleanly to defined roles (planner / researcher / writer) | Role-based crews with `Process.sequential` or `Process.hierarchical` | Fastest "20-50 lines of Python to a working multi-agent system" UX in 2026; opinionated abstractions remove plumbing decisions | Limited checkpointing; opinionated abstractions hard to escape when needs grow; growing-but-smaller ecosystem than LangGraph | Limited (CrewAI 0.x has partial state persistence; not as mature as LangGraph) | Limited (per-task streaming, not per-token in the multi-agent flow) | OpenTelemetry support (built-in tracing); integrates with AgentOps, Langfuse | MCP via `crewai-tools`; A2A community adapters; not native | MIT (OSS); CrewAI Enterprise commercial | Module 1 (when the role decomposition is obvious) |
| **OpenAI Agents SDK** | OpenAI-locked teams wanting the production successor to Swarm; conversational handoff workflows | Explicit handoffs (`Agent.handoffs = [...]`) + Runner orchestration | Cleanest handoff DX; built-in tracing surface; minimal abstraction; stable production release since March 2026 | Locked to OpenAI models (limits portability); Python-first (no official TypeScript); handoffs become unwieldy past 8-10 agent types | Per-run; persistence via your own DB | Native streaming (text + tool calls) | Built-in tracing UI; OTel-compatible export | MCP native (June 2025+); A2A community adapters | MIT (OSS) | Module 1 — alternative supervisor implementation; Module 5 |
| **Claude Agent SDK** | Anthropic-native production with computer use as a first-class primitive; Sonnet 4.6 / Opus 4.7 ecosystem | "Give Claude a computer" — Bash + filesystem + MCP integrations + sub-agent orchestration | Computer-use (72.5% OSWorld benchmark per Sonnet 4.6); MCP native first-party; extended-thinking integration; Managed Agents companion product ($0.08/session-hour) for state persistence | Cost ($15/MTok Sonnet 4.6 output makes high-volume loops expensive); runaway-loop guards must be implemented at the harness level; vendor lock-in to Anthropic models | Via Managed Agents (April 2026 public beta); not in the open SDK | Native streaming with extended-thinking | Native trace UI; OTel emit | MCP first-class (Anthropic owns the protocol); A2A via community adapters | MIT (OSS); Managed Agents commercial | Module 1 — alternative supervisor; Module 7 for cross-protocol composition (Path 04) |
| **Pydantic AI** | Type-safe agents for FastAPI-rooted teams; multi-LLM provider portability; strict typed IO | `Agent[Deps, ResultType]` with Pydantic-validated outputs; dependency injection | FastAPI-style ergonomics; strict typing across LLM calls; multi-provider support without code change; the "Pydantic team built this" guarantee of API stability | Less opinionated about multi-agent orchestration than CrewAI/AutoGen (teams build the orchestration layer themselves); newer ecosystem than LangGraph | None native (state via your own DB) | Native streaming (text + structured) | OpenTelemetry via Logfire (Pydantic team's product); OTel-compatible | MCP via `pydantic-ai-mcp`; A2A via community adapter | MIT (OSS) | Module 1 (when type safety dominates); pairs well with Module 5 LangGraph for orchestration |
| **Google ADK 1.0** | Vertex AI / Gemini-native teams; A2A-first multi-framework deployments; hierarchical agent trees | Hierarchical agent tree — root agent delegates to sub-agents, which can have their own sub-agents | Native A2A integration (cross-framework interoperability); 4-language parity (Python, Go, Java, TypeScript) since April 2026; Vertex AI integration; Gemini model native | Newest framework on the list (1.0 GA April 2026); ecosystem still maturing; tightest coupling to Google Cloud of the OSS options | Via Vertex AI session state; not in the OSS-only path | Native streaming via Vertex AI; SSE for long-running | Vertex AI native + OpenTelemetry | A2A is native (ADK is the reference implementation); MCP via the standard MCP client packages | Apache 2.0 (OSS) | Module 1 (hierarchical decomposition); strongest fit for Path 04 cross-framework A2A workflows |
| **Microsoft Agent Framework 1.0** | Microsoft-stack teams (.NET or Python on Azure); enterprise compliance requirements; Semantic Kernel + AutoGen migration target | Combines AutoGen's conversational patterns + Semantic Kernel's enterprise plumbing + new graph-based workflows | Production-ready 1.0 (April 2026); Azure App Service reference architecture; A2A + MCP cross-runtime interop; multi-provider connectors (OpenAI / Anthropic / Bedrock / Gemini / Ollama) | Microsoft-centric (.NET parity assumes Azure-first deployment); newer 1.0 than competitor LangGraph; positioning still settling | Native session-based state management | Native streaming | Native OpenTelemetry; integrates with App Insights, Datadog, Honeycomb; DevUI local debugger | A2A + MCP both native (positioned explicitly as "cross-runtime interoperability") | MIT (OSS) | Module 5 — alternative framework bridge for Microsoft-stack teams; replaces Semantic Kernel + AutoGen |
| **LlamaIndex Workflows** | Data-layer-rooted teams; event-driven multi-agent over retrieval + indexes; RAG-first multi-agent | Event-driven workflow (`Workflow` with `@step` handlers reacting to events) | Tightest integration with the data layer (indexes, retrievers, query engines); event-driven model decouples agent steps cleanly | Less polished multi-agent UX than dedicated multi-agent frameworks; community sees it as "LlamaIndex first, multi-agent second" | Workflow context persistence; less mature than LangGraph's checkpointing | Native streaming via the events | OTel via `llama-index-instrumentation`; Phoenix integration native | MCP via the standard MCP client packages; A2A via community adapters | MIT (OSS) | Module 4 (multi-agent RAG) — strongest single-framework match for Module 4's combined retrieval + multi-agent shape |
| **AutoGen / AG2** | Research-style conversational multi-agent; GroupChat patterns; legacy multi-agent codebases | GroupChat: agents take turns in a moderated conversation | Foundational conversational-multi-agent abstraction; AG2 (the 2024 fork) maintains the OSS path; rich ecosystem of patterns | High token cost (every turn re-sends accumulated history); the Microsoft-original AutoGen path is superseded by Microsoft Agent Framework 1.0; offline / quality-sensitive workflows over real-time | Limited (per-session, conversation-history-based) | Limited (conversation-based; not per-token in multi-agent) | OpenTelemetry via [`autogen-agentchat`](https://github.com/microsoft/autogen) ; AgentOps integration | MCP via community adapters; A2A community work | Apache 2.0 (OSS) | Module 2 (debate / critique) — closest framework match for the structured-conversation pattern Lab 11 implements |

Everything in this table is verified mid-2026 per the references at the bottom of the page. Framework capabilities shift quarterly; check the cited sources for current state before committing.

## Code-level comparison

Five canonical multi-agent operations every team needs to do. Snippets show the **smallest viable API surface** per framework — not production-ready code, just enough to recognize the shape. The full reference docs are linked at the bottom of the page.

### A — Defining a worker agent with tools

The agent-definition surface is the most divergent thing across these frameworks. Four families:

**Graph-state-rooted (LangGraph)** — agents are nodes in a `StateGraph`; tools are bound via `bind_tools()`:

```python
from langgraph.graph import StateGraph, MessagesState
from langchain_anthropic import ChatAnthropic

def billing_agent(state: MessagesState) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-5").bind_tools([lookup_invoice, apply_refund])
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("billing", billing_agent)
```

**Role-rooted (CrewAI)** — agents are `Agent` instances with role / goal / backstory + tools:

```python
from crewai import Agent
from crewai_tools import tool

billing_agent = Agent(
    role="Billing Specialist",
    goal="Resolve billing inquiries accurately and efficiently",
    backstory="10 years of customer billing experience",
    tools=[lookup_invoice, apply_refund],
    llm="anthropic/claude-sonnet-4-5",
)
```

**Handoff-rooted (OpenAI Agents SDK, Claude Agent SDK)** — agents declare what they hand off to:

```python
from agents import Agent

billing_agent = Agent(
    name="billing",
    instructions="You handle billing inquiries...",
    tools=[lookup_invoice, apply_refund],
    handoffs=[],  # leaf agent
    model="gpt-4o",
)
```

**Type-rooted (Pydantic AI)** — agents are generic over dependencies and result type:

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class BillingResolution(BaseModel):
    action_taken: str
    refund_amount: float | None

# Type-alias the generic, then instantiate:
BillingAgentType = Agent[BillingDeps, BillingResolution]
billing_agent = BillingAgentType(
    model="anthropic:claude-sonnet-4-5",
    deps_type=BillingDeps,
    result_type=BillingResolution,
    system_prompt="You handle billing inquiries...",
    tools=[lookup_invoice, apply_refund],
)
```

**Event-rooted (LlamaIndex Workflows)** — agents are `@step`-decorated handlers that consume + emit events:

```python
from llama_index.core.workflow import Workflow, step, Event

class BillingResolvedEvent(Event):
    resolution: str

class BillingWorkflow(Workflow):
    @step
    async def billing_handle(self, ev: BillingRequestEvent) -> BillingResolvedEvent:
        result = await call_llm_with_tools(ev.request, tools=[lookup_invoice, apply_refund])
        return BillingResolvedEvent(resolution=result)
```

**Hierarchical-rooted (Google ADK)** — agents declare sub-agents as a tree:

```python
from google.adk.agents import LlmAgent

billing_agent = LlmAgent(
    name="billing",
    model="gemini-2.5-flash",
    instruction="You handle billing inquiries...",
    tools=[lookup_invoice, apply_refund],
)
```

**Enterprise-rooted (Microsoft Agent Framework 1.0)** — `ChatAgent` from the framework, with Azure-pluggable connectors:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

billing_agent = ChatAgent(
    chat_client=OpenAIChatClient(model_id="gpt-4o"),
    name="billing",
    instructions="You handle billing inquiries...",
    tools=[lookup_invoice, apply_refund],
)
```

**Conversation-rooted (AutoGen / AG2)** — agents are `AssistantAgent` / `UserProxyAgent` instances that participate in GroupChat:

```python
from autogen_agentchat.agents import AssistantAgent

billing_agent = AssistantAgent(
    name="billing",
    model_client=anthropic_client,
    system_message="You handle billing inquiries...",
    tools=[lookup_invoice, apply_refund],
)
```

### B — Handing off from a supervisor to a worker

How control transfers across agents is the second-most divergent surface. The conceptual move is the same (the supervisor decides which worker to call next); the wire format differs.

**LangGraph** — `Command(goto=...)` from the supervisor node, or conditional edges based on a routing decision:

```python
from langgraph.graph import Command
from typing import Literal

def supervisor(state: MessagesState) -> Command[Literal["billing", "technical", "account"]]:
    decision = route_classifier(state["messages"])
    return Command(goto=decision.route, update={"routing_decision": decision})
```

**CrewAI** — orchestration is implicit via the `Crew` with `Process.hierarchical`:

```python
from crewai import Crew, Process

support_crew = Crew(
    agents=[supervisor_agent, billing_agent, technical_agent],
    tasks=[support_task],
    process=Process.hierarchical,
    manager_llm="anthropic/claude-sonnet-4-5",
)
result = support_crew.kickoff()
```

**OpenAI Agents SDK / Claude Agent SDK** — supervisor declares handoffs; LLM picks one at runtime:

```python
from agents import Agent, Runner

supervisor_agent = Agent(
    name="supervisor",
    instructions="Route the conversation to the right specialist...",
    handoffs=[billing_agent, technical_agent, account_agent],
    model="gpt-4o-mini",  # the cheap routing model
)
result = await Runner.run(supervisor_agent, user_message)
```

**Pydantic AI** — supervisor agent's tool calls return a typed routing decision; orchestration is application-level:

```python
class RouteDecision(BaseModel):
    route: Literal["billing", "technical", "account"]
    confidence: float

SupervisorAgentType = Agent[None, RouteDecision]
supervisor = SupervisorAgentType(model="anthropic:claude-3-5-haiku", result_type=RouteDecision)
decision = await supervisor.run(user_message)
worker_result = await {
    "billing": billing_agent,
    "technical": technical_agent,
    "account": account_agent,
}[decision.data.route].run(user_message)
```

**Google ADK** — declare sub-agents on the parent; routing is via the LLM's reasoning:

```python
from google.adk.agents import LlmAgent

supervisor = LlmAgent(
    name="supervisor",
    model="gemini-2.5-flash",
    sub_agents=[billing_agent, technical_agent, account_agent],
    instruction="Route the user to the right specialist...",
)
```

**Microsoft Agent Framework 1.0** — workflow with explicit edges, or `OrchestrationBuilder` for higher-level patterns:

```python
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .add_agent("supervisor", supervisor_agent)
    .add_agent("billing", billing_agent)
    .add_edge("supervisor", "billing", condition=lambda ctx: ctx.route == "billing")
    .build()
)
```

**LlamaIndex Workflows** — supervisor's `@step` emits a routing event; downstream `@step`s handle the matched type:

```python
class BillingRoutedEvent(Event):
    user_message: str

class SupervisorWorkflow(Workflow):
    @step
    async def supervisor(self, ev: StartEvent) -> BillingRoutedEvent | TechnicalRoutedEvent:
        decision = await classify(ev.message)
        if decision.route == "billing":
            return BillingRoutedEvent(user_message=ev.message)
        else:
            return TechnicalRoutedEvent(user_message=ev.message)
```

**AutoGen / AG2** — `GroupChat` with a `selector_func` chooses the next speaker:

```python
from autogen_agentchat.teams import SelectorGroupChat

team = SelectorGroupChat(
    participants=[supervisor, billing_agent, technical_agent],
    model_client=anthropic_client,
    selector_prompt="Route the conversation based on intent...",
)
```

### C — Sharing state across agents

State-sharing semantics determine whether the multi-agent system can checkpoint, replay, and resume. The differences here are structural; they don't go away with abstraction.

**LangGraph** — typed state with explicit reducer semantics; the state dict is the contract:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]  # accumulator reducer
    routing_decision: dict
    escalation_tier: int | None

graph = StateGraph(ConversationState)
```

**CrewAI** — context dictionary passed between tasks; the abstraction is implicit:

```python
task = Task(
    description="Resolve the billing inquiry",
    agent=billing_agent,
    context=[prior_task],  # outputs from prior_task are in the context
)
```

**OpenAI Agents SDK / Claude Agent SDK** — conversation context is the state; handoffs carry conversation history through:

```python
# Context flows automatically through conversation history.
# Custom state via a `context` object on Runner:
result = await Runner.run(supervisor_agent, user_message, context=app_context)
```

**Pydantic AI** — dependency-injected `Deps` object carries shared state; no implicit conversation history:

```python
class SupportDeps(BaseModel):
    user_id: str
    conversation_history: list[str]
    routing_decision: RouteDecision | None = None

BillingAgentType = Agent[SupportDeps, BillingResolution]
billing_agent = BillingAgentType(...)
```

**Google ADK** — session state managed by the framework; sub-agents inherit + mutate via `tool_context`:

```python
from google.adk.tools.tool_context import ToolContext

def lookup_invoice(invoice_id: str, tool_context: ToolContext) -> dict:
    state = tool_context.state  # shared session state
    state["last_invoice_lookup"] = invoice_id
    return {"invoice": ...}
```

**Microsoft Agent Framework 1.0** — first-class session-based state management:

```python
from agent_framework import WorkflowState

state = WorkflowState()
state["routing_decision"] = decision
# State persists across agent boundaries within the workflow run.
```

**LlamaIndex Workflows** — workflow `Context` object available in every `@step`:

```python
class SupervisorWorkflow(Workflow):
    @step
    async def supervisor(self, ctx: Context, ev: StartEvent) -> RoutedEvent:
        await ctx.set("routing_decision", decision)
        ...
```

**AutoGen / AG2** — GroupChat accumulates conversation history; shared state via `tool_calls` on the conversation:

```python
# Conversation history IS the shared state.
# Custom shared state via team.team_state / agent context:
```

### D — Dispatching N workers in parallel

The most pattern-specific operation; not every framework has a clean parallel-dispatch primitive.

**LangGraph** — `Send(node, state)` constructs from a conditional edge:

```python
from langgraph.constants import Send

def fan_out_to_specialists(state: PlanState):
    return [Send("specialist", {"subquestion": sq}) for sq in state["subquestions"]]

graph.add_conditional_edges("planner", fan_out_to_specialists, ["specialist"])
```

**CrewAI** — tasks run in parallel by setting `async_execution=True`:

```python
task1 = Task(description="...", agent=specialist1, async_execution=True)
task2 = Task(description="...", agent=specialist2, async_execution=True)
crew = Crew(tasks=[task1, task2])
```

**OpenAI Agents SDK / Claude Agent SDK** — `asyncio.gather` at the application level; framework doesn't own parallelism:

```python
import asyncio
results = await asyncio.gather(
    Runner.run(specialist1, query1),
    Runner.run(specialist2, query2),
    Runner.run(specialist3, query3),
)
```

**Pydantic AI** — same `asyncio.gather` pattern; framework doesn't add parallel-dispatch primitive:

```python
results = await asyncio.gather(
    specialist1.run(q1, deps=deps),
    specialist2.run(q2, deps=deps),
)
```

**Google ADK** — `ParallelAgent` is a built-in agent type that runs sub-agents concurrently:

```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    name="parallel_research",
    sub_agents=[specialist1, specialist2, specialist3],
)
```

**Microsoft Agent Framework 1.0** — workflow supports parallel branches via `OrchestrationBuilder`:

```python
workflow = (
    WorkflowBuilder()
    .add_agent("specialist1", agent1)
    .add_agent("specialist2", agent2)
    .add_parallel_branch("planner", ["specialist1", "specialist2"])
    .build()
)
```

**LlamaIndex Workflows** — emit multiple events; matching `@step`s run concurrently:

```python
class PlannerWorkflow(Workflow):
    @step
    async def planner(self, ctx: Context, ev: StartEvent) -> SubQuestionEvent:
        for sq in subquestions:
            ctx.send_event(SubQuestionEvent(question=sq))
        return None  # workflow continues with parallel @step handlers
```

**AutoGen / AG2** — limited; conversational model is sequential by design (each turn is one agent). Parallel requires escaping the GroupChat abstraction.

### E — Instrumenting for observability

The instrumentation surface is the dimension that interacts most with [Path 06](../../learning-paths/06-evaluation-observability/). The native observability story of each framework determines how cleanly Path 06 patterns plug in.

**LangGraph** — env-var driven LangSmith tracing, or OTel via OpenLLMetry/OpenInference:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_..."
os.environ["LANGCHAIN_PROJECT"] = "support-agent-prod"
# All LangGraph node executions emit traces automatically.
```

**CrewAI** — env-var driven AgentOps; native OTel since 0.85+:

```python
import agentops
agentops.init(api_key="...")
# CrewAI execution emits to AgentOps automatically.
```

**OpenAI Agents SDK** — built-in tracing UI; OTel-compatible export via the SDK's tracing module:

```python
# Tracing is on by default; view at https://platform.openai.com/traces
# Custom OTel exporter:
from agents.tracing import set_tracing_export_api_key, set_tracing_disabled
```

**Claude Agent SDK** — native trace UI; OTel emit via the Anthropic OTel SDK packages.

**Pydantic AI** — native OpenTelemetry via Logfire (Pydantic team's product) or any OTel backend:

```python
import logfire
logfire.configure()
# Agent calls automatically instrumented.
```

**Google ADK** — native Vertex AI tracing; OTel via `opentelemetry-instrumentation-vertexai`:

```python
from opentelemetry import trace
from opentelemetry.instrumentation.vertexai import VertexAIInstrumentor

VertexAIInstrumentor().instrument()
```

**Microsoft Agent Framework 1.0** — native OpenTelemetry; integrates with App Insights, Datadog, Honeycomb; DevUI local debugger:

```python
# Start the local debugger:
# agent-framework devui
# Production: pipe OTel to your APM.
```

**LlamaIndex Workflows** — `llama-index-instrumentation` package; Phoenix integration native:

```python
from llama_index.core import set_global_handler
set_global_handler("arize_phoenix")
# Workflow events emit OpenInference spans.
```

**AutoGen / AG2** — OpenTelemetry via `autogen-agentchat` instrumentation; AgentOps integration.

## Decision guide

A single "choose X if" rule per framework — the dominant constraint that selects this framework over the others. None of these are exclusive; multi-framework deployments across A2A boundaries are increasingly common in 2026.

1. **Choose LangGraph if** the most important thing is explicit graph control + durable execution + first-class HITL — and you're willing to learn the state-schema discipline. LangGraph is the production-default in regulated industries because the verified-enterprise-deployments list is the longest (Klarna, Uber, LinkedIn, JPMorgan, BlackRock, Cisco, Elastic, Replit).

2. **Choose CrewAI if** your workflow maps cleanly to defined roles (planner / researcher / writer / critic) and your priority is shipping a working multi-agent prototype in days, not weeks. CrewAI's opinionated abstractions are an advantage for the role-shaped problem and a constraint for everything else.

3. **Choose OpenAI Agents SDK if** you're already locked into the OpenAI ecosystem and you want the cleanest handoff DX with built-in tracing. The handoff model gets unwieldy past ~10 agent types; below that, it's the most productive surface.

4. **Choose Claude Agent SDK if** you need computer use, your stack is Anthropic-native (or you want to be), and you can absorb the higher per-token cost. Pairs with Managed Agents for hosted state/sandboxing if you don't want to run your own infrastructure.

5. **Choose Pydantic AI if** type safety and FastAPI-style ergonomics dominate, and you want multi-provider portability without code change. Pair with LangGraph for orchestration if multi-agent complexity grows past what dependency-injection-plus-asyncio can handle cleanly.

6. **Choose Google ADK 1.0 if** A2A interoperability is the central requirement (your agent will coordinate with non-Google agents) and Vertex AI / Gemini is your model stack. ADK is the reference A2A implementation; nothing else has the same protocol-fluency.

7. **Choose Microsoft Agent Framework 1.0 if** your team is on .NET or your enterprise is Azure-first and you need the compliance/observability story that comes with the Microsoft enterprise stack. MAF 1.0 is the migration target for both Semantic Kernel and AutoGen codebases.

8. **Choose LlamaIndex Workflows if** the multi-agent system is fundamentally about retrieval and the data-layer integration is more important than the multi-agent abstractions per se. Module 4 (multi-agent RAG) is the strongest single-framework fit.

9. **Choose AutoGen / AG2 if** you have a legacy AutoGen codebase or your workflow is fundamentally conversational (debate, multi-agent critique, GroupChat-shaped). For greenfield Microsoft-stack work, use Microsoft Agent Framework 1.0 instead; AG2 is the OSS continuation path for the original AutoGen patterns.

## How the frameworks map to Path 03 modules

| Path 03 module / pattern | Strongest framework match | Why |
|---|---|---|
| Module 1 (Foundations + supervisor-worker) | LangGraph, OpenAI Agents SDK, Claude Agent SDK | All three have explicit supervisor primitives |
| Module 2 (Generator-critic) | AutoGen/AG2 | The GroupChat pattern is the closest framework match for structured-conversation critique |
| Module 3 (Plan-and-execute) | LangGraph (`Send`), Google ADK (`ParallelAgent`), LlamaIndex (event-driven) | All three have native parallel-dispatch primitives |
| Module 4 (Multi-agent RAG) | LlamaIndex Workflows, LangGraph | LlamaIndex's data-layer integration is the tightest; LangGraph wins on orchestration discipline |
| Module 5 (Framework bridge) | LangGraph (canonical), Microsoft Agent Framework, Google ADK | This is the page Module 5 supplements — Module 5 picks LangGraph as the canonical framework; this page widens the lens |
| Module 6 (Multi-agent evaluation) | All — frameworks plug into Path 06's eval stack | The native observability column above determines integration friction |
| [Pattern 01 (Handoff contracts)](../../learning-paths/03-multi-agent-systems/patterns/01-handoff-contracts.md) | Pydantic AI (strongest), LangGraph (typed state) | Type-safety is the structural defense |
| [Pattern 02 (Shared-state boundaries)](../../learning-paths/03-multi-agent-systems/patterns/02-shared-state-boundaries.md) | LangGraph, Microsoft Agent Framework | Both have explicit state-schema discipline |
| [Pattern 03 (Escalation and fallback)](../../learning-paths/03-multi-agent-systems/patterns/03-escalation-and-fallback.md) | LangGraph (`interrupt()`), Microsoft Agent Framework (HITL) | Both have first-class human-in-the-loop primitives |
| [Pattern 04 (Per-agent cost budgeting)](../../learning-paths/03-multi-agent-systems/patterns/04-per-agent-cost-budgeting.md) | LangGraph, CrewAI (limited) | LangGraph's per-node hook is the cleanest budget enforcement point |
| [Pattern 05 (Retry policies)](../../learning-paths/03-multi-agent-systems/patterns/05-retry-policies.md) | All — implemented at the tool boundary with `tenacity` | Framework-agnostic; the wrapper sits below the framework |
| [Pattern 06 (Cross-agent provenance)](../../learning-paths/03-multi-agent-systems/patterns/06-cross-agent-provenance.md) | LangGraph (state captures the chain), Microsoft Agent Framework | State-rooted frameworks make provenance structural; conversation-rooted frameworks make it harder |

## Migration paths

Multi-framework migration paths in mid-2026:

**LangGraph → Microsoft Agent Framework 1.0**: motivated by Azure-native compliance requirements; the state-schema work translates fairly directly (typed state → MAF's session state); the graph nodes translate to MAF workflow agents. Reasonable migration; budget 2-4 weeks for a 3-agent system.

**AutoGen → Microsoft Agent Framework 1.0**: Microsoft published a migration guide (April 2026); the AssistantAgent → ChatAgent mapping is the core move. The benefit is checkpointing + simplified messaging + durability. AG2 users continuing on the OSS path can stay on AG2; MAF is the canonical Microsoft target.

**Semantic Kernel → Microsoft Agent Framework 1.0**: Microsoft published the migration guide; Kernel + plugin patterns map to Agent + Tool abstractions. Recommended for greenfield Microsoft-stack work.

**CrewAI → LangGraph**: motivated by the growth-pain of CrewAI's opinionated abstractions when the workflow stops mapping to clean roles. The role/task abstractions need to be unwound; the LangGraph rebuild is non-trivial — budget 4-6 weeks for a 4-agent system. Verify the migration is needed (role-shaped workflows don't need it).

**OpenAI Agents SDK → LangGraph**: motivated by needing multi-provider support or durable execution. The handoff pattern translates to LangGraph supervisor + conditional edges. Reasonable migration; the cleanest path is to write the LangGraph version alongside and cut over per-agent.

**Pydantic AI → LangGraph (orchestration only)**: not a migration but a composition — keep Pydantic AI for each individual agent's type-safe LLM call, use LangGraph for the orchestration around them. The two compose cleanly because Pydantic AI is unopinionated about multi-agent structure.

**Any framework → A2A cross-framework**: A2A is the inter-framework escape hatch. Per [Project 3](../../learning-paths/03-multi-agent-systems/projects/03-a2a-federated-multi-agent.md), an Org A LangGraph supervisor can dispatch to an Org B CrewAI specialist via A2A without either framework needing to know about the other. The migration "path" here is "stay where you are; add A2A endpoints."

## Anti-scope (what this page does not do)

- **No benchmark claims without sources.** GitHub-star counts, monthly downloads, and "fastest framework" claims appear in the comparison table only with cited sources and publication dates. A framework that's "fastest" in one benchmark on one workload is not generally fastest.
- **No "best framework overall" conclusion.** The decision guide's nine "choose X if" rules are deliberately mutually-exclusive starting points; in practice, multi-framework deployments are increasingly common.
- **No pricing claims without time-bounding.** Framework licensing is mostly OSS (every entry on this page is MIT or Apache 2.0); the LLM API spend dominates the framework cost question. Pricing claims for managed offerings (Claude Managed Agents, LangSmith Plus, CrewAI Enterprise) carry the date of the cited source.
- **No "feature parity table will be up to date next quarter" claim.** This page is verified mid-2026; framework features shift quarterly. Reverify against the cited official docs before committing.
- **No assertion that any one framework is "production-ready" or not.** All nine ship in production somewhere in 2026; what varies is *which production*. The comparison table's "Best fit" column captures the answer.
- **Not the LangGraph tutorial.** [Module 5 (Framework bridge)](../../learning-paths/03-multi-agent-systems/README.md) covers LangGraph's primitives end-to-end with from-scratch comparisons; this page widens to the multi-framework landscape but doesn't replace that depth.
- **No coverage of agent platforms (vs frameworks).** LangGraph Platform, Vertex AI Agent Builder, Bedrock AgentCore, and Azure AI Foundry are hosted platforms wrapping the underlying frameworks. They're a different decision (managed vs self-hosted) that crosses the framework choice orthogonally.

## References

The framework comparisons and 2026 production claims in this page are anchored in the following sources. Each is dated; check the cited source for current state before committing.

**Framework comparison and production guides (2026)**:
- [Uvik Software (May 2026), *Best Python AI Agent Frameworks in 2026 Compared*](https://uvik.net/blog/python-ai-agent-frameworks/) — 12-framework Python-focused comparison; production-readiness column; release dates for OpenAI Agents SDK (March 2026), Google ADK (April 2026), Anthropic Agent SDK (April 2026)
- [Uvik Software (May 2026), *Agentic AI Frameworks 2026: LangGraph vs CrewAI vs OpenAI SDK*](https://uvik.net/blog/agentic-ai-frameworks/) — 15-framework comparison with the verified enterprise deployment lists (Klarna, Uber, LinkedIn, etc. on LangGraph)
- [Gurusup (April 2026), *Best Multi-Agent Frameworks in 2026: LangGraph, CrewAI, AutoGen, OpenAI Agents SDK, Google ADK*](https://gurusup.com/blog/best-multi-agent-frameworks-2026) — dimensional table including orchestration model, streaming support, production readiness; framework-launch-date data
- [Firecrawl (May 2026), *The best open source frameworks for building AI agents in 2026*](https://www.firecrawl.dev/blog/best-open-source-agent-frameworks) — 7-framework open-source-focused comparison; monthly download counts (LangGraph 34.5M leads)
- [Alice Labs (April 2026), *AI Agent Frameworks 2026: Production-Tested Ranking*](https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026) — the "dominant constraint" framing that anchors the decision guide structure
- [Channel (March 2026), *AI Agent Frameworks Compared: Which Ones Ship?*](https://www.channel.tel/blog/ai-agent-frameworks-compared-2026-what-ships) — practitioner perspective ("47 rows of feature comparisons that all said 'it depends'") supporting the no-best-framework conclusion
- [dev.to / linou518 (March 2026), *The 2026 AI Agent Framework Decision Guide: LangGraph vs CrewAI vs Pydantic AI*](https://dev.to/linou518/the-2026-ai-agent-framework-decision-guide-langgraph-vs-crewai-vs-pydantic-ai-b2h) — Pydantic AI star count + the three-framework-dominant claim

**Framework-specific 2026 sources**:
- [Microsoft Agent Framework blog (April 3, 2026), *Microsoft Agent Framework Version 1.0*](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) — the 1.0 GA announcement; "enterprise-grade multi-agent orchestration, multi-provider model support, and cross-runtime interoperability via A2A and MCP" positioning
- [Microsoft Learn, *Microsoft Agent Framework Overview*](https://learn.microsoft.com/en-us/agent-framework/overview/) — current docs; the AutoGen + Semantic Kernel convergence framing
- [Visual Studio Magazine (April 6, 2026), *Microsoft Ships Production-Ready Agent Framework 1.0*](https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx) — coverage of the 1.0 release; the AutoGen + Semantic Kernel migration story
- [DigitalApplied (April 2026), *Microsoft Agent Framework 1.0: .NET and Python 2026*](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide) — DevUI local debugger; Azure App Service reference architecture
- [Zylos Research (April 2026), *Claude Agent SDK & Managed Agents: Anthropic's Q2 2026 Agent Infrastructure Play*](https://zylos.ai/research/2026-04-20-claude-agent-sdk-managed-agents-architecture) — the two-track strategy (Agent SDK + Managed Agents); production cost analysis; runaway-loop gap framing
- [dev.to (May 2026), *What Anthropic's $200 Agent SDK Credit Means*](https://dev.to/vainamoinen/what-anthropics-200-agent-sdk-credit-means-if-you-run-claude-p-in-production-ce2) — the June 15, 2026 pricing shift (claude -p + Agent SDK moves to metered API credit)
- [NxCode (March 2026), *Claude AI 2026: Complete Guide*](https://www.nxcode.io/resources/news/claude-ai-complete-guide-models-pricing-features-2026) — Claude 4.6 model line; computer use 72.5% OSWorld benchmark
- [Use Apify (March 2026), *LangGraph Agents in Production*](https://use-apify.com/blog/langgraph-agents-production) — PostgreSQL checkpointing recipe; production-deployment shape
- [Intuz Q1 2026, *Top 5 AI Agent Frameworks 2026*](https://www.intuz.com/blog/top-5-ai-agent-frameworks-2025) — production-cost benchmarks ($63-171/mo)
- [A2A Protocol GitHub](https://github.com/google-a2a/A2A) — A2A protocol governance + SDK references; 5-language parity (Python, JS, Java, Go, .NET) as of mid-2026
- [Linux Foundation (April 9, 2026), *A2A Protocol Surpasses 150 Organizations*](https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html) — the production-adoption milestone

**Framework official docs (verified mid-2026)**:
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/) — `StateGraph`, `MessagesState`, `add_conditional_edges`, `PostgresSaver`, `interrupt()`
- [CrewAI documentation](https://docs.crewai.com/) — `Crew`, `Process.hierarchical`, `Process.sequential`, role-based agents
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — `Agent`, `Runner`, `handoffs`, built-in tracing
- [Claude Agent SDK](https://docs.anthropic.com/en/api/agent-sdk) — MCP-native; computer use; sub-agent orchestration
- [Pydantic AI documentation](https://ai.pydantic.dev/) — `Agent[Deps, ResultType]`, dependency injection, FastAPI-style ergonomics
- [Google ADK documentation](https://google.github.io/adk-docs/) — `LlmAgent`, `ParallelAgent`, `sub_agents`, A2A native
- [LlamaIndex Workflows documentation](https://docs.llamaindex.ai/en/stable/module_guides/workflow/) — `Workflow`, `@step`, `Event`, `Context`
- [AutoGen / AG2 documentation](https://microsoft.github.io/autogen/stable/) — `AssistantAgent`, `SelectorGroupChat`, conversation-rooted patterns
