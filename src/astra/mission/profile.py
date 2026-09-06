"""Integrated spacecraft mission analysis for ASTRA."""

from dataclasses import dataclass

from astra.mission.analysis import analyze_hohmann_mission
from astra.physics.rocket import propellant_mass_for_delta_v


@dataclass(frozen=True)
class MissionProfile:
    """Integrated results for a spacecraft orbital-transfer mission."""

    initial_altitude: float
    final_altitude: float
    spacecraft_mass: float
    specific_impulse: float
    available_propellant: float
    required_delta_v: float
    required_propellant: float
    remaining_propellant: float
    transfer_time: float
    feasible: bool


def create_mission_profile(
    initial_altitude: float,
    final_altitude: float,
    spacecraft_mass: float,
    specific_impulse: float,
    available_propellant: float,
) -> MissionProfile:
    """Analyze an orbital transfer and its propellant requirements."""

    if spacecraft_mass <= 0:
        raise ValueError("Spacecraft mass must be greater than zero.")

    if specific_impulse <= 0:
        raise ValueError("Specific impulse must be greater than zero.")

    if available_propellant < 0:
        raise ValueError("Available propellant cannot be negative.")

    mission = analyze_hohmann_mission(
        initial_altitude=initial_altitude,
        final_altitude=final_altitude,
        available_delta_v=float("inf"),
    )

    required_propellant = propellant_mass_for_delta_v(
        initial_mass=spacecraft_mass,
        delta_v=mission.total_delta_v,
        specific_impulse=specific_impulse,
    )

    remaining_propellant = available_propellant - required_propellant

    feasible = (
        remaining_propellant >= 0
        and required_propellant < spacecraft_mass
    )

    return MissionProfile(
        initial_altitude=initial_altitude,
        final_altitude=final_altitude,
        spacecraft_mass=spacecraft_mass,
        specific_impulse=specific_impulse,
        available_propellant=available_propellant,
        required_delta_v=mission.total_delta_v,
        required_propellant=required_propellant,
        remaining_propellant=remaining_propellant,
        transfer_time=mission.transfer_time,
        feasible=feasible,
    )