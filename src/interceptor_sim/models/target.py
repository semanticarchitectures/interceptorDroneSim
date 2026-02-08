"""Adversarial UAV target model."""

from __future__ import annotations

import numpy as np

from interceptor_sim.core.entity import Entity
from interceptor_sim.utils.geometry import Vec2, bearing, distance


class Target(Entity):
    """Adversarial UAV that follows a sequence of waypoints.

    Attributes:
        waypoints: List of 2D positions the target flies through in order.
        waypoint_threshold: Distance at which the target considers a waypoint reached.
        rcs: Radar cross-section (m², used for detection model scaling).
    """

    def __init__(
        self,
        position: Vec2 | tuple[float, float],
        speed: float,
        waypoints: list[Vec2 | tuple[float, float]] | None = None,
        waypoint_threshold: float = 20.0,
        rcs: float = 0.01,
        name: str = "target",
    ) -> None:
        super().__init__(position=position, speed=speed, name=name)
        self.waypoints: list[Vec2] = [
            np.asarray(wp, dtype=np.float64) for wp in (waypoints or [])
        ]
        self.current_waypoint_idx = 0
        self.waypoint_threshold = waypoint_threshold
        self.rcs = rcs

        # Set initial heading toward first waypoint if available
        if self.waypoints:
            self.heading = bearing(self.position, self.waypoints[0])

    def update(self, dt: float) -> None:
        """Advance target along its waypoint path."""
        if not self.active:
            return

        if self.waypoints and self.current_waypoint_idx < len(self.waypoints):
            wp = self.waypoints[self.current_waypoint_idx]
            self.heading = bearing(self.position, wp)

            if distance(self.position, wp) < self.waypoint_threshold:
                self.current_waypoint_idx += 1

        super().update(dt)

    @property
    def has_reached_final_waypoint(self) -> bool:
        if not self.waypoints:
            return False
        return self.current_waypoint_idx >= len(self.waypoints)
