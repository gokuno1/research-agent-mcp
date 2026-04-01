---
name: engineering-system-decomposition
description: >-
  Decompose and study any physical/engineering system (SMPS, turbofan engine,
  ABS braking, PID controller, hydraulic press, PCB layout, etc.) from a
  design-thinking perspective — understanding architecture, core subsystems,
  design decisions, and the principles behind them. Works for electronics,
  mechanical, aerospace, automotive, control systems, power systems, thermal
  systems, and any other engineering domain. Use when the user wants to study,
  learn, analyze, or understand a physical system's design philosophy, or
  wants to know why an engineering system was designed the way it was.
---

# Engineering System Decomposition

Structured methodology to understand **any physical/engineering system at the design level** — its subsystems, why they exist in that form, the decisions behind them, and the reusable principles they embody.

**Goal:** Build a transferable mental model of the system's design logic, not memorization of specifications.

**Applies to:** Electronics, mechanical, aerospace, automotive, power systems, thermal systems, control systems, chemical processes, civil structures — any engineered physical system.

## When to Use

- User asks to "study", "understand", "analyze", or "decompose" a physical engineering system
- User wants to know *why* a system is designed the way it is (not just *what* it does)
- User wants to compare design approaches across systems or domains
- User wants to extract reusable engineering design principles
- User is building cross-domain intuition for engineering problem-solving

## Workflow Overview

```
Phase 1: Problem Space        → What physical problem demanded this system?
Phase 2: Architecture Map     → What are the subsystems, energy/signal flows, and critical paths?
Phase 3: Design Decisions     → What did they choose X over Y, and why?
Phase 4: Principle Extraction → What reusable engineering principle does this teach?
Phase 5: Validation           → Can I redesign it under different constraints?
```

---

## Phase 1: Problem Space (The "Before" Picture)

Before studying the system, understand the **physical reality it was designed to conquer**.

### Step 1.1 — Define the Problem Statement

Write one sentence: what physical limitation or need triggered this system's creation?

| System | Problem Statement |
|--------|-------------------|
| SMPS (Switch-Mode Power Supply) | Linear regulators waste energy as heat proportional to voltage drop, making them impractical for large step-down ratios or battery-powered devices |
| ABS (Anti-lock Braking) | Locked wheels lose static friction and directional control — the driver cannot steer during emergency braking |
| Turbofan engine | Pure turbojets are fuel-inefficient at subsonic speeds because all thrust comes from high-velocity exhaust |
| PID controller | On-off control causes oscillation; open-loop control can't handle disturbances or plant variations |

### Step 1.2 — Study Predecessors and Their Limitations

Build a table of what came before:

```
| Predecessor          | Strength                    | Where It Broke Down                      |
|----------------------|-----------------------------|------------------------------------------|
| [Prior system A]     | [What it did well]          | [Physical limit it hit]                  |
| [Prior system B]     | [What it did well]          | [Physical limit it hit]                  |
| [Prior system C]     | [What it did well]          | [Physical limit it hit]                  |
```

Example for SMPS:

| Predecessor | Strength | Where It Broke Down |
|-------------|----------|---------------------|
| Linear regulator (LM7805) | Simple, low noise, no switching transients | Efficiency = Vout/Vin, wastes (Vin-Vout)×I as heat; can't step up |
| Transformer + rectifier | Can step up/down, galvanic isolation | Large, heavy, only works with AC input, fixed ratio |
| Switched capacitor | No inductor needed, compact | Limited power, fixed integer ratios, poor regulation under load |

### Step 1.3 — Quantify the Design Targets

Find the specification envelope the system was designed to meet:

- **Primary performance metric:** (efficiency, force, speed, bandwidth, precision, temperature range)
- **Operating envelope:** (input range, load range, environmental conditions, duty cycle)
- **Physical constraints:** (size, weight, cost, power budget, material availability)
- **Safety/regulatory requirements:** (safety margins, certifications, failure mode requirements)
- **Lifetime and reliability targets:** (MTBF, cycles to failure, degradation limits)

### Where to Find Phase 1 Information

1. **Textbook introductory chapters** — typically explain why the system exists before explaining how
2. **Patent filings** — the "background of invention" section explicitly states what prior art failed to do
3. **Industry standards documents** (IEEE, SAE, ISO) — define the problem the standard addresses
4. **Historical engineering papers** — trace the evolution of solutions
5. **Application notes from component manufacturers** — often explain *why* this approach over alternatives

---

## Phase 2: Architecture Map (The Subsystem Diagram)

Map the system's architecture by identifying subsystems and tracing flows of **energy, material, signal, and force** — not code.

### Step 2.1 — Identify 4-7 Core Subsystems

Every well-designed engineering system decomposes into a small set of functional blocks. Identify them.

For each subsystem, answer:

| Question | Purpose |
|----------|---------|
| **What** does it do? (one sentence — in terms of energy/signal/material transformation) | Understand physical function |
| **Why** does it exist as a separate subsystem? | Understand separation of physical concerns |
| **What would break** if you removed or merged it with another? | Understand physical necessity |

Example — SMPS (Buck Converter):
```
┌─────────┐    ┌───────────┐    ┌─────────┐    ┌──────────┐
│ Input    │───▶│ Switching │───▶│ Energy  │───▶│ Output   │
│ Filter   │    │ Stage     │    │ Storage │    │ Filter   │
│ (EMI)    │    │ (MOSFET)  │    │ (L + C) │    │ & Load   │
└─────────┘    └─────┬─────┘    └─────────┘    └──────────┘
                     │
               ┌─────▼─────┐
               │ Feedback   │
               │ & Control  │
               │ (PWM loop) │
               └───────────┘
```

### Step 2.2 — Trace the Energy/Signal/Material Flow

Map the primary flow through the system:

```
[Input] → [Stage 1] → [Stage 2] → [Stage 3] → [Output]
           what transforms?  what stores?  what filters?
           what is the energy form at each stage?
```

At each boundary, mark:
- Is there an **energy domain conversion**? (electrical→mechanical, thermal→electrical, chemical→thermal)
- Is there a **signal conversion**? (analog→digital, continuous→discrete, voltage→current)
- Is there **energy storage**? (inductor, capacitor, flywheel, spring, thermal mass, battery)
- Is there an **impedance boundary**? (mechanical coupling, thermal interface, electrical matching)
- Is there a **feedback path**? (sensor→controller→actuator loop)

### Step 2.3 — Identify Critical Path vs Support Path

| Path Type | Definition | Design Priority |
|-----------|------------|-----------------|
| **Critical path** | The main energy/signal/material flow (power stage, load-bearing structure, signal chain) | Optimized for efficiency, speed, or strength |
| **Control path** | Feedback and regulation loops | Optimized for stability, accuracy, response time |
| **Support path** | Protection, cooling, lubrication, filtering, housekeeping | Optimized for reliability, must not interfere with critical path |

### Step 2.4 — System Dimensions Analysis

Every engineering system makes design choices across ten fundamental dimensions. For each, the goal is **not** to list specifications — it's to understand *why the system handles this dimension the way it does*, what alternatives existed, and what physics/economics forced the choice.

#### Signal & Information Representation (≈ Data Model)

- What is the fundamental information carrier? (voltage, current, frequency, pressure, position, optical, chemical concentration)
- Why was *this* representation chosen? (noise immunity, bandwidth, compatibility, simplicity)
- What encoding is used? (analog continuous, PWM, frequency-modulated, digital bus, pneumatic 3-15 PSI)
- What does the signal representation optimize for? What does it sacrifice?
- If you changed the signal domain (e.g., from analog voltage to digital serial), what subsystems would need redesign?

#### Safety, Security & Access Control (≈ Authentication)

- What are the safety-critical failure modes? How are they prevented?
- Where are the safety boundaries? (physical interlocks, emergency stops, thermal cutoffs, pressure relief valves, fuses)
- What is the safety system's cost on normal operation? (added weight, reduced efficiency, slower response, extra components)
- What does the system *trust* without verification vs *actively monitor*? (e.g., assumes supply voltage is clean vs actively filters it)
- What certifications/standards govern the safety design? (UL, CE, SIL, ASIL, MIL-STD)
- How would adding a safety interlock to the critical path change performance?

#### Energy Storage & State (≈ Memory)

- How and where does the system store energy? (inductors, capacitors, batteries, flywheels, springs, pressurized reservoirs, thermal mass)
- What is the energy storage strategy on the critical path? (pre-charged, continuously cycling, buffered, none)
- How is stored energy managed over time? (charge/discharge cycles, self-discharge, hysteresis, aging)
- What happens when energy storage is depleted? (shutdown, graceful degradation, backup source, dangerous failure)
- What is the implicit bet about energy availability? (e.g., "grid power is always present" — what breaks in a blackout?)

#### Processing, Control & Actuation (≈ CPU)

- What is the control architecture? (open-loop, closed-loop PID, cascade, feedforward, model-predictive, neural/adaptive)
- How is the control loop implemented? (analog circuit, microcontroller, PLC, FPGA, mechanical governor, pneumatic logic)
- What is the control bandwidth and update rate? Why is this sufficient (or a bottleneck)?
- Where are the stability concerns? (loop gain margins, phase margins, resonance, oscillation modes)
- How is computation partitioned? (local analog loops for fast response, digital supervisor for complex logic)

#### Communication & Signal Routing (≈ Network)

- How do subsystems communicate? (wires, buses, optical fiber, wireless, pneumatic lines, hydraulic lines, mechanical linkages)
- What protocol or signaling standard? (CAN bus, SPI, I2C, 4-20mA loop, RS-485, HART, fieldbus) *Why this one?*
- How many signal hops for the critical control loop? What determines latency?
- What failure modes are designed for? (broken wire, EMI interference, ground loop, signal reflection, hydraulic leak)
- Where does signal integrity matter most? (high-speed digital, precision analog, safety-critical paths)

#### Resource Sharing & Multi-Use (≈ Multitenancy)

- Are subsystems sharing resources? (common power bus, shared cooling, shared structural members, shared communication bus)
- How is isolation achieved between shared-resource users? (dedicated regulators, thermal barriers, mechanical decoupling, bus arbitration)
- What is the "noisy neighbor" problem? (one subsystem's switching noise corrupting another's analog signal, vibration from motor affecting sensor)
- What breaks first under multi-load stress? (power supply droops, thermal runaway, structural overload, bus saturation)
- If a new load is added to a shared resource, what analysis is required?

#### Fault Tolerance & Redundancy (≈ Fault Tolerance)

- What failure modes are explicitly designed for? (component failure, overload, environmental extremes, wear-out, corrosion)
- What is the redundancy strategy? (hot standby, cold standby, N+1, triple modular redundancy, voting logic)
- What is the fail-safe state? (off, locked position, known-safe configuration, controlled shutdown) *Why that state?*
- What is the blast radius of a single component failure? (one channel, one subsystem, entire system)
- What failure is *not* tolerated by design — and what catastrophic consequence does that imply?
- How does the system handle degraded operation? (limp mode, reduced capability, automatic reconfiguration)

#### Deployment, Installation & Field Conditions (≈ Deployment)

- What is the physical installation context? (factory floor, vehicle, outdoor exposed, cleanroom, undersea, airborne)
- What environmental conditions define the design envelope? (temperature range, humidity, vibration, shock, altitude, corrosive atmosphere)
- What are the hard dependencies? (supply voltage, coolant availability, foundation/mounting, auxiliary systems)
- How is commissioning done? (calibration, alignment, burn-in, acceptance testing)
- What field constraint most influenced the architecture? (e.g., "must fit in existing engine bay" shaped the design of replacement engines)
- How does the system handle upgrades or part replacement in the field?

#### Instrumentation & Condition Monitoring (≈ Monitoring)

- What are the critical parameters that indicate healthy vs degraded vs failing? (temperature, vibration, pressure, voltage, current, position, speed)
- How is the system instrumented? (built-in sensors, test points, diagnostic ports, BIT — built-in test)
- What does the system make easy to observe vs hard to observe? (external temperature easy; internal winding temperature hard)
- How do you distinguish "degraded" from "about to fail" from "normal variation"?
- What predictive/prognostic monitoring exists? (vibration trending, oil analysis, partial discharge detection, thermal imaging)

#### Repair, Reset & Restoration (≈ Recovery)

- What is the repair strategy? (replace component, replace module, replace entire unit, repair in-situ)
- What is the MTTR (mean time to repair)? What determines it? (access difficulty, parts availability, skill required, calibration needed)
- What state is lost during repair/reset? (calibration data, learned parameters, accumulated health data)
- Is the system designed for maintainability? (modular construction, standard interfaces, diagnostic access, keyed connectors to prevent mis-assembly)
- What is the cold-start story? (warm-up time, calibration sequence, break-in period, initial charging)

**Design thinking anchor for all dimensions:** For each, ask — *"What would the simplest/cheapest/textbook approach look like, why does it fail for this application's physics or operating conditions, and what specific constraint forced a different design?"*

### Where to Find Phase 2 Information

1. **Textbook block diagrams and system-level chapters**
2. **Manufacturer application notes and reference designs** — often the best real-world architecture source
3. **Patent drawings** — show subsystem boundaries and flows more clearly than any other source
4. **Industry training materials** (e.g., Bosch automotive training, TI power supply university)
5. **Maintenance manuals and service documentation** — reveal monitoring, recovery, and deployment realities
6. **Failure analysis reports and incident investigations** — reveal actual fault tolerance boundaries

---

## Phase 3: Design Decisions (The "Chose X over Y" Analysis)

The core of design understanding. Every well-engineered system makes 3-7 **bold, non-obvious choices** that define its character.

### Step 3.1 — List Each Decision

Format as "They chose X over Y". Scan all system dimensions:

```
| Decision Area               | They Chose...           | Over...                   | Why (physics/economics)       |
|-----------------------------|-------------------------|---------------------------|-------------------------------|
| Signal representation       | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Energy conversion topology  | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Control architecture        | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Energy storage              | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Material selection          | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Communication / routing     | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Safety strategy             | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Redundancy / fault tolerance| [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Deployment / packaging      | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Recovery / maintainability  | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
| Monitoring / diagnostics    | [chosen approach]       | [rejected alternative]    | [reasoning]                   |
```

Not every system has bold decisions in all areas. Focus on the 3-7 where the system made **non-obvious choices**. But scan all — sometimes the most interesting insight hides where you don't expect it.

### Step 3.2 — Analyze Each Tradeoff

For every decision:

1. **What did they gain?** — the performance, efficiency, reliability, or cost benefit
2. **What did they give up?** — the cost, complexity, weight, or limitation introduced
3. **Under what operating conditions does this shine?** — the sweet spot
4. **Under what conditions does this break down?** — the failure mode or limitation
5. **What physical assumption must hold?** — the implicit bet about the operating environment

### Step 3.3 — Run the Counterfactual

Ask: "What if they had chosen the other option?"

> "If an SMPS used a linear regulator instead of switching topology:
> Simpler, no EMI, no inductor needed, but at 12V→3.3V conversion the
> regulator dissipates 8.7V × I as heat. At 2A that's 17.4W of waste heat
> requiring a large heatsink, making it impractical for portable devices."

> "If ABS used open-loop braking instead of wheel-speed feedback:
> Simpler, cheaper, fewer sensors, but cannot adapt to varying road
> surfaces. On ice, wheels lock instantly; on dry pavement, braking
> force is suboptimal. The fundamental issue is that optimal slip ratio
> varies with surface — you must measure to control."

### Step 3.4 — Identify the Governing Physics

Every engineering design decision ultimately traces back to a **physical law or constraint** that makes one option better than another:

| Decision | Governing Physics |
|----------|-------------------|
| SMPS uses switching vs linear | P_loss = (Vin-Vout) × I — thermodynamics makes linear waste inescapable |
| Turbofan has bypass ratio | Propulsive efficiency ∝ (mass flow × low velocity) vs (low mass × high velocity) — momentum equation |
| ABS modulates brake pressure | Static friction coefficient > kinetic — once the wheel locks, you lose both grip and steering |
| Heat exchanger uses counterflow | ΔT_log is higher in counterflow than parallel flow — second law of thermodynamics |

This is the deepest level of understanding: *which equation made this choice inevitable?*

### Where to Find Phase 3 Information

1. **Design textbooks** with worked examples (not just theory — look for "design procedure" chapters)
2. **Patent claims** — explain what's novel and by implication what alternatives exist
3. **Comparison papers** (e.g., "Buck vs Boost vs Buck-Boost for solar MPPT")
4. **Application notes** where engineers explain *why* they chose a topology/approach
5. **Conference papers** (IEEE, SAE, ASME) — peer-reviewed design rationale
6. **Failure analysis / root cause reports** — reveal what happens when assumptions break

---

## Phase 4: Principle Extraction (The Transferable Knowledge)

Generalize from specific decisions to reusable engineering design principles.

### Step 4.1 — Extract the Principle Behind Each Decision

| System-Specific Decision | General Engineering Principle |
|--------------------------|------------------------------|
| SMPS uses switching + inductor | **Store-and-transfer beats dissipation** — use energy storage elements to move energy efficiently instead of burning excess as heat |
| ABS uses wheel-speed sensors | **Measure the variable you're controlling** — open-loop fails when the plant varies; close the loop around the quantity that matters |
| Turbofan has high bypass ratio | **Move more mass at lower velocity** — for the same thrust, slower exhaust is more fuel-efficient (momentum vs kinetic energy) |
| Bridge uses arch geometry | **Let geometry carry the load** — shape the structure so forces flow as compression, not bending (compression is cheaper per unit strength) |
| Gear reducer trades speed for torque | **Impedance matching** — transform the source characteristics to match the load's needs |

### Step 4.2 — Cross-Reference Across Known Systems

Build a principle × system matrix. This is the **most valuable artifact**.

```
| Principle                        | System A   | System B   | System C   |
|----------------------------------|------------|------------|------------|
| Feedback beats open-loop         | How?       | How?       | How?       |
| Impedance matching               | How?       | How?       | How?       |
| Store-and-transfer > dissipation | How?       | How?       | How?       |
| Separate critical from support   | How?       | How?       | How?       |
| Fail to known-safe state         | How?       | How?       | How?       |
```

### Step 4.3 — Build a Principle Library Entry

For each new principle:

```
**Principle:** [Name]
**Definition:** [One sentence — in terms of physics/engineering]
**Governing law:** [The equation or physical law that makes this true]
**Systems that use it:** [2-3 examples across different domains]
**When to apply:** [Conditions / problem characteristics]
**When it backfires:** [Conditions where this principle hurts]
```

### Step 4.4 — Bridge to Software Systems (Optional)

Many engineering principles have direct analogs in software:

| Engineering Principle | Software Analog |
|----------------------|-----------------|
| Feedback control (PID) | Auto-scaling, adaptive rate limiting |
| Impedance matching | API design, protocol bridging, buffer sizing |
| Fail-safe state | Circuit breaker pattern, graceful degradation |
| Redundancy (N+1) | Replica sets, leader election |
| Filtering (EMI, noise) | Input validation, rate limiting, debouncing |
| Thermal management | Back-pressure, load shedding |
| Modular replacement | Microservices, plug-in architecture |
| Predictive maintenance | Health checks, anomaly detection |

If the user studies both software and physical systems, this cross-domain mapping builds the deepest design intuition.

---

## Phase 5: Validation (Prove Your Understanding)

### Step 5.1 — Redesign Under Different Constraints

Change one constraint and redesign:
- "What if the operating temperature range doubled?"
- "What if weight had to be halved?"
- "What if the power source changed from AC mains to battery?"
- "What if this needed to work on Mars (low pressure, extreme cold, no maintenance)?"

Which subsystems change? Which stay? What new tradeoffs appear?

### Step 5.2 — Write an Engineering Design Rationale (EDR)

Write a one-page document as if you were the original designer proposing this system:

```
## Context
[What physical problem we face and operating constraints]

## Decision
[What architecture we chose and the key subsystem choices]

## Governing Physics
[The 2-3 physical laws/equations that make this architecture the right one]

## Consequences
### Positive
- [What we gain in performance, efficiency, reliability, cost]

### Negative
- [What we give up or make harder]

### Risks
- [What operating assumptions must hold]
```

**If you can write a convincing EDR, you understand the system.**

### Step 5.3 — Explain to a Peer (Feynman Test)

Produce a 5-minute explanation:
1. The physical problem (1 min)
2. What existed before and what physical limit it hit (1 min)
3. The 3 key design bets and the physics behind each (2 min)
4. The transferable principle this teaches (1 min)

---

## Output Format

Use the template in [study-template.md](study-template.md) to produce structured study notes.

For curated starting resources organized by engineering domain, see [resource-guide.md](resource-guide.md).

## Study Schedule (Suggested)

```
Week 1: Problem Space (Phase 1)
  ├── Day 1-2: Origin story — why was this invented, what came before
  ├── Day 3-4: Study 2-3 predecessor systems and their physical limitations
  └── Day 5:   Write problem statement + design targets + governing equations

Week 2: Architecture (Phase 2)
  ├── Day 1-2: Study block diagrams from textbooks, app notes, patents
  ├── Day 3-4: Draw subsystem diagram from memory, verify against sources
  └── Day 5:   Trace energy/signal flow end-to-end, mark every domain crossing

Week 3: Design Decisions (Phase 3)
  ├── Day 1-2: List all major "chose X over Y" decisions
  ├── Day 3:   Tradeoff analysis — identify governing physics for each
  └── Day 4-5: Extract principles, update cross-system table

Week 4: Validate (Phases 4-5)
  ├── Day 1-2: Redesign under altered physical constraints
  ├── Day 3:   Write the EDR
  └── Day 4-5: Explain it to someone or write a blog post
```

## Key Mindset

Stop asking: "What are the specifications of this system?"

Ask instead:
- **"What physical problem made someone invent this?"**
- **"What did they use before, and what law of physics did it violate or waste?"**
- **"What are the 3 bets they made about operating conditions, and what breaks if those bets are wrong?"**
- **"What governing equation made this choice inevitable?"**
- **"What principle can I steal for my own designs — even in a completely different domain?"**

## Important Note

Explain the physics and reasoning in depth before listing specifications.
Help build understanding, intuition, and cross-domain design thinking — not memorization of part numbers and datasheets.
