---
name: system-design-decomposition
description: >-
  Decompose and study any system (Aeron, Kafka, Disruptor, io_uring, RocksDB,
  etc.) from a system design perspective — understanding architecture, core
  components, design decisions, and the principles behind them, without reading
  source code. Use when the user wants to study, learn, analyze, or understand
  a system's architecture, design philosophy, or wants to know why a system
  was designed the way it was.
---

# System Design Decomposition

Structured methodology to understand **any system at the design level** — its components, why they exist, the decisions behind them, and the reusable principles they embody.

**Goal:** Build a transferable mental model of the system, not knowledge of its codebase.

## When to Use

- User asks to "study", "understand", "analyze", or "decompose" a system's design
- User wants to know *why* a system is designed the way it is
- User wants to compare architectural approaches across systems
- User wants to extract reusable design principles from a system
- User is building a personal knowledge base of system design patterns

## Workflow Overview

```
Phase 1: Problem Space        → Why does this system exist?
Phase 2: Architecture Map     → What are the components and data flows?
Phase 3: Design Decisions     → What did they choose X over Y, and why?
Phase 4: Principle Extraction → What reusable principles does this teach?
Phase 5: Validation           → Can I redesign it under different constraints?
```

---

## Phase 1: Problem Space (The "Before" Picture)

Before studying the system itself, understand the **world it was born into**.

### Step 1.1 — Define the Problem Statement

Write one sentence: what pain point triggered this system's creation?

| System | Problem Statement |
|--------|-------------------|
| Aeron | Existing messaging (TCP, JMS, ZeroMQ) adds unacceptable latency and GC pressure for financial-grade IPC/network messaging |
| Disruptor | Java's ArrayBlockingQueue causes lock contention and cache misses at high throughput between producer/consumer threads |
| Kafka | No system efficiently handles persistent, replayable, high-throughput event streaming for both real-time and batch consumers |

### Step 1.2 — Study Predecessors and Their Limitations

Build a comparison table of what came before:

```
| Predecessor      | Strength              | Where It Broke Down             |
|------------------|-----------------------|---------------------------------|
| [System A]       | [What it did well]    | [Why it wasn't good enough]     |
| [System B]       | [What it did well]    | [Why it wasn't good enough]     |
| [System C]       | [What it did well]    | [Why it wasn't good enough]     |
```

### Step 1.3 — Quantify the Performance Target

Find the design goals — throughput, latency, scale parameters:

- What throughput was the system designed for? (msg/sec, requests/sec)
- What latency target? (p50, p99, p999)
- What scale? (concurrent connections, data volume, cluster size)
- What constraints? (zero GC, kernel bypass, single-writer, etc.)
- What are consistency levels target ?
- What are availability targets?

### Where to Find Phase 1 Information

Search for and recommend these sources (in priority order):

1. **Origin blog post or announcement** — usually explains the "why" most clearly
2. **Creator's first conference talk** — first 10 minutes cover problem space
3. **Project README "motivation" section**
4. **Academic paper** (if one exists)
5. **Martin Fowler / InfoQ / ACM Queue articles** about the system

---

## Phase 2: Architecture Map (The Component Diagram)

Map the system's architecture **without reading code**. Build it from documentation and talks.

### Step 2.1 — Identify 4-7 Core Components

Every well-designed system has a small set of core abstractions. Identify them and draw as boxes with relationships.

For each component, answer:

| Question | Purpose |
|----------|---------|
| **What** does it do? (one sentence) | Understand responsibility |
| **Why** does it exist as a separate component? | Understand separation of concerns |
| **What would break** if you removed or merged it? | Understand its necessity |

### Step 2.2 — Trace the Data Flow

Map a single message/request from entry to exit:

```
Producer → [Component A] → [Component B] → [Component C] → Consumer
            what happens?   what happens?    what happens?
            copy? transform? buffer? route? persist?
```

Mark at each boundary:
- Is there a **serialization/deserialization**?
- Is there a **memory copy**?
- Is there a **context switch** (user-space ↔ kernel-space)?
- Is there a **network hop**?
- Is there a **disk I/O**?

### Step 2.3 — Identify Hot Path vs Cold Path

| Path Type | Definition | Optimization Level |
|-----------|------------|--------------------|
| **Hot path** | Per-message/per-request critical path | Nanosecond-optimized, zero-allocation |
| **Warm path** | Periodic operations (batching, flushing) | Millisecond-optimized |
| **Cold path** | Setup, configuration, recovery | Can be slower, correctness > speed |

### Where to Find Phase 2 Information

1. **Architecture docs** (GitHub wiki, `/doc` folder, design docs)
2. **Conference talks with architecture slides** — pause on diagrams, screenshot them
3. **"How X works internally" blog posts** by the team or community
4. **README diagrams**

---

## Phase 3: Design Decisions (The "Chose X over Y" Analysis)

The core of system design understanding. Every high-performance system makes 3-7 **bold, non-obvious choices**.

### Step 3.1 — List Each Decision

Format as "They chose X over Y":

```
| Decision Area      | They Chose...          | Over...                  | Why                                    |
|--------------------|------------------------|--------------------------|----------------------------------------|
| [Transport]        | [chosen approach]      | [rejected alternative]   | [reasoning]                            |
| [Threading model]  | [chosen approach]      | [rejected alternative]   | [reasoning]                            |
| [Memory model]     | [chosen approach]      | [rejected alternative]   | [reasoning]                            |
| [Persistence]      | [chosen approach]      | [rejected alternative]   | [reasoning]                            |
| [Flow control]     | [chosen approach]      | [rejected alternative]   | [reasoning]                            |
```

### Step 3.2 — Analyze Each Tradeoff

For every decision, answer:

1. **What did they gain?** — the performance/correctness/simplicity benefit
2. **What did they give up?** — the cost, limitation, or complexity introduced
3. **Under what workload does this shine?** — the sweet spot
4. **Under what workload does this break down?** — the failure mode
5. **What assumption must hold for this to work?** — the implicit bet

### Step 3.3 — Run the Counterfactual

For each decision, ask: "What if they had chosen the opposite?"

> "If Aeron used TCP instead of UDP + custom reliability:
> Reliable by default, simpler implementation, but kernel buffers add
> latency, can't do multicast, head-of-line blocking during packet loss,
> no control over retransmission timing."

This is the **most powerful learning tool** — it forces you to understand *why* the choice matters.

### Where to Find Phase 3 Information

1. **Design documents, RFCs, ADRs** in the repository
2. **Creator's blog posts** (e.g., Martin Thompson's blog for Aeron/Disruptor)
3. **Conference Q&A sections** — people ask "why not X?" and the creator explains
4. **GitHub issues/discussions** where alternatives were debated
5. **Comparison articles** (e.g., "Aeron vs ZeroMQ" discussions)

---

## Phase 4: Principle Extraction (The Transferable Knowledge)

Generalize from specific decisions to reusable performance principles.

### Step 4.1 — Extract the Principle Behind Each Decision

```
| System Decision                   | General Principle                              |
|-----------------------------------|------------------------------------------------|
| Pre-allocated log buffers (Aeron) | Zero-allocation hot path                       |
| Memory-mapped IPC (Aeron)         | Kernel bypass                                  |
| Append-only log (Kafka)           | Sequential I/O over random I/O                 |
| Single-writer (Disruptor)         | Avoid coordination on the write path           |
| Page cache delegation (Kafka)     | Let the OS do what it's good at                |
```

### Step 4.2 — Cross-Reference Across Known Systems

Build a principle × system matrix. This is the **most valuable artifact**.

```
| Principle                    | System A | System B | System C |
|------------------------------|----------|----------|----------|
| Zero-allocation hot path     | How?     | How?     | How?     |
| Kernel bypass / reduce hops  | How?     | How?     | How?     |
| Mechanical sympathy          | How?     | How?     | How?     |
| Batching / amortization      | How?     | How?     | How?     |
| Back-pressure over buffering | How?     | How?     | How?     |
```

### Step 4.3 — Build a Principle Library Entry

For each new principle discovered, produce:

```
**Principle:** [Name]
**Definition:** [One sentence]
**Systems that use it:** [2-3 examples with how]
**When to apply:** [Conditions where this helps]
**When it backfires:** [Conditions where this hurts]
```

---

## Phase 5: Validation (Prove Your Understanding)

### Step 5.1 — Redesign Under Different Constraints

Change one constraint and redesign:
- "What if this needed to work on a memory-constrained device?"
- "What if this needed strong ordering across 1000 publishers?"
- "What if latency didn't matter but throughput had to 10x?"

Draw the new architecture. Which components change? Which stay?

### Step 5.2 — Write an Architecture Decision Record (ADR)

Write a one-page ADR as if you were the original designer:

```
## Context
[What problem we face]

## Decision
[What we chose and the key design elements]

## Consequences
### Positive
- [What we gain]

### Negative
- [What we give up]

### Risks
- [What assumptions must hold]
```

**If you can write a convincing ADR, you understand the system.**

### Step 5.3 — Explain to a Peer (Feynman Test)

Produce a 5-minute explanation:
1. The problem (1 min)
2. What existed before and why it wasn't enough (1 min)
3. The 3 key design bets (2 min)
4. The principle this teaches (1 min)

---

## Output Format

Use the template in [study-template.md](study-template.md) to produce structured study notes.

For a catalog of well-known systems with recommended starting resources, see [resource-guide.md](resource-guide.md).

## Final Summary

```
Phase 1: Problem Space
  ├── Origin story — blog post, first conference talk
  ├── Provide 2-3 predecessors and their limitations
  └── Write problem statement + performance targets

Phase 2: Architecture
  ├── Watch 2-3 architecture talks, pause on every diagram
  ├── Draw component diagram from memory, verify
  └── Trace hot path end-to-end

Phase 3: Design Decisions
  ├── List all major "chose X over Y" decisions
  ├── Tradeoff analysis for each
  └── Extract principles, update cross-reference table

Phase 4: Validate
  ├── Redesign under altered constraints
  ├── Write the ADR
  └── Write a blog post or teach it to someone
```

## Key Mindset

Before asking: "How does this code work?"

Answer in detail:
- "What problem made someone build this?"
- "What did they try first, and why did it fail?"
- "What are the 3 bets they made, and what breaks if those bets are wrong?"
- "What principle can I steal for my own systems?"

## Important Note

Explain in detail before listing, comparing it. 
Help in building understanding, thinking, true innovation over rote memorization