---
title: APIs Math and Theory Foundation
slug: apis-math-foundation
level: beginner
estimated_time: 25 minutes
prerequisites:
  - APIs
unlocks:
  - API performance analysis
related_topics:
  - APIs
  - REST vs GraphQL
code_lab: ../../../labs/01-apis/api_demo.py
official_sources:
  - RFC9110
academic_sources: []
last_verified: 2026-06-09
---

# Math and Theory Foundation

## Core Formula or Model

APIs are evaluated using latency, throughput, and error rate.

- Latency: time per request
- Throughput: requests per second
- Error rate: failed requests divided by total requests

## Intuition

An API should serve as many requests as possible while keeping response times low and errors minimal.

## Step-by-Step Example

1. If an endpoint handles 200 requests in 10 seconds, throughput is 20 requests per second.
2. If 4 of those requests fail, error rate is 4 / 200 = 2%.
3. If average latency is 120 ms, P95 and P99 are the important tail latency metrics.

## Engineering Interpretation

- High throughput indicates capacity.
- Low error rate indicates stability.
- Tail latency is more meaningful than average latency for user experience.

## Limitations

- API performance depends on backend services and network conditions.
- Simple metrics do not capture request size or business complexity.

## Related Topics

- [API Gateways](../02-api-gateways/concept.md)
- [REST vs GraphQL](../05-rest-vs-graphql/concept.md)

## References

APIs are commonly measured by request latency, throughput, and error rate in operations engineering.


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Home](../../index.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [REST vs GraphQL](../05-rest-vs-graphql/concept.md)


