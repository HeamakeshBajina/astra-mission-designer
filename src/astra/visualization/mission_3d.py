"""Mission-aware 3D visualization for ASTRA."""

from dataclasses import dataclass

import plotly.graph_objects as go

from astra.mission.mission_execution import MissionExecutionResult
from astra.mission.mission_timeline import MissionEventType


@dataclass(frozen=True)
class MissionVisualizationData:
    """Prepared data for visualizing an executed mission."""

    trajectory: tuple[tuple[float, float, float], ...]
    burn_points: tuple[tuple[float, float, float], ...]
    coast_points: tuple[tuple[float, float, float], ...]
    burn_directions: tuple[tuple[float, float, float], ...]
    event_names: tuple[str, ...]
    event_times: tuple[float, ...]


def prepare_mission_visualization(
    result: MissionExecutionResult,
) -> MissionVisualizationData:
    """Extract mission-aware visualization data from an execution result."""

    trajectory = tuple(
        (
            point.state.x,
            point.state.y,
            point.state.z,
        )
        for point in result.history.points
    )

    burn_points: list[tuple[float, float, float]] = []
    coast_points: list[tuple[float, float, float]] = []
    burn_directions: list[tuple[float, float, float]] = []
    event_names: list[str] = []
    event_times: list[float] = []

    points_by_time = {
        point.time: point
        for point in result.history.points
    }

    for event in result.events:
        event_names.append(event.name)
        event_times.append(event.start_time)

        matching_point = points_by_time.get(event.start_time)

        if matching_point is None:
            matching_point = min(
                result.history.points,
                key=lambda point: abs(
                    point.time - event.start_time
                ),
            )

        position = (
            matching_point.state.x,
            matching_point.state.y,
            matching_point.state.z,
        )

        if event.event_type == MissionEventType.BURN:
            burn_points.append(position)
        else:
            coast_points.append(position)

    for event, execution_event in zip(
        result.events,
        result.events,
    ):
        if event.event_type != MissionEventType.BURN:
            continue

        matching_point = points_by_time.get(event.start_time)

        if matching_point is None:
            matching_point = min(
                result.history.points,
                key=lambda point: abs(
                    point.time - event.start_time
                ),
            )

        velocity = (
            matching_point.state.vx,
            matching_point.state.vy,
            matching_point.state.vz,
        )

        speed = (
            velocity[0] ** 2
            + velocity[1] ** 2
            + velocity[2] ** 2
        ) ** 0.5

        if speed > 0:
            burn_directions.append(
                (
                    velocity[0] / speed,
                    velocity[1] / speed,
                    velocity[2] / speed,
                )
            )
        else:
            burn_directions.append(
                (0.0, 0.0, 0.0)
            )

    return MissionVisualizationData(
        trajectory=trajectory,
        burn_points=tuple(burn_points),
        coast_points=tuple(coast_points),
        burn_directions=tuple(burn_directions),
        event_names=tuple(event_names),
        event_times=tuple(event_times),
    )


def create_mission_3d_figure(
    result: MissionExecutionResult,
    earth_radius: float = 6_371_000.0,
) -> go.Figure:
    """Create an interactive 3D mission-execution visualization."""

    if earth_radius <= 0:
        raise ValueError(
            "Earth radius must be greater than zero."
        )

    data = prepare_mission_visualization(result)

    figure = go.Figure()

    figure.add_trace(
        go.Scatter3d(
            x=[
                position[0]
                for position in data.trajectory
            ],
            y=[
                position[1]
                for position in data.trajectory
            ],
            z=[
                position[2]
                for position in data.trajectory
            ],
            mode="lines",
            name="Spacecraft trajectory",
            hovertemplate=(
                "x=%{x:.3e} m<br>"
                "y=%{y:.3e} m<br>"
                "z=%{z:.3e} m"
                "<extra>Trajectory</extra>"
            ),
        )
    )

    if data.burn_points:
        figure.add_trace(
            go.Scatter3d(
                x=[
                    position[0]
                    for position in data.burn_points
                ],
                y=[
                    position[1]
                    for position in data.burn_points
                ],
                z=[
                    position[2]
                    for position in data.burn_points
                ],
                mode="markers",
                name="Burn events",
                marker={"size": 6},
                text=[
                    name
                    for name, event in zip(
                        data.event_names,
                        result.events,
                    )
                    if event.event_type
                    == MissionEventType.BURN
                ],
                hovertemplate=(
                    "%{text}<br>"
                    "x=%{x:.3e} m<br>"
                    "y=%{y:.3e} m<br>"
                    "z=%{z:.3e} m"
                    "<extra>Burn</extra>"
                ),
            )
        )

    if data.coast_points:
        figure.add_trace(
            go.Scatter3d(
                x=[
                    position[0]
                    for position in data.coast_points
                ],
                y=[
                    position[1]
                    for position in data.coast_points
                ],
                z=[
                    position[2]
                    for position in data.coast_points
                ],
                mode="markers",
                name="Coast events",
                marker={"size": 4},
                hovertemplate=(
                    "x=%{x:.3e} m<br>"
                    "y=%{y:.3e} m<br>"
                    "z=%{z:.3e} m"
                    "<extra>Coast</extra>"
                ),
            )
        )

    if data.trajectory:
        start = data.trajectory[0]
        end = data.trajectory[-1]

        figure.add_trace(
            go.Scatter3d(
                x=[start[0]],
                y=[start[1]],
                z=[start[2]],
                mode="markers",
                name="Mission start",
                marker={"size": 7},
            )
        )

        figure.add_trace(
            go.Scatter3d(
                x=[end[0]],
                y=[end[1]],
                z=[end[2]],
                mode="markers",
                name="Mission end",
                marker={"size": 7},
            )
        )

    figure.update_layout(
        title="ASTRA Mission Execution",
        scene={
            "xaxis_title": "X position (m)",
            "yaxis_title": "Y position (m)",
            "zaxis_title": "Z position (m)",
            "aspectmode": "data",
        },
        legend_title="Mission Elements",
    )

    return figure
