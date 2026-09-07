"""Tests for multi-burn mission execution."""

import pytest

from astra.mission.burn_sequence import (
    MissionBurn,
    create_burn_sequence,
)
from astra.simulation.mission_executor import (
    execute_burn_sequence,
)
from astra.simulation.propagator import State


def test_mission_without_coasting_executes_burn():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Injection",
                time=0,
                delta_v=100,
                direction="prograde",
            )
        ]
    )

    result = execute_burn_sequence(
        initial_state,
        sequence,
    )

    final_state = result.states[-1]

    assert final_state.vy == pytest.approx(7_600)
    assert result.burn_indices == [0]


def test_mission_coasts_before_burn():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Delayed burn",
                time=100,
                delta_v=100,
                direction="prograde",
            )
        ]
    )

    result = execute_burn_sequence(
        initial_state,
        sequence,
        dt=10,
    )

    assert result.times[-1] == pytest.approx(100)
    assert result.states[-1].x != initial_state.x


def test_retrograde_burn_reduces_speed():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Retrograde burn",
                time=0,
                delta_v=200,
                direction="retrograde",
            )
        ]
    )

    result = execute_burn_sequence(
        initial_state,
        sequence,
    )

    final_state = result.states[-1]

    assert final_state.vy == pytest.approx(7_300)


def test_multiple_burns_execute_in_order():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Burn 1",
                time=0,
                delta_v=100,
                direction="prograde",
            ),
            MissionBurn(
                name="Burn 2",
                time=100,
                delta_v=200,
                direction="prograde",
            ),
        ]
    )

    result = execute_burn_sequence(
        initial_state,
        sequence,
        dt=10,
    )

    assert len(result.burn_indices) == 2
    assert result.times[-1] == pytest.approx(100)


def test_invalid_timestep_is_rejected():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Burn",
                time=0,
                delta_v=100,
                direction="prograde",
            )
        ]
    )

    with pytest.raises(ValueError):
        execute_burn_sequence(
            initial_state,
            sequence,
            dt=0,
        )


def test_invalid_burn_direction_is_rejected():
    initial_state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    sequence = create_burn_sequence(
        [
            MissionBurn(
                name="Invalid",
                time=0,
                delta_v=100,
                direction="sideways",
            )
        ]
    )

    with pytest.raises(ValueError):
        execute_burn_sequence(
            initial_state,
            sequence,
        )