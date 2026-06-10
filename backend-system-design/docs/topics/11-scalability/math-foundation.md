---
title: Scalability
slug: scalability
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Proxy vs Reverse Proxy
unlocks:
  - Caching
related_topics:
  - Proxy vs Reverse Proxy
  - Caching
code_lab: ../../../labs/11-scalability/demo.py
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

When utilization approaches 100%, queues grow quickly and tail latency becomes unstable. Scalability is usually about keeping the system inside a predictable operating range.

## Step-by-Step Example

1. Suppose traffic arrives at 500 operations per second.
2. If each worker handles 100 operations per second, at least 5 workers are needed before redundancy.
3. If a design target keeps utilization below 70%, use 8 workers or reduce work per operation.

## Engineering Interpretation

Track throughput, latency, saturation, queue depth, and cost per request. These measurements show whether theory matches production reality.

## Limitations

- Real systems have bursty traffic, dependency latency, and partial failures.
- Models are guides, not replacements for load testing.

## Related Topics

- [Proxy vs Reverse Proxy](../10-proxy-vs-reverse-proxy/concept.md)
- [Caching](../12-caching/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Proxy vs Reverse Proxy](../10-proxy-vs-reverse-proxy/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Caching](../12-caching/concept.md)


