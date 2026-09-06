"""Trajectory generation for ASTRA."""

from dataclasses import dataclass

from astra.simulation.propagator import State, rk4_step


@dataclass(frozen=True)
class Trajectory:
    """Numerically propagated spacecraft trajectory."""

    times: list[float]
    states: list[State]


def propagate_trajectory(
    initial_state: State,
    duration: float,
    dt: float,
) -> Trajectory:
    """Propagate a spacecraft trajectory using RK4 integration."""

    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    if dt <= 0:
        raise ValueError("Timestep must be greater than zero.")

    if dt > duration:
        raise ValueError("Timestep cannot exceed duration.")

    times = [0.0]
    states = [initial_state]

    current_state = initial_state
    elapsed = 0.0

    while elapsed + dt <= duration:
        current_state = rk4_step(current_state, dt)
        elapsed += dt

        times.append(elapsed)
        states.append(current_state)

    return Trajectory(
        times=times,
        states=states,
    )
