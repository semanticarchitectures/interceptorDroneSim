"""YAML scenario loader — wires up components and runs simulation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from interceptor_sim.core.engine import SimHistory, SimulationEngine
from interceptor_sim.engagement.kill_chain import EngagementManager
from interceptor_sim.models.interceptor import Interceptor
from interceptor_sim.models.sensor import Sensor
from interceptor_sim.models.target import Target


def load_scenario(path: str | Path) -> dict:
    """Load and return raw scenario dict from YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def build_from_scenario(
    scenario: dict, seed: int | None = None
) -> tuple[SimulationEngine, dict]:
    """Build simulation components from a scenario dictionary.

    Returns:
        Tuple of (engine, metadata dict with references to components).
    """
    rng = np.random.default_rng(seed)

    # Target
    tgt_cfg = scenario["target"]
    target = Target(
        position=tgt_cfg["position"],
        speed=tgt_cfg["speed"],
        waypoints=tgt_cfg.get("waypoints", []),
        rcs=tgt_cfg.get("rcs", 0.01),
        name=tgt_cfg.get("name", "target"),
    )

    # Surveillance sensor
    sensor_cfg = scenario["surveillance_sensor"]
    noise_cfg = sensor_cfg.get("noise", {})
    surveillance_sensor = Sensor(
        max_range=sensor_cfg["max_range"],
        field_of_regard=np.radians(sensor_cfg.get("field_of_regard_deg", 360)),
        pd_at_max_range=sensor_cfg.get("pd_at_max_range", 0.3),
        classification_accuracy=sensor_cfg.get("classification_accuracy", 0.8),
        range_noise_fraction=noise_cfg.get("range_noise_fraction", 0.0),
        bearing_noise_deg=noise_cfg.get("bearing_noise_deg", 0.0),
        speed_noise_fraction=noise_cfg.get("speed_noise_fraction", 0.0),
        heading_noise_deg=noise_cfg.get("heading_noise_deg", 0.0),
    )
    sensor_position = np.array(
        sensor_cfg.get("position", [0.0, 0.0]), dtype=np.float64
    )

    # Interceptor
    int_cfg = scenario["interceptor"]
    seeker_cfg = int_cfg.get("seeker", {})
    seeker = Sensor(
        max_range=seeker_cfg.get("max_range", 500.0),
        field_of_regard=np.radians(seeker_cfg.get("field_of_regard_deg", 60)),
        pd_at_max_range=seeker_cfg.get("pd_at_max_range", 0.5),
    )
    interceptor = Interceptor(
        position=int_cfg["position"],
        max_speed=int_cfg.get("max_speed", 100.0),
        max_turn_rate=np.radians(int_cfg.get("max_turn_rate_deg", 30)),
        seeker=seeker,
        kill_radius=int_cfg.get("kill_radius", 5.0),
        max_flight_time=int_cfg.get("max_flight_time", 60.0),
        name=int_cfg.get("name", "interceptor"),
    )

    # Capture launch position before simulation moves the interceptor
    launch_position = interceptor.position.copy()

    # Engagement manager
    eng_cfg = scenario.get("engagement", {})
    engagement = EngagementManager(
        target=target,
        interceptor=interceptor,
        surveillance_sensor=surveillance_sensor,
        sensor_position=sensor_position,
        terminal_guidance=eng_cfg.get("terminal_guidance", "proportional_nav"),
        nav_gain=eng_cfg.get("nav_gain", 4.0),
        terminal_handover_range=eng_cfg.get("terminal_handover_range", 100.0),
        stern_offset=eng_cfg.get("stern_offset", 0.0),
        approach_blend_range=eng_cfg.get("approach_blend_range", 500.0),
        rng=rng,
    )

    # Simulation engine
    sim_cfg = scenario.get("simulation", {})
    engine = SimulationEngine(
        target=target,
        interceptor=interceptor,
        engagement=engagement,
        dt=sim_cfg.get("dt", 0.1),
        max_time=sim_cfg.get("max_time", 120.0),
    )

    metadata = {
        "target": target,
        "interceptor": interceptor,
        "surveillance_sensor": surveillance_sensor,
        "sensor_position": sensor_position,
        "engagement": engagement,
        "engine": engine,
        "launch_position": launch_position,
        "protected_asset_position": sensor_position.copy(),
    }

    return engine, metadata


def run_scenario(path: str | Path, seed: int | None = None) -> SimHistory:
    """Load scenario from YAML, build components, and run simulation."""
    scenario = load_scenario(path)
    engine, _ = build_from_scenario(scenario, seed=seed)
    return engine.run()
