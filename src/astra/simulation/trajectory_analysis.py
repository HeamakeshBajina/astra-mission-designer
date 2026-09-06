"""Trajectory analysis utilities for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
from astra.simulation.trajectory import Trajectory


@dataclass(frozen=True)
class TrajectoryAnalysis:
    """Derived engineering quantities from a spacecraft trajectory."""

    radii: list[float]
    altitudes: list[float]
    speeds: list[float]
    specific_energies: list[float]


def analyze_trajectory(
    trajectory: Trajectory,
) -> TrajectoryAnalysis:
    """Calculate physical quantities for every trajectory state."""

    radii = []
    altitudes = []
    speeds = []
    specific_energies = []

    for state in trajectory.states:
        radius = math.hypot(state.x, state.y)
        speed = math.hypot(state.vx, state.vy)

        radii.append(radius)
        altitudes.append(radius - EARTH_RADIUS)
        speeds.append(speed)

        specific_energy = (
            speed**2 / 2
            - EARTH_MU / radius
        )

        specific_energies.append(specific_energy)

    return TrajectoryAnalysis(
        radii=radii,
        altitudes=altitudes,
        speeds=speeds,
        specific_energies=specific_energies,
    )
    