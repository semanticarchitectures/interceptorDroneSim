"""Proportional navigation guidance law."""

from __future__ import annotations

from interceptor_sim.utils.geometry import Vec2, bearing, closing_speed, line_of_sight_rate


def proportional_navigation(
    interceptor_pos: Vec2,
    interceptor_vel: Vec2,
    target_pos: Vec2,
    target_vel: Vec2,
    nav_gain: float = 4.0,
) -> float:
    """Return commanded heading using proportional navigation.

    PN steers to nullify the line-of-sight rate. The commanded heading
    is the current LOS bearing plus a correction proportional to the
    LOS rate and inversely related to closing speed.

    Args:
        interceptor_pos: Interceptor position.
        interceptor_vel: Interceptor velocity vector.
        target_pos: Target position.
        target_vel: Target velocity vector.
        nav_gain: Navigation constant (typically 3–5).

    Returns:
        Commanded heading (radians).
    """
    los_angle = bearing(interceptor_pos, target_pos)
    los_rate = line_of_sight_rate(
        interceptor_pos, interceptor_vel, target_pos, target_vel
    )
    vc = closing_speed(interceptor_pos, interceptor_vel, target_pos, target_vel)

    # Avoid division by zero when not closing
    if abs(vc) < 1e-3:
        return los_angle

    # PN lateral acceleration mapped to heading correction
    heading_correction = nav_gain * los_rate
    return los_angle + heading_correction
