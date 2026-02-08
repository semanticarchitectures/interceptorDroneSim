"""Sensor models for surveillance radar and onboard seeker."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from interceptor_sim.utils.geometry import Vec2, bearing, distance, unit_vector, wrap_angle


@dataclass
class SensorMeasurement:
    """Noisy measurement from a sensor observation."""

    measured_range: float
    measured_bearing: float
    measured_speed: float
    measured_heading: float
    estimated_position: Vec2
    estimated_velocity: Vec2
    true_range: float
    true_bearing: float
    true_speed: float
    true_heading: float


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
        range_noise_fraction: float = 0.0,
        bearing_noise_deg: float = 0.0,
        speed_noise_fraction: float = 0.0,
        heading_noise_deg: float = 0.0,
    ) -> None:
        self.max_range = max_range
        self.field_of_regard = field_of_regard  # total angular width (radians)
        self.boresight = boresight  # center of FoR (radians)
        self.pd_at_max_range = pd_at_max_range
        self.classification_accuracy = classification_accuracy
        self.range_noise_fraction = range_noise_fraction
        self.bearing_noise_rad = np.radians(bearing_noise_deg)
        self.speed_noise_fraction = speed_noise_fraction
        self.heading_noise_rad = np.radians(heading_noise_deg)

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

    def measure(
        self,
        sensor_pos: Vec2,
        target_pos: Vec2,
        target_speed: float,
        target_heading: float,
        rng: np.random.Generator | None = None,
    ) -> SensorMeasurement:
        """Produce a noisy measurement of target state.

        Applies Gaussian noise in polar coordinates (range, bearing) and to
        speed/heading, then converts to Cartesian estimated position/velocity.
        """
        gen = rng or np.random.default_rng()

        true_rng = distance(sensor_pos, target_pos)
        true_brg = bearing(sensor_pos, target_pos)

        # Apply noise
        range_sigma = self.range_noise_fraction * true_rng
        bearing_sigma = self.bearing_noise_rad
        speed_sigma = self.speed_noise_fraction * target_speed
        heading_sigma = self.heading_noise_rad

        if range_sigma > 0:
            meas_range = max(0.0, true_rng + gen.normal(0.0, range_sigma))
        else:
            meas_range = true_rng

        if bearing_sigma > 0:
            meas_bearing = true_brg + gen.normal(0.0, bearing_sigma)
        else:
            meas_bearing = true_brg

        if speed_sigma > 0:
            meas_speed = max(0.0, target_speed + gen.normal(0.0, speed_sigma))
        else:
            meas_speed = target_speed

        if heading_sigma > 0:
            meas_heading = target_heading + gen.normal(0.0, heading_sigma)
        else:
            meas_heading = target_heading

        # Convert to Cartesian
        estimated_position = sensor_pos + meas_range * unit_vector(meas_bearing)
        estimated_velocity = meas_speed * unit_vector(meas_heading)

        return SensorMeasurement(
            measured_range=meas_range,
            measured_bearing=meas_bearing,
            measured_speed=meas_speed,
            measured_heading=meas_heading,
            estimated_position=estimated_position,
            estimated_velocity=estimated_velocity,
            true_range=true_rng,
            true_bearing=true_brg,
            true_speed=target_speed,
            true_heading=target_heading,
        )
