"""Reference scenarios for validating ASTRA physics and simulation."""

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU, EARTH_RADIUS, G0
from astra.physics.orbital import (
    circular_orbital_velocity,
    escape_velocity,
    orbital_period,
)
from astra.physics.rocket import (
    delta_v_from_mass_ratio,
    final_mass_for_delta_v,
)
from astra.physics.thrust import ThrustModel


@dataclass(frozen=True)
class ReferenceScenario:
    """A known engineering scenario with expected reference values."""

    name: str
    description: str
    expected_values: dict[str, float]
    tolerances: dict[str, float]


def leo_circular_orbit() -> ReferenceScenario:
    """Return a 400 km circular Earth orbit reference case."""

    altitude = 400_000.0
    radius = EARTH_RADIUS + altitude

    velocity = circular_orbital_velocity(radius)
    period = orbital_period(radius)

    return ReferenceScenario(
        name="400 km Circular LEO",
        description=(
            "Reference circular orbit at 400 km altitude "
            "using the standard Earth gravitational parameter."
        ),
        expected_values={
            "radius": radius,
            "altitude": altitude,
            "velocity": velocity,
            "period": period,
        },
        tolerances={
            "radius": 1e-9,
            "altitude": 1e-9,
            "velocity": 1e-9,
            "period": 1e-9,
        },
    )


def escape_velocity_case() -> ReferenceScenario:
    """Return a reference escape-velocity case at 400 km altitude."""

    altitude = 400_000.0
    radius = EARTH_RADIUS + altitude
    velocity = escape_velocity(radius)

    specific_energy = (
        velocity**2 / 2.0
        - EARTH_MU / radius
    )

    return ReferenceScenario(
        name="400 km Escape Velocity",
        description=(
            "Escape velocity at 400 km altitude. "
            "The resulting specific orbital energy should "
            "approach zero for the ideal two-body model."
        ),
        expected_values={
            "radius": radius,
            "velocity": velocity,
            "specific_energy": specific_energy,
        },
        tolerances={
            "radius": 1e-9,
            "velocity": 1e-9,
            "specific_energy": 1e-6,
        },
    )


def hohmann_earth_case() -> ReferenceScenario:
    """Return a reference Hohmann transfer from 400 km to 800 km."""

    initial_radius = EARTH_RADIUS + 400_000.0
    final_radius = EARTH_RADIUS + 800_000.0

    v_initial = circular_orbital_velocity(initial_radius)
    v_final = circular_orbital_velocity(final_radius)

    transfer_radius = (
        initial_radius + final_radius
    ) / 2.0

    transfer_velocity_initial = math.sqrt(
        EARTH_MU
        * (
            2.0 / initial_radius
            - 1.0 / transfer_radius
        )
    )

    transfer_velocity_final = math.sqrt(
        EARTH_MU
        * (
            2.0 / final_radius
            - 1.0 / transfer_radius
        )
    )

    delta_v_1 = (
        transfer_velocity_initial
        - v_initial
    )

    delta_v_2 = (
        v_final
        - transfer_velocity_final
    )

    total_delta_v = abs(delta_v_1) + abs(delta_v_2)

    return ReferenceScenario(
        name="400 km to 800 km Hohmann Transfer",
        description=(
            "Two-impulse coplanar Hohmann transfer "
            "between two circular Earth orbits."
        ),
        expected_values={
            "initial_radius": initial_radius,
            "final_radius": final_radius,
            "delta_v_1": delta_v_1,
            "delta_v_2": delta_v_2,
            "total_delta_v": total_delta_v,
        },
        tolerances={
            "initial_radius": 1e-9,
            "final_radius": 1e-9,
            "delta_v_1": 1e-9,
            "delta_v_2": 1e-9,
            "total_delta_v": 1e-9,
        },
    )


def rocket_equation_case() -> ReferenceScenario:
    """Return a reference Tsiolkovsky rocket-equation case."""

    initial_mass = 1_000.0
    final_mass = 800.0
    specific_impulse = 300.0

    delta_v = delta_v_from_mass_ratio(
        initial_mass=initial_mass,
        final_mass=final_mass,
        specific_impulse=specific_impulse,
    )

    recovered_final_mass = final_mass_for_delta_v(
        initial_mass=initial_mass,
        delta_v=delta_v,
        specific_impulse=specific_impulse,
    )

    return ReferenceScenario(
        name="Tsiolkovsky Rocket Equation",
        description=(
            "Reference mass-ratio and delta-v calculation "
            "for a 300 s specific-impulse propulsion system."
        ),
        expected_values={
            "initial_mass": initial_mass,
            "final_mass": final_mass,
            "specific_impulse": specific_impulse,
            "delta_v": delta_v,
            "recovered_final_mass": recovered_final_mass,
        },
        tolerances={
            "initial_mass": 1e-12,
            "final_mass": 1e-12,
            "specific_impulse": 1e-12,
            "delta_v": 1e-9,
            "recovered_final_mass": 1e-9,
        },
    )


def finite_thrust_case() -> ReferenceScenario:
    """Return a finite-thrust mass-flow reference case."""

    thrust = 1_000.0
    specific_impulse = 300.0
    duration = 30.0
    initial_mass = 1_000.0

    thrust_model = ThrustModel(
        thrust=thrust,
        specific_impulse=specific_impulse,
    )

    mass_flow_rate = thrust / (
        specific_impulse * G0
    )

    propellant_consumed = (
        mass_flow_rate * duration
    )

    final_mass = initial_mass - propellant_consumed

    return ReferenceScenario(
        name="Finite Thrust Mass Flow",
        description=(
            "Constant-thrust propulsion reference case "
            "using mdot = T / (Isp g0)."
        ),
        expected_values={
            "mass_flow_rate": mass_flow_rate,
            "propellant_consumed": propellant_consumed,
            "final_mass": final_mass,
            "thrust": thrust_model.thrust,
        },
        tolerances={
            "mass_flow_rate": 1e-12,
            "propellant_consumed": 1e-9,
            "final_mass": 1e-9,
            "thrust": 1e-12,
        },
    )


def all_reference_scenarios() -> tuple[ReferenceScenario, ...]:
    """Return all ASTRA reference scenarios."""

    return (
        leo_circular_orbit(),
        escape_velocity_case(),
        hohmann_earth_case(),
        rocket_equation_case(),
        finite_thrust_case(),
    )
