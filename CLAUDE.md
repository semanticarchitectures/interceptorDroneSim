# Interceptor Drone Simulation

## Project Overview
Counter-UAS interceptor engagement simulation modeling the full kill chain: detection → classification → launch → midcourse guidance → sensor handover → terminal guidance → intercept. 2D kinematic fidelity with live visualization and post-run analytics.

## Tech Stack
- Python 3.11+, numpy, matplotlib, pyyaml
- Testing: pytest
- Linting: ruff

## Project Structure
- `src/interceptor_sim/` — main package
  - `core/` — engine (sim loop), entity (base class), scenario (YAML loader)
  - `models/` — target, interceptor, sensor
  - `guidance/` — pure_pursuit, proportional_nav, midcourse command guidance
  - `engagement/` — detection, classification, kill_chain state machine
  - `visualization/` — live_display (matplotlib animation), post_analysis (charts)
  - `utils/` — geometry (2D vector math)
- `tests/` — pytest unit tests
- `scenarios/` — YAML scenario definitions
- `scripts/` — CLI entry points

## Key Commands
```bash
pip install -e ".[dev]"                              # Install in dev mode
ruff check src/ tests/                               # Lint
pytest                                               # Run tests
python scripts/run_scenario.py scenarios/example_intercept.yaml  # Run simulation
python scripts/run_scenario.py scenarios/example_intercept.yaml --live  # Live viz
```

## Architecture
- **Entity** is the base class (position, speed, heading). Target and Interceptor extend it.
- **Kill chain state machine** (EngagementManager) drives phases: SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE.
- **Guidance** is strategy-pattern: interceptor switches from midcourse (command) to terminal (PN or pure pursuit) at seeker handover.
- **Sensor** is a generic model used for both surveillance radar and onboard seeker with different parameters.
- **Engine** runs fixed-timestep loop collecting SimHistory for post-analysis.
- **Scenarios** are YAML files defining all parameters — no code changes needed to reconfigure.

## Conventions
- All angles in radians internally, degrees only in YAML config and display.
- 2D coordinate system: +x = east, +y = north, angles CCW from +x.
- Numpy arrays for positions/velocities (float64).
