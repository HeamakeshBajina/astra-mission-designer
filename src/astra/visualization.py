"""Visualization utilities for ASTRA."""

import matplotlib.pyplot as plt

from astra.simulation.trajectory import Trajectory


def plot_trajectory(trajectory: Trajectory):
    """Plot the spacecraft's 2D trajectory."""

    x_positions = [state.x for state in trajectory.states]
    y_positions = [state.y for state in trajectory.states]

    figure, axis = plt.subplots()

    axis.plot(x_positions, y_positions)
    axis.set_xlabel("X Position (m)")
    axis.set_ylabel("Y Position (m)")
    axis.set_title("ASTRA Spacecraft Trajectory")
    axis.set_aspect("equal")

    return figure, axis