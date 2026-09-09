"""Tests for ASTRA three-dimensional orbit visualization."""

import math

import plotly.graph_objects as go
import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.constants import EARTH_MU
from astra.physics.thrust import ThrustModel
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.trajectory_history import simulate_trajectory
from astra.visualization.orbit_3d import (
    _earth_surface,
    _sample_indices,
    create_orbit_3d_figure,
    trajectory_coordinates,
)


EARTH_RADIUS = 6_371_000.0


def circular_state(
    altitude: float = 400_000.0,
) -> State3DThrust:
    """Return a circular equatorial orbit state."""

    radius = EARTH_RADIUS + altitude
    velocity = math.sqrt(
        EARTH_MU / radius
    )

    return State3DThrust(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
        mass=500.0,
    )


def zero_thrust() -> ThrustModel:
    """Return a zero-thrust propulsion model."""

    return ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )


def make_history(
    duration: float = 10.0,
    timestep: float = 1.0,
):
    """Create a test trajectory history."""

    return simulate_trajectory(
        initial_state=circular_state(),
        duration=duration,
        timestep=timestep,
        thrust_model=zero_thrust(),
        thrust_direction=BurnVector(
            1.0,
            0.0,
            0.0,
        ),
    )


def test_sample_indices_returns_all_indices_when_small() -> None:
    """Small trajectories should not be downsampled."""

    assert _sample_indices(
        count=5,
        max_points=10,
    ) == [0, 1, 2, 3, 4]


def test_sample_indices_limits_large_trajectory() -> None:
    """Large trajectories should be reduced to the requested limit."""

    indices = _sample_indices(
        count=100,
        max_points=10,
    )

    assert len(indices) == 10
    assert indices[0] == 0
    assert indices[-1] == 99
    assert indices == sorted(indices)


def test_sample_indices_rejects_invalid_count() -> None:
    """Zero trajectory points must be rejected."""

    with pytest.raises(
        ValueError,
        match="count",
    ):
        _sample_indices(
            count=0,
            max_points=10,
        )


def test_sample_indices_rejects_invalid_maximum() -> None:
    """Zero maximum points must be rejected."""

    with pytest.raises(
        ValueError,
        match="Maximum",
    ):
        _sample_indices(
            count=10,
            max_points=0,
        )


def test_earth_surface_has_expected_dimensions() -> None:
    """Earth surface arrays should have the requested resolution."""

    x_values, y_values, z_values = _earth_surface(
        radius=EARTH_RADIUS,
        resolution=10,
    )

    assert len(x_values) == 10
    assert len(y_values) == 10
    assert len(z_values) == 10

    assert all(
        len(row) == 10
        for row in x_values
    )

    assert all(
        len(row) == 10
        for row in y_values
    )

    assert all(
        len(row) == 10
        for row in z_values
    )


def test_earth_surface_points_have_requested_radius() -> None:
    """Generated Earth coordinates should lie on the sphere."""

    x_values, y_values, z_values = _earth_surface(
        radius=EARTH_RADIUS,
        resolution=12,
    )

    for x_row, y_row, z_row in zip(
        x_values,
        y_values,
        z_values,
    ):
        for x, y, z in zip(
            x_row,
            y_row,
            z_row,
        ):
            radius = math.sqrt(
                x * x
                + y * y
                + z * z
            )

            assert radius == pytest.approx(
                EARTH_RADIUS,
                rel=1e-12,
            )


def test_earth_surface_rejects_invalid_radius() -> None:
    """A non-positive Earth radius must be rejected."""

    with pytest.raises(
        ValueError,
        match="radius",
    ):
        _earth_surface(
            radius=0.0,
            resolution=10,
        )


def test_earth_surface_rejects_low_resolution() -> None:
    """Earth resolution must be sufficient to form a surface."""

    with pytest.raises(
        ValueError,
        match="resolution",
    ):
        _earth_surface(
            radius=EARTH_RADIUS,
            resolution=3,
        )


def test_figure_is_plotly_figure() -> None:
    """Visualization should return a Plotly Figure."""

    figure = create_orbit_3d_figure(
        make_history()
    )

    assert isinstance(
        figure,
        go.Figure,
    )


def test_figure_contains_earth_trajectory_start_and_spacecraft() -> None:
    """The figure should contain the core mission visualization traces."""

    figure = create_orbit_3d_figure(
        make_history()
    )

    names = [
        trace.name
        for trace in figure.data
    ]

    assert "Earth" in names
    assert "Trajectory" in names
    assert "Start" in names
    assert "Spacecraft" in names


def test_figure_contains_three_dimensional_traces() -> None:
    """Trajectory and marker traces must be 3D."""

    figure = create_orbit_3d_figure(
        make_history()
    )

    scatter_traces = [
        trace
        for trace in figure.data
        if isinstance(
            trace,
            go.Scatter3d,
        )
    ]

    assert len(scatter_traces) == 3


def test_figure_uses_data_aspect_mode() -> None:
    """The 3D scene should preserve spatial proportions."""

    figure = create_orbit_3d_figure(
        make_history()
    )

    assert (
        figure.layout.scene.aspectmode
        == "data"
    )


def test_figure_uses_requested_trajectory_limit() -> None:
    """Visualization should respect the trajectory sampling limit."""

    history = make_history(
        duration=100.0,
        timestep=1.0,
    )

    figure = create_orbit_3d_figure(
        history,
        max_trajectory_points=10,
    )

    trajectory = next(
        trace
        for trace in figure.data
        if trace.name == "Trajectory"
    )

    assert len(trajectory.x) == 10


def test_trajectory_coordinates_returns_positions() -> None:
    """Coordinate extraction should match trajectory positions."""

    history = make_history(
        duration=4.0,
        timestep=1.0,
    )

    coordinates = trajectory_coordinates(
        history,
        max_points=10,
    )

    assert coordinates == history.positions


def test_trajectory_coordinates_can_downsample() -> None:
    """Coordinate extraction should support large trajectories."""

    history = make_history(
        duration=20.0,
        timestep=1.0,
    )

    coordinates = trajectory_coordinates(
        history,
        max_points=5,
    )

    assert len(coordinates) == 5
    assert coordinates[0] == history.positions[0]
    assert coordinates[-1] == history.positions[-1]


def test_figure_uses_history_final_time_for_spacecraft() -> None:
    """The spacecraft marker should expose its mission time."""

    history = make_history(
        duration=12.5,
        timestep=1.0,
    )

    figure = create_orbit_3d_figure(history)

    spacecraft = next(
        trace
        for trace in figure.data
        if trace.name == "Spacecraft"
    )

    assert spacecraft.customdata[0] == pytest.approx(
        12.5
    )


def test_figure_accepts_j2_history() -> None:
    """The visualization should accept J2 trajectory histories."""

    from astra.simulation.trajectory_history import (
        simulate_trajectory_j2,
    )

    history = simulate_trajectory_j2(
        initial_state=circular_state(),
        duration=5.0,
        timestep=1.0,
        thrust_model=zero_thrust(),
        thrust_direction=BurnVector(
            1.0,
            0.0,
            0.0,
        ),
    )

    figure = create_orbit_3d_figure(history)

    assert isinstance(
        figure,
        go.Figure,
    )
    assert len(figure.data) == 4
