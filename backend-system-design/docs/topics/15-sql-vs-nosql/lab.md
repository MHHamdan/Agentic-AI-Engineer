---
title: SQL vs NoSQL
slug: sql-vs-nosql
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - CDN
unlocks:
  - ACID Transactions
related_topics:
  - CDN
  - ACID Transactions
code_lab: ../../../labs/15-sql-vs-nosql/demo.py
official_sources: []
academic_sources: []
last_verified: 2026-06-09
---
# Practical Lab

## Goal

Build a small demo that shows the key behavior of SQL vs NoSQL.

## What You Will Build

A minimal Python example under labs/15-sql-vs-nosql/demo.py that simulates the concept and prints the important metrics.

## Requirements

- Python 3.11+
- Basic command-line usage

## Files

- labs/15-sql-vs-nosql/demo.py
- labs/15-sql-vs-nosql/test_sql_vs_nosql.py

## Run the Example

```bash
cd labs/15-sql-vs-nosql
python demo.py
```

## Expected Output

The script should show how SQL vs NoSQL changes behavior under load, failure, or repeated operations.

## Exercises

- Add one more input case.
- Print metrics for query latency, consistency guarantees, write throughput, storage growth, and operational complexity.
- Write a test that covers an edge case.

## Troubleshooting

- If Python cannot find the file, confirm the lab directory exists.
- If output is confusing, reduce the input size and print intermediate state.

## Related Topics

- [CDN](../14-cdn/concept.md)
- [ACID Transactions](../16-acid-transactions/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [CDN](../14-cdn/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [ACID Transactions](../16-acid-transactions/concept.md)


