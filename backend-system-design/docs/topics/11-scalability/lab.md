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
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Scalability.

## What You Will Build

A minimal Python example under labs/11-scalability/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/11-scalability/demo.py
- labs/11-scalability/test_scalability.py

## Run the Example

```bash
cd labs/11-scalability
python demo.py
```

## Expected Output

The script should show how Scalability changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for throughput, latency, saturation, queue depth, and cost per request.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

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


