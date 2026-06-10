---
title: Long Polling vs WebSockets
slug: long-polling-vs-websockets
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - REST vs GraphQL
unlocks:
  - Rate Limiting
related_topics:
  - REST vs GraphQL
  - Rate Limiting
code_lab: ../../../labs/06-long-polling-vs-websockets/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Quiz

## Multiple Choice

1. What is the main purpose of Long Polling vs WebSockets?
   - A) To remove all network latency
   - B) To make a specific system tradeoff explicit
   - C) To avoid monitoring production systems
   - D) To guarantee infinite capacity

2. Which metric is useful for this topic?
   - A) connection count, message rate, latency, reconnect rate, and server memory per connection
   - B) Source-code line count only
   - C) Number of meetings
   - D) UI color palette

## Short Answer

1. Explain Long Polling vs WebSockets in one or two sentences.
2. Name one production failure mode related to this topic.

## Code Review Questions

1. What metric would you add to a demo for this topic?
2. What edge case should a test include?

## System Design Questions

1. Where would Long Polling vs WebSockets appear in a backend architecture?
2. What tradeoff would you discuss before using it?

## Answers

<details>
<summary>Show answers</summary>

1. B
2. A

Short answer examples:
- Long polling keeps an HTTP request open until new data is available, while WebSockets keep a persistent full-duplex connection open for real-time messages.
- A common failure mode is overload, stale state, duplicate work, or poor retry behavior.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Webhooks](../04-webhooks/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [JWTs](../03-jwts/concept.md)



