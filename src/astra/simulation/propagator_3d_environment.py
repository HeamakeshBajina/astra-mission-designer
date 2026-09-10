"""High-fidelity environmental 3D spacecraft propagator for ASTRA."""

from dataclasses import dataclass
import math

from astra.physics.atmosphere import (
    AtmosphericModel,
    DragModel,
    drag_acceleration,
)
from astra.physics.burn_vector import resolve_burn_direction
from astra.physics.j2 import j2_acceleration
from astra.physics.srp import (
    SolarRadiationPressureModel,
    srp_acceleration,
)
from astra.physics.thrust import ThrustModel
from astra.physics.constants import EARTH_MU


@dataclass(frozen=True)
class State3DEnvironment:
    """Three-dimensional spacecraft state including mass."""

    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float

    def __post_init__(self) -> None:
        """Validate the spacecraft state."""

        if self.mass <= 0:
            raise ValueError(
                "Spacecraft mass must be greater than zero."
            )

    @property
    def position(self) -> tuple[float, float, float]:
        """Return position vector in metres."""

        return (self.x, self.y, self.z)

    @property
    def velocity(self) -> tuple[float, float, float]:
        """Return velocity vector in metres per second."""

        return (self.vx, self.vy, self.vz)


@dataclass(frozen=True)
class EnvironmentalModels:
    """Environmental and propulsion models used by the propagator."""

    atmospheric_model: AtmosphericModel | None = None
    drag_model: DragModel | None = None
    srp_model: SolarRadiationPressureModel | None = None
    thrust_model: ThrustModel | None = None

    def __post_init__(self) -> None:
        """Validate environmental model combinations."""

        if (
            self.drag_model is not None
            and self.atmospheric_model is None
        ):
            raise ValueError(
                "A drag model requires an atmospheric model."
            )

        if (
            self.thrust_model is not None
            and self.thrust_model.thrust == 0.0
        ):
            raise ValueError(
                "A thrust model must have positive thrust."
            )


@dataclass(frozen=True)
class EnvironmentalForces:
    """Individual acceleration contributions."""

    gravity: tuple[float, float, float]
    j2: tuple[float, float, float]
    drag: tuple[float, float, float]
    srp: tuple[float, float, float]
    thrust: tuple[float, float, float]

    @property
    def total(self) -> tuple[float, float, float]:
        """Return total acceleration."""

        return (
            self.gravity[0]
            + self.j2[0]
            + self.drag[0]
            + self.srp[0]
            + self.thrust[0],
            self.gravity[1]
            + self.j2[1]
            + self.drag[1]
            + self.srp[1]
            + self.thrust[1],
            self.gravity[2]
            + self.j2[2]
            + self.drag[2]
            + self.srp[2]
            + self.thrust[2],
        )


def gravitational_acceleration(
    position: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Return central Earth gravitational acceleration."""

    x, y, z = position

    radius = math.sqrt(
        x * x
        + y * y
        + z * z
    )

    if radius <= 0:
        raise ValueError(
            "Position cannot be the zero vector."
        )

    factor = -EARTH_MU / radius**3

    return (
        factor * x,
        factor * y,
        factor * z,
    )


def environmental_forces(
    state: State3DEnvironment,
    models: EnvironmentalModels,
    thrust_direction: tuple[float, float, float] | None = None,
    sun_direction: tuple[float, float, float] | None = None,
    distance_from_sun: float | None = None,
    eclipse: bool = False,
    dry_mass: float | None = None,
) -> EnvironmentalForces:
    """Calculate all environmental and propulsion accelerations."""

    gravity = gravitational_acceleration(
        state.position
    )

    j2 = j2_acceleration(*state.position)

    if (
        models.drag_model is not None
        and models.atmospheric_model is not None
    ):
        drag = drag_acceleration(
            position=state.position,
            velocity=state.velocity,
            mass=state.mass,
            drag_model=models.drag_model,
            atmospheric_model=models.atmospheric_model,
        )
    else:
        drag = (0.0, 0.0, 0.0)

    if (
        models.srp_model is not None
        and sun_direction is not None
        and not eclipse
    ):
        srp = srp_acceleration(
            position=state.position,
            mass=state.mass,
            model=models.srp_model,
            sun_direction=sun_direction,
            distance_from_sun=distance_from_sun,
        )
    else:
        srp = (0.0, 0.0, 0.0)

    if (
        models.thrust_model is not None
        and thrust_direction is not None
        and models.thrust_model.thrust > 0.0
    ):
        direction = resolve_burn_direction(
            thrust_direction
        )

        thrust_acceleration_magnitude = (
            models.thrust_model.thrust
            / state.mass
        )

        if (
            dry_mass is not None
            and state.mass <= dry_mass
        ):
            thrust = (0.0, 0.0, 0.0)
        else:
            thrust = (
                thrust_acceleration_magnitude
                * direction[0],
                thrust_acceleration_magnitude
                * direction[1],
                thrust_acceleration_magnitude
                * direction[2],
            )
    else:
        thrust = (0.0, 0.0, 0.0)

    return EnvironmentalForces(
        gravity=gravity,
        j2=j2,
        drag=drag,
        srp=srp,
        thrust=thrust,
    )


def _derivatives(
    state: State3DEnvironment,
    models: EnvironmentalModels,
    thrust_direction: tuple[float, float, float] | None,
    sun_direction: tuple[float, float, float] | None,
    distance_from_sun: float | None,
    eclipse: bool,
    dry_mass: float | None,
) -> tuple[float, float, float, float, float, float, float]:
    """Return state derivatives."""

    forces = environmental_forces(
        state=state,
        models=models,
        thrust_direction=thrust_direction,
        sun_direction=sun_direction,
        distance_from_sun=distance_from_sun,
        eclipse=eclipse,
        dry_mass=dry_mass,
    )

    acceleration = forces.total

    if (
        models.thrust_model is not None
        and models.thrust_model.thrust > 0.0
        and thrust_direction is not None
        and (
            dry_mass is None
            or state.mass > dry_mass
        )
    ):
        mass_flow_rate = (
            -models.thrust_model.mass_flow_rate
        )
    else:
        mass_flow_rate = 0.0

    return (
        state.vx,
        state.vy,
        state.vz,
        acceleration[0],
        acceleration[1],
        acceleration[2],
        mass_flow_rate,
    )


def _add_scaled(
    state: State3DEnvironment,
    derivative: tuple[
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    ],
    scale: float,
) -> State3DEnvironment:
    """Add a scaled derivative to a spacecraft state."""

    return State3DEnvironment(
        x=state.x + derivative[0] * scale,
        y=state.y + derivative[1] * scale,
        z=state.z + derivative[2] * scale,
        vx=state.vx + derivative[3] * scale,
        vy=state.vy + derivative[4] * scale,
        vz=state.vz + derivative[5] * scale,
        mass=state.mass + derivative[6] * scale,
    )


def rk4_step_environment(
    state: State3DEnvironment,
    dt: float,
    models: EnvironmentalModels,
    thrust_direction: tuple[float, float, float] | None = None,
    sun_direction: tuple[float, float, float] | None = None,
    distance_from_sun: float | None = None,
    eclipse: bool = False,
    dry_mass: float | None = None,
) -> State3DEnvironment:
    """Advance an environmental spacecraft state by one RK4 step."""

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    if dry_mass is not None:
        if dry_mass <= 0:
            raise ValueError(
                "Dry mass must be greater than zero."
            )

        if state.mass < dry_mass:
            raise ValueError(
                "Spacecraft mass cannot be below dry mass."
            )

    k1 = _derivatives(
        state,
        models,
        thrust_direction,
        sun_direction,
        distance_from_sun,
        eclipse,
        dry_mass,
    )

    k2_state = _add_scaled(
        state,
        k1,
        dt / 2.0,
    )

    k2 = _derivatives(
        k2_state,
        models,
        thrust_direction,
        sun_direction,
        distance_from_sun,
        eclipse,
        dry_mass,
    )

    k3_state = _add_scaled(
        state,
        k2,
        dt / 2.0,
    )

    k3 = _derivatives(
        k3_state,
        models,
        thrust_direction,
        sun_direction,
        distance_from_sun,
        eclipse,
        dry_mass,
    )

    k4_state = _add_scaled(
        state,
        k3,
        dt,
    )

    k4 = _derivatives(
        k4_state,
        models,
        thrust_direction,
        sun_direction,
        distance_from_sun,
        eclipse,
        dry_mass,
    )

    result = State3DEnvironment(
        x=state.x
        + dt / 6.0
        * (
            k1[0]
            + 2.0 * k2[0]
            + 2.0 * k3[0]
            + k4[0]
        ),
        y=state.y
        + dt / 6.0
        * (
            k1[1]
            + 2.0 * k2[1]
            + 2.0 * k3[1]
            + k4[1]
        ),
        z=state.z
        + dt / 6.0
        * (
            k1[2]
            + 2.0 * k2[2]
            + 2.0 * k3[2]
            + k4[2]
        ),
        vx=state.vx
        + dt / 6.0
        * (
            k1[3]
            + 2.0 * k2[3]
            + 2.0 * k3[3]
            + k4[3]
        ),
        vy=state.vy
        + dt / 6.0
        * (
            k1[4]
            + 2.0 * k2[4]
            + 2.0 * k3[4]
            + k4[4]
        ),
        vz=state.vz
        + dt / 6.0
        * (
            k1[5]
            + 2.0 * k2[5]
            + 2.0 * k3[5]
            + k4[5]
        ),
        mass=state.mass
        + dt / 6.0
        * (
            k1[6]
            + 2.0 * k2[6]
            + 2.0 * k3[6]
            + k4[6]
        ),
    )

    if dry_mass is not None and result.mass < dry_mass:
        result = State3DEnvironment(
            x=result.x,
            y=result.y,
            z=result.z,
            vx=result.vx,
            vy=result.vy,
            vz=result.vz,
            mass=dry_mass,
        )

    return result


def propagate_environment(
    initial_state: State3DEnvironment,
    duration: float,
    dt: float,
    models: EnvironmentalModels,
    thrust_direction: tuple[float, float, float] | None = None,
    sun_direction: tuple[float, float, float] | None = None,
    distance_from_sun: float | None = None,
    eclipse: bool = False,
    dry_mass: float | None = None,
) -> State3DEnvironment:
    """Propagate a spacecraft through the configured environment."""

    if duration < 0:
        raise ValueError(
            "Duration cannot be negative."
        )

    if dt <= 0:
        raise ValueError(
            "Timestep must be greater than zero."
        )

    if dry_mass is not None:
        if dry_mass <= 0:
            raise ValueError(
                "Dry mass must be greater than zero."
            )

        if initial_state.mass < dry_mass:
            raise ValueError(
                "Initial mass cannot be below dry mass."
            )

    state = initial_state
    elapsed = 0.0

    while elapsed < duration:
        step = min(
            dt,
            duration - elapsed,
        )

        state = rk4_step_environment(
            state=state,
            dt=step,
            models=models,
            thrust_direction=thrust_direction,
            sun_direction=sun_direction,
            distance_from_sun=distance_from_sun,
            eclipse=eclipse,
            dry_mass=dry_mass,
        )

        elapsed += step

    return state



