---
title: Consistent Hashing
slug: consistent-hashing
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - CAP Theorem
unlocks:
  - Message Queues
related_topics:
  - CAP Theorem
  - Message Queues
code_lab: ../../../labs/23-consistent-hashing/demo.py
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

When utilization approaches 100%, queues grow quickly and tail latency becomes unstable. Consistent Hashing is usually about keeping the system inside a predictable operating range.

## Step-by-Step Example

1. Suppose traffic arrives at 500 operations per second.
2. If each worker handles 100 operations per second, at least 5 workers are needed before redundancy.
3. If a design target keeps utilization below 70%, use 8 workers or reduce work per operation.

## Engineering Interpretation

Track key movement percentage, node balance, hot key rate, and replica count. These measurements show whether theory matches production reality.

## Limitations

- Real systems have bursty traffic, dependency latency, and partial failures.
- Models are guides, not replacements for load testing.

## Related Topics

- [CAP Theorem](../22-cap-theorem/concept.md)
- [Message Queues](../24-message-queues/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [CAP Theorem](../22-cap-theorem/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Message Queues](../24-message-queues/concept.md)


