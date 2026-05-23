# References

Curated reading and sources used across the repo. Every external citation in concept, math, recipe, and pattern pages should resolve to something in this folder or to a primary upstream source (official spec, changelog, paper).

## Subfolders / pages

| File | Covers |
|---|---|
| `papers.md` | Foundational and recent papers — ReAct, RAG, Toolformer, Reflexion, MCP-related research, evaluation methods, safety research |
| `books.md` | Books worth reading, with one-paragraph descriptions and what they're best for |
| `talks.md` | Conference talks and lectures that hold up |
| `community.md` | Blogs, repos, and people whose writing is consistently useful |

## What we cite

This repo treats citations like a senior engineer treats commit messages — short, specific, accurate. Practical rules:

- **Primary sources first.** Spec page > changelog > blog post > tweet.
- **Original paper for techniques.** When citing ReAct, link Yao et al. 2023, not a summary blog.
- **Concrete versions for tools.** "LangGraph 1.0 GA changelog" not "the LangGraph docs."
- **Date the link if it's a moving page.** If you cite `docs.langchain.com/...`, note the verification date.

## What we don't cite as primary

- Marketing pages claiming "the best agent framework" — not useful as a technical source.
- Wikipedia — fine as orientation, not as the only source for a technical claim.
- Tweets or social posts unless they're the only public source (then note that explicitly).

## Reading order suggestions

For someone new to the field who wants the canonical paper trail:

1. **Foundation** — Brown et al. *Language Models are Few-Shot Learners* (GPT-3, 2020).
2. **Tools and reasoning** — Yao et al. *ReAct* (2023); Schick et al. *Toolformer* (2023).
3. **RAG** — Lewis et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020).
4. **Reflection** — Shinn et al. *Reflexion* (2023); Madaan et al. *Self-Refine* (2023).
5. **Planning** — Wang et al. *Plan-and-Solve* (2023); Yao et al. *Tree of Thoughts* (2023).
6. **Multi-agent** — Wu et al. *AutoGen* (2023); recent multi-agent benchmarks.
7. **Evaluation** — Ragas paper, the RAGAS framework documentation.
8. **Safety** — OWASP Top 10 for LLM Applications; Greshake et al. *Indirect Prompt Injection* (2023).

Full citations with links land in `papers.md` as the curriculum fills in.

## Contributing

Adding a paper, talk, or repo to the right list is a quick, valuable contribution. Include:

- Full citation (authors, title, venue, year).
- A one-sentence description of why it's worth the time.
- A direct link to the canonical source (arXiv > GitHub > publisher).

> 🟢 References are classified **stable**. We add new entries; we don't typically remove old ones unless they're proven wrong.
