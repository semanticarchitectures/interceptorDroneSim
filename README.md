# Interceptor Drone Simulation

A 2D kinematic simulation of counter-UAS interceptor engagements, modeling the full kill chain from detection through intercept.

## Features

- **Full kill chain simulation**: SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE
- **Multiple guidance laws**: Proportional navigation, pure pursuit, and midcourse command guidance
- **Sensor modeling**: Detection probability vs range, field of regard, classification confidence
- **YAML-configurable scenarios**: Change parameters without code modifications
- **Visualization**: Real-time matplotlib animation and post-run analysis charts

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run the example scenario
python scripts/run_scenario.py scenarios/example_intercept.yaml

# Run with live visualization
python scripts/run_scenario.py scenarios/example_intercept.yaml --live

# Run with a fixed random seed
python scripts/run_scenario.py scenarios/example_intercept.yaml --seed 42
```

## Development

```bash
# Lint
ruff check src/ tests/

# Test
pytest
```

## Scenario Format

Scenarios are YAML files defining target, sensor, interceptor, and engagement parameters. See `scenarios/example_intercept.yaml` for the full format.
