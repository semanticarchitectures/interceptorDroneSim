#!/usr/bin/env python3
"""CLI entry point for running interceptor drone simulations."""

from __future__ import annotations

import argparse
import sys

from interceptor_sim.core.scenario import load_scenario, build_from_scenario
from interceptor_sim.visualization.live_display import LiveDisplay
from interceptor_sim.visualization.post_analysis import (
    plot_trajectories,
    plot_range_timeline,
    plot_phase_timeline,
    print_summary,
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run an interceptor drone engagement simulation."
    )
    parser.add_argument("scenario", help="Path to YAML scenario file")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--live", action="store_true", help="Show live animation"
    )
    parser.add_argument(
        "--no-plots", action="store_true", help="Skip post-run plots"
    )
    args = parser.parse_args(argv)

    scenario = load_scenario(args.scenario)
    engine, meta = build_from_scenario(scenario, seed=args.seed)

    if args.live:
        display = LiveDisplay(engine)
        display.run()
    else:
        history = engine.run()

    # Post-run output
    if not args.live:
        print_summary(history, meta["engagement"])

        if not args.no_plots:
            plot_trajectories(history, sensor_position=meta["sensor_position"])
            plot_range_timeline(history)
            plot_phase_timeline(history, meta["engagement"])


if __name__ == "__main__":
    main()
