# Part 2 – System Design

## Overall Architecture
The system follows a microservices-based distributed architecture consisting of:

- Catalog Service (2 replicas)
- Order Service (2 replicas)
- Client Service (Gateway)
- Nginx (Static frontend)

The client-service acts as a single entry point and is responsible for:
- Load balancing
- Caching read requests
- Ensuring cache consistency

## Replication
Both catalog-service and order-service use primary-to-peer replication.
Write operations are executed locally, then replicated to the peer replica
using internal endpoints protected by an internal token.

Replication uses state transfer (setting the new quantity) rather than
re-applying operations, avoiding double-decrement issues.

## Load Balancing
The client-service implements round-robin load balancing across available
catalog and order replicas.

## Cache and Consistency
An in-memory LRU cache with TTL is used for read operations.
Before any write operation, catalog replicas invalidate cached entries
via an internal endpoint, guaranteeing strong consistency.
