"""Mission-level finite-thrust API for ASTRA."""

from dataclasses import dataclass

from astra.physics.burn_vector import BurnVector
from astra.physics.thrust import ThrustModel
from astra.simulation.finite_burn import FiniteBurn
from astra.simulation.numerical_validation import (
    propagate_to_time,
    propagate_to_time_j2,
)
from astra.simulation.propagator_3d_thrust import State3DThrust
from astra.simulation.propagator_3d_thrust_j2 import State3DThrustJ2


@dataclass(frozen=True)
class FiniteThrustMission:
    """Configuration for a single finite-thrust mission segment."""

    initial_state: State3DThrust
    thrust_model: ThrustModel
    burn: FiniteBurn
    burn_direction: BurnVector
    timestep: float = 1.0
    include_j2: bool = False

    def __post_init__(self) -> None:
        """Validate mission configuration."""
        if self.timestep <= 0:
            raise ValueError(
                "Mission timestep must be greater than zero."
            )

        if self.burn.thrust_model != self.thrust_model:
            raise ValueError(
                "Burn and mission must use the same thrust model."
            )

        if self.burn_direction.magnitude <= 0:
            raise ValueError(
                "Burn direction cannot be the zero vector."
            )

        if not self.burn.can_complete(
            self.initial_state.mass
        ):
            raise ValueError(
                "Mission burn cannot be completed with available propellant."
            )


@dataclass(frozen=True)
class MissionResult:
    """Result of an integrated finite-thrust mission."""

    initial_state: State3DThrust
    final_state: State3DThrust | State3DThrustJ2
    duration: float
    timestep: float
    include_j2: bool

    @property
    def propellant_consumed(self) -> float:
        """Return propellant consumed by the mission."""
        return (
            self.initial_state.mass -
            self.final_state.mass
        )

    @property
    def mass_remaining(self) -> float:
        """Return final spacecraft mass."""
        return self.final_state.mass

    @property
    def position(self) -> tuple[float, float, float]:
        """Return final position vector."""
        return (
            self.final_state.x,
            self.final_state.y,
            self.final_state.z,
        )

    @property
    def velocity(self) -> tuple[float, float, float]:
        """Return final velocity vector."""
        return (
            self.final_state.vx,
            self.final_state.vy,
            self.final_state.vz,
        )


def run_finite_thrust_mission(
    mission: FiniteThrustMission,
) -> MissionResult:
    """Execute a configured finite-thrust mission segment."""
    direction = mission.burn_direction.unit

    if mission.include_j2:
        initial_state = State3DThrustJ2(
            x=mission.initial_state.x,
            y=mission.initial_state.y,
            z=mission.initial_state.z,
            vx=mission.initial_state.vx,
            vy=mission.initial_state.vy,
            vz=mission.initial_state.vz,
            mass=mission.initial_state.mass,
        )

        final_state = propagate_to_time_j2(
            initial_state=initial_state,
            duration=mission.burn.duration,
            dt=mission.timestep,
            thrust_model=mission.thrust_model,
            thrust_direction=direction,
            dry_mass=mission.burn.dry_mass,
        )
    else:
        final_state = propagate_to_time(
            initial_state=mission.initial_state,
            duration=mission.burn.duration,
            dt=mission.timestep,
            thrust_model=mission.thrust_model,
            thrust_direction=direction,
            dry_mass=mission.burn.dry_mass,
        )

    return MissionResult(
        initial_state=mission.initial_state,
        final_state=final_state,
        duration=mission.burn.duration,
        timestep=mission.timestep,
        include_j2=mission.include_j2,
    )
