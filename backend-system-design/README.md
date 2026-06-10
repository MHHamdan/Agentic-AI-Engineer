# System Engineering Tutorials

A progressive GitHub learning repository for backend, system design, and distributed systems concepts.

## Start here

- [Documentation home](docs/index.md)
- [Learning path](docs/learning-path.md)
- [Topic index](docs/topic-index.md)
- [Glossary](docs/glossary.md)
- [References](docs/references.md)

## What this repository includes

- Guided topic structure with explanations, engineering foundations, theory, labs, and quizzes.
- Complete 29-topic path from API fundamentals through geohashing.
- Python code labs with FastAPI, GraphQL, pytest, and runnable examples.
- MkDocs documentation configured with Material theme.
- Validation scripts and GitHub Actions for docs and tests.

## Learning path

### Stage 1: Communication Fundamentals

- [APIs](docs/topics/01-apis/concept.md)
- [REST vs GraphQL](docs/topics/05-rest-vs-graphql/concept.md)
- [Webhooks](docs/topics/04-webhooks/concept.md)
- [Long Polling vs WebSockets](docs/topics/06-long-polling-vs-websockets/concept.md)

### Stage 2: Security and Access Control

- [JWTs](docs/topics/03-jwts/concept.md)
- [API Gateways](docs/topics/02-api-gateways/concept.md)
- [Rate Limiting](docs/topics/07-rate-limiting/concept.md)
- [Idempotency](docs/topics/08-idempotency/concept.md)

### Stage 3: Performance and Scalability

- [Load Balancing](docs/topics/09-load-balancing/concept.md)
- [Proxy vs Reverse Proxy](docs/topics/10-proxy-vs-reverse-proxy/concept.md)
- [Scalability](docs/topics/11-scalability/concept.md)
- [Caching](docs/topics/12-caching/concept.md)
- [Cache Eviction](docs/topics/13-cache-eviction/concept.md)
- [CDN](docs/topics/14-cdn/concept.md)

### Stage 4: Data and Databases

- [SQL vs NoSQL](docs/topics/15-sql-vs-nosql/concept.md)
- [ACID Transactions](docs/topics/16-acid-transactions/concept.md)
- [Indexes](docs/topics/17-indexes/concept.md)
- [Sharding](docs/topics/18-sharding/concept.md)
- [Change Data Capture](docs/topics/19-change-data-capture/concept.md)

### Stage 5: Distributed Systems

- [Availability](docs/topics/20-availability/concept.md)
- [Single Point of Failure](docs/topics/21-single-point-of-failure/concept.md)
- [CAP Theorem](docs/topics/22-cap-theorem/concept.md)
- [Consistent Hashing](docs/topics/23-consistent-hashing/concept.md)
- [Message Queues](docs/topics/24-message-queues/concept.md)
- [Stateful vs Stateless](docs/topics/25-stateful-vs-stateless/concept.md)

### Stage 6: Advanced Processing and Location Systems

- [Concurrency vs Parallelism](docs/topics/26-concurrency-vs-parallelism/concept.md)
- [Batch vs Stream Processing](docs/topics/27-batch-vs-stream-processing/concept.md)
- [Bloom Filters](docs/topics/28-bloom-filters/concept.md)
- [Geohashing](docs/topics/29-geohashing/concept.md)

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Build docs

```bash
mkdocs build --strict
mkdocs serve
```

## Run tests

```bash
python -m pytest
python -m ruff check .
python scripts/validate_links.py
python scripts/validate_citations.py
python scripts/validate_code_labs.py
```

## Project structure

- `docs/`: tutorial content and topic pages
- `labs/`: runnable Python labs and tests
- `examples/`: infrastructure and configuration examples
- `scripts/`: validation and generation helpers
- `.github/workflows/`: CI for docs and tests
