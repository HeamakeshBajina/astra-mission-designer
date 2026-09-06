"""Continuous mission trajectory simulation for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU
from astra.physics.orbital import circular_orbital_velocity
from astra.physics.transfers import hohmann_transfer
from astra.simulation.burns import apply_prograde_burn
from astra.simulation.burns import apply_retrograde_burn
from astra.simulation.propagator import State, rk4_step


@dataclass(frozen=True)
class BurnEvent:
    """Instantaneous spacecraft velocity change."""

    time: float
    delta_v: float
    state_before: State
    state_after: State
    name: str
    direction: str


@dataclass(frozen=True)
class MissionTrajectory:
    """Continuous spacecraft trajectory containing orbital burns."""

    times: list[float]
    states: list[State]
    burns: list[BurnEvent]


def simulate_continuous_hohmann(
    initial_radius: float,
    final_radius: float,
    dt: float = 10.0,
) -> MissionTrajectory:
    """Simulate a complete Hohmann transfer as one timeline."""

    if initial_radius <= 0:
        raise ValueError(
            "Initial radius must be greater than zero."
        )

    if final_radius <= 0:
        raise ValueError(
            "Final radius must be greater than zero."
        )

    if math.isclose(initial_radius, final_radius):
        raise ValueError(
            "Initial and final orbit radii must be different."
        )

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    transfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    initial_velocity = circular_orbital_velocity(
        initial_radius
    )

    initial_state = State(
        x=initial_radius,
        y=0.0,
        vx=0.0,
        vy=initial_velocity,
    )

    times = [0.0]
    states = [initial_state]
    burns = []

    raising = final_radius > initial_radius

    # -----------------------------------------------------
    # First burn
    # -----------------------------------------------------

    if raising:
        first_burn_state = apply_prograde_burn(
            initial_state,
            transfer.first_burn_delta_v,
        )
        burn_direction = "prograde"
    else:
        first_burn_state = apply_retrograde_burn(
            initial_state,
            transfer.first_burn_delta_v,
        )
        burn_direction = "retrograde"

    first_burn = BurnEvent(
        time=0.0,
        delta_v=transfer.first_burn_delta_v,
        state_before=initial_state,
        state_after=first_burn_state,
        name="First Hohmann burn",
        direction=burn_direction,
    )

    burns.append(first_burn)

    states[-1] = first_burn_state

    # -----------------------------------------------------
    # Transfer orbit propagation
    # -----------------------------------------------------

    elapsed = 0.0
    state = first_burn_state

    while elapsed + dt < transfer.transfer_time:
        state = rk4_step(
            state,
            dt,
        )

        elapsed += dt

        times.append(elapsed)
        states.append(state)

    remaining_time = transfer.transfer_time - elapsed

    if remaining_time > 0:
        state = rk4_step(
            state,
            remaining_time,
        )

        elapsed = transfer.transfer_time

        times.append(elapsed)
        states.append(state)

    # -----------------------------------------------------
    # Second burn
    # -----------------------------------------------------

    final_circular_velocity = circular_orbital_velocity(
        final_radius
    )

    current_speed = math.hypot(
        state.vx,
        state.vy,
    )

    second_burn_delta_v = abs(
        final_circular_velocity - current_speed
    )

    if raising:
        second_burn_state = apply_prograde_burn(
            state,
            second_burn_delta_v,
        )
        burn_direction = "prograde"
    else:
        second_burn_state = apply_retrograde_burn(
            state,
            second_burn_delta_v,
        )
        burn_direction = "retrograde"

    second_burn = BurnEvent(
        time=elapsed,
        delta_v=second_burn_delta_v,
        state_before=state,
        state_after=second_burn_state,
        name="Second Hohmann burn",
        direction=burn_direction,
    )

    burns.append(second_burn)

    states[-1] = second_burn_state

    # -----------------------------------------------------
    # Final orbit propagation
    # -----------------------------------------------------

    final_period = (
        2
        * math.pi
        * math.sqrt(
            final_radius**3 / EARTH_MU
        )
    )

    final_elapsed = 0.0
    state = second_burn_state

    while final_elapsed + dt < final_period:
        state = rk4_step(
            state,
            dt,
        )

        final_elapsed += dt
        elapsed += dt

        times.append(elapsed)
        states.append(state)

    remaining_final_time = final_period - final_elapsed

    if remaining_final_time > 0:
        state = rk4_step(
            state,
            remaining_final_time,
        )

        elapsed += remaining_final_time

        times.append(elapsed)
        states.append(state)

    return MissionTrajectory(
        times=times,
        states=states,
        burns=burns,
    )