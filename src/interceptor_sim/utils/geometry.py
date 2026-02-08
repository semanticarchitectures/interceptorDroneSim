"""2D vector math, LOS angles, and range calculations."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Vec2 = NDArray[np.floating]


def distance(a: Vec2, b: Vec2) -> float:
    """Euclidean distance between two 2D points."""
    return float(np.linalg.norm(b - a))


def bearing(from_pt: Vec2, to_pt: Vec2) -> float:
    """Bearing angle (radians) from *from_pt* to *to_pt*, measured CCW from +x."""
    delta = to_pt - from_pt
    return float(np.arctan2(delta[1], delta[0]))


def unit_vector(angle: float) -> Vec2:
    """Unit vector in direction *angle* (radians, CCW from +x)."""
    return np.array([np.cos(angle), np.sin(angle)], dtype=np.float64)


def wrap_angle(angle: float) -> float:
    """Wrap angle to [-pi, pi]."""
    return float((angle + np.pi) % (2 * np.pi) - np.pi)


def closing_speed(
    pos_a: Vec2, vel_a: Vec2, pos_b: Vec2, vel_b: Vec2
) -> float:
    """Closing speed along the line of sight (positive = closing)."""
    los = pos_b - pos_a
    los_dist = np.linalg.norm(los)
    if los_dist < 1e-9:
        return 0.0
    los_unit = los / los_dist
    return float(np.dot(vel_a - vel_b, los_unit))


def line_of_sight_rate(
    pos_a: Vec2, vel_a: Vec2, pos_b: Vec2, vel_b: Vec2
) -> float:
    """Line-of-sight angular rate (rad/s)."""
    rel_pos = pos_b - pos_a
    rel_vel = vel_b - vel_a
    r_sq = np.dot(rel_pos, rel_pos)
    if r_sq < 1e-9:
        return 0.0
    # LOS rate = (r x v) / |r|^2  (scalar in 2D)
    cross = rel_pos[0] * rel_vel[1] - rel_pos[1] * rel_vel[0]
    return float(cross / r_sq)
