# Architectural Performance Anti-Patterns — Deep Dive

Detailed patterns, real-world examples, and evaluation criteria for each of the 8 design-phase audit dimensions.

---

## A1: Communication Pattern — Extended

### Synchronous Call Chains

The most common architectural performance killer. Service A calls B, which calls C, which calls D.

**Latency:** Sum of all calls (serial). If any one is slow, everything is slow.
**Availability:** Product of all service availabilities. 4 services at 99.9% = 99.6% chain availability.

```
Sync chain:  A ──→ B ──→ C ──→ D ──→ response
             |     2ms    |     3ms    |     5ms    |     2ms
             Total: 12ms minimum, no parallelism possible

Async/parallel:  A ──→ B ──→ response    (2ms + 2ms = 4ms)
                   ├──→ C (fire & forget, 3ms, doesn't block response)
                   └──→ D (async, 5ms, results arrive later)
```

### Chatty vs Chunky APIs

| Pattern | Calls per Operation | Overhead | Fix |
|---------|-------------------|----------|-----|
| Get order, then get each line item, then get each product | 1 + N + N | N × (serialization + network + deserialization) | Single aggregate query returning full order |
| Check auth, then check permissions, then check rate limit | 3 sequential calls | 3 × network round trip | Combined policy endpoint or sidecar |
| REST resource per entity field | M fields × N entities | M×N HTTP requests | GraphQL, batch endpoint, or BFF pattern |

### Protocol Selection Guide

| Protocol | Latency | Throughput | Use When |
|----------|---------|------------|----------|
| gRPC + Protobuf | ~0.1-1ms | Very high | Internal service-to-service, streaming |
| HTTP/2 + JSON | ~1-5ms | High | External APIs, browser clients |
| HTTP/1.1 + JSON | ~2-10ms | Moderate | Legacy compatibility, simple integrations |
| Raw TCP + binary (SBE/FlatBuffers) | ~10-100µs | Extreme | Ultra-low-latency (trading, gaming) |
| Shared memory / IPC | ~1-10µs | Extreme | Co-located processes, same-machine |
| Kafka/messaging | ~1-50ms | Very high (async) | Event-driven, decoupled systems |

---

## A2: Data Flow & Serialization Boundaries — Extended

### Counting Serialization Boundaries

Every time data crosses a component boundary, it typically gets serialized and deserialized. Count them:

```
Example: Order placement flow

Client (JSON) ──→ API Gateway (parse JSON, re-serialize) ──→ Order Service 
  (deserialize, validate, serialize to DB format) ──→ Database (parse SQL/protocol)
  ──→ Order Service (deserialize result, serialize event) ──→ Message Queue
  (serialize message) ──→ Notification Service (deserialize)

Serialization boundaries: 7 serialize + 5 deserialize = 12 operations
```

**Each boundary costs:** CPU for codec + memory for intermediate objects + possible format conversion.

### Serialization Format Performance Comparison

| Format | Encode (ns) | Decode (ns) | Size (bytes) | Schema | Human-Readable |
|--------|------------|------------|-------------|--------|---------------|
| JSON | ~500-2000 | ~500-3000 | Large (verbose) | Optional | Yes |
| Protobuf | ~100-300 | ~100-500 | Small (compact) | Required | No |
| FlatBuffers | ~50-100 | ~10-50 (zero-copy) | Small | Required | No |
| SBE (Simple Binary Encoding) | ~10-50 | ~10-30 (flyweight) | Minimal | Required | No |
| Avro | ~200-500 | ~200-700 | Small | Required | No |
| MessagePack | ~200-500 | ~200-500 | Medium | Optional | No |

### Pass-Through Optimization

If a service receives data and forwards it without modification, it should NOT deserialize and re-serialize:

```
BAD:   Gateway receives bytes → deserialize → inspect → serialize → forward
GOOD:  Gateway receives bytes → inspect header only → forward bytes unchanged
BEST:  Gateway uses zero-copy (splice/sendfile) → forward without touching user space
```

---

## A3: State Management & Persistence — Extended

### Database Access Pattern Analysis

| Pattern | Reads/sec | Writes/sec | Recommended Store |
|---------|----------|-----------|-------------------|
| High read, rare write, key-value | 100K+ | <100 | Redis, Memcached + persistent backing store |
| High read, moderate write, relational | 10K+ | 1K+ | Read replicas + write primary |
| High write, append-only | N/A | 100K+ | Kafka, Chronicle Queue, time-series DB |
| Complex queries, moderate load | <10K | <1K | PostgreSQL, MySQL with proper indexing |
| Graph traversals | N/A | Moderate | Neo4j, Amazon Neptune |
| Full-text search | 10K+ | Moderate | Elasticsearch, OpenSearch |

### Consistency vs Latency Trade-off

```
Strong consistency (single leader):
  Write → replicate to all → acknowledge
  Latency: max(replica_latencies) + coordination
  Use when: Financial transactions, inventory counts

Eventual consistency:
  Write → acknowledge → replicate asynchronously
  Latency: local write only (~1ms)
  Use when: User profiles, activity feeds, analytics

Causal consistency:
  Write → acknowledge → replicate with causal ordering
  Latency: local write + causal metadata
  Use when: Chat messages, collaborative editing
```

### Distributed Transaction Red Flags

| Pattern | Problem | Alternative |
|---------|---------|-------------|
| 2-Phase Commit across services | Locks held for duration of slowest participant | Saga with compensating transactions |
| Distributed lock for data consistency | Lock contention = throughput ceiling | Optimistic concurrency, version vectors |
| Shared database between microservices | Tight coupling, schema change = coordinated deploy | Database per service + events |

---

## A4: Scalability Model — Extended

### Scaling Bottleneck Identification

For each component, ask: **What happens when load doubles?**

| Component Type | Common Bottleneck | Scaling Strategy |
|---------------|-------------------|------------------|
| Stateless compute | CPU (usually scales fine) | Horizontal scaling, autoscale |
| Stateful service | State migration, rebalancing | Partition from day one, consistent hashing |
| Single-leader database | Write throughput | Sharding, write-ahead log replication |
| Message queue | Partition count, consumer throughput | Pre-partition, parallel consumers |
| Cache layer | Memory capacity, eviction rate | Sharded cache (Redis Cluster), tiered caching |
| External API dependency | Their rate limits, not your scaling | Cache, queue, circuit-break |

### Amdahl's Law Reality Check

If 5% of processing is inherently serial (single-threaded, global lock, ordered operations):
- 2 cores: 1.9x speedup (not 2x)
- 8 cores: 4.7x speedup (not 8x)
- 64 cores: 13.3x speedup (not 64x)
- 1024 cores: 19.3x speedup (ceiling)

**Audit for:** What percentage of the hot path is inherently serial? This is the scalability ceiling.

---

## A5: Queue & Buffer Design — Extended

### Backpressure Strategies

| Strategy | How It Works | Trade-off |
|----------|-------------|-----------|
| **Bounded queue + reject** | Producer gets error when queue full | Data loss risk, producer must handle rejection |
| **Bounded queue + block** | Producer blocks until space available | Can cascade backpressure up the chain (good) |
| **Credit-based flow control** | Consumer grants credits to producer | Fine-grained, complex to implement |
| **Rate limiting** | Fixed throughput cap on producer | Simple, may reject valid traffic |
| **Load shedding** | Drop lower-priority work under load | Requires priority classification |
| **Reactive streams** | Demand-driven pull from consumer | Good for pipelines, requires reactive framework |

### Ring Buffer (Disruptor) vs Traditional Queue

| Property | `BlockingQueue` / Traditional | Ring Buffer (Disruptor) |
|----------|------------------------------|------------------------|
| Allocation | Object per entry + Node wrapper | Pre-allocated fixed array |
| Lock behavior | Lock on put + lock on take | Lock-free (CAS on sequence) |
| Cache behavior | Scattered node objects | Sequential, prefetcher-friendly |
| GC impact | Garbage per dequeue | Zero GC (entries reused) |
| Throughput | ~5M ops/sec | ~100M+ ops/sec |
| Latency | ~100ns-1µs | ~50-100ns |

**Design-phase takeaway:** If a queue sits on the hottest path and handles >1M messages/sec, a ring buffer design is not premature optimization — it's a necessary architectural choice.

---

## A6: Network Topology & Latency Budget — Extended

### Latency Reference Numbers

| Operation | Typical Latency |
|-----------|----------------|
| L1 cache hit | ~1 ns |
| L2 cache hit | ~4 ns |
| L3 cache hit | ~10-40 ns |
| Main memory access | ~100 ns |
| SSD random read | ~10-100 µs |
| HDD random read | ~2-10 ms |
| Same-datacenter round trip | ~0.5-1 ms |
| Same-region cross-AZ round trip | ~1-3 ms |
| Cross-region round trip (US East ↔ US West) | ~60-80 ms |
| Cross-continent round trip (US ↔ Europe) | ~100-150 ms |
| DNS resolution (uncached) | ~1-50 ms |
| TLS handshake | ~2-10 ms |
| TCP connection establishment | ~1-3 ms |

### Latency Budget Worksheet

```
Target p99 latency: _____ ms

Component                          Budget (ms)    Justification
─────────────────────────────────────────────────────────────────
Network ingress (client → LB)      _____          [region, protocol]
Load balancer → service            _____          [same AZ? TLS?]
Service processing                 _____          [CPU-bound estimate]
Service → database                 _____          [query complexity]
Database processing                _____          [index? table scan?]
Database → service                 _____          [result set size]
Service → cache                    _____          [if applicable]
Service → downstream service       _____          [if applicable]
Serialization overhead             _____          [format, payload size]
Observability overhead             _____          [tracing, logging]
─────────────────────────────────────────────────────────────────
TOTAL                              _____          must be < target

Safety margin (20% of target)      _____          for variance/spikes
```

---

## A7: Failure & Recovery Overhead — Extended

### Timeout Budget Design

Timeouts must be designed **top-down**, not bottom-up:

```
BAD (bottom-up, each service sets own timeout):
  API Gateway: 30s timeout
    → Service A: 10s timeout
      → Service B: 10s timeout
        → Database: 5s timeout
  
  Worst case: 30s user wait (terrible UX)
  Problem: Each team chose "safe" defaults independently

GOOD (top-down, budget allocated from SLA):
  User SLA: 2s p99
    → API Gateway: 1.8s budget
      → Service A: 1.2s budget
        → Service B: 0.8s budget
          → Database: 0.5s budget
  
  Each layer gets a fraction. If any layer exceeds, circuit-break immediately.
```

### Retry Amplification

```
Without coordination:
  100 requests/sec at ingress
  Service A retries 3x on failure → up to 300 requests to Service B
  Service B retries 3x on failure → up to 900 requests to Database
  
  10% failure rate → 10x load amplification during partial outage

With retry budgets:
  Each service allowed max 10% retry rate
  Circuit breaker opens after 5 consecutive failures
  Exponential backoff + jitter prevents thundering herd
```

---

## A8: Observability & Overhead Budget — Extended

### Overhead Budget Allocation

Rule of thumb: observability should cost **≤ 1-2% of request latency** and **≤ 5% of CPU**.

| Observability Type | Typical Overhead | Budget |
|-------------------|-----------------|--------|
| Structured logging (async) | ~1-10 µs per log line | ≤ 0.5% of request |
| Distributed tracing (sampled) | ~5-50 µs per span | ≤ 0.5% of request |
| Metrics (pre-aggregated counters) | ~10-100 ns per metric | ≤ 0.1% of request |
| Metrics (histograms with high cardinality) | ~1-10 µs per recording | ≤ 0.5% of request |
| Full request/response logging | ~100 µs - 10 ms | NEVER on hot path |

### Sampling Strategies

| Strategy | When to Use | Trade-off |
|----------|------------|-----------|
| Head-based (decide at ingress) | Default for most systems | Misses errors that happen mid-trace |
| Tail-based (decide after trace completes) | When you need all error traces | Requires buffering full traces, memory cost |
| Rate-based (N traces per second) | Simple, predictable overhead | May miss rare events at low rates |
| Error-only (always trace errors) | Debugging-focused | No baseline of healthy traces |
| Adaptive (increase sampling under anomaly) | Sophisticated systems | Complex to implement correctly |

---

## Cross-Cutting: Architecture Decision Record Checklist

When reviewing any HLD, check whether these decisions have been explicitly made (not left to implementation time):

- [ ] **Communication protocol** between every pair of communicating components
- [ ] **Serialization format** for each boundary
- [ ] **Consistency model** for each data store
- [ ] **Partitioning strategy** for each stateful component
- [ ] **Backpressure mechanism** for each queue / async boundary
- [ ] **Timeout budget** allocated top-down from SLA
- [ ] **Retry policy** with amplification analysis
- [ ] **Caching strategy** with invalidation approach
- [ ] **Failure mode** for each external dependency (what happens when X is down?)
- [ ] **Observability overhead budget** allocated and enforced

**Missing decisions = implicit defaults = performance surprises in production.**
