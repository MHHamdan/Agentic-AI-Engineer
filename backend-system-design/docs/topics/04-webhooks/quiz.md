---
title: Webhooks Quiz
slug: webhooks-quiz
level: intermediate
estimated_time: 10 minutes
prerequisites:
  - Webhooks
unlocks:
  - Event-driven system design
related_topics:
  - Webhooks
code_lab: ../../../labs/04-webhooks/webhook_demo.py
official_sources:
  - WebhooksGitHub
academic_sources: []
last_verified: 2026-06-09
---

# Quiz

## Multiple Choice

1. A webhook receiver should usually return which response code to acknowledge success?
   - A) 200
   - B) 404
   - C) 500
   - D) 302

2. What is an important security practice for webhooks?
   - A) Logging plain payloads
   - B) Validating signatures
   - C) Ignoring timestamps
   - D) Using GET requests only

## Short Answer

1. Why is asynchronous webhook processing recommended?
2. What is a common reason to retry webhook delivery?

## Code Review Questions

1. How would you verify a webhook signature in `webhook_demo.py`?
2. When should a webhook receiver return a 400 error?

## System Design Questions

1. Explain how webhooks differ from polling.
2. Describe a scenario where webhook retries are necessary.

## Answers

<details>
<summary>Show answers</summary>

1. A
2. B

Short answer examples:
- Asynchronous processing avoids blocking the sender and reduces timeout risk.
- Retries are needed when the receiver is temporarily unavailable.

Code review examples:
- Compute the expected signature and compare it to the header.
- Return 400 for invalid signatures or malformed payloads.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [REST vs GraphQL](../05-rest-vs-graphql/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)



