# Engineering System Resource Guide

Curated starting points for studying well-known engineering systems. Organized by domain. For each system, resources are listed in recommended study order (problem space → architecture → design decisions).

---

## Electronics — Power

### Switch-Mode Power Supply (SMPS — Buck/Boost/Flyback)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Fundamentals of Power Electronics" Ch.1 (Erickson & Maksimović) | Textbook origin |
| Architecture | TI Power Supply Design Seminar topics | Application notes |
| Deep dive | "Erta Power Electronics" YouTube — topology comparisons | Visual walkthrough |
| Design decisions | Comparison: Buck vs Boost vs Buck-Boost vs Flyback for given application | Topology selection |

**Key concepts:** Duty cycle, CCM/DCM boundary, inductor volt-second balance, capacitor charge balance, feedback loop compensation, EMI filtering, thermal derating

### Operational Amplifier Circuits

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "The Art of Electronics" Ch.4 (Horowitz & Hill) | Textbook origin |
| Architecture | TI "Op Amps for Everyone" design reference | Application guide |
| Deep dive | Bob Pease's columns on real-world op-amp behavior | Practitioner wisdom |

**Key concepts:** Virtual short, gain-bandwidth product, slew rate, input offset voltage, CMRR, stability (phase margin), compensation

### ADC / DAC (Analog-Digital Conversion)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Walt Kester: "Data Conversion Handbook" Ch.1-3 (Analog Devices) | Definitive reference |
| Architecture | ADC architecture comparison (SAR vs Sigma-Delta vs Pipeline vs Flash) | Selection guide |
| Deep dive | AN-283: "Sigma-Delta ADCs and DACs" (Analog Devices) | Deep architecture |

**Key concepts:** Quantization noise, oversampling, noise shaping, ENOB, DNL/INL, sampling theorem, aperture jitter, anti-aliasing

---

## Electronics — Digital & Communication

### FPGA vs ASIC Design Tradeoff

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Why FPGAs?" — origin of reconfigurable computing | Historical context |
| Architecture | Xilinx/Intel FPGA architecture white papers | Design docs |
| Deep dive | "FPGA vs ASIC: When to use which" comparison analyses | Decision framework |

**Key concepts:** LUT-based logic, routing fabric, DSP blocks, block RAM, NRE cost vs unit cost crossover, time-to-market, reconfigurability vs power efficiency

### PLL (Phase-Locked Loop)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | "Phaselock Techniques" Ch.1 (Gardner) | Textbook origin |
| Architecture | TI AN-1001: "An Introduction to PLLs" | Application note |
| Deep dive | Banerjee: "PLL Performance, Simulation, and Design" | Deep reference |

**Key concepts:** Phase detector, VCO, loop filter, lock range, capture range, phase noise, jitter, loop bandwidth tradeoff (speed vs noise)

---

## Mechanical — Machines & Mechanisms

### Internal Combustion Engine (4-Stroke)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Heywood: "Internal Combustion Engine Fundamentals" Ch.1-2 | Textbook origin |
| Architecture | How-it-works animations (Animagraffs, Lesics) | Visual architecture |
| Deep dive | SAE papers on engine design optimization | Engineering detail |

**Key concepts:** Otto/Diesel cycle, compression ratio, volumetric efficiency, valve timing (VVT), turbocharging, knock limit, emissions tradeoff, thermal efficiency ceiling (Carnot)

### Gear Train / Transmission

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Shigley's "Mechanical Engineering Design" gear chapters | Textbook origin |
| Architecture | Gear type comparison (spur, helical, bevel, planetary, worm) | Selection guide |
| Deep dive | Planetary gear kinematics and torque analysis | Deep mechanics |

**Key concepts:** Gear ratio, torque multiplication, efficiency per stage, backlash, contact ratio, Lewis bending stress, Hertzian contact stress, lubrication regimes

### Bearing Selection & Design

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | SKF Bearing Handbook — selection process | Industry reference |
| Architecture | Bearing type comparison (ball, roller, needle, thrust, journal, magnetic) | Selection guide |
| Deep dive | L10 life calculation, lubrication theory | Design procedure |

**Key concepts:** L10 life, dynamic load rating, speed limit (DN value), preload, clearance, lubrication film thickness, failure modes (spalling, cage failure, brinelling)

---

## Mechanical — Thermal & Fluid

### Heat Exchanger Design

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Incropera: "Fundamentals of Heat and Mass Transfer" Ch.11 | Textbook origin |
| Architecture | Shell-and-tube vs plate vs finned-tube vs microchannel comparison | Topology selection |
| Deep dive | LMTD method, effectiveness-NTU method, fouling factors | Design methods |

**Key concepts:** Counterflow vs parallel flow, LMTD, NTU-effectiveness, overall heat transfer coefficient, fouling resistance, pressure drop tradeoff, fin efficiency

### Hydraulic System (Industrial / Mobile)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Esposito: "Fluid Power with Applications" Ch.1-3 | Textbook origin |
| Architecture | Hydraulic circuit diagrams (ISO 1219 symbols) | Standardized notation |
| Deep dive | Proportional/servo valve design, load-sensing pump control | Advanced control |

**Key concepts:** Pascal's law, pressure-flow characteristics, valve types (directional, pressure, flow), pump types (gear, vane, piston), accumulator, servo/proportional control, cavitation, filtration

---

## Aerospace

### Turbofan Engine

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Mattingly: "Elements of Propulsion" Ch.1-3 | Textbook origin |
| Architecture | GE/Rolls-Royce engine cutaway diagrams and explanations | Visual architecture |
| Deep dive | Brayton cycle analysis, bypass ratio optimization | Thermodynamic detail |

**Key concepts:** Brayton cycle, bypass ratio, specific thrust vs specific fuel consumption, compressor surge, turbine cooling, FADEC control, thrust-specific fuel consumption

### Flight Control System

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | McLean: "Automatic Flight Control Systems" Ch.1 | Textbook origin |
| Architecture | Fly-by-wire architecture (Airbus A320 case study) | Design case study |
| Deep dive | Redundancy management, dissimilar redundancy, flight envelope protection | Safety architecture |

**Key concepts:** Fly-by-wire, triple/quad redundancy, dissimilar hardware/software, flight envelope protection, control law scheduling, sensor fusion, DO-178C certification

---

## Automotive

### Anti-Lock Braking System (ABS)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Bosch Automotive Handbook — ABS chapter | Industry reference |
| Architecture | ABS hydraulic modulator + ECU block diagram | System architecture |
| Deep dive | Slip ratio control algorithm, wheel speed estimation | Control detail |

**Key concepts:** Slip ratio, static vs kinetic friction, wheel speed sensors, hydraulic modulator (hold-apply-release), control cycle time, road surface adaptation

### Electric Vehicle Battery Management System (BMS)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Andrea: "Battery Management Systems for Large Lithium-Ion Battery Packs" | Textbook origin |
| Architecture | BMS architecture: cell monitoring, balancing, thermal management, SOC estimation | System architecture |
| Deep dive | Cell balancing (passive vs active), SOC estimation methods (Coulomb counting, EKF, EIS) | Design methods |

**Key concepts:** Cell balancing, state of charge (SOC), state of health (SOH), thermal runaway protection, precharge circuit, contactor control, isolation monitoring

---

## Control Systems

### PID Controller

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Åström & Murray: "Feedback Systems" Ch.1-2 | Textbook origin |
| Architecture | PID block diagram, anti-windup, derivative filtering | Standard structure |
| Deep dive | Tuning methods (Ziegler-Nichols, relay auto-tune, model-based) | Design procedure |

**Key concepts:** Proportional-integral-derivative action, tuning, anti-windup, derivative kick, bumpless transfer, cascade control, gain scheduling

### Industrial PLC / SCADA System

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Bolton: "Programmable Logic Controllers" Ch.1-2 | Textbook origin |
| Architecture | PLC system architecture (CPU, I/O modules, fieldbus, HMI, SCADA pyramid) | System architecture |
| Deep dive | IEC 61131-3 programming languages, safety PLCs (SIL-rated), redundancy | Standards & safety |

**Key concepts:** Scan cycle, I/O scanning, ladder logic, function block, fieldbus (Profinet, EtherNet/IP), safety integrity level (SIL), redundant CPU, watchdog

---

## Power Systems

### Three-Phase Transformer

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Chapman: "Electric Machinery Fundamentals" Ch.2-3 | Textbook origin |
| Architecture | Core geometry (core-type, shell-type), winding configurations (Δ-Y, Y-Y, etc.) | Design choices |
| Deep dive | Equivalent circuit, losses (copper, core), efficiency, voltage regulation | Design procedure |

**Key concepts:** Turns ratio, magnetizing current, leakage reactance, core losses (hysteresis + eddy current), copper losses, cooling methods (ONAN, ONAF, OFAF), tap changer

### Variable Frequency Drive (VFD)

| Phase | Resource | Type |
|-------|----------|------|
| Problem space | Mohan: "Power Electronics" Ch. on motor drives | Textbook origin |
| Architecture | VFD block diagram (rectifier → DC bus → inverter → motor) | System architecture |
| Deep dive | V/f control, vector control (FOC), space vector modulation | Control strategies |

**Key concepts:** Rectifier, DC bus, IGBT inverter, PWM modulation, V/f ratio, field-oriented control (FOC), regenerative braking, harmonic distortion, motor derating

---

## Cross-Domain Principle Index

Quick lookup: which systems demonstrate which principle.

| Principle | Systems |
|-----------|---------|
| **Feedback beats open-loop** | PID controller, ABS, PLL, SMPS (voltage regulation), BMS (SOC estimation) |
| **Impedance matching** | Transformer (turns ratio), gear train (torque matching), antenna matching network, audio amplifier output stage |
| **Store-and-transfer > dissipation** | SMPS (inductor), hydraulic accumulator, flywheel energy storage, regenerative braking |
| **Fail to known-safe state** | ABS (release pressure), flight control (revert to direct law), nuclear reactor (SCRAM = gravity drops rods), VFD (safe torque off) |
| **Redundancy for critical functions** | Fly-by-wire (triple/quad), BMS (redundant contactors), hydraulic brakes (dual circuit), PLC (redundant CPU) |
| **Separate critical from support path** | Engine (power vs cooling vs lubrication), SMPS (power stage vs control), aircraft (flight controls vs cabin systems) |
| **Move more mass at lower velocity** | Turbofan (high bypass), hydraulic press (high force from low-velocity fluid), gear reducer (speed→torque) |
| **Let geometry carry the load** | Arch bridge, pressure vessel (cylindrical shape), I-beam (bending), turbine blade airfoil |
| **Measure the variable you're controlling** | ABS (wheel speed for slip), PLL (phase for frequency), thermocouple in heat exchanger, current sensor in VFD |
| **Counterflow > parallel flow** | Heat exchanger, distillation column, catalytic converter with thermal recovery |
| **Trade spatial for temporal complexity** | Sigma-Delta ADC (oversampling trades time for resolution), PWM (time-domain encoding of amplitude) |
| **Modular replacement for field repair** | LRU (line replaceable unit) in aerospace, plug-in PLC I/O modules, cartridge fuse, modular BMS slave boards |
