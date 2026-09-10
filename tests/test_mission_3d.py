"""Tests for ASTRA mission-aware 3D visualization."""

import pytest

from astra.mission.mission_execution import (
    ExecutedMissionEvent,
    MissionExecutionResult,
)
from astra.mission.mission_timeline import MissionEventType
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.trajectory_history import (
    TrajectoryHistory,
    TrajectoryPoint,
)
from astra.visualization.mission_3d import (
    MissionVisualizationData,
    create_mission_3d_figure,
    prepare_mission_visualization,
)


def make_result(
    *,
    include_j2: bool = False,
) -> MissionExecutionResult:
    """Create a small deterministic mission result for visualization tests."""

    state_0 = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=1000.0,
    )

    state_1 = State3DThrust(
        x=7_000_100.0,
        y=7_500.0,
        z=100.0,
        vx=-10.0,
        vy=7_500.0,
        vz=5.0,
        mass=990.0,
    )

    state_2 = State3DThrust(
        x=7_000_200.0,
        y=15_000.0,
        z=200.0,
        vx=-20.0,
        vy=7_490.0,
        vz=10.0,
        mass=990.0,
    )

    history = TrajectoryHistory(
        points=(
            TrajectoryPoint(
                time=0.0,
                state=state_0,
            ),
            TrajectoryPoint(
                time=10.0,
                state=state_1,
            ),
            TrajectoryPoint(
                time=20.0,
                state=state_2,
            ),
        ),
        timestep=10.0,
        duration=20.0,
        include_j2=include_j2,
    )

    events = (
        ExecutedMissionEvent(
            name="Main burn",
            event_type=MissionEventType.BURN,
            start_time=10.0,
            end_time=15.0,
            initial_mass=1000.0,
            final_mass=990.0,
            propellant_consumed=10.0,
        ),
        ExecutedMissionEvent(
            name="Coast",
            event_type=MissionEventType.COAST,
            start_time=15.0,
            end_time=20.0,
            initial_mass=990.0,
            final_mass=990.0,
            propellant_consumed=0.0,
        ),
    )

    return MissionExecutionResult(
        initial_state=state_0,
        final_state=state_2,
        history=history,
        events=events,
        include_j2=include_j2,
    )


def test_prepare_returns_visualization_data() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert isinstance(data, MissionVisualizationData)


def test_trajectory_contains_all_history_positions() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert len(data.trajectory) == 3
    assert data.trajectory[0] == (
        7_000_000.0,
        0.0,
        0.0,
    )


def test_burn_event_is_extracted() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert len(data.burn_points) == 1


def test_coast_event_is_extracted() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert len(data.coast_points) == 1


def test_event_names_are_preserved() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert data.event_names == (
        "Main burn",
        "Coast",
    )


def test_event_times_are_preserved() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert data.event_times == (
        10.0,
        15.0,
    )


def test_burn_direction_is_unit_velocity_direction() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    direction = data.burn_directions[0]

    magnitude = sum(
        component * component
        for component in direction
    ) ** 0.5

    assert magnitude == pytest.approx(1.0)


def test_zero_velocity_produces_zero_burn_direction() -> None:
    result = make_result()

    zero_state = State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=0.0,
        vz=0.0,
        mass=1000.0,
    )

    history = TrajectoryHistory(
        points=(
            TrajectoryPoint(
                time=0.0,
                state=zero_state,
            ),
        ),
        timestep=1.0,
        duration=0.0,
        include_j2=False,
    )

    zero_result = MissionExecutionResult(
        initial_state=zero_state,
        final_state=zero_state,
        history=history,
        events=(
            ExecutedMissionEvent(
                name="Zero velocity burn",
                event_type=MissionEventType.BURN,
                start_time=0.0,
                end_time=0.0,
                initial_mass=1000.0,
                final_mass=1000.0,
                propellant_consumed=0.0,
            ),
        ),
        include_j2=False,
    )

    data = prepare_mission_visualization(zero_result)

    assert data.burn_directions == (
        (0.0, 0.0, 0.0),
    )


def test_create_figure_returns_plotly_figure() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    assert figure is not None
    assert hasattr(figure, "data")
    assert hasattr(figure, "layout")


def test_figure_contains_trajectory_trace() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    names = [
        trace.name
        for trace in figure.data
    ]

    assert "Spacecraft trajectory" in names


def test_figure_contains_burn_trace() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    names = [
        trace.name
        for trace in figure.data
    ]

    assert "Burn events" in names


def test_figure_contains_coast_trace() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    names = [
        trace.name
        for trace in figure.data
    ]

    assert "Coast events" in names


def test_figure_contains_start_and_end() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    names = [
        trace.name
        for trace in figure.data
    ]

    assert "Mission start" in names
    assert "Mission end" in names


def test_figure_has_three_dimensional_scene() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    assert figure.layout.scene is not None


def test_custom_earth_radius_is_accepted() -> None:
    result = make_result()

    figure = create_mission_3d_figure(
        result,
        earth_radius=6_400_000.0,
    )

    assert figure is not None


def test_invalid_earth_radius_is_rejected() -> None:
    result = make_result()

    with pytest.raises(ValueError):
        create_mission_3d_figure(
            result,
            earth_radius=0.0,
        )


def test_j2_execution_result_is_supported() -> None:
    result = make_result(include_j2=True)

    data = prepare_mission_visualization(result)

    assert len(data.trajectory) == 3


def test_empty_events_still_visualize_trajectory() -> None:
    result = make_result()

    empty_result = MissionExecutionResult(
        initial_state=result.initial_state,
        final_state=result.final_state,
        history=result.history,
        events=(),
        include_j2=result.include_j2,
    )

    data = prepare_mission_visualization(empty_result)

    assert len(data.trajectory) == 3
    assert data.burn_points == ()
    assert data.coast_points == ()


def test_visualization_preserves_absolute_history_times() -> None:
    result = make_result()

    data = prepare_mission_visualization(result)

    assert data.event_times[0] == 10.0
    assert data.event_times[1] == 15.0


def test_figure_has_expected_number_of_traces() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    assert len(figure.data) == 5


def test_figure_title_identifies_ast_ra_mission() -> None:
    result = make_result()

    figure = create_mission_3d_figure(result)

    assert figure.layout.title.text == "ASTRA Mission Execution"
