# DOS Project – Part 2

## Architecture
The system consists of:
- Catalog Service (2 replicas)
- Order Service (2 replicas)
- Client Service (Frontend + Cache + Load Balancer)

## Implemented Components
- Docker-based replication
- Client-side cache for read requests
- Load balancing using nginx / round-robin logic

## Pending / To Be Verified
- Strong cache consistency (invalidate on write)
- Replication correctness across services
- Performance evaluation
