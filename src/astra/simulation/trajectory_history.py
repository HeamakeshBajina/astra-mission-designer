"""Trajectory-history generation for ASTRA."""

from dataclasses import dataclass
from collections.abc import Sequence

from astra.physics.burn_vector import BurnVector
from astra.physics.thrust import ThrustModel
from astra.simulation.propagator_3d_thrust import (
    State3DThrust,
    rk4_step_thrust,
)
from astra.simulation.propagator_3d_thrust_j2 import (
    State3DThrustJ2,
    rk4_step_thrust_j2,
)


@dataclass(frozen=True)
class TrajectoryPoint:
    """A spacecraft state recorded at a specific mission time."""

    time: float
    state: State3DThrust | State3DThrustJ2


@dataclass(frozen=True)
class TrajectoryHistory:
    """Complete numerical history of a spacecraft trajectory."""

    points: tuple[TrajectoryPoint, ...]
    timestep: float
    duration: float
    include_j2: bool

    def __post_init__(self) -> None:
        """Validate trajectory-history metadata and time ordering."""

        if self.timestep <= 0:
            raise ValueError(
                "Trajectory timestep must be greater than zero."
            )

        if self.duration < 0:
            raise ValueError(
                "Trajectory duration cannot be negative."
            )

        if not self.points:
            raise ValueError(
                "Trajectory history cannot be empty."
            )

        previous_time = -1.0

        for point in self.points:
            if point.time < 0:
                raise ValueError(
                    "Trajectory time cannot be negative."
                )

            if point.time < previous_time:
                raise ValueError(
                    "Trajectory points must be ordered by time."
                )

            previous_time = point.time

    @property
    def point_count(self) -> int:
        """Return the number of recorded trajectory points."""

        return len(self.points)

    @property
    def times(self) -> tuple[float, ...]:
        """Return all recorded mission times."""

        return tuple(
            point.time
            for point in self.points
        )

    @property
    def states(
        self,
    ) -> tuple[State3DThrust | State3DThrustJ2, ...]:
        """Return all recorded spacecraft states."""

        return tuple(
            point.state
            for point in self.points
        )

    @property
    def positions(
        self,
    ) -> tuple[tuple[float, float, float], ...]:
        """Return all recorded Cartesian positions."""

        return tuple(
            (
                point.state.x,
                point.state.y,
                point.state.z,
            )
            for point in self.points
        )

    @property
    def velocities(
        self,
    ) -> tuple[tuple[float, float, float], ...]:
        """Return all recorded Cartesian velocities."""

        return tuple(
            (
                point.state.vx,
                point.state.vy,
                point.state.vz,
            )
            for point in self.points
        )

    @property
    def masses(self) -> tuple[float, ...]:
        """Return spacecraft mass at every recorded point."""

        return tuple(
            point.state.mass
            for point in self.points
        )

    @property
    def initial_state(
        self,
    ) -> State3DThrust | State3DThrustJ2:
        """Return the initial spacecraft state."""

        return self.points[0].state

    @property
    def final_state(
        self,
    ) -> State3DThrust | State3DThrustJ2:
        """Return the final spacecraft state."""

        return self.points[-1].state

    @property
    def final_time(self) -> float:
        """Return the final recorded mission time."""

        return self.points[-1].time


def _validate_inputs(
    initial_state: State3DThrust,
    duration: float,
    timestep: float,
    thrust_model: ThrustModel,
    thrust_direction: BurnVector | Sequence[float],
    dry_mass: float | None,
) -> tuple[float, float, tuple[float, float, float]]:
    """Validate and normalize trajectory-generation inputs."""

    if duration < 0:
        raise ValueError(
            "Trajectory duration cannot be negative."
        )

    if timestep <= 0:
        raise ValueError(
            "Trajectory timestep must be greater than zero."
        )

    if initial_state.mass <= 0:
        raise ValueError(
            "Initial mass must be greater than zero."
        )

    if dry_mass is not None:
        if dry_mass <= 0:
            raise ValueError(
                "Dry mass must be greater than zero."
            )

        if dry_mass > initial_state.mass:
            raise ValueError(
                "Dry mass cannot exceed initial mass."
            )

    if not isinstance(
        thrust_direction,
        BurnVector,
    ):
        thrust_direction = BurnVector(
            *thrust_direction
        )

    direction = thrust_direction.unit

    return (
        duration,
        timestep,
        direction,
    )


def _append_point(
    points: list[TrajectoryPoint],
    time: float,
    state: State3DThrust | State3DThrustJ2,
) -> None:
    """Append a trajectory point."""

    points.append(
        TrajectoryPoint(
            time=time,
            state=state,
        )
    )


def simulate_trajectory(
    initial_state: State3DThrust,
    duration: float,
    timestep: float,
    thrust_model: ThrustModel,
    thrust_direction: BurnVector | Sequence[float],
    dry_mass: float | None = None,
) -> TrajectoryHistory:
    """Generate a complete 3D finite-thrust trajectory history.

    The initial state is recorded at t=0. Subsequent states are
    generated using fourth-order Runge-Kutta integration. If the
    requested duration is not evenly divisible by the timestep,
    a final partial timestep is used so that the final recorded
    time is exactly the requested duration.

    Parameters
    ----------
    initial_state:
        Initial Cartesian spacecraft state.

    duration:
        Total propagation duration in seconds.

    timestep:
        Integration timestep in seconds.

    thrust_model:
        Constant-thrust propulsion model.

    thrust_direction:
        Direction of thrust.

    dry_mass:
        Optional minimum spacecraft mass.

    Returns
    -------
    TrajectoryHistory
        Complete time-ordered trajectory.
    """

    (
        duration,
        timestep,
        direction,
    ) = _validate_inputs(
        initial_state=initial_state,
        duration=duration,
        timestep=timestep,
        thrust_model=thrust_model,
        thrust_direction=thrust_direction,
        dry_mass=dry_mass,
    )

    points: list[TrajectoryPoint] = []

    current_state = initial_state
    current_time = 0.0

    _append_point(
        points,
        current_time,
        current_state,
    )

    while current_time < duration:
        step = min(
            timestep,
            duration - current_time,
        )

        current_state = rk4_step_thrust(
            state=current_state,
            dt=step,
            thrust_model=thrust_model,
            thrust_direction=direction,
            dry_mass=dry_mass,
        )

        current_time += step

        if abs(current_time - duration) < 1e-12:
            current_time = duration

        _append_point(
            points,
            current_time,
            current_state,
        )

    return TrajectoryHistory(
        points=tuple(points),
        timestep=timestep,
        duration=duration,
        include_j2=False,
    )


def simulate_trajectory_j2(
    initial_state: State3DThrust,
    duration: float,
    timestep: float,
    thrust_model: ThrustModel,
    thrust_direction: BurnVector | Sequence[float],
    dry_mass: float | None = None,
) -> TrajectoryHistory:
    """Generate a complete 3D finite-thrust trajectory with J2.

    The initial state is recorded at t=0. Subsequent states are
    generated using fourth-order Runge-Kutta integration with
    central gravity, J2 perturbation, finite thrust, and mass flow.

    Parameters
    ----------
    initial_state:
        Initial Cartesian spacecraft state.

    duration:
        Total propagation duration in seconds.

    timestep:
        Integration timestep in seconds.

    thrust_model:
        Constant-thrust propulsion model.

    thrust_direction:
        Direction of thrust.

    dry_mass:
        Optional minimum spacecraft mass.

    Returns
    -------
    TrajectoryHistory
        Complete time-ordered trajectory including J2.
    """

    (
        duration,
        timestep,
        direction,
    ) = _validate_inputs(
        initial_state=initial_state,
        duration=duration,
        timestep=timestep,
        thrust_model=thrust_model,
        thrust_direction=thrust_direction,
        dry_mass=dry_mass,
    )

    points: list[TrajectoryPoint] = []

    current_state = State3DThrustJ2(
        x=initial_state.x,
        y=initial_state.y,
        z=initial_state.z,
        vx=initial_state.vx,
        vy=initial_state.vy,
        vz=initial_state.vz,
        mass=initial_state.mass,
    )

    current_time = 0.0

    _append_point(
        points,
        current_time,
        current_state,
    )

    while current_time < duration:
        step = min(
            timestep,
            duration - current_time,
        )

        current_state = rk4_step_thrust_j2(
            state=current_state,
            dt=step,
            thrust_model=thrust_model,
            thrust_direction=direction,
            dry_mass=dry_mass,
        )

        current_time += step

        if abs(current_time - duration) < 1e-12:
            current_time = duration

        _append_point(
            points,
            current_time,
            current_state,
        )

    return TrajectoryHistory(
        points=tuple(points),
        timestep=timestep,
        duration=duration,
        include_j2=True,
    )
