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
# Practical Lab

## Goal

Build a small demo that shows the key behavior of Long Polling vs WebSockets.

## What You Will Build

A minimal Python example under labs/06-long-polling-vs-websockets/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/06-long-polling-vs-websockets/demo.py
- labs/06-long-polling-vs-websockets/test_long_polling_vs_websockets.py

## Run the Example

```bash
cd labs/06-long-polling-vs-websockets
python demo.py
```

## Expected Output

The script should show how Long Polling vs WebSockets changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for connection count, message rate, latency, reconnect rate, and server memory per connection.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [REST vs GraphQL](../05-rest-vs-graphql/concept.md)
- [Rate Limiting](../07-rate-limiting/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Webhooks](../04-webhooks/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [JWTs](../03-jwts/concept.md)


