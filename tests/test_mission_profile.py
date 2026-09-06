import pytest

from astra.mission.profile import create_mission_profile


def test_mission_profile_calculates_propellant_requirement():
    result = create_mission_profile(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert result.required_delta_v > 0
    assert result.required_propellant > 0
    assert result.transfer_time > 0


def test_mission_profile_is_feasible():
    result = create_mission_profile(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert result.feasible is True


def test_mission_profile_can_be_infeasible():
    result = create_mission_profile(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=10,
    )

    assert result.feasible is False


def test_remaining_propellant_is_correct():
    result = create_mission_profile(
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert result.remaining_propellant == pytest.approx(
        result.available_propellant - result.required_propellant
    )


def test_invalid_spacecraft_mass():
    with pytest.raises(ValueError):
        create_mission_profile(
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=0,
            specific_impulse=300,
            available_propellant=500,
        )


def test_invalid_propellant():
    with pytest.raises(ValueError):
        create_mission_profile(
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=-1,
        )