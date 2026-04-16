# Your Design Thinking Profile

Generated from the Order Matching Engine session (2026-04-08).
Update this file as you practice more systems.

## Strengths

1. **Correct high-level instincts** — you reach for the right general direction
   (BST for sorted data, separate threads for validation, multi-core for scaling).
   The issue is stopping before stress-testing the instinct.

2. **Honest about gaps** — you say "pass" or "I'm overwhelmed" instead of
   guessing. This is genuinely valuable in interviews — it invites collaboration.

3. **Receptive to correction** — when shown why an answer is wrong, you
   integrate it quickly and don't repeat the mistake.

## Anti-Patterns (Priority Order)

### 1. Solution-First (highest priority)
**What happens:** You name a technology before understanding what constraint
forces you toward it.
**Seen in:** "fast database" (no budget check), "Disruptor pattern" (no
single-thread derivation), "FIX gap fill" (wrong problem entirely)

**Drill:** Before proposing anything, complete:
"I need **[property]** because **[constraint]**, and **[solution]** provides
that because **[mechanism]**."

### 2. Missing Constraint Math
**What happens:** You don't convert requirements into numbers that kill options.
**Seen in:** Didn't compute 200ns budget, didn't check if database fits.

**Drill:** First thing for any problem:
"[requirement] = [X ns/bytes/ops per unit]. This eliminates: [list]."

### 3. Incomplete Trace-Through
**What happens:** You get the first step right but don't follow the chain.
**Seen in:** Identified first match but didn't track quantities through.

**Drill:** After every answer: "What happens NEXT? Follow the chain to
termination."

### 4. Narrow Framing
**What happens:** You see the primary actor but miss secondary ones.
**Seen in:** Buyer/seller but not market data, clearing, regulators.

**Drill:** For any event, list four categories:
- Direct participants, Observers, Controllers, Auditors

### 5. Abstraction Gap
**What happens:** You can describe operations but can't bridge to structural
requirements.

**What works for you:** The "start dumb, fix one thing" method. Don't try to
derive properties abstractly — build from concrete broken things.

## Systems Practiced

| System | Date | Key Lesson Learned | Patterns Observed |
|--------|------|--------------------|-------------------|
| Order Matching Engine | 2026-04-08 | Constraint math eliminates options instantly. Single-thread beats multi-thread when shared mutable state is the bottleneck. | All 5 anti-patterns active |

## Systems to Practice Next

### Low-Level (builds memory-layout thinking)
- **malloc / free** — forces you to think in bytes, alignment, fragmentation
- **LRU Cache** — bridges data structures and systems thinking
- **HashSet** — probe sequences, load factors, collision strategies

### Distributed (builds failure-mode thinking)
- **Kafka** — reuses many matching engine principles (append-only log, partitioning)
- **Distributed Cache** — consistency vs availability tension

### Hardware (builds physical-constraint thinking)
- **PCI Express** — protocol layers, bandwidth vs latency, backward compatibility
- **Cache Coherence (MESI)** — directly connects to matching engine's mechanical sympathy

### AI/ML (builds compute-bottleneck thinking)
- **Model Inference Server** — batching, precision, GPU memory management
- **Distributed Training** — data vs model parallelism, communication bottlenecks

For each: don't read the standard answer first. Start from the contract
(what does it promise?) and derive the design.
