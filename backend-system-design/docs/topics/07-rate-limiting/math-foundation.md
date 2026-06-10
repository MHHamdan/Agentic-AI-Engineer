---
title: Rate Limiting
slug: rate-limiting
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - Long Polling vs WebSockets
unlocks:
  - Idempotency
related_topics:
  - Long Polling vs WebSockets
  - Idempotency
code_lab: ../../../labs/07-rate-limiting/demo.py
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

When utilization approaches 100%, queues grow quickly and tail latency becomes unstable. Rate Limiting is usually about keeping the system inside a predictable operating range.

## Step-by-Step Example

1. Suppose traffic arrives at 500 operations per second.
2. If each worker handles 100 operations per second, at least 5 workers are needed before redundancy.
3. If a design target keeps utilization below 70%, use 8 workers or reduce work per operation.

## Engineering Interpretation

Track requests per window, burst size, rejected request rate, and remaining quota. These measurements show whether theory matches production reality.

## Limitations

- Real systems have bursty traffic, dependency latency, and partial failures.
- Models are guides, not replacements for load testing.

## Related Topics

- [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)
- [Idempotency](../08-idempotency/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [API Gateways](../02-api-gateways/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Idempotency](../08-idempotency/concept.md)


