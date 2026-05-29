# Security

Threats and defenses for agentic AI systems. The attack surface of an agent is broader than the attack surface of an LLM — every tool, every data source, every other agent it talks to extends what a malicious input can reach.

## What's covered

| Page | Covers | Status |
|---|---|---|
| [`prompt-injection.md`](./prompt-injection.md) | Direct and indirect prompt injection — what works, what doesn't | ✅ Shipped (Batch 56) |
| `tool-abuse.md` | Agents using tools in ways the designer didn't anticipate | 📋 Planned |
| `data-exfiltration.md` | Leaking secrets via tool calls, retrieved context, or output channels | 📋 Planned |
| `jailbreaks.md` | Bypassing safety constraints in the underlying LLM | 📋 Planned |
| `guardrails.md` | Input filtering, output filtering, content classification | 📋 Planned |
| `red-teaming.md` | Practical adversarial testing for your agent | 📋 Planned |

## A grounding note

The state of LLM security research moves quickly, and any specific defense can become outdated. We focus on:

- **Threat models** that haven't changed much in two years (prompt injection, data exfiltration, tool abuse) — these are stable enough to be worth writing about.
- **Defense-in-depth principles** rather than specific products — guardrails libraries come and go, but layering input filtering, output filtering, and authorization stays sensible.
- **Practical patterns** — sandboxing, least-privilege tool access, human approval gates, output classification.

We're explicit about what's well-understood (prompt-injection threat model) versus actively researched (universal defenses against indirect prompt injection — there aren't any reliable ones yet).

## Sources we trust

- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- The agent-security research from major labs (Anthropic, OpenAI, Google DeepMind)
- Academic papers on prompt injection and adversarial robustness

Every page cites the primary source for any specific attack class or defense it describes.

## Reporting security issues in this repo

If you discover a security issue **in the repo's code** (e.g., a recipe that leaks credentials, a lab that recommends a dangerous default), please open a [private security advisory](https://github.com/MHHamdan/Agentic-AI-Engineer/security/advisories/new) rather than a public issue.

Security issues **in third-party tools** we cover should be reported to the upstream maintainers.

## Contributing

Security content has to be careful. We accept contributions that:

- Document a threat with citations to original research.
- Describe a defense with honest claims about its limitations.
- Provide red-teaming patterns that an engineer can actually use.

We **don't** accept contributions that:

- Provide weaponizable exploits with no defensive purpose.
- Claim "100% prevention" of any class of attack.
- Marketing-style write-ups of specific commercial guardrail products.

> 🟡 Threat models are classified **slow-moving** (years).
> 🔴 Specific defense techniques and tool integrations are classified **fast-changing** (months).
