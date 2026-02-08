"""Interceptor drone model."""

from __future__ import annotations

from enum import Enum, auto

import numpy as np

from interceptor_sim.core.entity import Entity
from interceptor_sim.models.sensor import Sensor
from interceptor_sim.utils.geometry import Vec2, distance, wrap_angle


class InterceptorState(Enum):
    READY = auto()
    LAUNCHED = auto()
    TERMINAL = auto()
    DETONATED = auto()
    MISSED = auto()


class Interceptor(Entity):
    """Interceptor drone with launch, flight performance, and onboard seeker.

    Attributes:
        max_speed: Maximum speed (m/s).
        max_turn_rate: Maximum heading change rate (rad/s).
        seeker: Onboard sensor for terminal acquisition.
        kill_radius: Distance at which intercept is considered successful.
        max_flight_time: Fuel/battery endurance (seconds).
        guidance_law: Callable that returns commanded heading given state.
    """

    def __init__(
        self,
        position: Vec2 | tuple[float, float],
        max_speed: float = 100.0,
        max_turn_rate: float = np.radians(30),
        seeker: Sensor | None = None,
        kill_radius: float = 5.0,
        max_flight_time: float = 60.0,
        name: str = "interceptor",
    ) -> None:
        super().__init__(position=position, speed=0.0, name=name)
        self.max_speed = max_speed
        self.max_turn_rate = max_turn_rate
        self.seeker = seeker or Sensor(
            max_range=500.0,
            field_of_regard=np.radians(60),
            pd_at_max_range=0.5,
        )
        self.kill_radius = kill_radius
        self.max_flight_time = max_flight_time
        self.state = InterceptorState.READY
        self.flight_time = 0.0
        self.guidance_law = None  # set externally

    def launch(self, heading: float) -> None:
        """Launch the interceptor toward initial heading."""
        self.state = InterceptorState.LAUNCHED
        self.heading = heading
        self.speed = self.max_speed
        self.flight_time = 0.0

    def apply_guidance(self, commanded_heading: float, dt: float) -> None:
        """Steer toward commanded heading, limited by max turn rate."""
        heading_error = wrap_angle(commanded_heading - self.heading)
        max_delta = self.max_turn_rate * dt
        clamped = np.clip(heading_error, -max_delta, max_delta)
        self.heading = wrap_angle(self.heading + clamped)

    def check_intercept(self, target_pos: Vec2) -> bool:
        """Return True if target is within kill radius."""
        return distance(self.position, target_pos) <= self.kill_radius

    def update(self, dt: float) -> None:
        """Advance interceptor state and position."""
        if self.state not in (InterceptorState.LAUNCHED, InterceptorState.TERMINAL):
            return

        self.flight_time += dt
        if self.flight_time >= self.max_flight_time:
            self.state = InterceptorState.MISSED
            self.speed = 0.0
            self.active = False
            return

        super().update(dt)
