"""Midcourse command guidance — bearing commands from ground sensors."""

from __future__ import annotations

import numpy as np

from interceptor_sim.utils.geometry import Vec2, bearing, distance


def command_guidance(
    sensor_pos: Vec2,
    target_pos: Vec2,
    interceptor_pos: Vec2,
    estimated_target_vel: Vec2 | None = None,
    stern_offset: float = 0.0,
    approach_blend_range: float = 500.0,
) -> float:
    """Return commanded heading for midcourse guidance.

    When *estimated_target_vel* is provided and *stern_offset* > 0, computes a
    stern-attack aim point behind the target (opposite its velocity vector).
    As the interceptor closes within *approach_blend_range*, the aim point
    linearly blends from the offset position toward the target itself, ensuring
    a smooth transition to terminal guidance.

    Falls back to direct pursuit when no velocity estimate is available.

    Args:
        sensor_pos: Ground sensor position (used for track data origin).
        target_pos: Target position from ground sensor track.
        interceptor_pos: Current interceptor position.
        estimated_target_vel: Estimated target velocity vector (optional).
        stern_offset: Distance behind target for stern aim point (m).
        approach_blend_range: Range at which blend begins (m).

    Returns:
        Commanded heading (radians).
    """
    if estimated_target_vel is None or stern_offset <= 0.0:
        return bearing(interceptor_pos, target_pos)

    vel_norm = np.linalg.norm(estimated_target_vel)
    if vel_norm < 1e-6:
        return bearing(interceptor_pos, target_pos)

    vel_unit = estimated_target_vel / vel_norm
    stern_point = target_pos - stern_offset * vel_unit

    rng = distance(interceptor_pos, target_pos)
    if rng >= approach_blend_range:
        aim_point = stern_point
    else:
        # Linearly blend: at range=0 aim at target, at range=blend_range aim at stern_point
        blend = rng / approach_blend_range
        aim_point = (1.0 - blend) * target_pos + blend * stern_point

    return bearing(interceptor_pos, aim_point)
