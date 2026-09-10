"""Tests for ASTRA mission execution."""

import math

import pytest

from astra.physics.burn_vector import BurnVector
from astra.physics.thrust import ThrustModel
from astra.mission.mission_execution import (
    ExecutedMissionEvent,
    MissionExecutionEvent,
    MissionExecutionPlan,
    create_execution_plan_from_timeline,
    create_mission_execution_plan,
    execute_mission,
)
from astra.mission.mission_timeline import (
    MissionEvent,
    MissionEventType,
    create_mission_timeline,
)
from astra.simulation.propagator_3d_thrust import State3DThrust


EARTH_RADIUS = 6_371_000.0
EARTH_MU = 3.986004418e14


def circular_state(
    mass: float = 500.0,
) -> State3DThrust:
    """Create a circular low-Earth-orbit test state."""

    radius = EARTH_RADIUS + 400_000.0
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
        mass=mass,
    )


def burn_configuration(
    event: MissionEvent,
    thrust: float = 100.0,
    duration: float | None = None,
    dry_mass: float = 400.0,
) -> MissionExecutionEvent:
    """Create a standard test burn configuration."""

    actual_duration = (
        event.duration
        if duration is None
        else duration
    )

    adjusted_event = MissionEvent(
        name=event.name,
        start_time=event.start_time,
        duration=actual_duration,
        event_type=event.event_type,
    )

    return MissionExecutionEvent(
        event=adjusted_event,
        thrust_model=ThrustModel(
            thrust=thrust,
            specific_impulse=300.0,
        ),
        burn_direction=BurnVector(
            0.0,
            1.0,
            0.0,
        ),
        dry_mass=dry_mass,
    )


def test_execution_event_requires_burn_configuration() -> None:
    """Burn events require propulsion configuration."""

    event = MissionEvent(
        name="Burn 1",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    with pytest.raises(
        ValueError,
        match="thrust model",
    ):
        MissionExecutionEvent(event=event)


def test_execution_event_rejects_zero_burn_direction() -> None:
    """Burn events reject a zero direction."""

    event = MissionEvent(
        name="Burn 1",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    with pytest.raises(
        ValueError,
        match="zero vector",
    ):
        MissionExecutionEvent(
            event=event,
            thrust_model=ThrustModel(
                thrust=100.0,
                specific_impulse=300.0,
            ),
            burn_direction=BurnVector(
                0.0,
                0.0,
                0.0,
            ),
            dry_mass=400.0,
        )


def test_coast_event_needs_no_propulsion_configuration() -> None:
    """Coast events can be represented without propulsion parameters."""

    event = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    execution_event = MissionExecutionEvent(
        event=event,
    )

    assert execution_event.event == event


def test_plan_rejects_empty_events() -> None:
    """Execution plans cannot be empty."""

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        MissionExecutionPlan(events=())


def test_plan_counts_events() -> None:
    """Execution plan exposes burn and coast counts."""

    burn = MissionEvent(
        name="Burn",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    coast = MissionEvent(
        name="Coast",
        start_time=10.0,
        duration=20.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(burn),
            MissionExecutionEvent(
                event=coast,
            ),
        ]
    )

    assert plan.event_count == 2
    assert plan.burn_count == 1
    assert plan.coast_count == 1
    assert plan.duration == 30.0


def test_plan_rejects_overlapping_events() -> None:
    """Execution plans reject overlapping events."""

    first = MissionEvent(
        name="First",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.COAST,
    )

    second = MissionEvent(
        name="Second",
        start_time=10.0,
        duration=20.0,
        event_type=MissionEventType.COAST,
    )

    with pytest.raises(
        ValueError,
        match="cannot overlap",
    ):
        create_mission_execution_plan(
            [
                MissionExecutionEvent(event=first),
                MissionExecutionEvent(event=second),
            ]
        )


def test_timeline_can_be_converted_to_execution_plan() -> None:
    """Timeline events receive executable configurations."""

    burn = MissionEvent(
        name="Injection",
        start_time=0.0,
        duration=5.0,
        event_type=MissionEventType.BURN,
    )

    coast = MissionEvent(
        name="Transfer coast",
        start_time=5.0,
        duration=50.0,
        event_type=MissionEventType.COAST,
    )

    timeline = create_mission_timeline(
        [
            burn,
            coast,
        ]
    )

    plan = create_execution_plan_from_timeline(
        timeline,
        {
            "Injection": burn_configuration(burn),
        },
    )

    assert plan.event_count == 2
    assert plan.burn_count == 1
    assert plan.coast_count == 1


def test_missing_burn_configuration_is_rejected() -> None:
    """Timeline conversion requires every burn to be configured."""

    burn = MissionEvent(
        name="Injection",
        start_time=0.0,
        duration=5.0,
        event_type=MissionEventType.BURN,
    )

    timeline = create_mission_timeline([burn])

    with pytest.raises(
        ValueError,
        match="Missing execution configuration",
    ):
        create_execution_plan_from_timeline(
            timeline,
            {},
        )


def test_zero_duration_mission_event_is_executable() -> None:
    """Zero-duration events are accepted."""

    coast = MissionEvent(
        name="Instant checkpoint",
        start_time=0.0,
        duration=0.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(
                event=coast,
            )
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    assert result.duration == 0.0
    assert result.event_count == 1


def test_coast_preserves_mass() -> None:
    """A coast event consumes no propellant."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=100.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(
                event=coast,
            )
        ]
    )

    initial = circular_state()

    result = execute_mission(
        initial_state=initial,
        plan=plan,
        timestep=10.0,
    )

    assert result.final_mass == pytest.approx(
        initial.mass
    )
    assert result.total_propellant_consumed == pytest.approx(
        0.0
    )


def test_burn_consumes_propellant() -> None:
    """A finite-thrust burn reduces spacecraft mass."""

    burn = MissionEvent(
        name="Burn",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(
                burn,
                thrust=100.0,
            )
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    assert result.final_mass < result.initial_state.mass
    assert result.total_propellant_consumed > 0.0


def test_burn_result_records_event_mass() -> None:
    """Executed events record initial and final mass."""

    burn = MissionEvent(
        name="Burn",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(burn)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    event_result = result.events[0]

    assert isinstance(
        event_result,
        ExecutedMissionEvent,
    )
    assert event_result.name == "Burn"
    assert event_result.initial_mass == pytest.approx(
        result.initial_state.mass
    )
    assert event_result.final_mass == pytest.approx(
        result.final_state.mass
    )
    assert event_result.propellant_consumed > 0.0


def test_mission_duration_matches_last_event() -> None:
    """Mission duration equals the final event end time."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=100.0,
        event_type=MissionEventType.COAST,
    )

    burn = MissionEvent(
        name="Burn",
        start_time=100.0,
        duration=25.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast),
            burn_configuration(burn),
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=5.0,
    )

    assert result.duration == pytest.approx(125.0)
    assert result.history.final_time == pytest.approx(
        125.0
    )


def test_mission_history_starts_at_zero() -> None:
    """Mission history always begins at t=0."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=50.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=5.0,
    )

    assert result.history.times[0] == 0.0


def test_mission_history_uses_absolute_event_times() -> None:
    """Segment history is translated to absolute mission time."""

    burn = MissionEvent(
        name="Burn",
        start_time=20.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(burn)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=5.0,
    )

    assert result.history.final_time == pytest.approx(
        30.0
    )
    assert result.events[0].start_time == pytest.approx(
        20.0
    )


def test_gap_between_events_becomes_coast() -> None:
    """Unscheduled gaps are automatically propagated as coasts."""

    first = MissionEvent(
        name="First coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    second = MissionEvent(
        name="Second coast",
        start_time=50.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=first),
            MissionExecutionEvent(event=second),
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=5.0,
    )

    assert result.duration == pytest.approx(
        60.0
    )
    assert result.final_mass == pytest.approx(
        result.initial_state.mass
    )


def test_multiple_burns_execute_sequentially() -> None:
    """Multiple burns are executed in chronological order."""

    first = MissionEvent(
        name="Burn 1",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    second = MissionEvent(
        name="Burn 2",
        start_time=20.0,
        duration=10.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(first),
            burn_configuration(
                second,
                thrust=50.0,
            ),
        ]
    )

    result = execute_mission(
        initial_state=circular_state(
            mass=600.0
        ),
        plan=plan,
        timestep=1.0,
    )

    assert result.event_count == 2
    assert result.final_mass < result.initial_state.mass
    assert result.events[0].name == "Burn 1"
    assert result.events[1].name == "Burn 2"
    assert (
        result.events[1].initial_mass
        < result.events[0].initial_mass
    )


def test_j2_execution_returns_j2_history() -> None:
    """J2-enabled execution records a J2 trajectory."""

    coast = MissionEvent(
        name="J2 coast",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=2.0,
        include_j2=True,
    )

    assert result.include_j2 is True
    assert result.history.include_j2 is True


def test_non_j2_execution_returns_central_gravity_history() -> None:
    """Default execution uses the central-gravity propagator."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=2.0,
        include_j2=False,
    )

    assert result.include_j2 is False
    assert result.history.include_j2 is False


def test_invalid_initial_mass_is_rejected() -> None:
    """Execution rejects non-positive spacecraft mass."""

    state = State3DThrust(
        x=EARTH_RADIUS + 400_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_668.0,
        vz=0.0,
        mass=0.0,
    )

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    with pytest.raises(
        ValueError,
        match="Initial spacecraft mass",
    ):
        execute_mission(
            initial_state=state,
            plan=plan,
        )


def test_invalid_timestep_is_rejected() -> None:
    """Execution rejects a non-positive timestep."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    with pytest.raises(
        ValueError,
        match="timestep",
    ):
        execute_mission(
            initial_state=circular_state(),
            plan=plan,
            timestep=0.0,
        )


def test_final_state_is_available() -> None:
    """Execution returns a complete final spacecraft state."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    assert result.final_state.x != 0.0
    assert result.final_state.mass > 0.0


def test_history_point_count_matches_executed_time_steps() -> None:
    """History contains the initial state plus propagated steps."""

    coast = MissionEvent(
        name="Coast",
        start_time=0.0,
        duration=10.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=coast)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=2.0,
    )

    assert result.history.point_count == 6


def test_total_propellant_equals_mass_difference() -> None:
    """Mission propellant accounting is internally consistent."""

    burn = MissionEvent(
        name="Burn",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.BURN,
    )

    plan = create_mission_execution_plan(
        [
            burn_configuration(burn)
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    expected = (
        result.initial_state.mass
        - result.final_state.mass
    )

    assert result.total_propellant_consumed == pytest.approx(
        expected
    )


def test_event_results_are_chronological() -> None:
    """Executed mission events preserve chronological order."""

    first = MissionEvent(
        name="First",
        start_time=0.0,
        duration=5.0,
        event_type=MissionEventType.COAST,
    )

    second = MissionEvent(
        name="Second",
        start_time=5.0,
        duration=5.0,
        event_type=MissionEventType.COAST,
    )

    plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(event=first),
            MissionExecutionEvent(event=second),
        ]
    )

    result = execute_mission(
        initial_state=circular_state(),
        plan=plan,
        timestep=1.0,
    )

    assert result.events[0].end_time <= (
        result.events[1].start_time
    )


def test_different_burn_directions_change_final_state() -> None:
    """Changing burn direction changes the spacecraft trajectory."""

    event = MissionEvent(
        name="Burn",
        start_time=0.0,
        duration=20.0,
        event_type=MissionEventType.BURN,
    )

    prograde_plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(
                event=event,
                thrust_model=ThrustModel(
                    thrust=100.0,
                    specific_impulse=300.0,
                ),
                burn_direction=BurnVector(
                    0.0,
                    1.0,
                    0.0,
                ),
                dry_mass=400.0,
            )
        ]
    )

    radial_plan = create_mission_execution_plan(
        [
            MissionExecutionEvent(
                event=event,
                thrust_model=ThrustModel(
                    thrust=100.0,
                    specific_impulse=300.0,
                ),
                burn_direction=BurnVector(
                    1.0,
                    0.0,
                    0.0,
                ),
                dry_mass=400.0,
            )
        ]
    )

    initial = circular_state()

    prograde_result = execute_mission(
        initial_state=initial,
        plan=prograde_plan,
        timestep=1.0,
    )

    radial_result = execute_mission(
        initial_state=initial,
        plan=radial_plan,
        timestep=1.0,
    )

    assert (
        prograde_result.final_state.vy
        != pytest.approx(
            radial_result.final_state.vy
        )
    )
