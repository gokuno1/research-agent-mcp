# Performance Audit Report Template

Use the appropriate template based on the audit mode. For **Both Modes**, combine sections from Design and Implementation templates.

---

## Design Mode Report Template

```markdown
# Design Performance Audit: [System / Project Name]

**Date:** YYYY-MM-DD
**Audited by:** AI Performance Audit (Design Mode)
**Scope:** [Full system design / specific subsystem / specific flow]
**Source documents:** [List of design docs, HLD, RFCs reviewed]

## Executive Summary

[2-5 sentences: Can this design meet its stated performance requirements? What are the top blockers?]

**Verdict:** [One of: Design meets requirements / Design likely meets requirements with noted risks / Design has critical gaps that will miss SLA / Design lacks performance requirements — cannot evaluate]

**Top findings:**
1. [Finding 1 — dimension, component, impact, difficulty to change later]
2. [Finding 2]
3. [Finding 3]

---

## 1. Performance Requirements (as stated or inferred)

| Requirement | Value | Source |
|-------------|-------|--------|
| Target throughput | [e.g., 10K requests/sec] | [doc reference] |
| Target p50 latency | [e.g., 50ms] | [doc reference] |
| Target p99 latency | [e.g., 200ms] | [doc reference] |
| Concurrent users/connections | [e.g., 50K] | [doc reference] |
| Data volume | [e.g., 1TB/day ingestion] | [doc reference] |
| Availability SLA | [e.g., 99.95%] | [doc reference] |

**Missing requirements:** [List any critical performance requirements not specified — FLAG THESE]

---

## 2. System Topology

### Components

| Component | Type | Technology (if specified) | Stateful? | Scaling Model |
|-----------|------|--------------------------|-----------|---------------|
| [Name] | [Service/DB/Queue/Cache] | [e.g., PostgreSQL] | Yes/No | [Horizontal/Vertical/N/A] |

### Critical Data Flows

| # | Flow Name | Path | Frequency | Latency Budget |
|---|-----------|------|-----------|----------------|
| F1 | [e.g., Order placement] | Client → GW → OrderSvc → DB → Queue → GW → Client | [e.g., 5K/sec] | [e.g., 100ms p99] |
| F2 | [Name] | [Path] | [Freq] | [Budget] |

---

## 3. Latency Budget Analysis

### Flow: [Flow Name]

| Hop | From → To | Estimated Latency | Budget Allocated | Status |
|-----|-----------|-------------------|------------------|--------|
| 1 | Client → API Gateway | [Xms] | [Yms] | OK / AT RISK / OVER |
| 2 | Gateway → Service A | [Xms] | [Yms] | OK / AT RISK / OVER |
| ... | ... | ... | ... | ... |
| **Total** | | **[Sum]ms** | **[Target]ms** | **PASS / FAIL** |

**Safety margin:** [X]ms remaining ([Y]% of budget)

---

## 4. Findings by Architectural Dimension

### A1: Communication Pattern

| ID | Finding | Components Affected | Impact | Difficulty to Change Later | Priority |
|----|---------|-------------------|--------|---------------------------|----------|
| A1-1 | [Description] | [Components] | High/Med/Low | High/Med/Low | P0/P1/P2/P3 |

**Analysis:** [Why this matters, what happens at scale]

**Recommendation:** [Specific architectural change]

---

[Repeat for A2 through A8, including only dimensions with findings]

---

## 5. Architecture Decision Gaps

Decisions not explicitly made in the design that will affect performance:

| # | Missing Decision | Default If Not Decided | Risk |
|---|-----------------|----------------------|------|
| 1 | [e.g., Serialization format between services] | [e.g., JSON — slowest option] | [Impact] |
| 2 | [e.g., Backpressure strategy for event bus] | [e.g., Unbounded — will OOM under load] | [Impact] |

---

## 6. Prioritized Recommendations

| Priority | Finding ID | Recommendation | Effort | Impact | Must Decide Before |
|----------|-----------|----------------|--------|--------|-------------------|
| P0 | A1-1 | [Change] | [S/M/L] | [Impact] | Implementation starts |
| P0 | A3-2 | [Change] | [S/M/L] | [Impact] | DB schema design |
| P1 | A5-1 | [Change] | [S/M/L] | [Impact] | Queue selection |

### Decisions Needed Before Implementation

1. [Decision + options + recommended choice]
2. [Decision + options + recommended choice]

### Acceptable as Designed (with noted risks)

1. [Component/choice that is OK but has a known ceiling at X scale]

---

## 7. Comparison with Reference Architecture (if applicable)

| Dimension | This Design | [Reference System] | Gap | Remediation |
|-----------|------------|-------------------|-----|-------------|
| A1 | [Pattern] | [Pattern] | [Delta] | [Change needed] |
| A2 | [Pattern] | [Pattern] | [Delta] | [Change needed] |
```

---

## Implementation Mode Report Template

```markdown
# Implementation Performance Audit: [Project Name]

**Date:** YYYY-MM-DD
**Audited by:** AI Performance Audit (Implementation Mode)
**Scope:** [Full codebase / specific module / specific subsystem]

## Executive Summary

[2-5 sentences summarizing the most critical findings and their estimated performance impact]

**Top findings:**
1. [Finding 1 — dimension, location, estimated impact]
2. [Finding 2 — dimension, location, estimated impact]
3. [Finding 3 — dimension, location, estimated impact]

**Overall assessment:** [Critical issues / Significant room for improvement / Moderate optimizations / Well-optimized with minor tuning]

---

## 1. Runtime Context

| Property | Value |
|----------|-------|
| Language / Runtime | [e.g., Java 17, OpenJDK, HotSpot] |
| GC Model | [e.g., G1GC, ZGC, manual, reference counting] |
| Threading Model | [e.g., thread-per-request, event loop, actor model] |
| I/O Model | [e.g., blocking NIO, Netty, io_uring] |
| Build Profile | [e.g., Maven, release with -O2, debug] |
| Deployment | [e.g., Docker container, 4 CPU / 8GB RAM, k8s] |

---

## 2. Hot Path Map

### Primary Hot Paths (per-request / per-message)

| # | Path | Entry Point | Critical Operations | Estimated Frequency |
|---|------|-------------|--------------------|--------------------|
| HP1 | [Name] | [Class.method / function] | [Key operations] | [e.g., 10K/sec] |
| HP2 | [Name] | [Class.method / function] | [Key operations] | [e.g., 5K/sec] |

### Secondary Paths (periodic / batch)

| # | Path | Entry Point | Frequency |
|---|------|-------------|-----------|
| SP1 | [Name] | [Entry] | [e.g., every 30s] |

---

## 3. Findings by Dimension

### D1: Memory Allocation & GC Pressure

| ID | Location | Pattern | Severity | Hot Path | Description |
|----|----------|---------|----------|----------|-------------|
| D1-1 | `File:Line` | [Pattern name] | P0/P1/P2/P3 | HP1 | [Brief description] |

**Evidence:** [Code snippet or metric]

**Recommended fix:** [Concrete change]

**Estimated impact:** [e.g., "Eliminates ~500 allocations/sec on HP1"]

---

[Repeat for D2 through D10, including only dimensions with findings]

---

## 4. Prioritized Action Plan

| Priority | Finding ID | Change | Effort | Expected Impact |
|----------|-----------|--------|--------|-----------------|
| P0 | D1-1 | [Change] | [S/M/L] | [Impact] |
| P1 | D4-1 | [Change] | [S/M/L] | [Impact] |

### Quick Wins (high impact, low effort)

1. [Finding + fix]

### Architectural Changes (high impact, high effort)

1. [Finding + required architectural change]

---

## 5. Comparative Analysis (if applicable)

| Dimension | [System A] | [System B] | Gap |
|-----------|-----------|-----------|-----|
| D1 | [Pattern] | [Pattern] | [Delta] |

**What [System A] must change to match [System B]:**
- [Change 1 — effort: low/medium/high/architectural]

---

## 6. Notes & Caveats

- [Limitations — e.g., no runtime profiling data available]
- [Assumptions — e.g., assumed production traffic of X requests/sec]
- [Areas needing runtime profiling to confirm]
```
