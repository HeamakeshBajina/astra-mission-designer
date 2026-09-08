"""Tests for ASTRA's finite-duration thrust model."""

import pytest

from astra.physics.constants import G0
from astra.physics.thrust import ThrustModel


def test_mass_flow_rate_matches_definition():
    """Mass flow should satisfy mdot = T / (Isp * g0)."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    expected = 1000.0 / (300.0 * G0)

    assert model.mass_flow_rate == pytest.approx(
        expected
    )


def test_zero_thrust_has_zero_mass_flow():
    """Zero thrust should produce zero propellant flow."""

    model = ThrustModel(
        thrust=0.0,
        specific_impulse=300.0,
    )

    assert model.mass_flow_rate == pytest.approx(
        0.0
    )


def test_propellant_consumed_over_duration():
    """Propellant consumption should scale with burn duration."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    duration = 60.0

    expected = (
        model.mass_flow_rate * duration
    )

    assert model.propellant_consumed(
        duration
    ) == pytest.approx(expected)


def test_longer_burn_consumes_more_propellant():
    """A longer burn should consume more propellant."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    short_burn = model.propellant_consumed(60.0)
    long_burn = model.propellant_consumed(120.0)

    assert long_burn > short_burn


def test_remaining_mass_is_initial_minus_consumed():
    """Remaining mass should equal initial mass minus propellant used."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    initial_mass = 500.0
    duration = 60.0

    expected = (
        initial_mass
        - model.propellant_consumed(duration)
    )

    assert model.remaining_mass(
        initial_mass,
        duration,
    ) == pytest.approx(expected)


def test_negative_thrust_is_rejected():
    """Negative thrust should not be accepted."""

    with pytest.raises(ValueError):
        ThrustModel(
            thrust=-1.0,
            specific_impulse=300.0,
        )


def test_zero_specific_impulse_is_rejected():
    """Zero specific impulse should not be accepted."""

    with pytest.raises(ValueError):
        ThrustModel(
            thrust=1000.0,
            specific_impulse=0.0,
        )


def test_negative_specific_impulse_is_rejected():
    """Negative specific impulse should not be accepted."""

    with pytest.raises(ValueError):
        ThrustModel(
            thrust=1000.0,
            specific_impulse=-1.0,
        )


def test_negative_duration_is_rejected():
    """Negative burn duration should not be accepted."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    with pytest.raises(ValueError):
        model.propellant_consumed(-1.0)


def test_non_positive_initial_mass_is_rejected():
    """Non-positive initial mass should not be accepted."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    with pytest.raises(ValueError):
        model.remaining_mass(
            initial_mass=0.0,
            duration=10.0,
        )


def test_burn_cannot_consume_more_mass_than_available():
    """A burn cannot consume more mass than the spacecraft has."""

    model = ThrustModel(
        thrust=1000.0,
        specific_impulse=300.0,
    )

    with pytest.raises(ValueError):
        model.remaining_mass(
            initial_mass=1.0,
            duration=100.0,
        )
