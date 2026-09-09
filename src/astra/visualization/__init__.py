"""Visualization utilities for ASTRA."""

import matplotlib.pyplot as plt

from astra.physics.constants import EARTH_RADIUS
from astra.simulation.trajectory import Trajectory
from astra.simulation.trajectory_analysis import analyze_trajectory


def plot_trajectory(trajectory: Trajectory):
    """Plot a spacecraft trajectory around Earth."""

    x_positions = [state.x for state in trajectory.states]
    y_positions = [state.y for state in trajectory.states]

    figure, axis = plt.subplots()

    axis.plot(
        x_positions,
        y_positions,
        label="Spacecraft trajectory",
    )

    earth = plt.Circle(
        (0, 0),
        EARTH_RADIUS,
        fill=True,
        alpha=0.35,
        label="Earth",
    )

    axis.add_patch(earth)

    axis.set_xlabel("X Position (m)")
    axis.set_ylabel("Y Position (m)")
    axis.set_title("ASTRA Spacecraft Trajectory")
    axis.set_aspect("equal")
    axis.legend()

    return figure, axis


def plot_trajectory_analysis(trajectory: Trajectory):
    """Plot altitude, speed, and orbital energy over time."""

    analysis = analyze_trajectory(trajectory)

    times = trajectory.times

    altitudes_km = [
        altitude / 1_000
        for altitude in analysis.altitudes
    ]

    speeds_km_s = [
        speed / 1_000
        for speed in analysis.speeds
    ]

    energies_mj_kg = [
        energy / 1_000_000
        for energy in analysis.specific_energies
    ]

    figure, axes = plt.subplots(3, 1, figsize=(9, 12))

    axes[0].plot(times, altitudes_km)
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Altitude (km)")
    axes[0].set_title("Altitude vs Time")
    axes[0].ticklabel_format(
        style="plain",
        axis="y",
        useOffset=False,
    )

    axes[1].plot(times, speeds_km_s)
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Speed (km/s)")
    axes[1].set_title("Speed vs Time")
    axes[1].ticklabel_format(
        style="plain",
        axis="y",
        useOffset=False,
    )

    axes[2].plot(times, energies_mj_kg)
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylabel("Specific Energy (MJ/kg)")
    axes[2].set_title("Specific Orbital Energy vs Time")
    axes[2].ticklabel_format(
        style="plain",
        axis="y",
        useOffset=False,
    )

    figure.tight_layout()

    return figure, axes
