"""Detection probability and track formation logic."""

from __future__ import annotations

import numpy as np

from interceptor_sim.models.sensor import Sensor
from interceptor_sim.utils.geometry import Vec2


class TrackState:
    """Represents a sensor track on a detected target."""

    def __init__(self, target_id: str) -> None:
        self.target_id = target_id
        self.detected = False
        self.detection_count = 0
        self.track_confirmed = False
        self.confirm_threshold = 3  # detections needed to confirm track

    def process_detection(self, detected: bool) -> None:
        """Update track state with a detection result."""
        if detected:
            self.detection_count += 1
            self.detected = True
            if self.detection_count >= self.confirm_threshold:
                self.track_confirmed = True
        # Track persists even without detection (coast)


def attempt_detection(
    sensor: Sensor,
    sensor_pos: Vec2,
    target_pos: Vec2,
    rng: np.random.Generator | None = None,
) -> bool:
    """Attempt detection of a target using the given sensor."""
    return sensor.try_detect(sensor_pos, target_pos, rng=rng)
