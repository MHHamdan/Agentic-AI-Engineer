---
title: CAP Theorem
slug: cap-theorem
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Single Point of Failure
unlocks:
  - Consistent Hashing
related_topics:
  - Single Point of Failure
  - Consistent Hashing
code_lab: ../../../labs/22-cap-theorem/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Quiz

## Multiple Choice

1. What is the main purpose of CAP Theorem?
   - A) To remove all network latency
   - B) To make a specific system tradeoff explicit
   - C) To avoid monitoring production systems
   - D) To guarantee infinite capacity

2. Which metric is useful for this topic?
   - A) stale read rate, write availability, quorum latency, and conflict rate
   - B) Source-code line count only
   - C) Number of meetings
   - D) UI color palette

## Short Answer

1. Explain CAP Theorem in one or two sentences.
2. Name one production failure mode related to this topic.

## Code Review Questions

1. What metric would you add to a demo for this topic?
2. What edge case should a test include?

## System Design Questions

1. Where would CAP Theorem appear in a backend architecture?
2. What tradeoff would you discuss before using it?

## Answers

<details>
<summary>Show answers</summary>

1. B
2. A

Short answer examples:
- CAP theorem says a distributed data system facing a network partition must choose between consistency and availability.
- A common failure mode is overload, stale state, duplicate work, or poor retry behavior.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Single Point of Failure](../21-single-point-of-failure/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Consistent Hashing](../23-consistent-hashing/concept.md)



