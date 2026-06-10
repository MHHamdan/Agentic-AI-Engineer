---
title: Proxy vs Reverse Proxy
slug: proxy-vs-reverse-proxy
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Load Balancing
unlocks:
  - Scalability
related_topics:
  - Load Balancing
  - Scalability
code_lab: ../../../labs/10-proxy-vs-reverse-proxy/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Quiz

## Multiple Choice

1. What is the main purpose of Proxy vs Reverse Proxy?
   - A) To remove all network latency
   - B) To make a specific system tradeoff explicit
   - C) To avoid monitoring production systems
   - D) To guarantee infinite capacity

2. Which metric is useful for this topic?
   - A) request latency, cache hit rate, upstream error rate, and connection reuse
   - B) Source-code line count only
   - C) Number of meetings
   - D) UI color palette

## Short Answer

1. Explain Proxy vs Reverse Proxy in one or two sentences.
2. Name one production failure mode related to this topic.

## Code Review Questions

1. What metric would you add to a demo for this topic?
2. What edge case should a test include?

## System Design Questions

1. Where would Proxy vs Reverse Proxy appear in a backend architecture?
2. What tradeoff would you discuss before using it?

## Answers

<details>
<summary>Show answers</summary>

1. B
2. A

Short answer examples:
- A forward proxy represents clients, while a reverse proxy represents servers.
- A common failure mode is overload, stale state, duplicate work, or poor retry behavior.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Load Balancing](../09-load-balancing/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Scalability](../11-scalability/concept.md)



