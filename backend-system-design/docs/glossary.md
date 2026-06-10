# Glossary

## API

**Definition:** A contract that allows software systems to communicate through defined requests and responses.

**Why it matters:** APIs are the main interface between clients, services, integrations, and backend systems.

**Related topics:**

- [APIs](topics/01-apis/concept.md)
- [API Gateways](topics/02-api-gateways/concept.md)
- [REST vs GraphQL](topics/05-rest-vs-graphql/concept.md)

**Also known as:** Application Programming Interface

## API Gateway

**Definition:** A service that routes, secures, observes, and sometimes transforms API requests before they reach backend services.

**Why it matters:** Gateways centralize access control, routing, rate limits, and monitoring in service architectures.

**Related topics:**

- [API Gateways](topics/02-api-gateways/concept.md)
- [JWTs](topics/03-jwts/concept.md)
- [Rate Limiting](topics/07-rate-limiting/concept.md)

**Also known as:** API proxy, request router

## JWT

**Definition:** A compact token format used to transmit signed claims between parties.

**Why it matters:** JWTs support stateless authentication and authorization in API systems.

**Related topics:**

- [JWTs](topics/03-jwts/concept.md)
- [API Gateways](topics/02-api-gateways/concept.md)

**Also known as:** JSON Web Token

## Webhook

**Definition:** An HTTP callback sent from one system to another when an event occurs.

**Why it matters:** Webhooks enable event delivery without requiring consumers to poll continuously.

**Related topics:**

- [Webhooks](topics/04-webhooks/concept.md)
- [APIs](topics/01-apis/concept.md)
- [Change Data Capture](topics/19-change-data-capture/concept.md)

**Also known as:** HTTP callback, event callback

## REST

**Definition:** An architectural style for APIs that models operations around resources, URLs, and HTTP methods.

**Why it matters:** REST is widely used for simple, cacheable, and interoperable web APIs.

**Related topics:**

- [REST vs GraphQL](topics/05-rest-vs-graphql/concept.md)
- [APIs](topics/01-apis/concept.md)
- [Caching](topics/12-caching/concept.md)

**Also known as:** Representational State Transfer

## GraphQL

**Definition:** A query language and runtime for APIs that lets clients request exactly the data they need.

**Why it matters:** GraphQL can reduce over-fetching and improve client-driven data access.

**Related topics:**

- [REST vs GraphQL](topics/05-rest-vs-graphql/concept.md)
- [APIs](topics/01-apis/concept.md)

**Also known as:** Graph query API

## Long Polling

**Definition:** A communication pattern where the server holds an HTTP request open until data is available or a timeout occurs.

**Why it matters:** Long polling approximates real-time updates while staying within ordinary HTTP request behavior.

**Related topics:**

- [Long Polling vs WebSockets](topics/06-long-polling-vs-websockets/concept.md)
- [Webhooks](topics/04-webhooks/concept.md)

**Also known as:** Hanging request, held request

## WebSocket

**Definition:** A persistent, full-duplex connection that lets client and server exchange messages in both directions.

**Why it matters:** WebSockets are useful for low-latency systems such as chat, live dashboards, and collaborative tools.

**Related topics:**

- [Long Polling vs WebSockets](topics/06-long-polling-vs-websockets/concept.md)
- [Load Balancing](topics/09-load-balancing/concept.md)

**Also known as:** Persistent socket connection

## Rate Limiting

**Definition:** A control that restricts how many requests a client, user, or service can make over a time window.

**Why it matters:** Rate limiting protects systems from abuse, overload, and unfair capacity usage.

**Related topics:**

- [Rate Limiting](topics/07-rate-limiting/concept.md)
- [API Gateways](topics/02-api-gateways/concept.md)

**Also known as:** Quota enforcement, request throttling

## Idempotency

**Definition:** A property where repeating the same operation produces the same final effect as doing it once.

**Why it matters:** Idempotency makes retries safer in payment systems, APIs, queues, and distributed workflows.

**Related topics:**

- [Idempotency](topics/08-idempotency/concept.md)
- [Message Queues](topics/24-message-queues/concept.md)

**Also known as:** Safe retry behavior

## Load Balancing

**Definition:** The distribution of incoming traffic across multiple backend instances or nodes.

**Why it matters:** Load balancing improves capacity, availability, and failover behavior.

**Related topics:**

- [Load Balancing](topics/09-load-balancing/concept.md)
- [Availability](topics/20-availability/concept.md)
- [Single Point of Failure](topics/21-single-point-of-failure/concept.md)

**Also known as:** Traffic distribution, request balancing

## Proxy

**Definition:** An intermediary that forwards requests between clients and other systems.

**Why it matters:** Proxies can add routing, access control, caching, visibility, and network isolation.

**Related topics:**

- [Proxy vs Reverse Proxy](topics/10-proxy-vs-reverse-proxy/concept.md)
- [API Gateways](topics/02-api-gateways/concept.md)

**Also known as:** Forward proxy, intermediary

## Reverse Proxy

**Definition:** A proxy that represents backend servers to clients and forwards client requests to internal services.

**Why it matters:** Reverse proxies commonly handle TLS termination, routing, caching, and load balancing.

**Related topics:**

- [Proxy vs Reverse Proxy](topics/10-proxy-vs-reverse-proxy/concept.md)
- [Load Balancing](topics/09-load-balancing/concept.md)
- [CDN](topics/14-cdn/concept.md)

**Also known as:** Edge proxy, origin proxy

## Scalability

**Definition:** A system's ability to handle increased load by adding resources or improving efficiency.

**Why it matters:** Scalability lets systems support more users, more data, and higher throughput.

**Related topics:**

- [Scalability](topics/11-scalability/concept.md)
- [Load Balancing](topics/09-load-balancing/concept.md)
- [Sharding](topics/18-sharding/concept.md)

**Also known as:** Capacity growth

## Caching

**Definition:** Storing data closer to where it is needed so future reads are faster or cheaper.

**Why it matters:** Caching reduces latency, origin load, and repeated expensive work.

**Related topics:**

- [Caching](topics/12-caching/concept.md)
- [Cache Eviction](topics/13-cache-eviction/concept.md)
- [CDN](topics/14-cdn/concept.md)

**Also known as:** Read optimization, memoized storage

## Cache Eviction

**Definition:** The policy for removing items from a cache when capacity is limited or data is no longer useful.

**Why it matters:** Eviction controls memory usage and affects cache hit rate, freshness, and performance.

**Related topics:**

- [Cache Eviction](topics/13-cache-eviction/concept.md)
- [Caching](topics/12-caching/concept.md)

**Also known as:** Cache replacement policy

## CDN

**Definition:** A distributed network that serves content from locations close to users.

**Why it matters:** CDNs reduce latency and origin traffic for static assets, downloads, media, and cacheable responses.

**Related topics:**

- [CDN](topics/14-cdn/concept.md)
- [Caching](topics/12-caching/concept.md)
- [Reverse Proxy](topics/10-proxy-vs-reverse-proxy/concept.md)

**Also known as:** Content Delivery Network, edge cache

## SQL

**Definition:** A relational database query language and database style based on tables, schemas, and declarative queries.

**Why it matters:** SQL databases are often strong choices for structured data, joins, transactions, and consistency.

**Related topics:**

- [SQL vs NoSQL](topics/15-sql-vs-nosql/concept.md)
- [ACID Transactions](topics/16-acid-transactions/concept.md)
- [Indexes](topics/17-indexes/concept.md)

**Also known as:** Structured Query Language, relational database

## NoSQL

**Definition:** A broad class of non-relational database models such as document, key-value, wide-column, and graph databases.

**Why it matters:** NoSQL systems can fit flexible schemas, high write volume, or specialized access patterns.

**Related topics:**

- [SQL vs NoSQL](topics/15-sql-vs-nosql/concept.md)
- [Sharding](topics/18-sharding/concept.md)

**Also known as:** Non-relational database

## ACID Transaction

**Definition:** A transaction with atomicity, consistency, isolation, and durability guarantees.

**Why it matters:** ACID transactions protect critical state changes from partial updates and concurrency anomalies.

**Related topics:**

- [ACID Transactions](topics/16-acid-transactions/concept.md)
- [SQL vs NoSQL](topics/15-sql-vs-nosql/concept.md)

**Also known as:** Database transaction

## Index

**Definition:** A data structure that speeds up lookups, filtering, sorting, or uniqueness checks.

**Why it matters:** Indexes improve read performance but add storage overhead and write maintenance cost.

**Related topics:**

- [Indexes](topics/17-indexes/concept.md)
- [SQL vs NoSQL](topics/15-sql-vs-nosql/concept.md)

**Also known as:** Database index, lookup structure

## Sharding

**Definition:** Splitting data across multiple partitions or machines using a shard key.

**Why it matters:** Sharding helps scale storage and write throughput beyond a single database node.

**Related topics:**

- [Sharding](topics/18-sharding/concept.md)
- [Scalability](topics/11-scalability/concept.md)
- [Consistent Hashing](topics/23-consistent-hashing/concept.md)

**Also known as:** Horizontal partitioning

## Change Data Capture

**Definition:** Recording database changes and publishing them to downstream systems.

**Why it matters:** CDC supports replication, event pipelines, search indexing, analytics, and cache updates.

**Related topics:**

- [Change Data Capture](topics/19-change-data-capture/concept.md)
- [Webhooks](topics/04-webhooks/concept.md)
- [Message Queues](topics/24-message-queues/concept.md)

**Also known as:** CDC, change log streaming

## Availability

**Definition:** The percentage of time a system is operational and able to serve requests.

**Why it matters:** Availability defines reliability goals and helps guide redundancy, failover, and incident response.

**Related topics:**

- [Availability](topics/20-availability/concept.md)
- [Single Point of Failure](topics/21-single-point-of-failure/concept.md)

**Also known as:** Uptime, service availability

## Single Point of Failure

**Definition:** A component whose failure can cause the entire system or workflow to fail.

**Why it matters:** Removing single points of failure is central to resilient architecture design.

**Related topics:**

- [Single Point of Failure](topics/21-single-point-of-failure/concept.md)
- [Availability](topics/20-availability/concept.md)
- [Load Balancing](topics/09-load-balancing/concept.md)

**Also known as:** SPOF, critical dependency

## CAP Theorem

**Definition:** A distributed systems model stating that during a network partition, a system must choose between consistency and availability.

**Why it matters:** CAP helps engineers reason about partition behavior in distributed databases and replicated systems.

**Related topics:**

- [CAP Theorem](topics/22-cap-theorem/concept.md)
- [Availability](topics/20-availability/concept.md)
- [ACID Transactions](topics/16-acid-transactions/concept.md)

**Also known as:** Consistency, Availability, Partition tolerance theorem

## Consistent Hashing

**Definition:** A hashing strategy that maps keys to nodes so adding or removing nodes moves only a subset of keys.

**Why it matters:** Consistent hashing is useful for distributed caches, routing rings, and sharded systems.

**Related topics:**

- [Consistent Hashing](topics/23-consistent-hashing/concept.md)
- [Sharding](topics/18-sharding/concept.md)
- [Caching](topics/12-caching/concept.md)

**Also known as:** Hash ring

## Message Queue

**Definition:** A system that stores messages from producers until consumers process them.

**Why it matters:** Queues decouple services, buffer spikes, support retries, and move slow work out of request paths.

**Related topics:**

- [Message Queues](topics/24-message-queues/concept.md)
- [Idempotency](topics/08-idempotency/concept.md)
- [Batch vs Stream Processing](topics/27-batch-vs-stream-processing/concept.md)

**Also known as:** Queue, work queue, broker

## Stateful Service

**Definition:** A service that keeps client, session, or workflow state locally inside the running instance.

**Why it matters:** Stateful services can be harder to scale and recover because requests may depend on a specific instance.

**Related topics:**

- [Stateful vs Stateless](topics/25-stateful-vs-stateless/concept.md)
- [Availability](topics/20-availability/concept.md)

**Also known as:** Sessionful service

## Stateless Service

**Definition:** A service that handles each request independently and stores durable state outside the instance.

**Why it matters:** Stateless services are easier to scale horizontally, replace, and load balance.

**Related topics:**

- [Stateful vs Stateless](topics/25-stateful-vs-stateless/concept.md)
- [Load Balancing](topics/09-load-balancing/concept.md)

**Also known as:** Shared-state service, externalized-state service

## Concurrency

**Definition:** Managing multiple tasks in overlapping time, even if they are not executing at the exact same instant.

**Why it matters:** Concurrency improves responsiveness and throughput for IO-bound work.

**Related topics:**

- [Concurrency vs Parallelism](topics/26-concurrency-vs-parallelism/concept.md)
- [Message Queues](topics/24-message-queues/concept.md)

**Also known as:** Interleaved execution

## Parallelism

**Definition:** Executing multiple tasks at the same time, usually across multiple CPU cores or workers.

**Why it matters:** Parallelism can speed up CPU-bound or independent work when resources are available.

**Related topics:**

- [Concurrency vs Parallelism](topics/26-concurrency-vs-parallelism/concept.md)
- [Batch vs Stream Processing](topics/27-batch-vs-stream-processing/concept.md)

**Also known as:** Simultaneous execution

## Batch Processing

**Definition:** Processing a bounded group of records at scheduled intervals or after accumulation.

**Why it matters:** Batch processing is efficient for large offline jobs, reporting, and periodic data transformations.

**Related topics:**

- [Batch vs Stream Processing](topics/27-batch-vs-stream-processing/concept.md)
- [Change Data Capture](topics/19-change-data-capture/concept.md)

**Also known as:** Offline processing, scheduled processing

## Stream Processing

**Definition:** Processing events continuously as they arrive.

**Why it matters:** Stream processing supports low-latency analytics, monitoring, fraud detection, and real-time workflows.

**Related topics:**

- [Batch vs Stream Processing](topics/27-batch-vs-stream-processing/concept.md)
- [Message Queues](topics/24-message-queues/concept.md)

**Also known as:** Real-time processing, event stream processing

## Bloom Filter

**Definition:** A probabilistic set structure that can say an item is definitely absent or possibly present.

**Why it matters:** Bloom filters reduce expensive lookups when false positives are acceptable but false negatives are not.

**Related topics:**

- [Bloom Filters](topics/28-bloom-filters/concept.md)
- [Caching](topics/12-caching/concept.md)
- [Indexes](topics/17-indexes/concept.md)

**Also known as:** Probabilistic membership filter

## Geohashing

**Definition:** Encoding latitude and longitude into a string where prefixes represent geographic regions.

**Why it matters:** Geohashing helps bucket locations for nearby search, map indexing, and regional aggregation.

**Related topics:**

- [Geohashing](topics/29-geohashing/concept.md)
- [Indexes](topics/17-indexes/concept.md)

**Also known as:** Geographic hash, location prefix

## Navigation

- Home: [System Engineering Tutorials](index.md)
- Learning Path: [Full roadmap](learning-path.md)
- Topic Index: [All topics](topic-index.md)
- Start Topic: [APIs](topics/01-apis/concept.md)
- End Topic: [Geohashing](topics/29-geohashing/concept.md)
