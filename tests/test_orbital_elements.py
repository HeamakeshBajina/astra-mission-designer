"""Tests for classical orbital-element calculations."""

import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.physics.orbital_elements import (
    OrbitalElements,
    orbital_elements_from_state,
)
from astra.simulation.propagator_3d import State3D


def circular_state(
    radius: float,
    inclination_degrees: float = 0.0,
) -> State3D:
    """Create a circular state at the ascending node."""

    speed = math.sqrt(EARTH_MU / radius)
    inclination = math.radians(inclination_degrees)

    return State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=speed * math.cos(inclination),
        vz=speed * math.sin(inclination),
    )


def test_circular_equatorial_orbit() -> None:
    state = circular_state(
        EARTH_RADIUS + 400_000.0
    )

    elements = orbital_elements_from_state(state)

    assert elements.semi_major_axis == pytest.approx(
        EARTH_RADIUS + 400_000.0,
        rel=1e-12,
    )
    assert elements.eccentricity == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert elements.inclination == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert elements.raan == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_circular_inclined_orbit() -> None:
    state = circular_state(
        EARTH_RADIUS + 500_000.0,
        inclination_degrees=45.0,
    )

    elements = orbital_elements_from_state(state)

    assert elements.semi_major_axis == pytest.approx(
        EARTH_RADIUS + 500_000.0,
        rel=1e-12,
    )
    assert elements.eccentricity == pytest.approx(
        0.0,
        abs=1e-12,
    )
    assert elements.inclination == pytest.approx(
        45.0,
        abs=1e-10,
    )
    assert elements.raan == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_elliptical_equatorial_orbit() -> None:
    radius = EARTH_RADIUS + 400_000.0
    velocity = math.sqrt(
        EARTH_MU
        * (
            2.0 / radius
            - 1.0 / 10_000_000.0
        )
    )

    state = State3D(
        x=radius,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
    )

    elements = orbital_elements_from_state(state)

    assert elements.semi_major_axis == pytest.approx(
        10_000_000.0,
        rel=1e-12,
    )
    assert elements.eccentricity > 0.0
    assert elements.inclination == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_known_inclination() -> None:
    state = circular_state(
        EARTH_RADIUS + 600_000.0,
        inclination_degrees=63.4,
    )

    elements = orbital_elements_from_state(state)

    assert elements.inclination == pytest.approx(
        63.4,
        abs=1e-10,
    )


def test_true_anomaly_at_periapsis() -> None:
    semi_major_axis = 10_000_000.0
    eccentricity = 0.2

    periapsis = (
        semi_major_axis
        * (1.0 - eccentricity)
    )

    velocity = math.sqrt(
        EARTH_MU
        * (
            2.0 / periapsis
            - 1.0 / semi_major_axis
        )
    )

    state = State3D(
        x=periapsis,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
    )

    elements = orbital_elements_from_state(state)

    assert elements.semi_major_axis == pytest.approx(
        semi_major_axis,
        rel=1e-12,
    )
    assert elements.eccentricity == pytest.approx(
        eccentricity,
        rel=1e-12,
    )
    assert elements.true_anomaly == pytest.approx(
        0.0,
        abs=1e-10,
    )


def test_true_anomaly_at_apoapsis() -> None:
    semi_major_axis = 10_000_000.0
    eccentricity = 0.2

    apoapsis = (
        semi_major_axis
        * (1.0 + eccentricity)
    )

    velocity = math.sqrt(
        EARTH_MU
        * (
            2.0 / apoapsis
            - 1.0 / semi_major_axis
        )
    )

    state = State3D(
        x=apoapsis,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=velocity,
        vz=0.0,
    )

    elements = orbital_elements_from_state(state)

    assert elements.true_anomaly == pytest.approx(
        180.0,
        abs=1e-10,
    )


def test_raan_for_inclined_orbit() -> None:
    radius = EARTH_RADIUS + 700_000.0
    inclination = math.radians(45.0)
    raan = math.radians(90.0)

    speed = math.sqrt(EARTH_MU / radius)

    state = State3D(
        x=0.0,
        y=radius,
        z=0.0,
        vx=-speed * math.cos(inclination),
        vy=0.0,
        vz=speed * math.sin(inclination),
    )

    elements = orbital_elements_from_state(state)

    assert elements.inclination == pytest.approx(
        45.0,
        abs=1e-10,
    )
    assert elements.raan == pytest.approx(
        90.0,
        abs=1e-10,
    )


def test_invalid_zero_position() -> None:
    state = State3D(
        x=0.0,
        y=0.0,
        z=0.0,
        vx=1.0,
        vy=1.0,
        vz=1.0,
    )

    with pytest.raises(
        ValueError,
        match="center",
    ):
        orbital_elements_from_state(state)


def test_invalid_zero_angular_momentum() -> None:
    state = State3D(
        x=7_000_000.0,
        y=0.0,
        z=0.0,
        vx=1.0,
        vy=0.0,
        vz=0.0,
    )

    with pytest.raises(
        ValueError,
        match="angular momentum",
    ):
        orbital_elements_from_state(state)


def test_angles_are_normalized() -> None:
    state = State3D(
        x=-7_000_000.0,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=-math.sqrt(EARTH_MU / 7_000_000.0),
        vz=0.0,
    )

    elements = orbital_elements_from_state(state)

    assert 0.0 <= elements.raan < 360.0
    assert 0.0 <= elements.argument_of_periapsis < 360.0
    assert 0.0 <= elements.true_anomaly < 360.0


def test_returns_orbital_elements_dataclass() -> None:
    state = circular_state(
        EARTH_RADIUS + 400_000.0
    )

    elements = orbital_elements_from_state(state)

    assert isinstance(elements, OrbitalElements)
