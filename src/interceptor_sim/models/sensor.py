"""Sensor models for surveillance radar and onboard seeker."""

from __future__ import annotations

import numpy as np

from interceptor_sim.utils.geometry import Vec2, bearing, distance, wrap_angle


class Sensor:
    """Generic sensor with detection range, field of regard, and Pd vs range.

    Works for both ground-based surveillance radar and interceptor onboard seeker.
    """

    def __init__(
        self,
        max_range: float,
        field_of_regard: float = 2 * np.pi,
        boresight: float = 0.0,
        pd_at_max_range: float = 0.3,
        classification_accuracy: float = 0.8,
    ) -> None:
        self.max_range = max_range
        self.field_of_regard = field_of_regard  # total angular width (radians)
        self.boresight = boresight  # center of FoR (radians)
        self.pd_at_max_range = pd_at_max_range
        self.classification_accuracy = classification_accuracy

    def detection_probability(self, rng: float) -> float:
        """Probability of detection as a function of range.

        Uses a simple model: Pd = 1 at range 0, linearly decreasing to
        pd_at_max_range at max_range, 0 beyond.
        """
        if rng > self.max_range:
            return 0.0
        fraction = rng / self.max_range
        return 1.0 - fraction * (1.0 - self.pd_at_max_range)

    def in_field_of_regard(self, sensor_pos: Vec2, target_pos: Vec2) -> bool:
        """Check whether target falls within the sensor field of regard."""
        if self.field_of_regard >= 2 * np.pi:
            return True
        angle_to_target = bearing(sensor_pos, target_pos)
        angular_offset = abs(wrap_angle(angle_to_target - self.boresight))
        return angular_offset <= self.field_of_regard / 2

    def try_detect(
        self, sensor_pos: Vec2, target_pos: Vec2, rng: np.random.Generator | None = None
    ) -> bool:
        """Roll for detection of target at given positions."""
        if not self.in_field_of_regard(sensor_pos, target_pos):
            return False
        rng_val = distance(sensor_pos, target_pos)
        pd = self.detection_probability(rng_val)
        gen = rng or np.random.default_rng()
        return bool(gen.random() < pd)

    def try_classify(self, rng: np.random.Generator | None = None) -> bool:
        """Roll for correct classification (given detection)."""
        gen = rng or np.random.default_rng()
        return bool(gen.random() < self.classification_accuracy)
