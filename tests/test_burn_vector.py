"""Tests for ASTRA burn-vector utilities and integration."""

import math

import pytest

from astra.physics.burn_vector import (
    BurnVector,
    normalize_vector,
    prograde_direction,
    radial_in_direction,
    radial_out_direction,
    resolve_burn_direction,
    retrograde_direction,
)
from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.finite_burn_simulation import simulate_burn
from astra.simulation.propagator_3d_thrust import State3DThrust


def make_state() -> State3DThrust:
    return State3DThrust(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_500.0,
        vz=0.0,
        mass=500.0,
    )


def make_burn() -> FiniteBurn:
    return FiniteBurn(
        thrust_model=ThrustModel(
            thrust=1000.0,
            specific_impulse=300.0,
        ),
        duration=10.0,
        dry_mass=450.0,
    )


def test_vector_magnitude():
    vector = BurnVector(3.0, 4.0, 0.0)

    assert vector.magnitude == pytest.approx(5.0)


def test_vector_normalization():
    vector = BurnVector(3.0, 4.0, 0.0)

    assert vector.unit == pytest.approx(
        (0.6, 0.8, 0.0)
    )


def test_normalized_vector_has_unit_magnitude():
    vector = BurnVector(2.0, -3.0, 6.0)

    unit = vector.unit

    assert math.sqrt(
        sum(component * component for component in unit)
    ) == pytest.approx(1.0)


def test_zero_vector_is_rejected():
    with pytest.raises(ValueError):
        BurnVector(0.0, 0.0, 0.0).unit


def test_normalize_vector():
    assert normalize_vector(
        (0.0, 5.0, 0.0)
    ) == pytest.approx(
        (0.0, 1.0, 0.0)
    )


def test_vector_scaling():
    vector = BurnVector(1.0, -2.0, 3.0)

    scaled = vector.scaled(4.0)

    assert scaled == BurnVector(
        4.0,
        -8.0,
        12.0,
    )


def test_vector_unpacking():
    vector = BurnVector(1.0, 2.0, 3.0)

    x, y, z = vector

    assert (x, y, z) == (1.0, 2.0, 3.0)


def test_prograde_direction():
    direction = prograde_direction(
        (0.0, 7_500.0, 0.0)
    )

    assert direction.unit == pytest.approx(
        (0.0, 1.0, 0.0)
    )


def test_retrograde_direction():
    direction = retrograde_direction(
        (0.0, 7_500.0, 0.0)
    )

    assert direction.unit == pytest.approx(
        (0.0, -1.0, 0.0)
    )


def test_radial_out_direction():
    direction = radial_out_direction(
        (7_000_000.0, 0.0, 0.0)
    )

    assert direction.unit == pytest.approx(
        (1.0, 0.0, 0.0)
    )


def test_radial_in_direction():
    direction = radial_in_direction(
        (7_000_000.0, 0.0, 0.0)
    )

    assert direction.unit == pytest.approx(
        (-1.0, 0.0, 0.0)
    )


def test_resolve_tuple_direction():
    assert resolve_burn_direction(
        (0.0, 0.0, 8.0)
    ) == pytest.approx(
        (0.0, 0.0, 1.0)
    )


def test_resolve_burn_vector():
    direction = BurnVector(
        2.0,
        0.0,
        0.0,
    )

    assert resolve_burn_direction(
        direction
    ) == pytest.approx(
        (1.0, 0.0, 0.0)
    )


def test_zero_tuple_direction_is_rejected():
    with pytest.raises(ValueError):
        resolve_burn_direction(
            (0.0, 0.0, 0.0)
        )


def test_prograde_burn_works_with_propagator():
    result = simulate_burn(
        make_state(),
        make_burn(),
        prograde_direction(
            (0.0, 7_500.0, 0.0)
        ),
        dt=1.0,
    )

    assert result.final_state.mass < result.initial_state.mass


def test_radial_burn_works_with_propagator():
    result = simulate_burn(
        make_state(),
        make_burn(),
        radial_out_direction(
            (
                make_state().x,
                make_state().y,
                make_state().z,
            )
        ),
        dt=1.0,
    )

    assert result.final_state.x != result.initial_state.x


def test_retrograde_burn_works_with_propagator():
    result = simulate_burn(
        make_state(),
        make_burn(),
        retrograde_direction(
            (
                make_state().vx,
                make_state().vy,
                make_state().vz,
            )
        ),
        dt=1.0,
    )

    assert result.final_state.mass < result.initial_state.mass


def test_three_dimensional_burn_changes_z_velocity():
    result = simulate_burn(
        make_state(),
        make_burn(),
        BurnVector(
            0.0,
            0.0,
            1.0,
        ),
        dt=1.0,
    )

    assert result.final_state.vz != pytest.approx(
        result.initial_state.vz
    )


def test_scaled_vectors_have_same_direction():
    vector_a = BurnVector(
        1.0,
        2.0,
        3.0,
    )

    vector_b = vector_a.scaled(10.0)

    assert vector_a.unit == pytest.approx(
        vector_b.unit
    )
