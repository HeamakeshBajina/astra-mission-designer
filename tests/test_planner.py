import pytest

from astra.mission.planner import create_mission_plan


def test_mission_plan_contains_name():
    plan = create_mission_plan(
        mission_name="LEO Raise",
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert plan.mission_name == "LEO Raise"


def test_mission_plan_contains_profile():
    plan = create_mission_plan(
        mission_name="LEO Raise",
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert plan.profile.required_delta_v > 0
    assert plan.profile.required_propellant > 0


def test_mission_plan_can_be_feasible():
    plan = create_mission_plan(
        mission_name="LEO Raise",
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=500,
    )

    assert plan.profile.feasible is True


def test_mission_plan_can_be_infeasible():
    plan = create_mission_plan(
        mission_name="LEO Raise",
        initial_altitude=400_000,
        final_altitude=800_000,
        spacecraft_mass=1_000,
        specific_impulse=300,
        available_propellant=10,
    )

    assert plan.profile.feasible is False


def test_empty_mission_name_is_rejected():
    with pytest.raises(ValueError):
        create_mission_plan(
            mission_name="",
            initial_altitude=400_000,
            final_altitude=800_000,
            spacecraft_mass=1_000,
            specific_impulse=300,
            available_propellant=500,
        )