import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.orbital import (
    circular_orbital_velocity,
    escape_velocity,
    orbital_period,
    specific_orbital_energy,
)


def test_circular_orbital_velocity_at_earth_surface():
    velocity = circular_orbital_velocity(EARTH_RADIUS)

    assert math.isclose(velocity, 7909.8, rel_tol=1e-3)


def test_escape_velocity_is_sqrt_two_times_orbital_velocity():
    orbital_velocity = circular_orbital_velocity(EARTH_RADIUS)
    escape = escape_velocity(EARTH_RADIUS)

    assert math.isclose(escape, math.sqrt(2) * orbital_velocity)


def test_orbital_period():
    radius = EARTH_RADIUS + 400_000

    period = orbital_period(radius)

    assert 5_000 < period < 6_000


def test_specific_orbital_energy():
    radius = EARTH_RADIUS + 400_000

    energy = specific_orbital_energy(radius)

    expected = -EARTH_MU / (2 * radius)

    assert math.isclose(energy, expected)


def test_invalid_radius():
    with pytest.raises(ValueError):
        circular_orbital_velocity(0)