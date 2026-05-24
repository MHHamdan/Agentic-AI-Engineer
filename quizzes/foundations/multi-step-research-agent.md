---
quiz_id: foundations-multi-step-research-agent
title: "Multi-step research agent"
source:
  - concepts/tools/search-tools.md
  - tools/search/snapshot-v1.0.md
  - labs/03-multi-step-research-agent/
length_minutes: 8
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Why does Lab 03 split search into TWO tools (`web_search` for snippets and `fetch_page` for full content) instead of one combined tool?"
    options:
      A: "OpenAI's function-calling API requires at least two tools."
      B: "It lets the agent triage results cheaply via snippets before paying the cost of full-page fetches."
      C: "Most search libraries don't return full text in their search results."
      D: "It's the LangChain convention and we're following it for consistency."
    answer: B
    explanation: |
      The split exists for cost-aware triage. `web_search` returns short snippets
      across many results cheaply. `fetch_page` is bandwidth-heavy, slow, and
      hits real failure modes (paywalls, timeouts, 404s). The agent gets to
      *decide* which 1-2 URLs from the snippet list are worth the full fetch,
      and skip the rest. If you merge them, you lose this triage step and the
      agent burns context and time fetching every result. The point isn't the
      tool count; it's the pattern: search broadly, fetch selectively, synthesize.
    review:
      page: concepts/tools/search-tools.md
      section: "Two tools, not one"

  - id: q2
    difficulty: easy
    question: "How does Lab 03 decide which URLs to list as citations in the final answer?"
    options:
      A: "It asks the LLM to enumerate the citations as part of the final response."
      B: "It includes every URL the agent saw in any search-results page."
      C: "The loop records URLs the moment `fetch_page` returns ok/too_long — separately from the LLM's working memory."
      D: "It uses a regex over the final answer text to extract URLs."
    answer: C
    explanation: |
      Citations are recorded by the agent loop, not by the LLM. The moment
      `fetch_page` returns a successful result, the URL goes into a `citations`
      list maintained by the loop's state. The model can't add a URL it didn't
      actually fetch, can't remove one, and can't fabricate a title. Asking the
      LLM to enumerate citations at the end is unreliable across long
      trajectories — models hallucinate URLs, especially when they "remember"
      having read something they only saw in snippets. Including every search
      result conflates "I saw this in results" with "I actually read this,"
      which destroys the value of citations. The structural property is what
      makes them trustworthy.
    review:
      page: labs/03-multi-step-research-agent/README.md
      section: "Steps"

  - id: q3
    difficulty: medium
    question: "An agent calls `web_search('latest agentic AI papers')` and the tool returns `{\"status\": \"empty\", \"detail\": \"no results returned\"}`. What's the *correct* next action?"
    options:
      A: "Surface 'I could not find any information' immediately — empty results are final."
      B: "Re-issue the exact same query — search engines sometimes return different results."
      C: "Re-query with different terms. If that's also empty, surface a graceful 'not found' answer without fabricating."
      D: "Switch to a different LLM model — the empty result is the model's fault."
    answer: C
    explanation: |
      Empty results from one query don't mean the answer doesn't exist; they
      often mean the query was poorly phrased. The right move is to refine —
      different keywords, different scope, maybe a wider time window. *If*
      multiple refined queries also return empty (Lab 03 caps this with the
      repeated-action detector), then surfacing "I could not find a reliable
      answer" is the right behavior. A is too eager to give up. B is the
      classic infinite-loop bug — Lab 03's repeated-action detector exists
      specifically to prevent it. D blames the wrong layer; the LLM didn't
      cause the search to return empty, so changing models won't help.
    review:
      page: concepts/tools/search-tools.md
      section: "Failure modes you'll see"

  - id: q4
    difficulty: medium
    question: "Why does Lab 03 use `requests` + `BeautifulSoup` for `fetch_page` instead of `ddgs.extract()` or `tavily_client.extract()`, which would return cleaner Markdown?"
    options:
      A: "Performance — `requests` is faster than the library extract methods."
      B: "Pedagogical — abstracting HTTP failures hides the timeout / 404 / paywall handling that's the whole point of the lab."
      C: "Licensing — the extract methods have stricter terms than direct HTTP."
      D: "Compatibility — the extract methods don't work with all Python versions."
    answer: B
    explanation: |
      The lab's point is to *expose* the real failure modes of web I/O —
      timeouts, HTTP 4xx/5xx, paywalls, redirects. The library extract methods
      hide most of these behind a clean abstraction, which is exactly what you
      want in production code but exactly the wrong thing for learning. The
      lab's `fetch_page` builds up the structured-error pattern from Lab 02
      against real HTTP, so the failure-mode walkthrough in step 6 has
      something concrete to demonstrate. The README explicitly notes that
      production code *should* consider `ddgs.extract` or `tavily.extract` for
      cleaner output.
    review:
      page: labs/03-multi-step-research-agent/README.md
      section: "Solution discussion"

  - id: q5
    difficulty: medium
    question: "What does the `_action_hash(name, args)` tracking in the agent loop prevent?"
    options:
      A: "Calling the same tool twice in one run."
      B: "Calling a tool with the *exact same arguments* twice — different argument values still go through."
      C: "Calling the LLM more than once per question."
      D: "Returning duplicate URLs in the citations list."
    answer: B
    explanation: |
      The hash captures `(tool_name, args)` as a pair. Two `web_search` calls
      with different `recency` arguments are considered different actions and
      both execute. Two `fetch_page` calls on the *same* URL count as a
      repeat. The mechanism prevents the specific failure mode of "model
      didn't understand why the result was empty and tries the identical
      query again expecting different results" — which is the most common
      infinite-loop failure in research agents. A is too restrictive (the
      agent legitimately calls `web_search` many times). C is unrelated. D
      is a downstream effect but not what the mechanism targets.
    review:
      page: labs/03-multi-step-research-agent/README.md
      section: "Steps"

  - id: q6
    difficulty: medium
    question: "Lab 03's `fetch_page` returns `{\"status\": \"too_long\", \"text\": ...[:max_chars], \"truncated_at\": max_chars}` when a page exceeds the character cap. Why is this preferable to silently truncating or raising an exception?"
    options:
      A: "It looks more professional in test output."
      B: "It lets the agent reason about the truncation — it knows the content is partial and can choose to fetch a more specific page or accept the partial information."
      C: "It allows the loop to retry the fetch automatically."
      D: "Truncating without flagging is illegal under most web ToS."
    answer: B
    explanation: |
      The `too_long` status with `truncated_at` gives the agent the *information*
      that the content is partial. It can then decide: accept the partial text
      (often fine if the relevant section is in the first 8K chars), fetch a
      different page that's smaller, or refine its query to land on a more
      specific source. Silent truncation removes this information; the agent
      might confidently synthesize from the head of a page and miss critical
      content in the tail. Raising an exception would crash the loop. Returning
      structured information about what happened is the Lab 02 pattern applied
      to a new failure mode.
    review:
      page: concepts/tools/search-tools.md
      section: "Snippet vs. full-page tradeoffs"

  - id: q7
    difficulty: hard
    question: "A teammate says: 'Lab 03 builds a search agent — that's basically RAG, right? Same idea, different corpus.' What's the most accurate response?"
    options:
      A: "Yes — both retrieve documents based on a query, so they're the same pattern."
      B: "No — search queries a corpus you don't control (the open web); RAG queries a corpus you built for purpose (your indexed documents). The mechanics, reliability profile, and citation semantics differ."
      C: "Yes for the user, no for the developer."
      D: "RAG is just web search with embeddings — the only difference is the similarity function."
    answer: B
    explanation: |
      Search and RAG share a *shape* (query → ranked results → use them to
      answer) but are fundamentally different in what corpus they query and
      what control you have over it. With web search, you have no control over
      indexing, no control over freshness, no guarantee a result will be
      retrievable next month. With RAG, you chose the documents, you chunked
      them, you embedded them, you indexed them — you own the corpus.
      Citation semantics differ too: "I read this URL" vs. "I retrieved this
      chunk from document X." Production systems often use both (search for
      open web, RAG for proprietary knowledge), but conflating them leads to
      bad designs. D is wrong because embeddings are not what defines RAG —
      the defining property is the controlled corpus.
    review:
      page: concepts/tools/search-tools.md
      section: "Why search is not RAG"

  - id: q8
    difficulty: hard
    question: "You're shipping a research agent to production for paying customers. Your prototype works great with `ddgs`. What's the most honest reason to consider switching to a paid backend like Tavily?"
    options:
      A: "Paid APIs always return better results than free ones."
      B: "`ddgs` carries a 'for educational purposes only' disclaimer and is subject to rate limits and aggressive upstream blocking. A production service for paying customers needs a backend with terms and an SLA-shaped behavior model."
      C: "Tavily uses a faster algorithm than DuckDuckGo."
      D: "The free tier on Tavily is unlimited."
    answer: B
    explanation: |
      The honest reasons to switch are the practical ones: `ddgs` is
      explicitly "for educational purposes only" per its own PyPI page, it
      depends on scraping that upstream engines actively try to block, and
      there's no support contract if it breaks. For a paid customer-facing
      product, you want an API with terms of use you can rely on. A is
      marketing language — quality varies by query and provider. C is also
      marketing — speed depends on caching and load. D is factually wrong:
      Tavily's free tier is 1,000 calls/month per the verified docs (and even
      that number can change — verify at signup time). Production needs
      stability and supportability, not a guarantee of better individual
      results.
    review:
      page: tools/search/snapshot-v1.0.md
      section: "`ddgs` (the default)"
---

# 🧠 Quiz · Multi-step research agent

> ⏱ ~8 min · 🎯 Pass: 6/8 · 📖 Sources:
>
> - [`concepts/tools/search-tools.md`](../../concepts/tools/search-tools.md)
> - [`tools/search/snapshot-v1.0.md`](../../tools/search/snapshot-v1.0.md)
> - [`labs/03-multi-step-research-agent/`](../../labs/03-multi-step-research-agent/)

The questions test the *patterns* of multi-step research agents — citation tracking, failure modes, the search-vs-RAG distinction — not the syntax of any specific library. If you understand why each design choice exists, the questions should feel natural.

---

## Question 1 *(easy)*

Why does Lab 03 split search into TWO tools (`web_search` for snippets and `fetch_page` for full content) instead of one combined tool?

A. OpenAI's function-calling API requires at least two tools.  
B. It lets the agent triage results cheaply via snippets before paying the cost of full-page fetches.  
C. Most search libraries don't return full text in their search results.  
D. It's the LangChain convention and we're following it for consistency.

<details>
<summary>Show answer</summary>

**Answer: B** — Triage is the whole point.

The split exists for cost-aware triage. `web_search` returns short snippets across many results cheaply. `fetch_page` is bandwidth-heavy, slow, and hits real failure modes (paywalls, timeouts, 404s). The agent gets to *decide* which 1-2 URLs from the snippet list are worth the full fetch, and skip the rest. If you merge them, you lose this triage step and the agent burns context and time fetching every result. The point isn't the tool count; it's the pattern: search broadly, fetch selectively, synthesize.

→ Review: [`search-tools.md` § "Two tools, not one"](../../concepts/tools/search-tools.md#two-tools-not-one)

</details>

---

## Question 2 *(easy)*

How does Lab 03 decide which URLs to list as citations in the final answer?

A. It asks the LLM to enumerate the citations as part of the final response.  
B. It includes every URL the agent saw in any search-results page.  
C. The loop records URLs the moment `fetch_page` returns ok/too_long — separately from the LLM's working memory.  
D. It uses a regex over the final answer text to extract URLs.

<details>
<summary>Show answer</summary>

**Answer: C** — The loop is the source of truth, not the LLM.

Citations are recorded by the agent loop, not by the LLM. The moment `fetch_page` returns a successful result, the URL goes into a `citations` list maintained by the loop's state. The model can't add a URL it didn't actually fetch, can't remove one, and can't fabricate a title. Asking the LLM to enumerate citations at the end is unreliable across long trajectories — models hallucinate URLs, especially when they "remember" having read something they only saw in snippets. Including every search result conflates "I saw this in results" with "I actually read this," which destroys the value of citations. The structural property is what makes them trustworthy.

→ Review: [`lab 03 README` § "Steps"](../../labs/03-multi-step-research-agent/README.md#steps)

</details>

---

## Question 3 *(medium)*

An agent calls `web_search('latest agentic AI papers')` and the tool returns `{"status": "empty", "detail": "no results returned"}`. What's the *correct* next action?

A. Surface 'I could not find any information' immediately — empty results are final.  
B. Re-issue the exact same query — search engines sometimes return different results.  
C. Re-query with different terms. If that's also empty, surface a graceful 'not found' answer without fabricating.  
D. Switch to a different LLM model — the empty result is the model's fault.

<details>
<summary>Show answer</summary>

**Answer: C** — Refine, then degrade gracefully.

Empty results from one query don't mean the answer doesn't exist; they often mean the query was poorly phrased. The right move is to refine — different keywords, different scope, maybe a wider time window. *If* multiple refined queries also return empty (Lab 03 caps this with the repeated-action detector), then surfacing "I could not find a reliable answer" is the right behavior. A is too eager to give up. B is the classic infinite-loop bug — Lab 03's repeated-action detector exists specifically to prevent it. D blames the wrong layer; the LLM didn't cause the search to return empty, so changing models won't help.

→ Review: [`search-tools.md` § "Failure modes you'll see"](../../concepts/tools/search-tools.md#failure-modes-youll-see)

</details>

---

## Question 4 *(medium)*

Why does Lab 03 use `requests` + `BeautifulSoup` for `fetch_page` instead of `ddgs.extract()` or `tavily_client.extract()`, which would return cleaner Markdown?

A. Performance — `requests` is faster than the library extract methods.  
B. Pedagogical — abstracting HTTP failures hides the timeout / 404 / paywall handling that's the whole point of the lab.  
C. Licensing — the extract methods have stricter terms than direct HTTP.  
D. Compatibility — the extract methods don't work with all Python versions.

<details>
<summary>Show answer</summary>

**Answer: B** — The failure modes ARE the point.

The lab's point is to *expose* the real failure modes of web I/O — timeouts, HTTP 4xx/5xx, paywalls, redirects. The library extract methods hide most of these behind a clean abstraction, which is exactly what you want in production code but exactly the wrong thing for learning. The lab's `fetch_page` builds up the structured-error pattern from Lab 02 against real HTTP, so the failure-mode walkthrough in step 6 has something concrete to demonstrate. The README explicitly notes that production code *should* consider `ddgs.extract` or `tavily.extract` for cleaner output.

→ Review: [`lab 03 README` § "Solution discussion"](../../labs/03-multi-step-research-agent/README.md#solution-discussion)

</details>

---

## Question 5 *(medium)*

What does the `_action_hash(name, args)` tracking in the agent loop prevent?

A. Calling the same tool twice in one run.  
B. Calling a tool with the *exact same arguments* twice — different argument values still go through.  
C. Calling the LLM more than once per question.  
D. Returning duplicate URLs in the citations list.

<details>
<summary>Show answer</summary>

**Answer: B** — Identical-args repeats are the bug.

The hash captures `(tool_name, args)` as a pair. Two `web_search` calls with different `recency` arguments are considered different actions and both execute. Two `fetch_page` calls on the *same* URL count as a repeat. The mechanism prevents the specific failure mode of "model didn't understand why the result was empty and tries the identical query again expecting different results" — which is the most common infinite-loop failure in research agents. A is too restrictive (the agent legitimately calls `web_search` many times). C is unrelated. D is a downstream effect but not what the mechanism targets.

→ Review: [`lab 03 README` § "Steps"](../../labs/03-multi-step-research-agent/README.md#steps)

</details>

---

## Question 6 *(medium)*

Lab 03's `fetch_page` returns `{"status": "too_long", "text": ...[:max_chars], "truncated_at": max_chars}` when a page exceeds the character cap. Why is this preferable to silently truncating or raising an exception?

A. It looks more professional in test output.  
B. It lets the agent reason about the truncation — it knows the content is partial and can choose to fetch a more specific page or accept the partial information.  
C. It allows the loop to retry the fetch automatically.  
D. Truncating without flagging is illegal under most web ToS.

<details>
<summary>Show answer</summary>

**Answer: B** — Structured status is information the agent can use.

The `too_long` status with `truncated_at` gives the agent the *information* that the content is partial. It can then decide: accept the partial text (often fine if the relevant section is in the first 8K chars), fetch a different page that's smaller, or refine its query to land on a more specific source. Silent truncation removes this information; the agent might confidently synthesize from the head of a page and miss critical content in the tail. Raising an exception would crash the loop. Returning structured information about what happened is the Lab 02 pattern applied to a new failure mode.

→ Review: [`search-tools.md` § "Snippet vs. full-page tradeoffs"](../../concepts/tools/search-tools.md#snippet-vs-full-page-tradeoffs)

</details>

---

## Question 7 *(hard)*

A teammate says: "Lab 03 builds a search agent — that's basically RAG, right? Same idea, different corpus." What's the most accurate response?

A. Yes — both retrieve documents based on a query, so they're the same pattern.  
B. No — search queries a corpus you don't control (the open web); RAG queries a corpus you built for purpose (your indexed documents). The mechanics, reliability profile, and citation semantics differ.  
C. Yes for the user, no for the developer.  
D. RAG is just web search with embeddings — the only difference is the similarity function.

<details>
<summary>Show answer</summary>

**Answer: B** — Corpus control is the key difference.

Search and RAG share a *shape* (query → ranked results → use them to answer) but are fundamentally different in what corpus they query and what control you have over it. With web search, you have no control over indexing, no control over freshness, no guarantee a result will be retrievable next month. With RAG, you chose the documents, you chunked them, you embedded them, you indexed them — you own the corpus. Citation semantics differ too: "I read this URL" vs. "I retrieved this chunk from document X." Production systems often use both (search for open web, RAG for proprietary knowledge), but conflating them leads to bad designs. D is wrong because embeddings are not what defines RAG — the defining property is the controlled corpus.

→ Review: [`search-tools.md` § "Why search is not RAG"](../../concepts/tools/search-tools.md#why-search-is-not-rag)

</details>

---

## Question 8 *(hard)*

You're shipping a research agent to production for paying customers. Your prototype works great with `ddgs`. What's the most honest reason to consider switching to a paid backend like Tavily?

A. Paid APIs always return better results than free ones.  
B. `ddgs` carries a "for educational purposes only" disclaimer and is subject to rate limits and aggressive upstream blocking. A production service for paying customers needs a backend with terms and an SLA-shaped behavior model.  
C. Tavily uses a faster algorithm than DuckDuckGo.  
D. The free tier on Tavily is unlimited.

<details>
<summary>Show answer</summary>

**Answer: B** — Terms of use, not result quality.

The honest reasons to switch are the practical ones: `ddgs` is explicitly "for educational purposes only" per its own PyPI page, it depends on scraping that upstream engines actively try to block, and there's no support contract if it breaks. For a paid customer-facing product, you want an API with terms of use you can rely on. A is marketing language — quality varies by query and provider. C is also marketing — speed depends on caching and load. D is factually wrong: Tavily's free tier is 1,000 calls/month per the verified docs (and even that number can change — verify at signup time). Production needs stability and supportability, not a guarantee of better individual results.

→ Review: [`snapshot-v1.0.md` § "ddgs (the default)"](../../tools/search/snapshot-v1.0.md#ddgs-the-default)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the search-tools concept page; redo the failure-mode walkthrough in step 6 of Lab 03. |
| < 4/8 | Re-do Lab 03 with the concept page open. The questions map directly to specific sections. |

You've now finished the **practical Foundations path** — three labs (01, 02, 03), the LangGraph bridge (Lab 05), the math, and the framework concept. Path 02 (Agentic RAG) is the natural next step; its patterns transfer cleanly from Lab 03.
