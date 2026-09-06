"""Mission-level analysis for ASTRA."""

from dataclasses import dataclass

from astra.physics.transfers import HohmannTransfer, hohmann_transfer


@dataclass(frozen=True)
class MissionAnalysis:
    """Summary of a spacecraft orbital-transfer mission."""

    initial_altitude: float
    final_altitude: float
    total_delta_v: float
    transfer_time: float
    feasible: bool


def analyze_hohmann_mission(
    initial_altitude: float,
    final_altitude: float,
    available_delta_v: float,
) -> MissionAnalysis:
    """Analyze the feasibility of a Hohmann orbital transfer.

    Parameters
    ----------
    initial_altitude : float
        Initial orbit altitude above Earth's surface, in metres.

    final_altitude : float
        Final orbit altitude above Earth's surface, in metres.

    available_delta_v : float
        Spacecraft's available delta-v budget, in metres per second.

    Returns
    -------
    MissionAnalysis
        Mission-level analysis results.
    """
    if initial_altitude < 0:
        raise ValueError("Initial altitude cannot be negative.")

    if final_altitude < 0:
        raise ValueError("Final altitude cannot be negative.")

    if available_delta_v < 0:
        raise ValueError("Available delta-v cannot be negative.")

    from astra.physics.constants import EARTH_RADIUS

    initial_radius = EARTH_RADIUS + initial_altitude
    final_radius = EARTH_RADIUS + final_altitude

    transfer: HohmannTransfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    return MissionAnalysis(
        initial_altitude=initial_altitude,
        final_altitude=final_altitude,
        total_delta_v=transfer.total_delta_v,
        transfer_time=transfer.transfer_time,
        feasible=available_delta_v >= transfer.total_delta_v,
    )