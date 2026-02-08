"""Tests for Entity base class and Target/Interceptor models."""

import numpy as np

from interceptor_sim.core.entity import Entity
from interceptor_sim.models.interceptor import Interceptor, InterceptorState
from interceptor_sim.models.target import Target


class TestEntity:
    def test_initial_state(self):
        e = Entity(position=(10.0, 20.0), speed=5.0, heading=0.0, name="test")
        assert e.name == "test"
        np.testing.assert_array_almost_equal(e.position, [10.0, 20.0])
        assert e.speed == 5.0
        assert e.active is True

    def test_velocity_property(self):
        e = Entity(position=(0, 0), speed=10.0, heading=0.0)
        np.testing.assert_array_almost_equal(e.velocity, [10.0, 0.0])

        e.heading = np.pi / 2
        np.testing.assert_array_almost_equal(e.velocity, [0.0, 10.0], decimal=10)

    def test_update_moves_entity(self):
        e = Entity(position=(0, 0), speed=10.0, heading=0.0)
        e.update(dt=1.0)
        np.testing.assert_array_almost_equal(e.position, [10.0, 0.0])

    def test_inactive_entity_does_not_move(self):
        e = Entity(position=(0, 0), speed=10.0, heading=0.0)
        e.active = False
        e.update(dt=1.0)
        np.testing.assert_array_almost_equal(e.position, [0.0, 0.0])


class TestTarget:
    def test_follows_waypoints(self):
        t = Target(
            position=(0, 0), speed=100.0,
            waypoints=[(100, 0), (100, 100)],
            waypoint_threshold=15.0,
        )
        # Run enough steps to reach first waypoint
        for _ in range(20):
            t.update(0.1)
        # Should be heading toward or past first waypoint
        assert t.position[0] > 50.0

    def test_reaches_final_waypoint(self):
        t = Target(
            position=(0, 0), speed=50.0,
            waypoints=[(50, 0)],
            waypoint_threshold=10.0,
        )
        for _ in range(100):
            t.update(0.1)
        assert t.has_reached_final_waypoint


class TestInterceptor:
    def test_starts_ready(self):
        i = Interceptor(position=(0, 0))
        assert i.state == InterceptorState.READY
        assert i.speed == 0.0

    def test_launch(self):
        i = Interceptor(position=(0, 0), max_speed=100.0)
        i.launch(heading=0.0)
        assert i.state == InterceptorState.LAUNCHED
        assert i.speed == 100.0

    def test_does_not_move_when_ready(self):
        i = Interceptor(position=(0, 0), max_speed=100.0)
        i.update(dt=1.0)
        np.testing.assert_array_almost_equal(i.position, [0.0, 0.0])

    def test_check_intercept(self):
        i = Interceptor(position=(0, 0), kill_radius=10.0)
        assert i.check_intercept(np.array([5.0, 0.0]))
        assert not i.check_intercept(np.array([15.0, 0.0]))

    def test_timeout(self):
        i = Interceptor(position=(0, 0), max_speed=10.0, max_flight_time=1.0)
        i.launch(heading=0.0)
        for _ in range(20):
            i.update(0.1)
        assert i.state == InterceptorState.MISSED
