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
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Proxy vs Reverse Proxy.

## What You Will Build

A minimal Python example under labs/10-proxy-vs-reverse-proxy/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/10-proxy-vs-reverse-proxy/demo.py
- labs/10-proxy-vs-reverse-proxy/test_proxy_vs_reverse_proxy.py

## Run the Example

```bash
cd labs/10-proxy-vs-reverse-proxy
python demo.py
```

## Expected Output

The script should show how Proxy vs Reverse Proxy changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for request latency, cache hit rate, upstream error rate, and connection reuse.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [Load Balancing](../09-load-balancing/concept.md)
- [Scalability](../11-scalability/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Load Balancing](../09-load-balancing/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Scalability](../11-scalability/concept.md)


