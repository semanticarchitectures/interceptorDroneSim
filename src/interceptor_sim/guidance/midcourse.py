"""Midcourse command guidance — bearing commands from ground sensors."""

from __future__ import annotations

from interceptor_sim.utils.geometry import Vec2, bearing


def command_guidance(
    sensor_pos: Vec2,
    target_pos: Vec2,
    interceptor_pos: Vec2,
) -> float:
    """Return commanded heading for midcourse guidance.

    Uses ground sensor data to command the interceptor toward the target.
    The interceptor steers toward the target's position as seen from the
    ground sensor's track.

    Args:
        sensor_pos: Ground sensor position (used for track data origin).
        target_pos: Target position from ground sensor track.
        interceptor_pos: Current interceptor position.

    Returns:
        Commanded heading (radians).
    """
    return bearing(interceptor_pos, target_pos)
