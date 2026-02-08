"""Tests for Sensor model."""

import numpy as np
import pytest

from interceptor_sim.models.sensor import Sensor, SensorMeasurement


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


class TestSensorMeasurement:
    def test_measure_returns_dataclass(self):
        s = Sensor(
            max_range=5000.0,
            range_noise_fraction=0.015,
            bearing_noise_deg=2.0,
            speed_noise_fraction=0.02,
            heading_noise_deg=3.0,
        )
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([3000.0, 0.0])
        m = s.measure(sensor_pos, target_pos, 30.0, 0.0, rng=np.random.default_rng(42))
        assert isinstance(m, SensorMeasurement)
        assert m.true_range == pytest.approx(3000.0)
        assert m.true_bearing == pytest.approx(0.0)

    def test_noise_is_bounded(self):
        """Over many samples, noise should be within ~4 sigma."""
        s = Sensor(
            max_range=5000.0,
            range_noise_fraction=0.015,
            bearing_noise_deg=2.0,
            speed_noise_fraction=0.02,
            heading_noise_deg=3.0,
        )
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([3000.0, 0.0])
        rng = np.random.default_rng(123)

        range_errors = []
        bearing_errors = []
        for _ in range(500):
            m = s.measure(sensor_pos, target_pos, 30.0, 0.0, rng=rng)
            range_errors.append(m.measured_range - m.true_range)
            bearing_errors.append(m.measured_bearing - m.true_bearing)

        # Range error std should be close to 0.015 * 3000 = 45
        range_std = np.std(range_errors)
        assert 20.0 < range_std < 80.0

        # Bearing error std should be close to 2° in radians = 0.0349
        bearing_std = np.std(bearing_errors)
        assert 0.015 < bearing_std < 0.06

    def test_bearing_error_dominates_at_range(self):
        """At 3000m, 2° bearing → ~105m cross-range vs 1.5% range → ~45m."""
        s = Sensor(
            max_range=5000.0,
            range_noise_fraction=0.015,
            bearing_noise_deg=2.0,
        )
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([3000.0, 0.0])
        rng = np.random.default_rng(99)

        cross_errors = []
        along_errors = []
        for _ in range(500):
            m = s.measure(sensor_pos, target_pos, 30.0, 0.0, rng=rng)
            # Along-range = x error, cross-range = y error (target is on +x axis)
            along_errors.append(m.estimated_position[0] - target_pos[0])
            cross_errors.append(m.estimated_position[1] - target_pos[1])

        assert np.std(cross_errors) > np.std(along_errors)

    def test_zero_noise_produces_truth(self):
        s = Sensor(max_range=5000.0)  # all noise defaults to 0
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([1000.0, 500.0])
        m = s.measure(sensor_pos, target_pos, 30.0, np.pi / 4, rng=np.random.default_rng(1))

        assert m.measured_range == pytest.approx(m.true_range)
        assert m.measured_bearing == pytest.approx(m.true_bearing)
        assert m.measured_speed == pytest.approx(30.0)
        assert m.measured_heading == pytest.approx(np.pi / 4)
        np.testing.assert_allclose(m.estimated_position, target_pos, atol=1e-10)
