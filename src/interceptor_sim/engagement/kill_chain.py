"""Engagement state machine driving the kill chain."""

from __future__ import annotations

from enum import Enum, auto

import numpy as np

from interceptor_sim.engagement.classification import ClassificationState
from interceptor_sim.engagement.detection import TrackState, attempt_detection
from interceptor_sim.guidance.midcourse import command_guidance
from interceptor_sim.guidance.proportional_nav import proportional_navigation
from interceptor_sim.guidance.pure_pursuit import pure_pursuit
from interceptor_sim.models.interceptor import Interceptor, InterceptorState
from interceptor_sim.models.sensor import Sensor, SensorMeasurement
from interceptor_sim.models.target import Target
from interceptor_sim.utils.geometry import Vec2, bearing, distance


class Phase(Enum):
    SEARCH = auto()
    TRACK = auto()
    CLASSIFY = auto()
    LAUNCH = auto()
    MIDCOURSE = auto()
    TERMINAL = auto()
    COMPLETE = auto()


class EngagementResult(Enum):
    PENDING = auto()
    HIT = auto()
    MISS = auto()
    TIMEOUT = auto()


class EngagementManager:
    """Drives the engagement through discrete kill-chain phases.

    Phases: SEARCH → TRACK → CLASSIFY → LAUNCH → MIDCOURSE → TERMINAL → COMPLETE
    """

    def __init__(
        self,
        target: Target,
        interceptor: Interceptor,
        surveillance_sensor: Sensor,
        sensor_position: Vec2,
        terminal_guidance: str = "proportional_nav",
        nav_gain: float = 4.0,
        terminal_handover_range: float = 100.0,
        stern_offset: float = 0.0,
        approach_blend_range: float = 500.0,
        rng: np.random.Generator | None = None,
    ) -> None:
        self.target = target
        self.interceptor = interceptor
        self.surveillance_sensor = surveillance_sensor
        self.sensor_position = np.asarray(sensor_position, dtype=np.float64)
        self.terminal_guidance = terminal_guidance
        self.nav_gain = nav_gain
        self.terminal_handover_range = terminal_handover_range
        self.stern_offset = stern_offset
        self.approach_blend_range = approach_blend_range
        self.rng = rng or np.random.default_rng()

        self.phase = Phase.SEARCH
        self.result = EngagementResult.PENDING
        self.track = TrackState(target.name)
        self.classification = ClassificationState()

        self.phase_log: list[tuple[float, Phase]] = []
        self._phase_start_time = 0.0

        # Noisy estimates updated each midcourse step
        self.estimated_target_pos: Vec2 | None = None
        self.estimated_target_vel: Vec2 | None = None
        self.latest_measurement: SensorMeasurement | None = None

    def step(self, t: float, dt: float) -> None:
        """Advance engagement logic by one timestep."""
        if self.phase == Phase.COMPLETE:
            return

        if self.phase == Phase.SEARCH:
            self._step_search(t)
        elif self.phase == Phase.TRACK:
            self._step_track(t)
        elif self.phase == Phase.CLASSIFY:
            self._step_classify(t)
        elif self.phase == Phase.LAUNCH:
            self._step_launch(t)
        elif self.phase == Phase.MIDCOURSE:
            self._step_midcourse(t, dt)
        elif self.phase == Phase.TERMINAL:
            self._step_terminal(t, dt)

    def _transition(self, new_phase: Phase, t: float) -> None:
        self.phase_log.append((t, new_phase))
        self.phase = new_phase

    def _step_search(self, t: float) -> None:
        detected = attempt_detection(
            self.surveillance_sensor,
            self.sensor_position,
            self.target.position,
            rng=self.rng,
        )
        self.track.process_detection(detected)
        if self.track.detected:
            self._transition(Phase.TRACK, t)

    def _step_track(self, t: float) -> None:
        detected = attempt_detection(
            self.surveillance_sensor,
            self.sensor_position,
            self.target.position,
            rng=self.rng,
        )
        self.track.process_detection(detected)
        if self.track.track_confirmed:
            self._transition(Phase.CLASSIFY, t)

    def _step_classify(self, t: float) -> None:
        self.classification.process_look(self.surveillance_sensor, rng=self.rng)
        if self.classification.classified:
            self._transition(Phase.LAUNCH, t)

    def _step_launch(self, t: float) -> None:
        launch_heading = bearing(self.interceptor.position, self.target.position)
        self.interceptor.launch(launch_heading)
        self._transition(Phase.MIDCOURSE, t)

    def _step_midcourse(self, t: float, dt: float) -> None:
        # Check if interceptor has timed out
        if self.interceptor.state == InterceptorState.MISSED:
            self.result = EngagementResult.MISS
            self._transition(Phase.COMPLETE, t)
            return

        # Noisy measurement from surveillance sensor
        measurement = self.surveillance_sensor.measure(
            self.sensor_position,
            self.target.position,
            self.target.speed,
            self.target.heading,
            rng=self.rng,
        )
        self.latest_measurement = measurement
        self.estimated_target_pos = measurement.estimated_position.copy()
        self.estimated_target_vel = measurement.estimated_velocity.copy()

        # Command guidance with stern attack
        cmd_heading = command_guidance(
            self.sensor_position,
            self.estimated_target_pos,
            self.interceptor.position,
            estimated_target_vel=self.estimated_target_vel,
            stern_offset=self.stern_offset,
            approach_blend_range=self.approach_blend_range,
        )
        self.interceptor.apply_guidance(cmd_heading, dt)

        # Deterministic handover: transition when estimated range <= threshold
        est_range = distance(self.interceptor.position, self.estimated_target_pos)
        if est_range <= self.terminal_handover_range:
            self.interceptor.state = InterceptorState.TERMINAL
            self._transition(Phase.TERMINAL, t)

    def _step_terminal(self, t: float, dt: float) -> None:
        # Check for intercept
        if self.interceptor.check_intercept(self.target.position):
            self.interceptor.state = InterceptorState.DETONATED
            self.target.active = False
            self.result = EngagementResult.HIT
            self._transition(Phase.COMPLETE, t)
            return

        # Check for timeout
        if self.interceptor.state == InterceptorState.MISSED:
            self.result = EngagementResult.MISS
            self._transition(Phase.COMPLETE, t)
            return

        # Apply terminal guidance
        if self.terminal_guidance == "proportional_nav":
            cmd_heading = proportional_navigation(
                self.interceptor.position,
                self.interceptor.velocity,
                self.target.position,
                self.target.velocity,
                nav_gain=self.nav_gain,
            )
        else:
            cmd_heading = pure_pursuit(
                self.interceptor.position, self.target.position
            )

        self.interceptor.apply_guidance(cmd_heading, dt)
