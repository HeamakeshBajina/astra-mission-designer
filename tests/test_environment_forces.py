"""Tests for ASTRA atmospheric, SRP, and environmental propagation models."""

import math

import pytest

from astra.physics.atmosphere import (
    AtmosphericModel,
    DragModel,
    atmospheric_rotation_velocity,
    drag_acceleration,
    relative_atmospheric_velocity,
)
from astra.physics.srp import (
    SolarRadiationPressureModel,
    solar_pressure_at_distance,
    srp_acceleration,
)
from astra.physics.constants import EARTH_RADIUS
from astra.simulation.propagator_3d_environment import (
    EnvironmentalForces,
    EnvironmentalModels,
    State3DEnvironment,
    environmental_forces,
    gravitational_acceleration,
    propagate_environment,
    rk4_step_environment,
)
from astra.physics.thrust import ThrustModel


LEO_RADIUS = EARTH_RADIUS + 400_000.0


# ---------------------------------------------------------------------------
# Atmospheric model
# ---------------------------------------------------------------------------


def test_default_atmosphere_has_positive_surface_density():
    model = AtmosphericModel()

    assert model.density(0.0) == pytest.approx(1.225)


def test_atmospheric_density_decreases_with_altitude():
    model = AtmosphericModel()

    surface = model.density(0.0)
    higher = model.density(100_000.0)

    assert higher < surface


def test_atmospheric_density_follows_exponential_model():
    model = AtmosphericModel(
        reference_density=1.0,
        reference_altitude=0.0,
        scale_height=10_000.0,
    )

    expected = math.exp(-2.0)

    assert model.density(20_000.0) == pytest.approx(
        expected
    )


def test_atmospheric_density_at_reference_altitude():
    model = AtmosphericModel(
        reference_density=0.5,
        reference_altitude=100_000.0,
        scale_height=8_500.0,
    )

    assert model.density(100_000.0) == pytest.approx(0.5)


def test_atmospheric_density_above_validity_range_is_zero():
    model = AtmosphericModel(
        maximum_altitude=100_000.0,
    )

    assert model.density(100_001.0) == 0.0


def test_atmospheric_density_below_minimum_range_is_zero():
    model = AtmosphericModel(
        minimum_altitude=100_000.0,
        reference_altitude=100_000.0,
    )

    assert model.density(99_999.0) == 0.0


def test_negative_altitude_is_rejected():
    model = AtmosphericModel()

    with pytest.raises(ValueError):
        model.density(-1.0)


def test_atmospheric_radius_conversion():
    model = AtmosphericModel(
        reference_density=1.0,
        reference_altitude=0.0,
        scale_height=10_000.0,
    )

    assert model.density_at_radius(
        EARTH_RADIUS
    ) == pytest.approx(1.0)


def test_radius_below_earth_surface_is_rejected():
    model = AtmosphericModel()

    with pytest.raises(ValueError):
        model.density_at_radius(
            EARTH_RADIUS - 1.0
        )


def test_invalid_atmospheric_parameters_are_rejected():
    with pytest.raises(ValueError):
        AtmosphericModel(
            reference_density=0.0
        )

    with pytest.raises(ValueError):
        AtmosphericModel(
            scale_height=0.0
        )

    with pytest.raises(ValueError):
        AtmosphericModel(
            minimum_altitude=100_000.0,
            maximum_altitude=100_000.0,
        )


# ---------------------------------------------------------------------------
# Atmospheric rotation
# ---------------------------------------------------------------------------


def test_atmospheric_rotation_velocity_at_x_axis():
    velocity = atmospheric_rotation_velocity(
        position=(EARTH_RADIUS, 0.0, 0.0)
    )

    assert velocity[0] == pytest.approx(0.0)
    assert velocity[1] > 0.0
    assert velocity[2] == pytest.approx(0.0)


def test_atmospheric_rotation_velocity_at_y_axis():
    velocity = atmospheric_rotation_velocity(
        position=(0.0, EARTH_RADIUS, 0.0)
    )

    assert velocity[0] < 0.0
    assert velocity[1] == pytest.approx(0.0)
    assert velocity[2] == pytest.approx(0.0)


def test_relative_velocity_subtracts_atmospheric_rotation():
    relative = relative_atmospheric_velocity(
        velocity=(0.0, 8_000.0, 0.0),
        position=(LEO_RADIUS, 0.0, 0.0),
    )

    assert relative[0] == pytest.approx(0.0)
    assert relative[1] < 8_000.0
    assert relative[2] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Drag model
# ---------------------------------------------------------------------------


def test_drag_model_rejects_negative_parameters():
    with pytest.raises(ValueError):
        DragModel(
            drag_coefficient=-1.0,
            reference_area=1.0,
        )

    with pytest.raises(ValueError):
        DragModel(
            drag_coefficient=2.2,
            reference_area=-1.0,
        )


def test_drag_acceleration_opposes_relative_motion():
    atmosphere = AtmosphericModel(
        reference_density=1.0,
        reference_altitude=400_000.0,
        scale_height=100_000.0,
    )

    drag_model = DragModel(
        drag_coefficient=2.2,
        reference_area=10.0,
    )

    acceleration = drag_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        drag_model=drag_model,
        atmospheric_model=atmosphere,
    )

    assert acceleration[0] == pytest.approx(0.0)
    assert acceleration[1] < 0.0
    assert acceleration[2] == pytest.approx(0.0)


def test_drag_is_zero_when_density_is_zero():
    atmosphere = AtmosphericModel(
        maximum_altitude=100_000.0,
    )

    drag_model = DragModel(
        drag_coefficient=2.2,
        reference_area=10.0,
    )

    acceleration = drag_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        drag_model=drag_model,
        atmospheric_model=atmosphere,
    )

    assert acceleration == (
        0.0,
        0.0,
        0.0,
    )


def test_drag_is_zero_for_zero_area():
    atmosphere = AtmosphericModel(
        reference_density=1.0,
        reference_altitude=400_000.0,
        scale_height=100_000.0,
    )

    drag_model = DragModel(
        drag_coefficient=2.2,
        reference_area=0.0,
    )

    acceleration = drag_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        drag_model=drag_model,
        atmospheric_model=atmosphere,
    )

    assert acceleration == (
        0.0,
        0.0,
        0.0,
    )


def test_drag_acceleration_scales_with_area():
    atmosphere = AtmosphericModel(
        reference_density=1.0,
        reference_altitude=400_000.0,
        scale_height=100_000.0,
    )

    small = DragModel(
        drag_coefficient=2.2,
        reference_area=5.0,
    )

    large = DragModel(
        drag_coefficient=2.2,
        reference_area=10.0,
    )

    small_acceleration = drag_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        drag_model=small,
        atmospheric_model=atmosphere,
    )

    large_acceleration = drag_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        velocity=(0.0, 7_700.0, 0.0),
        mass=1_000.0,
        drag_model=large,
        atmospheric_model=atmosphere,
    )

    assert large_acceleration[1] == pytest.approx(
        2.0 * small_acceleration[1]
    )


def test_drag_rejects_nonpositive_mass():
    with pytest.raises(ValueError):
        drag_acceleration(
            position=(LEO_RADIUS, 0.0, 0.0),
            velocity=(0.0, 7_700.0, 0.0),
            mass=0.0,
            drag_model=DragModel(
                drag_coefficient=2.2,
                reference_area=10.0,
            ),
        )


# ---------------------------------------------------------------------------
# SRP model
# ---------------------------------------------------------------------------


def test_default_solar_pressure_is_physical_order():
    model = SolarRadiationPressureModel()

    assert model.solar_pressure == pytest.approx(
        4.56e-6
    )


def test_solar_pressure_is_inverse_square_with_distance():
    pressure = solar_pressure_at_distance(
        distance_from_sun=2.0 * 149_597_870_700.0
    )

    assert pressure == pytest.approx(
        4.56e-6 / 4.0
    )


def test_solar_pressure_rejects_invalid_distance():
    with pytest.raises(ValueError):
        solar_pressure_at_distance(
            distance_from_sun=0.0
        )


def test_srp_acceleration_points_away_from_sun():
    model = SolarRadiationPressureModel(
        reference_area=10.0,
    )

    acceleration = srp_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        mass=1_000.0,
        model=model,
        sun_direction=(1.0, 0.0, 0.0),
    )

    assert acceleration[0] < 0.0
    assert acceleration[1] == pytest.approx(0.0)
    assert acceleration[2] == pytest.approx(0.0)


def test_srp_acceleration_is_zero_for_zero_area():
    model = SolarRadiationPressureModel(
        reference_area=0.0,
    )

    acceleration = srp_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        mass=1_000.0,
        model=model,
        sun_direction=(1.0, 0.0, 0.0),
    )

    assert acceleration == (
        0.0,
        0.0,
        0.0,
    )


def test_srp_acceleration_scales_with_area():
    small = SolarRadiationPressureModel(
        reference_area=5.0,
    )

    large = SolarRadiationPressureModel(
        reference_area=10.0,
    )

    small_acceleration = srp_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        mass=1_000.0,
        model=small,
        sun_direction=(1.0, 0.0, 0.0),
    )

    large_acceleration = srp_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0),
        mass=1_000.0,
        model=large,
        sun_direction=(1.0, 0.0, 0.0),
    )

    assert large_acceleration[0] == pytest.approx(
        2.0 * small_acceleration[0]
    )


def test_srp_acceleration_rejects_zero_sun_direction():
    model = SolarRadiationPressureModel(
        reference_area=10.0,
    )

    with pytest.raises(ValueError):
        srp_acceleration(
            position=(LEO_RADIUS, 0.0, 0.0),
            mass=1_000.0,
            model=model,
            sun_direction=(0.0, 0.0, 0.0),
        )


def test_srp_acceleration_rejects_nonpositive_mass():
    model = SolarRadiationPressureModel(
        reference_area=10.0,
    )

    with pytest.raises(ValueError):
        srp_acceleration(
            position=(LEO_RADIUS, 0.0, 0.0),
            mass=0.0,
            model=model,
            sun_direction=(1.0, 0.0, 0.0),
        )


def test_srp_model_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        SolarRadiationPressureModel(
            solar_pressure=-1.0
        )

    with pytest.raises(ValueError):
        SolarRadiationPressureModel(
            reflectivity_coefficient=-1.0
        )

    with pytest.raises(ValueError):
        SolarRadiationPressureModel(
            reference_area=-1.0
        )


# ---------------------------------------------------------------------------
# Environmental propagator
# ---------------------------------------------------------------------------


def test_state_rejects_nonpositive_mass():
    with pytest.raises(ValueError):
        State3DEnvironment(
            x=LEO_RADIUS,
            y=0.0,
            z=0.0,
            vx=0.0,
            vy=7_700.0,
            vz=0.0,
            mass=0.0,
        )


def test_gravity_points_toward_earth():
    acceleration = gravitational_acceleration(
        position=(LEO_RADIUS, 0.0, 0.0)
    )

    assert acceleration[0] < 0.0
    assert acceleration[1] == pytest.approx(0.0)
    assert acceleration[2] == pytest.approx(0.0)


def test_environmental_models_require_atmosphere_for_drag():
    with pytest.raises(ValueError):
        EnvironmentalModels(
            drag_model=DragModel(
                drag_coefficient=2.2,
                reference_area=10.0,
            )
        )


def test_environmental_models_accept_independent_models():
    models = EnvironmentalModels(
        atmospheric_model=AtmosphericModel(),
        drag_model=DragModel(
            drag_coefficient=2.2,
            reference_area=10.0,
        ),
        srp_model=SolarRadiationPressureModel(
            reference_area=10.0,
        ),
    )

    assert models.drag_model is not None
    assert models.srp_model is not None


def test_environmental_forces_separate_components():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels()

    forces = environmental_forces(
        state=state,
        models=models,
    )

    assert isinstance(
        forces,
        EnvironmentalForces,
    )

    assert forces.gravity[0] < 0.0
    assert forces.j2 != (
        0.0,
        0.0,
        0.0,
    )
    assert forces.drag == (
        0.0,
        0.0,
        0.0,
    )
    assert forces.srp == (
        0.0,
        0.0,
        0.0,
    )
    assert forces.thrust == (
        0.0,
        0.0,
        0.0,
    )


def test_environmental_forces_include_drag_and_srp():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels(
        atmospheric_model=AtmosphericModel(
            reference_density=1e-10,
            reference_altitude=400_000.0,
            scale_height=100_000.0,
        ),
        drag_model=DragModel(
            drag_coefficient=2.2,
            reference_area=10.0,
        ),
        srp_model=SolarRadiationPressureModel(
            reference_area=10.0,
        ),
    )

    forces = environmental_forces(
        state=state,
        models=models,
        sun_direction=(1.0, 0.0, 0.0),
    )

    assert forces.drag[1] < 0.0
    assert forces.srp[0] < 0.0


def test_eclipse_removes_srp():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels(
        srp_model=SolarRadiationPressureModel(
            reference_area=10.0,
        )
    )

    forces = environmental_forces(
        state=state,
        models=models,
        sun_direction=(1.0, 0.0, 0.0),
        eclipse=True,
    )

    assert forces.srp == (
        0.0,
        0.0,
        0.0,
    )


def test_thrust_acceleration_is_included():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels(
        thrust_model=ThrustModel(
            thrust=1_000.0,
            specific_impulse=300.0,
        )
    )

    forces = environmental_forces(
        state=state,
        models=models,
        thrust_direction=(0.0, 1.0, 0.0),
    )

    assert forces.thrust[0] == pytest.approx(0.0)
    assert forces.thrust[1] == pytest.approx(1.0)
    assert forces.thrust[2] == pytest.approx(0.0)


def test_thrust_stops_at_dry_mass():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=500.0,
    )

    models = EnvironmentalModels(
        thrust_model=ThrustModel(
            thrust=1_000.0,
            specific_impulse=300.0,
        )
    )

    forces = environmental_forces(
        state=state,
        models=models,
        thrust_direction=(0.0, 1.0, 0.0),
        dry_mass=500.0,
    )

    assert forces.thrust == (
        0.0,
        0.0,
        0.0,
    )


def test_rk4_environment_step_changes_state():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels()

    result = rk4_step_environment(
        state=state,
        dt=1.0,
        models=models,
    )

    assert result.x != state.x
    assert result.vy != state.vy
    assert result.mass == pytest.approx(
        state.mass
    )


def test_rk4_environment_step_depletes_mass_with_thrust():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels(
        thrust_model=ThrustModel(
            thrust=1_000.0,
            specific_impulse=300.0,
        )
    )

    result = rk4_step_environment(
        state=state,
        dt=10.0,
        models=models,
        thrust_direction=(0.0, 1.0, 0.0),
        dry_mass=100.0,
    )

    expected_mass = (
        1_000.0
        - 1_000.0
        / (
            300.0
            * 9.80665
        )
        * 10.0
    )

    assert result.mass == pytest.approx(
        expected_mass
    )


def test_propagation_zero_duration_returns_same_state():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    result = propagate_environment(
        initial_state=state,
        duration=0.0,
        dt=1.0,
        models=EnvironmentalModels(),
    )

    assert result == state


def test_propagation_uses_partial_final_timestep():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    result = propagate_environment(
        initial_state=state,
        duration=2.5,
        dt=1.0,
        models=EnvironmentalModels(),
    )

    assert result != state


def test_propagation_with_environmental_forces():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    models = EnvironmentalModels(
        atmospheric_model=AtmosphericModel(
            reference_density=1e-10,
            reference_altitude=400_000.0,
            scale_height=100_000.0,
        ),
        drag_model=DragModel(
            drag_coefficient=2.2,
            reference_area=10.0,
        ),
        srp_model=SolarRadiationPressureModel(
            reference_area=10.0,
        ),
    )

    result = propagate_environment(
        initial_state=state,
        duration=10.0,
        dt=1.0,
        models=models,
        sun_direction=(1.0, 0.0, 0.0),
    )

    assert result.mass == pytest.approx(
        state.mass
    )

    assert result != state


def test_environment_propagation_rejects_invalid_duration():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    with pytest.raises(ValueError):
        propagate_environment(
            initial_state=state,
            duration=-1.0,
            dt=1.0,
            models=EnvironmentalModels(),
        )


def test_environment_propagation_rejects_invalid_timestep():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=1_000.0,
    )

    with pytest.raises(ValueError):
        propagate_environment(
            initial_state=state,
            duration=10.0,
            dt=0.0,
            models=EnvironmentalModels(),
        )


def test_dry_mass_is_not_crossed():
    state = State3DEnvironment(
        x=LEO_RADIUS,
        y=0.0,
        z=0.0,
        vx=0.0,
        vy=7_700.0,
        vz=0.0,
        mass=100.0,
    )

    models = EnvironmentalModels(
        thrust_model=ThrustModel(
            thrust=1_000.0,
            specific_impulse=300.0,
        )
    )

    result = propagate_environment(
        initial_state=state,
        duration=1_000.0,
        dt=10.0,
        models=models,
        thrust_direction=(0.0, 1.0, 0.0),
        dry_mass=90.0,
    )

    assert result.mass >= 90.0


def test_environmental_force_total_is_vector_sum():
    forces = EnvironmentalForces(
        gravity=(1.0, 2.0, 3.0),
        j2=(4.0, 5.0, 6.0),
        drag=(7.0, 8.0, 9.0),
        srp=(10.0, 11.0, 12.0),
        thrust=(13.0, 14.0, 15.0),
    )

    assert forces.total == (
        35.0,
        40.0,
        45.0,
    )
