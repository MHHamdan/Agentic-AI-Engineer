# Security Policy

This repository is an open educational resource — it ships code samples, recipes, and labs, not a product with a deployed surface. Even so, a few things in here can be security-relevant: example code that handles secrets, recipes that demonstrate authentication, and security-focused content in [`security/`](./security/). We take security issues in this material seriously and will respond promptly.

---

## Supported versions

Because the repository's content evolves continuously, we support **the current `main` branch only**. Older tags are not maintained for security updates. If you depend on a specific snapshot of the content, pin it to a tag and update on your schedule.

| Version | Supported |
|---|---|
| `main` (latest) | ✅ |
| Previous tagged releases | ❌ |

---

## Reporting a vulnerability

**Please report security issues privately**, not as public issues or pull requests.

The preferred channel is GitHub's private security advisory feature:

➡️ **[Open a private security advisory](https://github.com/MHHamdan/Agentic-AI-Engineer/security/advisories/new)**

This is encrypted in transit and only visible to the repository maintainers.

If you can't use GitHub's advisory feature, contact [@MHHamdan](https://github.com/MHHamdan) directly through a private GitHub message.

When reporting, please include:

- A clear description of the issue and where it appears (file path, link, or recipe name).
- A proof-of-concept or minimal reproduction if relevant.
- The impact you observed or anticipate.
- Whether the issue is in this repo's own content or in an upstream dependency.

We commit to:

- Acknowledging your report within 7 days.
- Providing a more detailed response within 14 days outlining next steps.
- Crediting you in the fix (unless you prefer to remain anonymous).

---

## What counts as a security issue in this repo

| In scope | Out of scope |
|---|---|
| Example code or recipes that demonstrate insecure patterns without warning | Bugs that don't have security impact (open a regular issue) |
| Secrets accidentally committed in code, notebooks, or `.env` files | Stylistic or content disagreements (open a regular issue) |
| CI workflows that could be abused to exfiltrate secrets or run untrusted code | Vulnerabilities in dependencies (report to the upstream project, then optionally let us know) |
| Lab notebooks that, if run as-instructed, would create insecure systems | Vulnerabilities in third-party tools we discuss (LangGraph, MCP servers, etc. — report upstream) |
| Compromise of the repository's supply chain | Behavior of LLM providers (OpenAI, Anthropic, Google — report to those vendors) |

---

## Disclosing security-adjacent content in the repo

Some content in this repo intentionally discusses adversarial techniques — prompt injection, tool abuse, red-teaming, etc. We follow these principles when accepting such content:

- Threat models and defenses with citations: **yes**.
- Defensive patterns engineers can apply: **yes**.
- Weaponizable exploits with no defensive purpose: **no**.
- "100% prevention" claims for any class of attack: **no**.

See [`security/README.md`](./security/) and [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full policy.

---

## Coordinated disclosure for upstream issues

If you find an issue in an upstream dependency (e.g., a CVE in a library we recommend), please report it to the upstream project first, following their security policy. Once a fix is available or a CVE is assigned, let us know so we can update affected pages in this repo and add a migration note.

---

## Acknowledgements

Security researchers who report valid issues will be acknowledged in `CHANGELOG.md` (with their consent), and optionally credited on the relevant fix's pull request.

Thank you for helping keep this resource safe.
