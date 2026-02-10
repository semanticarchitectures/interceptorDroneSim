"""Real-time 2D matplotlib animation of the engagement."""

from __future__ import annotations

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from interceptor_sim.core.engine import SimulationEngine
from interceptor_sim.utils.geometry import distance


class LiveDisplay:
    """Animates the simulation in real time using matplotlib."""

    def __init__(
        self,
        engine: SimulationEngine,
        interval_ms: int = 50,
        launch_position: np.ndarray | None = None,
    ) -> None:
        self.engine = engine
        self.interval_ms = interval_ms
        self.steps_per_frame = max(1, int((interval_ms / 1000) / engine.dt))
        self.launch_position = launch_position

        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 8))
        self.ax.set_aspect("equal")
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_title("Interceptor Drone Engagement")
        self.ax.grid(True, alpha=0.3)

        # Plot elements
        (self.target_trail,) = self.ax.plot([], [], "r-", alpha=0.4, linewidth=1)
        (self.interceptor_trail,) = self.ax.plot([], [], "b-", alpha=0.4, linewidth=1)
        (self.estimated_trail,) = self.ax.plot(
            [], [], "r--", alpha=0.4, linewidth=1, label="Estimated Track"
        )
        (self.target_marker,) = self.ax.plot([], [], "r^", markersize=10, label="Target")
        (self.interceptor_marker,) = self.ax.plot(
            [], [], "bs", markersize=10, label="Interceptor"
        )
        self.sensor_marker = self.ax.plot(
            engine.engagement.sensor_position[0],
            engine.engagement.sensor_position[1],
            "gD",
            markersize=8,
            label="Sensor",
        )

        # Launch site marker (if different from sensor)
        if launch_position is not None:
            sensor_pos = engine.engagement.sensor_position
            if distance(launch_position, sensor_pos) > 1.0:
                self.ax.plot(
                    launch_position[0],
                    launch_position[1],
                    "b+",
                    markersize=10,
                    markeredgewidth=2,
                    label="Launch Site",
                )

        self.phase_text = self.ax.text(
            0.02, 0.98, "", transform=self.ax.transAxes,
            verticalalignment="top", fontsize=11, fontfamily="monospace",
        )

        self.ax.legend(loc="upper right")

        self._target_xs: list[float] = []
        self._target_ys: list[float] = []
        self._interceptor_xs: list[float] = []
        self._interceptor_ys: list[float] = []
        self._estimated_xs: list[float] = []
        self._estimated_ys: list[float] = []

    def _init_animation(self):
        self.target_trail.set_data([], [])
        self.interceptor_trail.set_data([], [])
        self.estimated_trail.set_data([], [])
        self.target_marker.set_data([], [])
        self.interceptor_marker.set_data([], [])
        self.phase_text.set_text("")
        return (
            self.target_trail, self.interceptor_trail, self.estimated_trail,
            self.target_marker, self.interceptor_marker,
            self.phase_text,
        )

    def _update_frame(self, frame):
        for _ in range(self.steps_per_frame):
            if not self.engine.step():
                break

        tgt = self.engine.target.position
        intc = self.engine.interceptor.position

        self._target_xs.append(tgt[0])
        self._target_ys.append(tgt[1])
        self._interceptor_xs.append(intc[0])
        self._interceptor_ys.append(intc[1])

        # Estimated target position trail
        est_pos = self.engine.engagement.estimated_target_pos
        if est_pos is not None:
            self._estimated_xs.append(est_pos[0])
            self._estimated_ys.append(est_pos[1])

        self.target_trail.set_data(self._target_xs, self._target_ys)
        self.interceptor_trail.set_data(self._interceptor_xs, self._interceptor_ys)
        self.estimated_trail.set_data(self._estimated_xs, self._estimated_ys)
        self.target_marker.set_data([tgt[0]], [tgt[1]])
        self.interceptor_marker.set_data([intc[0]], [intc[1]])

        phase = self.engine.engagement.phase
        result = self.engine.engagement.result
        true_range = distance(tgt, intc)
        info = (
            f"Time: {self.engine.time:.1f}s\n"
            f"Phase: {phase.name}\n"
            f"Result: {result.name}\n"
            f"True Range: {true_range:.0f}m"
        )
        if est_pos is not None:
            est_range = distance(intc, est_pos)
            info += f"\nEst Range:  {est_range:.0f}m"
        self.phase_text.set_text(info)

        # Auto-scale axes
        all_x = self._target_xs + self._interceptor_xs + self._estimated_xs
        all_y = self._target_ys + self._interceptor_ys + self._estimated_ys
        if all_x and all_y:
            margin = 200
            self.ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
            self.ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

        return (
            self.target_trail, self.interceptor_trail, self.estimated_trail,
            self.target_marker, self.interceptor_marker,
            self.phase_text,
        )

    def _total_frames(self) -> int:
        """Estimate total animation frames from sim duration."""
        total_steps = int(self.engine.max_time / self.engine.dt)
        return total_steps // self.steps_per_frame + 1

    def run(self) -> None:
        """Start the live animation (blocking)."""
        self._anim = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            init_func=self._init_animation,
            interval=self.interval_ms,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()

    def save(self, path: str, fps: int = 20, dpi: int = 150) -> None:
        """Save the animation to a video file (MP4 via ffmpeg or GIF)."""
        self._anim = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            init_func=self._init_animation,
            frames=self._total_frames(),
            interval=self.interval_ms,
            blit=False,
            cache_frame_data=False,
            repeat=False,
        )
        if path.endswith(".gif"):
            writer = animation.PillowWriter(fps=fps)
        else:
            writer = animation.FFMpegWriter(fps=fps)
        self._anim.save(path, writer=writer, dpi=dpi)
        print(f"Saved animation to {path}")
