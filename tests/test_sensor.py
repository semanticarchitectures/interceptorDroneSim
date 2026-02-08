"""Tests for Sensor model."""

import numpy as np
import pytest

from interceptor_sim.models.sensor import Sensor


class TestSensor:
    def test_detection_probability_at_zero(self):
        s = Sensor(max_range=1000.0, pd_at_max_range=0.3)
        assert s.detection_probability(0.0) == pytest.approx(1.0)

    def test_detection_probability_at_max_range(self):
        s = Sensor(max_range=1000.0, pd_at_max_range=0.3)
        assert s.detection_probability(1000.0) == pytest.approx(0.3)

    def test_detection_probability_beyond_max_range(self):
        s = Sensor(max_range=1000.0, pd_at_max_range=0.3)
        assert s.detection_probability(1500.0) == 0.0

    def test_detection_probability_at_half_range(self):
        s = Sensor(max_range=1000.0, pd_at_max_range=0.3)
        expected = 1.0 - 0.5 * (1.0 - 0.3)  # 0.65
        assert s.detection_probability(500.0) == pytest.approx(expected)

    def test_full_field_of_regard(self):
        s = Sensor(max_range=1000.0, field_of_regard=2 * np.pi)
        # Should see in any direction
        assert s.in_field_of_regard(np.array([0, 0]), np.array([100, 0]))
        assert s.in_field_of_regard(np.array([0, 0]), np.array([-100, 0]))
        assert s.in_field_of_regard(np.array([0, 0]), np.array([0, 100]))

    def test_narrow_field_of_regard(self):
        s = Sensor(
            max_range=1000.0,
            field_of_regard=np.radians(60),
            boresight=0.0,
        )
        # Directly ahead: in FoR
        assert s.in_field_of_regard(np.array([0, 0]), np.array([100, 0]))
        # 90 degrees off: out of FoR
        assert not s.in_field_of_regard(np.array([0, 0]), np.array([0, 100]))

    def test_try_detect_deterministic(self):
        s = Sensor(max_range=1000.0, pd_at_max_range=0.3)
        rng = np.random.default_rng(42)
        # At range 0, Pd=1.0, should always detect
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([0.001, 0.0])
        results = [s.try_detect(sensor_pos, target_pos, rng=rng) for _ in range(10)]
        assert all(results)

    def test_try_classify(self):
        s = Sensor(max_range=1000.0, classification_accuracy=1.0)
        rng = np.random.default_rng(42)
        assert s.try_classify(rng=rng)
