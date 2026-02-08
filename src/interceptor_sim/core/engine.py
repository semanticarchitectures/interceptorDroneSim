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
    estimated_target_pos: np.ndarray | None = None
    estimated_target_vel: np.ndarray | None = None


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

    @property
    def estimated_target_positions(self) -> np.ndarray:
        """Estimated target positions; NaN where no estimate is available."""
        result = []
        for s in self.states:
            if s.estimated_target_pos is not None:
                result.append(s.estimated_target_pos)
            else:
                result.append(np.array([np.nan, np.nan]))
        return np.array(result)


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

    def _record_state(self) -> None:
        """Record current simulation state including estimated target position."""
        est_pos = None
        est_vel = None
        if self.engagement.estimated_target_pos is not None:
            est_pos = self.engagement.estimated_target_pos.copy()
        if self.engagement.estimated_target_vel is not None:
            est_vel = self.engagement.estimated_target_vel.copy()

        self.history.record(
            SimState(
                time=self.time,
                target_pos=self.target.position.copy(),
                interceptor_pos=self.interceptor.position.copy(),
                phase=self.engagement.phase,
                target_active=self.target.active,
                interceptor_speed=self.interceptor.speed,
                estimated_target_pos=est_pos,
                estimated_target_vel=est_vel,
            )
        )

    def step(self) -> bool:
        """Run one simulation timestep. Returns False when sim is complete."""
        if self.time >= self.max_time:
            return False
        if self.engagement.phase == Phase.COMPLETE:
            return False

        # Record state
        self._record_state()

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
        self._record_state()
        return self.history
