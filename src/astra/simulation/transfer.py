"""Hohmann transfer trajectory simulation for ASTRA."""

import math
from dataclasses import dataclass

from astra.physics.constants import EARTH_MU
from astra.physics.transfers import hohmann_transfer
from astra.simulation.propagator import State
from astra.simulation.trajectory import Trajectory
from astra.simulation.trajectory import propagate_trajectory


@dataclass(frozen=True)
class TransferTrajectory:
    """Numerically simulated Hohmann transfer."""

    initial_orbit: Trajectory
    transfer_orbit: Trajectory
    final_orbit: Trajectory


def simulate_hohmann_transfer(
    initial_radius: float,
    final_radius: float,
    dt: float = 10.0,
) -> TransferTrajectory:
    """Simulate a Hohmann transfer between two circular orbits."""

    if initial_radius <= 0:
        raise ValueError("Initial radius must be greater than zero.")

    if final_radius <= 0:
        raise ValueError("Final radius must be greater than zero.")

    if math.isclose(initial_radius, final_radius):
        raise ValueError(
            "Initial and final orbit radii must be different."
        )

    if dt <= 0:
        raise ValueError("Timestep must be greater than zero.")

    transfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    initial_velocity = math.sqrt(
        EARTH_MU / initial_radius
    )

    transfer_velocity = math.sqrt(
        EARTH_MU
        * (
            2 / initial_radius
            - 1 / transfer.transfer_semi_major_axis
        )
    )

    final_velocity = math.sqrt(
        EARTH_MU / final_radius
    )

    transfer_duration = transfer.transfer_time

    initial_state = State(
        x=initial_radius,
        y=0.0,
        vx=0.0,
        vy=initial_velocity,
    )

    transfer_state = State(
        x=initial_radius,
        y=0.0,
        vx=0.0,
        vy=transfer_velocity,
    )

    final_state = State(
        x=final_radius,
        y=0.0,
        vx=0.0,
        vy=final_velocity,
    )

    initial_orbit = propagate_trajectory(
        initial_state=initial_state,
        duration=2 * math.pi
        * math.sqrt(initial_radius**3 / EARTH_MU),
        dt=dt,
    )

    transfer_orbit = propagate_trajectory(
        initial_state=transfer_state,
        duration=transfer_duration,
        dt=dt,
    )

    final_orbit = propagate_trajectory(
        initial_state=final_state,
        duration=2 * math.pi
        * math.sqrt(final_radius**3 / EARTH_MU),
        dt=dt,
    )

    return TransferTrajectory(
        initial_orbit=initial_orbit,
        transfer_orbit=transfer_orbit,
        final_orbit=final_orbit,
    )