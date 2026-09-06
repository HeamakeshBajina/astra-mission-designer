"""High-level mission planning for ASTRA."""

from dataclasses import dataclass

from astra.mission.profile import MissionProfile
from astra.mission.profile import create_mission_profile


@dataclass(frozen=True)
class MissionPlan:
    """Complete spacecraft mission plan."""

    mission_name: str
    profile: MissionProfile


def create_mission_plan(
    mission_name: str,
    initial_altitude: float,
    final_altitude: float,
    spacecraft_mass: float,
    specific_impulse: float,
    available_propellant: float,
) -> MissionPlan:
    """Create a complete orbital-transfer mission plan."""

    if not mission_name.strip():
        raise ValueError("Mission name cannot be empty.")

    profile = create_mission_profile(
        initial_altitude=initial_altitude,
        final_altitude=final_altitude,
        spacecraft_mass=spacecraft_mass,
        specific_impulse=specific_impulse,
        available_propellant=available_propellant,
    )

    return MissionPlan(
        mission_name=mission_name,
        profile=profile,
    )