"""Tests for ASTRA's finite-duration burn model."""

import pytest

from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn


def make_burn() -> FiniteBurn:
    """Create a representative finite burn for testing."""

    return FiniteBurn(
        thrust_model=ThrustModel(
            thrust=1000.0,
            specific_impulse=300.0,
        ),
        duration=10.0,
        dry_mass=450.0,
    )


def test_propellant_required_matches_mass_flow():
    """Burn propellant should equal mass flow multiplied by duration."""

    burn = make_burn()

    expected = (
        burn.thrust_model.mass_flow_rate
        * burn.duration
    )

    assert burn.propellant_required == pytest.approx(
        expected
    )


def test_final_mass_preserves_dry_mass():
    """A valid burn must leave at least the dry mass."""

    burn = make_burn()

    initial_mass = 500.0
    final_mass = burn.final_mass(initial_mass)

    assert final_mass >= burn.dry_mass


def test_final_mass_is_initial_mass_minus_propellant():
    """Final mass should equal initial mass minus consumed propellant."""

    burn = make_burn()

    initial_mass = 500.0

    expected = (
        initial_mass -
        burn.propellant_required
    )

    assert burn.final_mass(initial_mass) == pytest.approx(
        expected
    )


def test_can_complete_valid_burn():
    """A sufficiently fueled spacecraft can complete the burn."""

    burn = make_burn()

    assert burn.can_complete(500.0)


def test_burn_fails_when_propellant_is_insufficient():
    """A burn requiring too much propellant must be rejected."""

    burn = make_burn()

    with pytest.raises(ValueError):
        burn.final_mass(451.0)


def test_can_complete_propagates_insufficient_propellant_error():
    """can_complete should reject a burn that cannot physically finish."""

    burn = make_burn()

    with pytest.raises(ValueError):
        burn.can_complete(451.0)


def test_initial_mass_below_dry_mass_is_rejected():
    """Initial mass cannot be below dry mass."""

    burn = make_burn()

    with pytest.raises(ValueError):
        burn.final_mass(400.0)


def test_zero_duration_requires_no_propellant():
    """A zero-duration burn should require no propellant."""

    burn = FiniteBurn(
        thrust_model=ThrustModel(
            thrust=1000.0,
            specific_impulse=300.0,
        ),
        duration=0.0,
        dry_mass=450.0,
    )

    assert burn.propellant_required == pytest.approx(0.0)
    assert burn.final_mass(500.0) == pytest.approx(500.0)


def test_negative_duration_is_rejected():
    """Negative burn duration must be rejected."""

    with pytest.raises(ValueError):
        FiniteBurn(
            thrust_model=ThrustModel(
                thrust=1000.0,
                specific_impulse=300.0,
            ),
            duration=-1.0,
            dry_mass=450.0,
        )


def test_non_positive_dry_mass_is_rejected():
    """Dry mass must be greater than zero."""

    with pytest.raises(ValueError):
        FiniteBurn(
            thrust_model=ThrustModel(
                thrust=1000.0,
                specific_impulse=300.0,
            ),
            duration=10.0,
            dry_mass=0.0,
        )
