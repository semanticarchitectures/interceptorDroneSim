"""Time-stepping simulation engine."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from interceptor_sim.engagement.kill_chain import EngagementManager, Phase
from interceptor_sim.models.interceptor import Interceptor
from interceptor_sim.models.target import Target


@dataclass
class SimState:
    """Snapshot of simulation state at one timestep."""

    time: float
    target_pos: np.ndarray
    interceptor_pos: np.ndarray
    phase: Phase
    target_active: bool
    interceptor_speed: float


@dataclass
class SimHistory:
    """Time history of all simulation states."""

    states: list[SimState] = field(default_factory=list)

    def record(self, state: SimState) -> None:
        self.states.append(state)

    @property
    def times(self) -> list[float]:
        return [s.time for s in self.states]

    @property
    def target_positions(self) -> np.ndarray:
        return np.array([s.target_pos for s in self.states])

    @property
    def interceptor_positions(self) -> np.ndarray:
        return np.array([s.interceptor_pos for s in self.states])


class SimulationEngine:
    """Fixed-timestep simulation loop.

    Each tick: update entities → run engagement logic → record state.
    """

    def __init__(
        self,
        target: Target,
        interceptor: Interceptor,
        engagement: EngagementManager,
        dt: float = 0.1,
        max_time: float = 120.0,
    ) -> None:
        self.target = target
        self.interceptor = interceptor
        self.engagement = engagement
        self.dt = dt
        self.max_time = max_time
        self.history = SimHistory()
        self.time = 0.0

    def step(self) -> bool:
        """Run one simulation timestep. Returns False when sim is complete."""
        if self.time >= self.max_time:
            return False
        if self.engagement.phase == Phase.COMPLETE:
            return False

        # Record state
        self.history.record(
            SimState(
                time=self.time,
                target_pos=self.target.position.copy(),
                interceptor_pos=self.interceptor.position.copy(),
                phase=self.engagement.phase,
                target_active=self.target.active,
                interceptor_speed=self.interceptor.speed,
            )
        )

        # Update entities
        self.target.update(self.dt)
        self.interceptor.update(self.dt)

        # Run engagement logic
        self.engagement.step(self.time, self.dt)

        self.time += self.dt
        return True

    def run(self) -> SimHistory:
        """Run simulation to completion."""
        while self.step():
            pass

        # Record final state
        self.history.record(
            SimState(
                time=self.time,
                target_pos=self.target.position.copy(),
                interceptor_pos=self.interceptor.position.copy(),
                phase=self.engagement.phase,
                target_active=self.target.active,
                interceptor_speed=self.interceptor.speed,
            )
        )
        return self.history
