# System Design Study Template

Copy this template when studying a new system. Fill in each section following the phases in SKILL.md.

---

## System: [Name]

**One-line summary:** [What this system does in one sentence]

**Category:** [Messaging | Storage Engine | Database | Networking | Concurrency Primitive | Cache | Consensus | Other]

**Created by:** [Person/Organization]

**Origin year:** [Year first released/published]

---

## Phase 1: Problem Space

### Problem Statement

> [One sentence: what pain point triggered this system's creation?]

### Performance Targets

| Metric | Target |
|--------|--------|
| Throughput | [X msg/sec, requests/sec, MB/s] |
| Latency (p50) | [X ms/us/ns] |
| Latency (p99) | [X ms/us/ns] |
| Scale | [concurrent connections, data volume, cluster size] |
| Key constraint | [zero GC, kernel bypass, single-writer, etc.] |

### Predecessor Analysis

| Predecessor | Strength | Where It Broke Down |
|-------------|----------|---------------------|
| [System A] | [What it did well] | [Why not good enough] |
| [System B] | [What it did well] | [Why not good enough] |
| [System C] | [What it did well] | [Why not good enough] |

### Key Insight That Enabled This System

> [What new idea, technique, or shift in thinking made this system possible?]

---

## Phase 2: Architecture

### Component Diagram

```
[Draw the 4-7 core components and their relationships]
[Use ASCII art or describe the topology]
```

### Component Inventory

| Component | Responsibility (one sentence) | Why it's separate | What breaks if removed |
|-----------|-------------------------------|-------------------|------------------------|
| [Comp A] | | | |
| [Comp B] | | | |
| [Comp C] | | | |
| [Comp D] | | | |

### Data Flow (Hot Path)

```
[Entry Point] → [Step 1] → [Step 2] → [Step 3] → [Exit Point]
                 copy?       buffer?    persist?
                 serialize?  transform? route?
```

**Serialization boundaries:** [list where data changes format]

**Memory copies:** [list where data is copied]

**Kernel crossings:** [list user-space ↔ kernel-space transitions]

**Network hops:** [list network round-trips]

### Hot / Warm / Cold Path Classification

| Path | Example Operations | Optimization Level |
|------|--------------------|--------------------|
| Hot | [per-message operations] | [nanosecond, zero-alloc] |
| Warm | [periodic operations] | [millisecond] |
| Cold | [setup/recovery operations] | [correctness > speed] |

### System Dimensions

For each dimension, capture: what approach was taken, why (not the naive/default approach), and what breaks if the underlying assumption changes.

#### Data Model

- **Fundamental abstraction:** [log / table / document / key-value / graph / stream / fixed-schema record]
- **Why this model:** [what it optimizes for, what access patterns it enables]
- **What it makes expensive:** [queries/patterns that fight the data model]
- **Redesign trigger:** [if you changed the data model, what else breaks?]

#### Authentication & Security

- **Identity model:** [how identity is established — certs, tokens, shared secret, none]
- **Security boundary location:** [network edge / per-request / per-component / storage layer]
- **Hot path cost:** [zero / TLS handshake / per-request token validation / crypto per write]
- **Trust vs verify tradeoff:** [what is trusted without verification, and why]

#### Memory

- **Memory usage pattern:** [heap / off-heap / mmap / shared memory / direct buffers]
- **Hot path allocation strategy:** [pre-allocated / pooled / arena / zero-allocation]
- **Lifecycle management:** [GC / refcount / arena / manual / RAII]
- **Exhaustion behavior:** [back-pressure / spill to disk / OOM / eviction / degraded mode]
- **Implicit bet:** [what assumption about memory availability must hold]

#### CPU

- **Threading model:** [single-threaded / thread-per-core / thread pool / event loop / dedicated threads]
- **Core scheduling:** [pinning / affinity / work-stealing / OS-managed]
- **CPU-level optimizations:** [cache-line awareness / false sharing prevention / SIMD / prefetch / NUMA]
- **Contention points:** [locks / CAS / shared mutable state / memory barriers]

#### Network

- **Wire protocol:** [TCP / UDP / QUIC / custom] — *why this one?*
- **Critical path round-trips:** [number and what determines the minimum]
- **Serialization approach:** [binary / text / zero-copy / schema-driven / self-describing]
- **Failure modes designed for:** [partition / latency spike / asymmetric failure / reordering]
- **Kernel interaction:** [standard sockets / sendfile / io_uring / DPDK / mmap]

#### Multitenancy

- **Isolation model:** [shared / dedicated / hybrid] — at what granularity?
- **Isolation mechanism:** [process / container / namespace / logical partition / resource pools]
- **Noisy neighbor mitigation:** [rate limits / quotas / fair scheduling / priority queues]
- **First bottleneck under multi-tenant load:** [memory / CPU / I/O / network / connections]

#### Fault Tolerance

- **Handled failure modes:** [node crash / disk failure / network partition / Byzantine / split-brain]
- **Replication strategy:** [sync / async / quorum] — *why?*
- **Consistency guarantee:** [strong / eventual / causal / linearizable] — at what cost?
- **Blast radius:** [one request / one partition / one tenant / whole cluster]
- **What is NOT tolerated:** [failure that brings the system down by design]

#### Deployment

- **Topology:** [single-node / client-server / leader-follower / peer-to-peer / sharded cluster]
- **Hard dependencies:** [JVM / kernel version / hardware / co-located services]
- **Rolling upgrade story:** [supported / version skew tolerance / blue-green / canary]
- **Architecture-shaping constraint:** [what deployment reality most influenced design]

#### Monitoring & Observability

- **Critical health metrics:** [what tells you healthy vs degraded vs broken]
- **Instrumentation approach:** [built-in metrics / logs / traces / eBPF]
- **Easy to observe:** [what the system surfaces well]
- **Hard to observe:** [what requires deep investigation]
- **Predictive signals:** [what to monitor to predict failure before it happens]

#### Recovery

- **Recovery mechanism:** [WAL replay / snapshot + log / rebuild from replica / re-fetch]
- **RTO (recovery time):** [target and what determines it]
- **RPO (data loss window):** [how much can be lost, is it tunable]
- **Determinism:** [deterministic replay or best-effort — can you prove correctness?]
- **Cold start:** [time from zero to serving, and what's the bottleneck]

---

## Phase 3: Design Decisions

### Decision Table

Scan all system dimensions for decisions. Focus on the 3-7 where the system made **non-obvious choices**.

| # | Decision Area | They Chose | Over | Why |
|---|---------------|------------|------|-----|
| 1 | [Data model] | [X] | [Y] | [reasoning] |
| 2 | [Transport / Network] | [X] | [Y] | [reasoning] |
| 3 | [Threading / CPU] | [X] | [Y] | [reasoning] |
| 4 | [Memory] | [X] | [Y] | [reasoning] |
| 5 | [Persistence] | [X] | [Y] | [reasoning] |
| 6 | [Flow Control] | [X] | [Y] | [reasoning] |
| 7 | [Auth / Security] | [X] | [Y] | [reasoning] |
| 8 | [Multitenancy] | [X] | [Y] | [reasoning] |
| 9 | [Fault tolerance] | [X] | [Y] | [reasoning] |
| 10 | [Deployment] | [X] | [Y] | [reasoning] |
| 11 | [Recovery] | [X] | [Y] | [reasoning] |
| 12 | [Observability] | [X] | [Y] | [reasoning] |

### Tradeoff Deep-Dive

#### Decision 1: [Name]

- **Gained:** [performance/correctness/simplicity benefit]
- **Gave up:** [cost, limitation, complexity introduced]
- **Sweet spot:** [workload where this shines]
- **Failure mode:** [workload where this breaks down]
- **Implicit bet:** [assumption that must hold]

**Counterfactual:** "If they had chosen [alternative] instead..."
> [What would change? What would break? What would improve?]

*(Repeat for each major decision)*

---

## Phase 4: Principles Extracted

### Decision → Principle Mapping

| System-Specific Decision | General Principle |
|--------------------------|-------------------|
| [Specific choice] | [Reusable principle name] |
| [Specific choice] | [Reusable principle name] |
| [Specific choice] | [Reusable principle name] |

### Cross-Reference With Other Systems

| Principle | This System | [System X] | [System Y] |
|-----------|-------------|------------|------------|
| [Principle 1] | [How applied here] | [How applied there] | [How applied there] |
| [Principle 2] | [How applied here] | [How applied there] | [How applied there] |

### New Principle Library Entries

**Principle:** [Name]
**Definition:** [One sentence]
**Systems that use it:** [Examples]
**When to apply:** [Conditions]
**When it backfires:** [Anti-conditions]

---

## Phase 5: Validation

### Redesign Exercise

**Altered constraint:** [e.g., "What if memory was limited to 256MB?"]

**What changes:**
- [Component X would need to...]
- [Decision Y would flip to...]

**What stays the same:**
- [Component Z is unaffected because...]

### Architecture Decision Record (ADR)

**Context:** [Problem faced]

**Decision:** [What was chosen and key design elements]

**Consequences:**
- Positive: [What was gained]
- Negative: [What was given up]
- Risks: [What assumptions must hold]

### Feynman Explanation (5-minute version)

1. **The problem (1 min):** [Why this system needed to exist]
2. **What came before (1 min):** [Predecessors and their failures]
3. **The 3 key bets (2 min):** [Core design decisions]
4. **The lesson (1 min):** [Transferable principle]

---

## Sources Used

| Type | Source | What I Learned |
|------|--------|----------------|
| Origin story | [URL/title] | [Key insight] |
| Architecture talk | [URL/title] | [Key insight] |
| Design doc | [URL/title] | [Key insight] |
| Blog post | [URL/title] | [Key insight] |
| Comparison | [URL/title] | [Key insight] |

---

## Personal Notes

[Anything that surprised you, connections to other systems, open questions]
