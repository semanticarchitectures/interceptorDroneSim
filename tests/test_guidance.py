"""Tests for guidance laws."""

import numpy as np
import pytest

from interceptor_sim.guidance.midcourse import command_guidance
from interceptor_sim.guidance.proportional_nav import proportional_navigation
from interceptor_sim.guidance.pure_pursuit import pure_pursuit


class TestPurePursuit:
    def test_bearing_east(self):
        heading = pure_pursuit(np.array([0, 0]), np.array([100, 0]))
        assert heading == pytest.approx(0.0)

    def test_bearing_north(self):
        heading = pure_pursuit(np.array([0, 0]), np.array([0, 100]))
        assert heading == pytest.approx(np.pi / 2)

    def test_bearing_southwest(self):
        heading = pure_pursuit(np.array([0, 0]), np.array([-100, -100]))
        assert heading == pytest.approx(-3 * np.pi / 4)


class TestProportionalNav:
    def test_head_on_no_correction(self):
        # Target moving left, interceptor moving right — head on
        int_pos = np.array([0.0, 0.0])
        int_vel = np.array([100.0, 0.0])
        tgt_pos = np.array([1000.0, 0.0])
        tgt_vel = np.array([-30.0, 0.0])

        heading = proportional_navigation(int_pos, int_vel, tgt_pos, tgt_vel)
        # LOS rate should be ~0, so heading ≈ bearing to target (0)
        assert abs(heading) < 0.1

    def test_crossing_target_correction(self):
        # Target moving perpendicular — needs lead
        int_pos = np.array([0.0, 0.0])
        int_vel = np.array([100.0, 0.0])
        tgt_pos = np.array([1000.0, 0.0])
        tgt_vel = np.array([0.0, 30.0])  # moving north

        heading = proportional_navigation(int_pos, int_vel, tgt_pos, tgt_vel)
        # Should command heading above 0 (lead north)
        assert heading > 0


class TestCommandGuidance:
    def test_commands_toward_target(self):
        sensor_pos = np.array([0.0, 0.0])
        target_pos = np.array([1000.0, 500.0])
        interceptor_pos = np.array([100.0, 0.0])

        heading = command_guidance(sensor_pos, target_pos, interceptor_pos)
        expected = np.arctan2(500.0, 900.0)
        assert heading == pytest.approx(expected)
