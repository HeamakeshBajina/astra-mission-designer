import math

import pytest

from astra.simulation.burns import apply_prograde_burn
from astra.simulation.burns import apply_retrograde_burn
from astra.simulation.propagator import State


def test_prograde_burn_increases_velocity():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_prograde_burn(
        state,
        delta_v=100,
    )

    assert result.vx == pytest.approx(0)
    assert result.vy == pytest.approx(7_600)


def test_prograde_burn_preserves_position():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_prograde_burn(
        state,
        delta_v=100,
    )

    assert result.x == state.x
    assert result.y == state.y


def test_prograde_burn_increases_speed_by_delta_v():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_prograde_burn(
        state,
        delta_v=100,
    )

    initial_speed = math.hypot(
        state.vx,
        state.vy,
    )

    final_speed = math.hypot(
        result.vx,
        result.vy,
    )

    assert final_speed - initial_speed == pytest.approx(100)


def test_retrograde_burn_decreases_velocity():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_retrograde_burn(
        state,
        delta_v=100,
    )

    assert result.vx == pytest.approx(0)
    assert result.vy == pytest.approx(7_400)


def test_retrograde_burn_preserves_position():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_retrograde_burn(
        state,
        delta_v=100,
    )

    assert result.x == state.x
    assert result.y == state.y


def test_retrograde_burn_decreases_speed_by_delta_v():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    result = apply_retrograde_burn(
        state,
        delta_v=100,
    )

    initial_speed = math.hypot(
        state.vx,
        state.vy,
    )

    final_speed = math.hypot(
        result.vx,
        result.vy,
    )

    assert initial_speed - final_speed == pytest.approx(100)


def test_negative_delta_v_is_rejected():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=7_500,
    )

    with pytest.raises(ValueError):
        apply_prograde_burn(
            state,
            delta_v=-100,
        )

    with pytest.raises(ValueError):
        apply_retrograde_burn(
            state,
            delta_v=-100,
        )


def test_zero_velocity_is_rejected():
    state = State(
        x=7_000_000,
        y=0,
        vx=0,
        vy=0,
    )

    with pytest.raises(ValueError):
        apply_prograde_burn(
            state,
            delta_v=100,
        )

    with pytest.raises(ValueError):
        apply_retrograde_burn(
            state,
            delta_v=100,
        )