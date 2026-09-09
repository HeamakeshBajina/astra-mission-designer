"""Interactive three-dimensional orbit visualization for ASTRA."""

from __future__ import annotations

from collections.abc import Sequence
import math

import plotly.graph_objects as go

from astra.simulation.trajectory_history import TrajectoryHistory


def _sample_indices(
    count: int,
    max_points: int,
) -> list[int]:
    """Return evenly distributed trajectory indices."""

    if count <= 0:
        raise ValueError(
            "Trajectory point count must be greater than zero."
        )

    if max_points <= 0:
        raise ValueError(
            "Maximum trajectory points must be greater than zero."
        )

    if count <= max_points:
        return list(range(count))

    if max_points == 1:
        return [0]

    return [
        round(
            index * (count - 1)
            / (max_points - 1)
        )
        for index in range(max_points)
    ]


def _earth_surface(
    radius: float,
    resolution: int = 30,
) -> tuple[
    list[list[float]],
    list[list[float]],
    list[list[float]],
]:
    """Generate Cartesian coordinates for a spherical Earth."""

    if radius <= 0:
        raise ValueError(
            "Earth radius must be greater than zero."
        )

    if resolution < 4:
        raise ValueError(
            "Earth resolution must be at least four."
        )

    theta_values = [
        math.pi * index / (resolution - 1)
        for index in range(resolution)
    ]

    phi_values = [
        2.0 * math.pi * index / (resolution - 1)
        for index in range(resolution)
    ]

    x_values: list[list[float]] = []
    y_values: list[list[float]] = []
    z_values: list[list[float]] = []

    for theta in theta_values:
        x_row: list[float] = []
        y_row: list[float] = []
        z_row: list[float] = []

        for phi in phi_values:
            x_row.append(
                radius
                * math.sin(theta)
                * math.cos(phi)
            )
            y_row.append(
                radius
                * math.sin(theta)
                * math.sin(phi)
            )
            z_row.append(
                radius
                * math.cos(theta)
            )

        x_values.append(x_row)
        y_values.append(y_row)
        z_values.append(z_row)

    return (
        x_values,
        y_values,
        z_values,
    )


def _validate_trajectory(
    history: TrajectoryHistory,
) -> None:
    """Validate a trajectory before visualization."""

    if history.point_count <= 0:
        raise ValueError(
            "Trajectory history cannot be empty."
        )

    if history.final_time < 0:
        raise ValueError(
            "Trajectory final time cannot be negative."
        )


def create_orbit_3d_figure(
    history: TrajectoryHistory,
    earth_radius: float = 6_371_000.0,
    max_trajectory_points: int = 2_000,
    earth_resolution: int = 30,
) -> go.Figure:
    """Create an interactive 3D orbit figure.

    Parameters
    ----------
    history:
        Complete ASTRA trajectory history.

    earth_radius:
        Earth radius in metres.

    max_trajectory_points:
        Maximum number of trajectory points rendered.

    earth_resolution:
        Resolution used to generate the Earth sphere.

    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly 3D figure.
    """

    _validate_trajectory(history)

    indices = _sample_indices(
        history.point_count,
        max_trajectory_points,
    )

    positions = history.positions

    x_values = [
        positions[index][0]
        for index in indices
    ]
    y_values = [
        positions[index][1]
        for index in indices
    ]
    z_values = [
        positions[index][2]
        for index in indices
    ]

    earth_x, earth_y, earth_z = _earth_surface(
        earth_radius,
        earth_resolution,
    )

    figure = go.Figure()

    figure.add_trace(
        go.Surface(
            x=earth_x,
            y=earth_y,
            z=earth_z,
            name="Earth",
            hoverinfo="name",
            showscale=False,
        )
    )

    figure.add_trace(
        go.Scatter3d(
            x=x_values,
            y=y_values,
            z=z_values,
            mode="lines",
            name="Trajectory",
            hovertemplate=(
                "X: %{x:.3e} m"
                "<br>Y: %{y:.3e} m"
                "<br>Z: %{z:.3e} m"
                "<extra>Trajectory</extra>"
            ),
        )
    )

    initial_position = positions[0]
    final_position = positions[-1]

    figure.add_trace(
        go.Scatter3d(
            x=[initial_position[0]],
            y=[initial_position[1]],
            z=[initial_position[2]],
            mode="markers",
            marker={"size": 6},
            name="Start",
            hovertemplate=(
                "T+0 s"
                "<extra>Start</extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter3d(
            x=[final_position[0]],
            y=[final_position[1]],
            z=[final_position[2]],
            mode="markers",
            marker={"size": 7},
            name="Spacecraft",
            hovertemplate=(
                "T+%{customdata:.2f} s"
                "<extra>Spacecraft</extra>"
            ),
            customdata=[history.final_time],
        )
    )

    figure.update_layout(
        title="ASTRA 3D Orbital Trajectory",
        scene={
            "xaxis_title": "X (m)",
            "yaxis_title": "Y (m)",
            "zaxis_title": "Z (m)",
            "aspectmode": "data",
        },
        margin={
            "l": 0,
            "r": 0,
            "t": 50,
            "b": 0,
        },
    )

    return figure


def trajectory_coordinates(
    history: TrajectoryHistory,
    max_points: int = 2_000,
) -> tuple[
    tuple[float, float, float],
    ...,
]:
    """Return sampled trajectory coordinates."""

    _validate_trajectory(history)

    indices = _sample_indices(
        history.point_count,
        max_points,
    )

    return tuple(
        history.positions[index]
        for index in indices
    )
