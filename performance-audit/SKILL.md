---
name: performance-audit
description: >-
  Systematically audit any system for performance bottlenecks — works on both
  existing codebases (implementation audit) and high-level designs, architecture
  docs, or system specs (design audit). Identifies memory leaks, high latency,
  GC pressure, lock contention, inefficient I/O, and architectural decisions
  that bake in performance ceilings. Use when analyzing existing projects for
  optimization, reviewing HLD/architecture for performance pitfalls, comparing
  system performance characteristics, or when the user asks about making a
  system faster, more efficient, or lower-latency.
---

# Performance Audit

Systematic identification of performance-critical issues in **any system at any stage** — from an architecture whiteboard sketch to a running production codebase.

**Core principle:** The most expensive performance bugs are architectural. A bad design locks in latency ceilings that no amount of code optimization can fix. Catch them early.

## When to Use

- **Design-phase review** — auditing an HLD, architecture doc, system design, or design spec for performance pitfalls before any code is written
- **Implementation audit** — scanning an existing codebase for bottlenecks, memory leaks, GC pressure
- **Comparative analysis** — understanding why one system is faster than another (e.g., QuickFIX vs Chronicle FIX)
- **Pre-launch review** — production-readiness check for latency-sensitive systems
- **Design review during implementation** — code exists but you want to evaluate the architectural choices, not just the code

## Step 0: Determine Audit Mode

Before anything else, determine which mode applies:

| Signal | Mode |
|--------|------|
| Architecture doc, HLD, design spec, system diagram, RFC, no code yet | **Design Mode** |
| Existing codebase, source files, running system | **Implementation Mode** |
| Code exists + you also want to evaluate architectural decisions | **Both modes** (Design first, then Implementation) |
| Comparing two systems (one or both may be designs) | **Comparative Mode** (run appropriate mode on each, then compare) |

---

# Design Mode — Architectural Performance Audit

Use when reviewing a system design, HLD, architecture doc, or spec **before or independent of code**.

## Design Checklist

Create a todo for each item and complete in order:

1. **Parse the design artifacts** — read all available docs, diagrams, specs, RFCs
2. **Identify system boundaries** — services, components, external dependencies, trust boundaries
3. **Map data flows** — trace the critical request/message path through the system
4. **Run 8-dimension architectural scan** — evaluate each dimension (see below)
5. **Identify latency budget violations** — do the hops and operations fit within the target latency?
6. **Classify findings** — severity × difficulty-to-change-later matrix
7. **Produce design audit report** — structured findings with architectural recommendations

## Design Phase 1: Parse & Understand

Extract from the design documents:

| What to Find | Why |
|--------------|-----|
| **Stated requirements** — throughput, latency (p50/p99/p999), SLA | Sets the performance bar |
| **Scale parameters** — concurrent users, messages/sec, data volume | Determines if design scales |
| **Component inventory** — services, databases, queues, caches, gateways | Map the topology |
| **Technology choices** — languages, frameworks, databases, message brokers | Each has performance characteristics |
| **Deployment model** — regions, zones, containers, bare metal | Network topology = latency floor |

**If requirements are missing:** Flag this as Finding #1. You cannot evaluate performance without knowing what "fast enough" means.

## Design Phase 2: Map Critical Data Flows

Trace the path of the most frequent/important operations:

1. **Identify the top 3-5 critical flows** — the operations that will run at the highest frequency or have the strictest latency requirements
2. **For each flow, trace:** initiator → every component touched → response
3. **Count:** network hops, serialization boundaries, I/O waits, synchronization points
4. **Calculate latency floor:** Sum of (network round-trips × expected latency per hop) + (I/O operations × expected I/O latency). This is the theoretical minimum — the design cannot be faster than this.

**Example flow trace:**
```
Client → API Gateway → Auth Service → Order Service → Database → Order Service → Message Queue → API Gateway → Client
         [hop 1]       [hop 2]        [hop 3]        [I/O 1]                     [I/O 2]        [hop 4]
         ~1ms          ~1ms           ~1ms            ~2ms                        ~1ms           ~1ms
                                                                     Latency floor: ~7ms
```

## Design Phase 3: 8-Dimension Architectural Scan

For each critical flow, evaluate these 8 architectural dimensions. For detailed patterns, see [design-antipatterns.md](design-antipatterns.md).

### A1: Communication Pattern

**What to evaluate:** How components talk to each other.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Synchronous request-reply chains (A calls B calls C calls D) | Latency = sum of all calls; one slow service blocks everything | Async messaging, event-driven, parallel fan-out |
| Chatty protocols (many small calls per operation) | Network round-trip overhead dominates | Batch APIs, coarse-grained operations, data locality |
| No distinction between reads and writes | Can't optimize read path independently | CQRS, read replicas, materialized views |
| REST/JSON for high-throughput internal services | Parsing overhead, verbose wire format | gRPC/Protobuf, binary protocols, shared memory |

### A2: Data Flow & Serialization Boundaries

**What to evaluate:** How many times data changes representation as it flows through the system.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Data serialized/deserialized at every service boundary | CPU cost × number of boundaries on hot path | Shared binary format end-to-end, pass-through where possible |
| Different serialization formats between services | Each boundary requires full format conversion | Standardize on one efficient format (Protobuf, Avro, SBE) |
| Large payloads flowing through services that don't need them | Bandwidth waste, memory pressure, unnecessary parsing | Claim-check pattern, pass references not payloads |
| No schema evolution strategy | Forces breaking changes, dual-write complexity | Schema registry, backward-compatible evolution |

### A3: State Management & Persistence

**What to evaluate:** Where state lives, how it's accessed, and consistency trade-offs.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Single database for all workloads | Read/write contention, can't scale independently | Separate read/write stores, polyglot persistence |
| Strong consistency where eventual suffices | Coordination overhead, cross-region latency | Eventual consistency for non-critical reads |
| Shared mutable state between services | Coupling, contention, distributed locking | Event sourcing, owned-state-per-service |
| No caching layer for read-heavy data | Every read hits the database | Cache-aside, read-through cache, materialized views |
| Distributed transactions (2PC) on hot paths | Latency = slowest participant + coordination | Saga pattern, compensating transactions |

### A4: Scalability Model

**What to evaluate:** How the system handles increasing load.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Vertical scaling assumption for stateful components | Hits hardware ceiling, single point of failure | Partition/shard state, horizontal scaling |
| No partitioning strategy for data | Single-node bottleneck as data grows | Consistent hashing, range partitioning, shard-per-tenant |
| Shared-nothing claimed but shared database | Database becomes the bottleneck | Actually partition the data or use database per service |
| No load shedding / admission control | System degrades ungracefully under overload | Rate limiting, circuit breakers, priority queues |

### A5: Queue & Buffer Design

**What to evaluate:** How work is buffered between producers and consumers.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Unbounded queues | Memory exhaustion under load spike | Bounded queues with backpressure |
| No backpressure mechanism | Fast producer overwhelms slow consumer | Flow control, credit-based, reactive streams |
| Queue per message (no batching) | Per-message overhead dominates throughput | Micro-batching, batch flush on size or time |
| Persistent queue for ephemeral data | Unnecessary disk I/O on hot path | In-memory ring buffer (Disruptor pattern) |
| Single consumer on ordered queue | Throughput limited to one consumer's speed | Partitioned queues with parallel consumers |

### A6: Network Topology & Latency Budget

**What to evaluate:** Whether the physical deployment supports the latency requirements.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Cross-region calls on hot path | 50-200ms per hop, cannot be reduced | Co-locate services, regional deployment, replicate data |
| Cross-AZ calls for every request | 1-3ms per hop, adds up with multiple hops | Prefer same-AZ, use AZ-aware routing |
| External API call in critical path | Uncontrollable latency, availability risk | Cache, replicate, or make async |
| No latency budget allocated per hop | Can't tell if design is feasible | Assign ms budget per component, verify sum < target |
| DNS resolution on every request | 1-10ms per resolution | DNS caching, connection pooling, service mesh |

### A7: Failure & Recovery Overhead

**What to evaluate:** Whether error handling adds unacceptable latency.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Synchronous retries on hot path | Latency multiplied by retry count on failure | Async retry with queue, circuit breaker |
| No timeout budget (each service sets its own) | Cascading timeouts exceed user-facing SLA | Top-down timeout budget, deadline propagation |
| Retry storms (all clients retry simultaneously) | Amplifies load on already-struggling service | Exponential backoff + jitter, retry budgets |
| Health checks that are as expensive as real requests | Monitoring load competes with traffic | Lightweight health endpoints, sampling |
| No graceful degradation strategy | Partial failure → total failure | Feature flags, fallback responses, bulkheading |

### A8: Observability & Overhead Budget

**What to evaluate:** Whether monitoring/tracing/logging design adds latency.

| Red Flag | Why It Hurts | Better Alternative |
|----------|-------------|-------------------|
| Synchronous trace/log export on hot path | Each request waits for observability I/O | Async export, buffered/batched flushing |
| Per-request distributed trace with full payload capture | Memory and bandwidth overhead | Sampling (1-5% in production), head-based sampling |
| Unbounded metric cardinality | Memory growth, aggregation cost | Bounded label values, pre-aggregation |
| No overhead budget for observability | "Just add more metrics" until it hurts | Allocate ≤ 1-2% of request latency to observability |

## Design Phase 4: Latency Budget Validation

After the scan, validate the critical flows against requirements:

```
For each critical flow:
  1. Sum the latency floor (network hops + I/O operations)
  2. Add processing time estimates per component
  3. Add serialization costs at each boundary
  4. Add observability overhead
  5. Compare total to the latency requirement (p99, not p50)
  6. Include failure-path latency (retry + timeout = worst case)

  If estimated p99 > requirement: THE DESIGN DOES NOT MEET THE SLA.
  Flag specific hops/components that must be eliminated or optimized.
```

## Design Phase 5: Classify & Report

Use the design-mode sections of [report-template.md](report-template.md).

Severity for design findings uses a different matrix than implementation — **how hard is it to change later?**

| | Easy to Change Later | Moderate to Change | Hard/Impossible to Change |
|---|---|---|---|
| **High Impact** (breaks SLA) | P1 – Flag it | **P0 – Must fix before building** | **P0 – BLOCKING** |
| **Medium Impact** (degrades perf) | P2 – Note it | P1 – Should fix | **P0 – Must fix** |
| **Low Impact** (minor overhead) | P3 – Backlog | P2 – Note it | P1 – Should fix |

The key insight: architectural decisions that are **hard to change later** AND **hurt performance** are the highest priority, even if the impact seems "medium" now — because they become P0s in production with no easy fix.

---

# Implementation Mode — Code-Level Performance Audit

Use when scanning an existing codebase. This is the original 10-dimension scan.

## Implementation Checklist

Create a todo for each item and complete in order:

1. **Identify runtime & language** — determine language, runtime, GC model, threading model
2. **Map hot paths** — find the critical execution paths (request handling, message processing, tight loops)
3. **Run 10-dimension scan** — analyze each dimension on the hot paths (see below)
4. **Classify findings** — severity × frequency matrix
5. **Produce audit report** — structured report with prioritized findings
6. **Recommend fixes** — concrete, actionable changes ranked by impact/effort

## Impl Phase 1: Identify Runtime Characteristics

| Factor | Why It Matters | What to Check |
|--------|---------------|---------------|
| **Language** | Determines allocation model, FFI cost, safety guarantees | File extensions, build files |
| **GC model** | Stop-the-world vs concurrent vs manual; generational vs regional | Runtime docs, VM flags |
| **Threading model** | OS threads, green threads, event loop, actors | Thread pool configs, async patterns |
| **I/O model** | Blocking, NIO, io_uring, epoll | Socket/file APIs used |
| **Build profile** | Debug vs release, optimization level, LTO | Build configs, compiler flags |
| **Deployment** | Container memory limits, CPU pinning, NUMA | Dockerfiles, k8s specs |

## Impl Phase 2: Map Hot Paths

1. Identify entry points (HTTP handlers, message listeners, event callbacks, main loops)
2. Trace the call chain from entry to response/completion
3. Mark loops, recursive calls, and fan-out points
4. Note paths that execute per-request vs per-startup vs per-batch

**Priority:** Per-request hot paths > periodic batch paths > startup paths

## Impl Phase 3: 10-Dimension Scan

For each hot path, analyze these 10 dimensions. For detailed patterns per dimension, see [analysis-dimensions.md](analysis-dimensions.md).

| Dimension | What to Find | Fix Direction |
|-----------|-------------|---------------|
| **D1: Memory Allocation & GC Pressure** | Objects created per operation, autoboxing, temp collections, string concat in loops | Object pooling, flyweight, off-heap, primitive specialization |
| **D2: Data Copying & Serialization** | Unnecessary byte/string conversions, defensive copies, multiple intermediate representations | Zero-copy parsing, flyweight over buffer, shared immutables |
| **D3: I/O & Network Patterns** | Blocking I/O, N+1 queries, unbuffered writes, missing connection pooling | Async I/O, batching, buffered writers, connection pools |
| **D4: Lock Contention** | Global locks on hot paths, exclusive locks for reads, false sharing | Lock striping, RW locks, lock-free, thread-local |
| **D5: Data Structure Choice** | LinkedList misuse, linear search on large collections, unbounded growth | Match structure to access pattern, cache-friendly choices |
| **D6: Thread Model** | Thread-per-connection at scale, blocking in event loops, no backpressure | Event-driven I/O, bounded pools, backpressure |
| **D7: Caching** | Repeated queries, regex recompilation, reflection in loops, no eviction | LRU caches, pre-compiled patterns, method handle caching |
| **D8: Logging Overhead** | String formatting for disabled log levels, sync appenders, logging in loops | Guard levels, async appenders, sampling |
| **D9: Memory Layout** | Pointer chasing, boxed primitives, false sharing, AoS vs SoA mismatch | Contiguous layouts, primitive collections, cache-line padding |
| **D10: Error Handling** | Exceptions for control flow, stack trace on hot path, broad catch blocks | Return codes, pre-validation, cached exceptions |

For full details on each dimension with code examples, see [analysis-dimensions.md](analysis-dimensions.md).

## Impl Phase 4: Classify Findings

| | **Low Frequency** (startup, config) | **Medium Frequency** (per-batch, periodic) | **High Frequency** (per-request, per-message) |
|---|---|---|---|
| **High Impact** (blocks thread, large alloc, I/O wait) | P3 – Fix if easy | P2 – Should fix | **P0 – Fix immediately** |
| **Medium Impact** (extra alloc, suboptimal structure) | P4 – Note it | P3 – Fix if easy | **P1 – Fix soon** |
| **Low Impact** (minor inefficiency) | Skip | P4 – Note it | P3 – Fix if easy |

## Impl Phase 5: Produce Report

Use the template in [report-template.md](report-template.md).

---

# Comparative Mode

When comparing two systems (e.g., QuickFIX vs Chronicle FIX):

1. Run the appropriate mode (Design, Implementation, or both) on each system
2. Create side-by-side comparison per dimension
3. Identify **architectural decisions** that create the performance gap
4. Distinguish fixable implementation issues from fundamental design trade-offs
5. Produce a migration/improvement roadmap: what the slower system must change and at what cost

---

## Key Principles

- **Architecture > code** — the most impactful performance decisions are made at the design level
- **Hot paths first** — never optimize cold code, never over-architect cold flows
- **Latency budgets are additive** — every hop, serialization, and I/O adds up; verify the sum
- **Hard-to-change-later = high priority** — even if impact seems medium today
- **Measure, don't guess** — use profiling data when available; use structural analysis when not
- **Context matters** — the same pattern can be fine or catastrophic depending on scale

## Additional Resources

- [design-antipatterns.md](design-antipatterns.md) — deep-dive on architectural performance pitfalls
- [analysis-dimensions.md](analysis-dimensions.md) — deep-dive on each code-level dimension with examples
- [language-patterns.md](language-patterns.md) — language-specific performance anti-patterns
- [report-template.md](report-template.md) — output report template (both modes)
