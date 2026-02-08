"""Classification confidence accumulation and threshold logic."""

from __future__ import annotations

import numpy as np

from interceptor_sim.models.sensor import Sensor


class ClassificationState:
    """Accumulates classification confidence over multiple sensor looks."""

    def __init__(self, threshold: float = 0.8) -> None:
        self.confidence = 0.0
        self.threshold = threshold
        self.classified = False
        self.looks = 0

    def process_look(
        self, sensor: Sensor, rng: np.random.Generator | None = None
    ) -> None:
        """Process one classification look and update confidence.

        Uses Bayesian-style update: each correct classification increases
        confidence, each incorrect one decreases it.
        """
        if self.classified:
            return

        self.looks += 1
        correct = sensor.try_classify(rng=rng)

        if correct:
            # Bayesian update toward 1.0
            self.confidence = self.confidence + (1.0 - self.confidence) * 0.3
        else:
            # Decay toward 0
            self.confidence = self.confidence * 0.7

        if self.confidence >= self.threshold:
            self.classified = True
