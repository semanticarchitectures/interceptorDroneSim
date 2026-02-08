"""Post-run analysis charts: trajectory, timeline, engagement metrics."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from interceptor_sim.core.engine import SimHistory
from interceptor_sim.engagement.kill_chain import EngagementManager, Phase
from interceptor_sim.utils.geometry import distance


def plot_trajectories(
    history: SimHistory,
    sensor_position: np.ndarray | None = None,
    save_path: str | Path | None = None,
) -> None:
    """Plot 2D trajectories of target and interceptor."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect("equal")

    tgt_pos = history.target_positions
    int_pos = history.interceptor_positions

    ax.plot(tgt_pos[:, 0], tgt_pos[:, 1], "r-", linewidth=2, label="Target")
    ax.plot(int_pos[:, 0], int_pos[:, 1], "b-", linewidth=2, label="Interceptor")

    # Start markers
    ax.plot(tgt_pos[0, 0], tgt_pos[0, 1], "ro", markersize=10)
    ax.plot(int_pos[0, 0], int_pos[0, 1], "bs", markersize=10)

    # End markers
    ax.plot(tgt_pos[-1, 0], tgt_pos[-1, 1], "rx", markersize=12, markeredgewidth=3)
    ax.plot(int_pos[-1, 0], int_pos[-1, 1], "bx", markersize=12, markeredgewidth=3)

    if sensor_position is not None:
        ax.plot(
            sensor_position[0], sensor_position[1],
            "gD", markersize=10, label="Sensor",
        )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Engagement Trajectories")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_range_timeline(
    history: SimHistory,
    save_path: str | Path | None = None,
) -> None:
    """Plot range between target and interceptor over time."""
    fig, ax = plt.subplots(figsize=(10, 5))

    times = history.times
    tgt_pos = history.target_positions
    int_pos = history.interceptor_positions

    ranges = [distance(t, i) for t, i in zip(tgt_pos, int_pos)]

    ax.plot(times, ranges, "k-", linewidth=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Range (m)")
    ax.set_title("Target–Interceptor Range vs Time")
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_phase_timeline(
    history: SimHistory,
    engagement: EngagementManager,
    save_path: str | Path | None = None,
) -> None:
    """Plot engagement phase transitions over time."""
    fig, ax = plt.subplots(figsize=(10, 3))

    phase_colors = {
        Phase.SEARCH: "#aaaaaa",
        Phase.TRACK: "#ffcc00",
        Phase.CLASSIFY: "#ff9900",
        Phase.LAUNCH: "#ff3300",
        Phase.MIDCOURSE: "#3366ff",
        Phase.TERMINAL: "#9900ff",
        Phase.COMPLETE: "#00cc00",
    }

    # Build phase intervals from history
    phase_intervals: list[tuple[float, float, Phase]] = []
    current_phase = history.states[0].phase
    start_time = history.states[0].time
    for state in history.states[1:]:
        if state.phase != current_phase:
            phase_intervals.append((start_time, state.time, current_phase))
            current_phase = state.phase
            start_time = state.time
    phase_intervals.append((start_time, history.states[-1].time, current_phase))

    for t_start, t_end, phase in phase_intervals:
        ax.barh(
            0, t_end - t_start, left=t_start, height=0.5,
            color=phase_colors.get(phase, "#cccccc"),
            edgecolor="black", linewidth=0.5,
        )
        if t_end - t_start > 0.5:
            ax.text(
                (t_start + t_end) / 2, 0, phase.name,
                ha="center", va="center", fontsize=8, fontweight="bold",
            )

    ax.set_xlabel("Time (s)")
    ax.set_yticks([])
    ax.set_title("Engagement Phase Timeline")

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def print_summary(history: SimHistory, engagement: EngagementManager) -> None:
    """Print engagement summary metrics to console."""
    final = history.states[-1]
    final_range = distance(final.target_pos, final.interceptor_pos)

    print("=" * 50)
    print("ENGAGEMENT SUMMARY")
    print("=" * 50)
    print(f"  Result:          {engagement.result.name}")
    print(f"  Duration:        {final.time:.1f} s")
    print(f"  Final range:     {final_range:.1f} m")
    print("  Phase log:")
    for t, phase in engagement.phase_log:
        print(f"    {t:6.1f}s → {phase.name}")
    print("=" * 50)
