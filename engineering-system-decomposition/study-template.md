# Engineering System Study Template

Copy this template when studying a new physical/engineering system. Fill in each section following the phases in SKILL.md.

---

## System: [Name]

**One-line summary:** [What this system does — in terms of physical transformation — in one sentence]

**Domain:** [Electronics | Mechanical | Aerospace | Automotive | Power Systems | Thermal | Control Systems | Chemical Process | Civil/Structural | Other]

**Invented/Developed by:** [Person/Organization]

**Origin era:** [Decade or year of first practical implementation]

---

## Phase 1: Problem Space

### Problem Statement

> [One sentence: what physical limitation or need triggered this system's creation?]

### Design Targets

| Metric | Target |
|--------|--------|
| Primary performance metric | [efficiency %, force N, speed rpm, bandwidth Hz, precision mm, etc.] |
| Operating envelope | [input range, load range, temperature, pressure, speed range] |
| Physical constraints | [size, weight, cost, power budget] |
| Safety / regulatory | [standards, certifications, safety margins] |
| Lifetime / reliability | [MTBF, cycles, degradation limits] |

### Predecessor Analysis

| Predecessor | Strength | Physical Limit It Hit |
|-------------|----------|-----------------------|
| [System A] | [What it did well] | [Why physics/economics made it insufficient] |
| [System B] | [What it did well] | [Why physics/economics made it insufficient] |
| [System C] | [What it did well] | [Why physics/economics made it insufficient] |

### Key Insight That Enabled This System

> [What new idea, technique, material, or shift in thinking made this system possible?]

### Governing Equations

| Equation | What It Governs | Why It Matters to This System |
|----------|-----------------|-------------------------------|
| [equation] | [physical relationship] | [how it constrains or enables the design] |
| [equation] | [physical relationship] | [how it constrains or enables the design] |

---

## Phase 2: Architecture

### Subsystem Diagram

```
[Draw the 4-7 core subsystems and their relationships]
[Show energy, signal, and material flows with arrows]
[Mark domain crossings (electrical↔mechanical, thermal↔electrical, etc.)]
```

### Subsystem Inventory

| Subsystem | Physical Function (one sentence) | Why It's Separate | What Breaks If Removed |
|-----------|----------------------------------|-------------------|------------------------|
| [Sub A] | | | |
| [Sub B] | | | |
| [Sub C] | | | |
| [Sub D] | | | |

### Energy / Signal / Material Flow (Critical Path)

```
[Input] → [Stage 1] → [Stage 2] → [Stage 3] → [Output]
           energy form?  conversion?   storage?
           signal type?   domain crossing?
```

**Energy domain crossings:** [list where energy changes form]

**Signal conversions:** [list where signal representation changes]

**Energy storage points:** [list where energy is buffered]

**Impedance boundaries:** [list where matching or coupling occurs]

**Feedback loops:** [list sensor→controller→actuator paths]

### Critical / Control / Support Path Classification

| Path | Example Operations | Design Priority |
|------|-------------------|-----------------|
| Critical | [main energy/material flow] | [efficiency, speed, strength] |
| Control | [feedback and regulation] | [stability, accuracy, response time] |
| Support | [protection, cooling, filtering] | [reliability, must not interfere with critical path] |

### System Dimensions

For each dimension, capture: what approach was taken, why the naive/default approach was insufficient, and what breaks if assumptions change.

#### Signal & Information Representation

- **Information carrier:** [voltage / current / frequency / pressure / position / optical / chemical]
- **Why this representation:** [noise immunity, bandwidth, compatibility, simplicity]
- **Encoding:** [analog continuous / PWM / frequency-modulated / digital bus / pneumatic]
- **What it sacrifices:** [bandwidth, resolution, noise tolerance, complexity]

#### Safety, Security & Access Control

- **Safety-critical failure modes:** [what can go wrong that's dangerous]
- **Safety boundaries:** [interlocks / emergency stops / thermal cutoffs / relief valves / fuses]
- **Cost on normal operation:** [added weight / reduced efficiency / extra components]
- **Trust vs verify:** [what is assumed safe vs actively monitored]
- **Governing standards:** [UL / CE / SIL / ASIL / MIL-STD / other]

#### Energy Storage & State

- **Storage elements:** [inductors / capacitors / batteries / flywheels / springs / pressurized vessels / thermal mass]
- **Critical path strategy:** [pre-charged / continuously cycling / buffered / none]
- **Lifecycle management:** [charge-discharge cycles / self-discharge / aging / hysteresis]
- **Exhaustion behavior:** [shutdown / degraded mode / backup source / dangerous failure]
- **Implicit bet:** [what energy availability assumption must hold]

#### Processing, Control & Actuation

- **Control architecture:** [open-loop / PID / cascade / feedforward / model-predictive / adaptive]
- **Implementation:** [analog circuit / microcontroller / PLC / FPGA / mechanical governor / pneumatic]
- **Bandwidth & update rate:** [frequency, and why sufficient or a bottleneck]
- **Stability concerns:** [gain margin / phase margin / resonance / oscillation modes]

#### Communication & Signal Routing

- **Communication medium:** [wires / buses / optical / wireless / pneumatic / hydraulic / mechanical linkage]
- **Protocol / standard:** [CAN / SPI / I2C / 4-20mA / RS-485 / HART / fieldbus] — *why?*
- **Critical loop latency:** [hops and what determines delay]
- **Failure modes designed for:** [broken wire / EMI / ground loop / reflection / leak]

#### Resource Sharing & Multi-Use

- **Shared resources:** [power bus / cooling / structure / communication bus]
- **Isolation mechanism:** [dedicated regulators / thermal barriers / mechanical decoupling / bus arbitration]
- **Noisy neighbor problem:** [switching noise / vibration / thermal coupling / bus contention]
- **First bottleneck under multi-load stress:** [power droop / thermal runaway / structural overload]

#### Fault Tolerance & Redundancy

- **Handled failure modes:** [component failure / overload / environmental extremes / wear-out / corrosion]
- **Redundancy strategy:** [hot standby / cold standby / N+1 / TMR / voting] — *why?*
- **Fail-safe state:** [off / locked / known-safe position / controlled shutdown]
- **Blast radius:** [one channel / one subsystem / entire system]
- **Degraded operation:** [limp mode / reduced capability / automatic reconfiguration]

#### Deployment, Installation & Field Conditions

- **Installation context:** [factory / vehicle / outdoor / cleanroom / undersea / airborne]
- **Environmental envelope:** [temperature / humidity / vibration / shock / altitude / corrosion]
- **Hard dependencies:** [supply voltage / coolant / foundation / auxiliary systems]
- **Architecture-shaping field constraint:** [what installation reality most influenced design]

#### Instrumentation & Condition Monitoring

- **Critical health parameters:** [temperature / vibration / pressure / voltage / current / position]
- **Instrumentation approach:** [built-in sensors / test points / diagnostic ports / BIT]
- **Easy to observe:** [what the system surfaces well]
- **Hard to observe:** [what requires special equipment or disassembly]
- **Predictive signals:** [vibration trending / oil analysis / partial discharge / thermal imaging]

#### Repair, Reset & Restoration

- **Repair strategy:** [replace component / replace module / replace unit / repair in-situ]
- **MTTR and determinants:** [access difficulty / parts availability / skill required / calibration]
- **State lost during repair:** [calibration data / learned parameters / health history]
- **Maintainability design:** [modular construction / standard interfaces / keyed connectors]
- **Cold start:** [warm-up time / calibration sequence / break-in period]

---

## Phase 3: Design Decisions

### Decision Table

Scan all system dimensions. Focus on the 3-7 where the system made **non-obvious choices**.

| # | Decision Area | They Chose | Over | Why (Physics/Economics) |
|---|---------------|------------|------|-------------------------|
| 1 | [Signal representation] | [X] | [Y] | [reasoning] |
| 2 | [Energy topology] | [X] | [Y] | [reasoning] |
| 3 | [Control architecture] | [X] | [Y] | [reasoning] |
| 4 | [Material/Energy storage] | [X] | [Y] | [reasoning] |
| 5 | [Safety strategy] | [X] | [Y] | [reasoning] |
| 6 | [Redundancy] | [X] | [Y] | [reasoning] |
| 7 | [Deployment/Packaging] | [X] | [Y] | [reasoning] |

### Tradeoff Deep-Dive

#### Decision 1: [Name]

- **Gained:** [performance / efficiency / reliability / cost benefit]
- **Gave up:** [cost, complexity, weight, limitation introduced]
- **Sweet spot:** [operating conditions where this shines]
- **Failure mode:** [conditions where this breaks down]
- **Implicit bet:** [physical assumption that must hold]
- **Governing equation:** [the physics that makes this choice inevitable]

**Counterfactual:** "If they had chosen [alternative] instead..."
> [What would change physically? What would break? What would improve?]

*(Repeat for each major decision)*

---

## Phase 4: Principles Extracted

### Decision → Principle Mapping

| System-Specific Decision | General Engineering Principle | Governing Law |
|--------------------------|------------------------------|---------------|
| [Specific choice] | [Reusable principle name] | [Physical law] |
| [Specific choice] | [Reusable principle name] | [Physical law] |
| [Specific choice] | [Reusable principle name] | [Physical law] |

### Cross-Reference With Other Systems

| Principle | This System | [System X] | [System Y] |
|-----------|-------------|------------|------------|
| [Principle 1] | [How applied here] | [How applied there] | [How applied there] |
| [Principle 2] | [How applied here] | [How applied there] | [How applied there] |

### New Principle Library Entries

**Principle:** [Name]
**Definition:** [One sentence — in terms of physics/engineering]
**Governing law:** [Equation or physical law]
**Systems that use it:** [Examples across domains]
**When to apply:** [Conditions]
**When it backfires:** [Anti-conditions]

### Software Analog (Optional)

| Engineering Principle | Software Analog | Why the Same Logic Applies |
|----------------------|-----------------|---------------------------|
| [Principle] | [Software pattern] | [Shared underlying constraint] |

---

## Phase 5: Validation

### Redesign Exercise

**Altered constraint:** [e.g., "What if operating temperature range doubled?"]

**What changes:**
- [Subsystem X would need to...]
- [Decision Y would flip to...]

**What stays the same:**
- [Subsystem Z is unaffected because...]

### Engineering Design Rationale (EDR)

**Context:** [Physical problem and operating constraints]

**Decision:** [Architecture chosen and key subsystem choices]

**Governing Physics:** [2-3 equations that make this the right architecture]

**Consequences:**
- Positive: [What was gained]
- Negative: [What was given up]
- Risks: [What operating assumptions must hold]

### Feynman Explanation (5-minute version)

1. **The physical problem (1 min):** [Why this system needed to exist]
2. **What came before (1 min):** [Predecessors and the physical limits they hit]
3. **The 3 key bets (2 min):** [Core design decisions and the physics behind each]
4. **The lesson (1 min):** [Transferable principle, ideally cross-domain]

---

## Sources Used

| Type | Source | What I Learned |
|------|--------|----------------|
| Textbook | [Title/chapter] | [Key insight] |
| Patent | [Patent number/title] | [Key insight] |
| Application note | [Manufacturer/title] | [Key insight] |
| Conference paper | [Title/venue] | [Key insight] |
| Training material | [Source] | [Key insight] |

---

## Personal Notes

[Anything that surprised you, connections to other domains, open questions, ideas for projects]
