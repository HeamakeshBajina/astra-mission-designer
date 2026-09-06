import math

import pytest

from astra.physics.constants import G0
from astra.physics.rocket import (
    delta_v_from_mass_ratio,
    final_mass_for_delta_v,
    propellant_mass_for_delta_v,
)


def test_delta_v_from_mass_ratio():
    delta_v = delta_v_from_mass_ratio(
        initial_mass=1000,
        final_mass=500,
        specific_impulse=300,
    )

    expected = 300 * G0 * math.log(2)

    assert math.isclose(delta_v, expected)


def test_final_mass_for_delta_v():
    initial_mass = 1000
    specific_impulse = 300

    delta_v = delta_v_from_mass_ratio(
        initial_mass,
        500,
        specific_impulse,
    )

    final_mass = final_mass_for_delta_v(
        initial_mass,
        delta_v,
        specific_impulse,
    )

    assert math.isclose(final_mass, 500)


def test_propellant_mass():
    propellant = propellant_mass_for_delta_v(
        initial_mass=1000,
        delta_v=1000,
        specific_impulse=300,
    )

    assert 250 < propellant < 300


def test_invalid_mass():
    with pytest.raises(ValueError):
        delta_v_from_mass_ratio(
            initial_mass=500,
            final_mass=500,
            specific_impulse=300,
        )


def test_invalid_specific_impulse():
    with pytest.raises(ValueError):
        delta_v_from_mass_ratio(
            initial_mass=1000,
            final_mass=500,
            specific_impulse=0,
        )


def test_negative_delta_v():
    with pytest.raises(ValueError):
        final_mass_for_delta_v(
            initial_mass=1000,
            delta_v=-1,
            specific_impulse=300,
        )