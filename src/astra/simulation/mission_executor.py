"""Multi-burn mission execution for ASTRA."""

from dataclasses import dataclass
import math

from astra.mission.burn_sequence import BurnSequence
from astra.simulation.burns import (
    apply_prograde_burn,
    apply_retrograde_burn,
)
from astra.simulation.propagator import State, rk4_step


@dataclass(frozen=True)
class ExecutedMission:
    """Numerically executed multi-burn mission."""

    times: list[float]
    states: list[State]
    burn_indices: list[int]


def execute_burn_sequence(
    initial_state: State,
    sequence: BurnSequence,
    dt: float = 10.0,
) -> ExecutedMission:
    """Execute a time-ordered sequence of instantaneous burns."""

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    times = [0.0]
    states = [initial_state]
    burn_indices = []

    current_time = 0.0
    current_state = initial_state

    for burn in sequence.burns:
        if burn.time < current_time:
            raise ValueError(
                "Burn times must not move backwards."
            )

        coast_time = burn.time - current_time

        while coast_time > dt:
            current_state = rk4_step(
                current_state,
                dt,
            )

            current_time += dt
            coast_time -= dt

            times.append(current_time)
            states.append(current_state)

        if coast_time > 0:
            current_state = rk4_step(
                current_state,
                coast_time,
            )

            current_time = burn.time

            times.append(current_time)
            states.append(current_state)

        direction = burn.direction.lower()

        if direction == "prograde":
            current_state = apply_prograde_burn(
                current_state,
                burn.delta_v,
            )
        elif direction == "retrograde":
            current_state = apply_retrograde_burn(
                current_state,
                burn.delta_v,
            )
        else:
            raise ValueError(
                "Burn direction must be 'prograde' "
                "or 'retrograde'."
            )

        burn_indices.append(len(states) - 1)

        states[-1] = current_state

    return ExecutedMission(
        times=times,
        states=states,
        burn_indices=burn_indices,
    )