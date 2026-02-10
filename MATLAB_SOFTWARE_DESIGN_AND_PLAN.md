# MATLAB Digital Twin: Software Design Document and Plan

This document describes the software design and implementation plan for a MATLAB‑native digital twin of the interceptor engagement simulator. It is intended to guide development before substantial MATLAB coding begins.

## 1) Scope and Goals

**Goal:** Implement a MATLAB digital twin that reproduces the *system‑level behaviors* of the Python simulator (kill chain phases, guidance logic outcomes, and engagement metrics) using MATLAB/Simulink best practices rather than a line‑by‑line translation.

**In scope**
- 2D kinematic target and interceptor dynamics.
- Kill chain state machine with SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE.
- Sensor detection/classification and noisy measurement models.
- Guidance laws: midcourse command guidance, terminal PN and pure pursuit.
- Repeatable simulation runs via scenario configuration and RNG seeding.
- Logging, analysis plots, and summary metrics.

**Out of scope (initial release)**
- 3D dynamics, wind, or high‑fidelity aerodynamics.
- Multiple simultaneous interceptors/targets (design allows for it).
- Real‑time HW‑in‑the‑loop integration.

## 2) System Overview

The digital twin is composed of:

- **Scenario Loader**: Reads YAML/JSON/structs into MATLAB configuration structs.
- **Simulation Runner**: Fixed‑step loop (or Simulink fixed‑step model) coordinating updates.
- **Models**: Target, Interceptor, Sensor.
- **Engagement Logic**: Kill chain state machine, detection/classification logic, and phase transitions.
- **Guidance Laws**: Midcourse command guidance, terminal PN / pure pursuit.
- **Logging & Analysis**: Timetables, plots, KPI extraction.

## 3) Architecture

### 3.1 Folder / Package Structure

```
matlab/
  +sim/
    ScenarioLoader.m
    SimulationRunner.m
    Logging.m
  +models/
    TargetModel.m
    InterceptorModel.m
    SensorModel.m
  +engagement/
    KillChainStateflow.slx   % or KillChain.m for script-based
    DetectionLogic.m
    ClassificationLogic.m
  +guidance/
    CommandGuidance.m
    ProNav.m
    PurePursuit.m
  +analysis/
    PlotTrajectories.m
    PlotTimeline.m
    SummaryMetrics.m
```

### 3.2 Data Model

**Scenario struct**
- `Scenario.target`: position, speed, waypoints, rcs.
- `Scenario.surveillanceSensor`: max range, FoR, Pd, noise.
- `Scenario.interceptor`: position, max speed, max turn rate, seeker, kill radius, max flight time.
- `Scenario.engagement`: terminal guidance, nav gain, handover range, stern offset, blend range.
- `Scenario.simulation`: dt, max time, seed.

**State struct (vector‑ready)**
- `pos` (N×2), `speed` (N×1), `heading` (N×1), `active` (N×1)
- For extensibility, use array‑based state instead of scalar objects.

**History (timetable)**
- `Time`, `TargetPos`, `InterceptorPos`, `Phase`, `EstTargetPos`, `EstTargetVel`, `Result`

### 3.3 Execution Flow

**Option A — MATLAB Script Loop (initial target)**
1) Load scenario.
2) Initialize models and engagement logic.
3) For `t = 0:dt:tMax`:
   - Update target.
   - Update interceptor.
   - Update kill chain and guidance.
   - Record to history.

**Option B — Simulink + Stateflow (later enhancement)**
- Stateflow chart for kill chain.
- MATLAB Function blocks for guidance and measurement.
- Fixed‑step solver, Data Inspector logging.

## 4) Component Design

### 4.1 ScenarioLoader
**Inputs:** YAML/JSON file or struct.  
**Outputs:** `Scenario` struct with defaults applied.  
**Notes:** Use `readstruct` for YAML/JSON if available; otherwise a small parser.

### 4.2 TargetModel
**State:** position, heading, speed, waypoint list, current waypoint index.  
**Methods:** `init`, `step(dt)`, `hasReachedFinalWaypoint`.  
**Behavior:** update heading toward current waypoint; advance if within threshold.

### 4.3 InterceptorModel
**State:** position, heading, speed, flight time, state (READY/LAUNCHED/TERMINAL/MISSED/DETONATED).  
**Methods:** `launch`, `applyGuidance`, `step(dt)`, `checkIntercept`.  
**Behavior:** turn‑rate limiting, max flight time enforcement.

### 4.4 SensorModel
**State:** max range, FoR, Pd model, noise parameters.  
**Methods:** `tryDetect`, `tryClassify`, `measure`.  
**Behavior:** probabilistic detection/classification; Gaussian noise in range/bearing/speed/heading.

### 4.5 Engagement / Kill Chain
**State machine:** SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE  
**Transitions:**  
- SEARCH → TRACK: detection confirmed.  
- TRACK → CLASSIFY: track confirmation threshold met.  
- CLASSIFY → LAUNCH: classification confidence ≥ threshold.  
- LAUNCH → MIDCOURSE: interceptor launched.  
- MIDCOURSE → TERMINAL: estimated range ≤ handover range.  
- TERMINAL → COMPLETE: hit/miss/timeout.

**Artifacts:** Stateflow chart (preferred) or MATLAB function with `switch/case`.

### 4.6 Guidance Laws
- **CommandGuidance**: midcourse bearing command, stern‑attack blending.
- **ProNav**: proportional navigation for terminal phase.
- **PurePursuit**: fallback terminal law.

All guidance laws accept vectorized inputs where possible.

### 4.7 Logging & Analysis
- Use `timetable` for state history.
- Analysis functions generate:
  - Trajectory plot.
  - Range‑over‑time plot.
  - Phase timeline plot.
  - Summary metrics.

## 5) Toolboxes and MATLAB Best Practices

- **Stateflow** for kill chain logic.
- **Simulink** (fixed‑step) if model‑based execution is desired.
- **Sensor Fusion and Tracking Toolbox** for higher‑fidelity sensor models (optional).
- **Parallel Computing Toolbox** for Monte Carlo sweeps.
- Use vectorized state arrays and `timetable` logs.

## 6) Interfaces

### 6.1 Scenario Input
Accept a scenario YAML/JSON or MATLAB struct equivalent to Python’s example:
- target, surveillance sensor, interceptor, engagement, simulation.

### 6.2 Outputs
- `history` timetable with positions, estimates, phase, and result.
- Plots and summary metrics.

## 7) Verification and Validation

**Deterministic parity**
- Use fixed seed and compare trajectory shape, phase timings, and final result.

**Statistical parity**
- Compare hit/miss rate distributions across Monte Carlo runs.

**Unit tests**
- Guidance functions, sensor detection probability, state transitions.

## 8) Implementation Plan

### Phase 0 — Setup (1–2 days)
- Create MATLAB folder/package structure.
- Add `ScenarioLoader` and `SimulationRunner` stubs.
- Define scenario and state structs.

### Phase 1 — Core Models (3–5 days)
- Implement `TargetModel`, `InterceptorModel`, `SensorModel`.
- Add geometry helpers (bearing, distance, wrap).
- Unit tests for model updates.

### Phase 2 — Engagement Logic (3–5 days)
- Implement kill chain state machine (Stateflow or MATLAB function).
- Implement detection/classification logic.
- Validate phase transitions with a deterministic scenario.

### Phase 3 — Guidance (2–3 days)
- Implement command guidance, PN, pure pursuit.
- Validate against expected trajectories and terminal behavior.

### Phase 4 — Logging & Analysis (2–3 days)
- Add `timetable` logging.
- Implement plots and summary metrics.

### Phase 5 — Verification (2–4 days)
- Deterministic regression vs Python scenario.
- Monte Carlo comparison on key metrics.

## 9) Risks and Mitigations

- **State machine complexity**: Use Stateflow for traceability and testing.
- **Non‑determinism**: Centralize RNG seeding and usage.
- **Performance**: Use vectorization and preallocation; use `parfor` for sweeps.
- **Scope creep**: Keep 2D kinematics for initial release.

## 10) Deliverables

- MATLAB source in `matlab/` packages.
- Simulink/Stateflow model (if used).
- Test scripts and example scenarios.
- Analysis plots and summary metrics.


