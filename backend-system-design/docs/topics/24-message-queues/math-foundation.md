---
title: Message Queues
slug: message-queues
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Consistent Hashing
unlocks:
  - Stateful vs Stateless
related_topics:
  - Consistent Hashing
  - Stateful vs Stateless
code_lab: ../../../labs/24-message-queues/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Math and Theory Foundation

## Core Formula or Model

A useful starting model is:

- Load = arrival rate x work per request
- Capacity = workers x service rate
- Utilization = load / capacity

## Intuition

When utilization approaches 100%, queues grow quickly and tail latency becomes unstable. Message Queues is usually about keeping the system inside a predictable operating range.

## Step-by-Step Example

1. Suppose traffic arrives at 500 operations per second.
2. If each worker handles 100 operations per second, at least 5 workers are needed before redundancy.
3. If a design target keeps utilization below 70%, use 8 workers or reduce work per operation.

## Engineering Interpretation

Track queue depth, consumer lag, throughput, retry rate, and dead-letter count. These measurements show whether theory matches production reality.

## Limitations

- Real systems have bursty traffic, dependency latency, and partial failures.
- Models are guides, not replacements for load testing.

## Related Topics

- [Consistent Hashing](../23-consistent-hashing/concept.md)
- [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Consistent Hashing](../23-consistent-hashing/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Stateful vs Stateless](../25-stateful-vs-stateless/concept.md)


