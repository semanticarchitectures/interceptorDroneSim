"""Base entity class holding 2D kinematic state."""

from __future__ import annotations

import numpy as np

from interceptor_sim.utils.geometry import Vec2, unit_vector


class Entity:
    """Base class for all simulation entities (targets, interceptors, sensors).

    State: 2D position, speed, heading (radians CCW from +x).
    """

    def __init__(
        self,
        position: Vec2 | tuple[float, float],
        speed: float = 0.0,
        heading: float = 0.0,
        name: str = "",
    ) -> None:
        self.position = np.asarray(position, dtype=np.float64)
        self.speed = speed
        self.heading = heading
        self.name = name
        self.active = True

    @property
    def velocity(self) -> Vec2:
        return self.speed * unit_vector(self.heading)

    def update(self, dt: float) -> None:
        """Advance position by one timestep."""
        if self.active:
            self.position = self.position + self.velocity * dt

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"pos=[{self.position[0]:.1f}, {self.position[1]:.1f}], "
            f"spd={self.speed:.1f}, hdg={np.degrees(self.heading):.1f}°)"
        )
