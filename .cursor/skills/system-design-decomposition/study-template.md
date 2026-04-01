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

---

## Phase 3: Design Decisions

### Decision Table

| # | Decision Area | They Chose | Over | Why |
|---|---------------|------------|------|-----|
| 1 | [Transport] | [X] | [Y] | [reasoning] |
| 2 | [Threading] | [X] | [Y] | [reasoning] |
| 3 | [Memory] | [X] | [Y] | [reasoning] |
| 4 | [Persistence] | [X] | [Y] | [reasoning] |
| 5 | [Flow Control] | [X] | [Y] | [reasoning] |

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
