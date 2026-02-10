# Digital Twin Architecture & Design (MATLAB)

This document summarizes the architecture of the Python interceptor simulation and presents a MATLAB‑native digital twin design. The MATLAB design is not a line‑by‑line translation; it uses MATLAB/Simulink best practices, vectorization, and appropriate toolboxes.

## Findings (Python Architecture Review)

- Fixed‑step simulation loop records time history and runs entity updates then engagement logic.
- Discrete kill‑chain state machine: SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE.
- Entity models:
  - Target follows waypoint guidance with constant speed.
  - Interceptor applies turn‑rate‑limited guidance, max speed, and flight‑time constraints.
  - Sensor provides probabilistic detection, classification confidence, and noisy measurements.
- Guidance laws:
  - Midcourse command guidance with stern‑attack aim‑point blending.
  - Terminal guidance: proportional navigation (PN) or pure pursuit.
- Scenario is YAML‑driven and supports repeatable runs with RNG seeding.
- Visualization is separate from simulation (live animation and post‑run plots).

## MATLAB Digital Twin Architecture (Best Practice)

### 1) Top‑Level Structure
Use a model‑based architecture with clean module boundaries:

```
+sim/
  ScenarioLoader.m
  SimulationRunner.m
  Logging.m
+models/
  TargetModel.m
  InterceptorModel.m
  SensorModel.m
+engagement/
  KillChainStateflow.slx   % or KillChain.m for script‑based
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

### 2) Recommended MATLAB/Simulink Tooling

- **Simulink + Stateflow** for the kill‑chain state machine.
- **Aerospace Toolbox / Aerospace Blockset** for kinematics and navigation if extending beyond 2D.
- **Sensor Fusion and Tracking Toolbox** for higher‑fidelity sensor and tracking models.
- **Control System Toolbox** for guidance law testing.
- **Parallel Computing Toolbox** for Monte Carlo and parameter sweeps.

### 3) Data Model (MATLAB‑Native)
Use struct‑based and vectorized state containers (scales to multiple targets/interceptors):

- `State.pos` (N×2), `State.speed` (N×1), `State.heading` (N×1), `State.active` (N×1)
- Scenario parameter struct from YAML/JSON: `Scenario.target`, `Scenario.interceptor`, etc.
- Logs as `timetable` for time‑stamped analysis.

### 4) Simulation Execution Pattern
Two supported approaches:

**Option A — MATLAB Script Loop**
- Fixed `dt` loop to `tMax`.
- Update sequence:
  1) `TargetModel.step`
  2) `InterceptorModel.step`
  3) `KillChain.step`
- Record to `timetable` each step.

**Option B — Simulink Model**
- Fixed‑step solver.
- Stateflow for kill‑chain.
- MATLAB Function blocks for guidance and sensor logic.
- Simulink Data Inspector for logging.

### 5) Engagement/Kill Chain Design
Implement as Stateflow chart with clear transitions:

- SEARCH → TRACK: detection confirmed.
- TRACK → CLASSIFY: track confirmation threshold met.
- CLASSIFY → LAUNCH: classification confidence crosses threshold.
- LAUNCH → MIDCOURSE: interceptor launched.
- MIDCOURSE → TERMINAL: estimated range ≤ handover threshold.
- TERMINAL → COMPLETE: hit/miss/timeout.

### 6) Sensor & Measurement Modeling

- Detection probability as a function of range.
- Stochastic detection and classification via `rand` / `randn`.
- Noisy measurement in polar space (range/bearing), convert to Cartesian.

For higher fidelity: replace with Sensor Fusion and Tracking Toolbox models and tracking filters.

### 7) Guidance Laws (Vectorized)
Keep guidance laws as standalone functions with vectorized inputs:

- `CommandGuidance` for midcourse (stern‑attack blending).
- `ProNav` for terminal.
- `PurePursuit` fallback.

Vectorization enables multiple interceptors/targets with minimal code changes.

### 8) Logging & Analysis
Use `timetable` for logs and separate analysis scripts:

- `PlotTrajectories` (2D paths, estimated track).
- `PlotTimeline` (phase timeline).
- `SummaryMetrics` (intercept time, final range, handover range, etc.).

### 9) Validation Strategy
To validate the MATLAB twin against the Python system behavior:

- **Parameter parity**: Use identical scenario values.
- **Deterministic checks**: Fixed RNG seed, compare trajectories and timings.
- **Monte Carlo**: Compare distributions of hit/miss, intercept time, and final range.

## Notes on MATLAB‑Native Implementation

- Prefer Stateflow for phase logic rather than a large `switch`/`if` chain.
- Use `timetable` for logs instead of growing arrays.
- Keep models stateless where possible and pass in state structs.
- Encapsulate guidance and sensor math in isolated functions for testing.


