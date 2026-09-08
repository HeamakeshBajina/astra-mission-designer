"""Multi-step finite-burn mission simulation for ASTRA."""

from dataclasses import dataclass

from astra.physics.burn_vector import BurnVector
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.propagator_3d_thrust import (
    State3DThrust,
    rk4_step_thrust,
)


BurnDirection = BurnVector | tuple[float, float, float]


@dataclass(frozen=True)
class BurnSimulation:
    """Complete result of a finite-duration spacecraft burn."""

    states: tuple[State3DThrust, ...]
    timestep: float

    @property
    def initial_state(self) -> State3DThrust:
        """Return the initial spacecraft state."""
        return self.states[0]

    @property
    def final_state(self) -> State3DThrust:
        """Return the final spacecraft state."""
        return self.states[-1]

    @property
    def duration(self) -> float:
        """Return simulated duration in seconds."""
        return sum(
            self._step_durations
        )

    @property
    def _step_durations(self) -> tuple[float, ...]:
        """Return actual integration step durations."""
        return (
            self._calculate_step_durations()
        )

    def _calculate_step_durations(self) -> tuple[float, ...]:
        """Calculate the durations represented by the trajectory."""
        if len(self.states) <= 1:
            return ()

        return (
            self.timestep,
        ) * (len(self.states) - 1)


def simulate_burn(
    initial_state: State3DThrust,
    burn: FiniteBurn,
    thrust_direction: BurnDirection,
    dt: float = 1.0,
) -> BurnSimulation:
    """Simulate a complete finite-duration burn."""

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    if not burn.can_complete(initial_state.mass):
        raise ValueError(
            "Burn cannot complete with available propellant."
        )

    states = [initial_state]
    current_state = initial_state
    elapsed = 0.0

    while elapsed < burn.duration:
        step = min(
            dt,
            burn.duration - elapsed,
        )

        current_state = rk4_step_thrust(
            state=current_state,
            dt=step,
            thrust_model=burn.thrust_model,
            thrust_direction=thrust_direction,
            dry_mass=burn.dry_mass,
        )

        states.append(current_state)
        elapsed += step

    return BurnSimulation(
        states=tuple(states),
        timestep=dt,
    )


def simulate_finite_burn(
    initial_state: State3DThrust,
    burn: FiniteBurn,
    thrust_direction: BurnDirection,
    dt: float = 1.0,
) -> list[State3DThrust]:
    """Backward-compatible list-based finite-burn simulation."""

    return list(
        simulate_burn(
            initial_state=initial_state,
            burn=burn,
            thrust_direction=thrust_direction,
            dt=dt,
        ).states
    )
