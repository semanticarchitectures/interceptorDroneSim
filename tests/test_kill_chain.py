"""Tests for engagement kill chain state machine."""

import numpy as np

from interceptor_sim.engagement.classification import ClassificationState
from interceptor_sim.engagement.detection import TrackState
from interceptor_sim.engagement.kill_chain import (
    EngagementManager,
    EngagementResult,
    Phase,
)
from interceptor_sim.models.interceptor import Interceptor
from interceptor_sim.models.sensor import Sensor
from interceptor_sim.models.target import Target


class TestTrackState:
    def test_initial_state(self):
        ts = TrackState("tgt_1")
        assert not ts.detected
        assert not ts.track_confirmed
        assert ts.detection_count == 0

    def test_track_confirmation(self):
        ts = TrackState("tgt_1")
        for _ in range(3):
            ts.process_detection(True)
        assert ts.track_confirmed

    def test_no_confirm_without_detections(self):
        ts = TrackState("tgt_1")
        ts.process_detection(False)
        ts.process_detection(False)
        ts.process_detection(False)
        assert not ts.track_confirmed


class TestClassificationState:
    def test_builds_confidence(self):
        cs = ClassificationState(threshold=0.8)
        # Perfect sensor
        sensor = Sensor(max_range=1000, classification_accuracy=1.0)
        rng = np.random.default_rng(42)
        for _ in range(20):
            cs.process_look(sensor, rng=rng)
        assert cs.classified

    def test_low_accuracy_slow_classification(self):
        cs = ClassificationState(threshold=0.8)
        sensor = Sensor(max_range=1000, classification_accuracy=0.5)
        rng = np.random.default_rng(42)
        # With 50% accuracy, should take longer (may or may not classify in 5 looks)
        for _ in range(5):
            cs.process_look(sensor, rng=rng)
        # Just verify confidence is between 0 and 1
        assert 0.0 <= cs.confidence <= 1.0


class TestEngagementManager:
    def _make_engagement(self, seed=42):
        target = Target(
            position=(2000.0, 0.0),
            speed=30.0,
            waypoints=[(0.0, 0.0)],
            name="tgt",
        )
        sensor = Sensor(
            max_range=5000.0,
            pd_at_max_range=0.99,  # high Pd for deterministic tests
            classification_accuracy=0.99,
            # zero noise for predictable tests
            range_noise_fraction=0.0,
            bearing_noise_deg=0.0,
            speed_noise_fraction=0.0,
            heading_noise_deg=0.0,
        )
        interceptor = Interceptor(
            position=(0.0, 0.0),
            max_speed=100.0,
            kill_radius=10.0,
            max_flight_time=60.0,
        )
        em = EngagementManager(
            target=target,
            interceptor=interceptor,
            surveillance_sensor=sensor,
            sensor_position=(0.0, 0.0),
            terminal_handover_range=100.0,
            stern_offset=0.0,
            approach_blend_range=500.0,
            rng=np.random.default_rng(seed),
        )
        return target, interceptor, em

    def test_starts_in_search(self):
        _, _, em = self._make_engagement()
        assert em.phase == Phase.SEARCH

    def test_progresses_through_phases(self):
        target, interceptor, em = self._make_engagement()
        dt = 0.1
        # Run until we get past SEARCH
        for i in range(100):
            t = i * dt
            target.update(dt)
            interceptor.update(dt)
            em.step(t, dt)
            if em.phase != Phase.SEARCH:
                break
        assert em.phase != Phase.SEARCH

    def test_full_engagement(self):
        """Run a complete engagement and check it reaches COMPLETE."""
        target, interceptor, em = self._make_engagement(seed=1)
        dt = 0.1
        for i in range(2000):
            t = i * dt
            target.update(dt)
            interceptor.update(dt)
            em.step(t, dt)
            if em.phase == Phase.COMPLETE:
                break
        assert em.phase == Phase.COMPLETE
        assert em.result in (EngagementResult.HIT, EngagementResult.MISS)

    def test_deterministic_handover(self):
        """Handover should occur when estimated range <= terminal_handover_range."""
        target, interceptor, em = self._make_engagement(seed=1)
        dt = 0.1
        entered_terminal = False
        for i in range(2000):
            t = i * dt
            target.update(dt)
            interceptor.update(dt)
            em.step(t, dt)
            if em.phase == Phase.TERMINAL:
                entered_terminal = True
                break
            if em.phase == Phase.COMPLETE:
                break
        assert entered_terminal

    def test_estimated_position_stored(self):
        """During midcourse, estimated_target_pos should be populated."""
        target, interceptor, em = self._make_engagement(seed=1)
        dt = 0.1
        # Run until midcourse
        for i in range(2000):
            t = i * dt
            target.update(dt)
            interceptor.update(dt)
            em.step(t, dt)
            if em.phase == Phase.MIDCOURSE:
                # Step once more to get a measurement
                target.update(dt)
                interceptor.update(dt)
                em.step(t + dt, dt)
                break
        # With zero noise, estimated pos should equal true pos
        assert em.estimated_target_pos is not None
        np.testing.assert_allclose(
            em.estimated_target_pos, target.position, atol=1.0
        )
