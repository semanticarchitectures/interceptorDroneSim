"""Pure pursuit guidance law — steer directly toward target."""

from __future__ import annotations

from interceptor_sim.utils.geometry import Vec2, bearing


def pure_pursuit(interceptor_pos: Vec2, target_pos: Vec2) -> float:
    """Return commanded heading that points directly at the target.

    Args:
        interceptor_pos: Current interceptor position.
        target_pos: Current target position.

    Returns:
        Commanded heading (radians, CCW from +x).
    """
    return bearing(interceptor_pos, target_pos)
