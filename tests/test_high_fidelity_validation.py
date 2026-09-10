"""Tests for ASTRA high-fidelity validation and reference scenarios."""

import math

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS
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
from astra.validation.reference_scenarios import (
    all_reference_scenarios,
    escape_velocity_case,
    finite_thrust_case,
    hohmann_earth_case,
    leo_circular_orbit,
    rocket_equation_case,
)
from astra.validation.high_fidelity_validation import (
    ValidationReport,
    build_validation_report,
    compare_value,
    specific_orbital_energy,
    validate_circular_orbit,
    validate_circular_orbit_energy,
    validate_convergence,
    validate_reference_scenario,
    validate_trajectory,
)


def test_all_reference_scenarios_exist():
    scenarios = all_reference_scenarios()

    assert len(scenarios) == 5
    assert len(
        {scenario.name for scenario in scenarios}
    ) == 5


def test_leo_reference_scenario():
    scenario = leo_circular_orbit()

    assert scenario.expected_values["altitude"] == 400_000.0
    assert scenario.expected_values["radius"] == pytest.approx(
        EARTH_RADIUS + 400_000.0
    )


def test_leo_reference_velocity_matches_astira():
    scenario = leo_circular_orbit()

    expected = circular_orbital_velocity(
        scenario.expected_values["radius"]
    )

    assert scenario.expected_values["velocity"] == pytest.approx(
        expected
    )


def test_leo_reference_period_is_physical():
    scenario = leo_circular_orbit()

    period = scenario.expected_values["period"]

    assert 5_000.0 < period < 6_000.0


def test_escape_velocity_reference():
    scenario = escape_velocity_case()

    radius = scenario.expected_values["radius"]

    expected_velocity = escape_velocity(radius)

    assert scenario.expected_values["velocity"] == pytest.approx(
        expected_velocity
    )


def test_escape_velocity_has_zero_specific_energy():
    scenario = escape_velocity_case()

    assert abs(
        scenario.expected_values["specific_energy"]
    ) < 1e-6


def test_hohmann_reference_values_are_positive():
    scenario = hohmann_earth_case()

    assert scenario.expected_values["delta_v_1"] > 0
    assert scenario.expected_values["delta_v_2"] > 0
    assert scenario.expected_values["total_delta_v"] > 0


def test_hohmann_total_delta_v_is_sum():
    scenario = hohmann_earth_case()

    values = scenario.expected_values

    assert values["total_delta_v"] == pytest.approx(
        values["delta_v_1"]
        + values["delta_v_2"]
    )


def test_hohmann_reference_is_between_expected_range():
    scenario = hohmann_earth_case()

    total_delta_v = scenario.expected_values[
        "total_delta_v"
    ]

    assert 150.0 < total_delta_v < 1_000.0


def test_rocket_equation_reference():
    scenario = rocket_equation_case()

    values = scenario.expected_values

    calculated = delta_v_from_mass_ratio(
        initial_mass=values["initial_mass"],
        final_mass=values["final_mass"],
        specific_impulse=values["specific_impulse"],
    )

    assert calculated == pytest.approx(
        values["delta_v"]
    )


def test_rocket_equation_recovers_final_mass():
    scenario = rocket_equation_case()

    values = scenario.expected_values

    recovered = final_mass_for_delta_v(
        initial_mass=values["initial_mass"],
        delta_v=values["delta_v"],
        specific_impulse=values["specific_impulse"],
    )

    assert recovered == pytest.approx(
        values["final_mass"]
    )


def test_finite_thrust_reference():
    scenario = finite_thrust_case()

    values = scenario.expected_values

    model = ThrustModel(
        thrust=values["thrust"],
        specific_impulse=300.0,
    )

    assert model.mass_flow_rate == pytest.approx(
        values["mass_flow_rate"]
    )


def test_reference_comparison_passes():
    result = validate_reference_scenario(
        name="simple",
        expected_values={"value": 10.0},
        actual_values={"value": 10.0000001},
        tolerances={"value": 1e-6},
    )

    assert result.passed
    assert len(result.metrics) == 1


def test_reference_comparison_fails():
    result = validate_reference_scenario(
        name="simple",
        expected_values={"value": 10.0},
        actual_values={"value": 11.0},
        tolerances={"value": 1e-6},
    )

    assert not result.passed
    assert len(result.failed_metrics) == 1


def test_compare_value_reports_absolute_error():
    metric = compare_value(
        name="velocity",
        expected=100.0,
        actual=101.0,
        tolerance=2.0,
    )

    assert metric.absolute_error == pytest.approx(1.0)
    assert metric.relative_error == pytest.approx(0.01)
    assert metric.passed


def test_compare_value_rejects_negative_tolerance():
    with pytest.raises(ValueError):
        compare_value(
            name="value",
            expected=1.0,
            actual=1.0,
            tolerance=-1.0,
        )


def test_compare_value_rejects_nonfinite_expected():
    with pytest.raises(ValueError):
        compare_value(
            name="value",
            expected=math.inf,
            actual=1.0,
            tolerance=1.0,
        )


def test_compare_value_rejects_nonfinite_actual():
    with pytest.raises(ValueError):
        compare_value(
            name="value",
            expected=1.0,
            actual=math.nan,
            tolerance=1.0,
        )


def test_circular_orbit_validation():
    radius = EARTH_RADIUS + 400_000.0
    velocity = circular_orbital_velocity(radius)

    result = validate_circular_orbit(
        radius=radius,
        actual_velocity=velocity,
    )

    assert result.passed
    assert result.maximum_absolute_error == 0.0


def test_circular_orbit_validation_detects_error():
    radius = EARTH_RADIUS + 400_000.0
    velocity = circular_orbital_velocity(radius)

    result = validate_circular_orbit(
        radius=radius,
        actual_velocity=velocity + 10.0,
        tolerance=1e-6,
    )

    assert not result.passed


def test_circular_orbit_rejects_invalid_radius():
    with pytest.raises(ValueError):
        validate_circular_orbit(
            radius=0.0,
            actual_velocity=1.0,
        )


def test_specific_orbital_energy_for_circular_orbit():
    radius = EARTH_RADIUS + 400_000.0
    velocity = circular_orbital_velocity(radius)

    expected = -EARTH_MU / (2.0 * radius)

    assert specific_orbital_energy(
        radius=radius,
        velocity=velocity,
    ) == pytest.approx(expected)


def test_circular_orbit_energy_validation():
    radius = EARTH_RADIUS + 400_000.0
    velocity = circular_orbital_velocity(radius)

    result = validate_circular_orbit_energy(
        radius=radius,
        velocity=velocity,
    )

    assert result.passed


def test_circular_orbit_energy_detects_error():
    radius = EARTH_RADIUS + 400_000.0
    velocity = circular_orbital_velocity(radius)

    result = validate_circular_orbit_energy(
        radius=radius,
        velocity=velocity + 100.0,
        tolerance=1e-6,
    )

    assert not result.passed


def test_trajectory_validation_passes():
    trajectory = (
        (1.0, 0.0, 0.0),
        (2.0, 0.0, 0.0),
        (3.0, 0.0, 0.0),
    )

    result = validate_trajectory(
        expected_positions=trajectory,
        actual_positions=trajectory,
        position_tolerance=1e-9,
    )

    assert result.passed
    assert len(result.metrics) == 3


def test_trajectory_validation_detects_position_error():
    expected = (
        (1.0, 0.0, 0.0),
    )

    actual = (
        (2.0, 0.0, 0.0),
    )

    result = validate_trajectory(
        expected_positions=expected,
        actual_positions=actual,
        position_tolerance=0.1,
    )

    assert not result.passed


def test_trajectory_length_mismatch_rejected():
    with pytest.raises(ValueError):
        validate_trajectory(
            expected_positions=((1.0, 0.0, 0.0),),
            actual_positions=(),
            position_tolerance=1.0,
        )


def test_trajectory_validation_requires_3d_vectors():
    with pytest.raises(ValueError):
        validate_trajectory(
            expected_positions=((1.0, 0.0),),
            actual_positions=((1.0, 0.0),),
            position_tolerance=1.0,
        )


def test_convergence_validation_passes():
    result = validate_convergence(
        coarse_error=0.01,
        medium_error=0.000625,
        fine_error=0.0000390625,
        tolerance=0.001,
        expected_order=4.0,
    )

    assert result.passed


def test_convergence_requires_positive_order():
    with pytest.raises(ValueError):
        validate_convergence(
            coarse_error=1.0,
            medium_error=0.5,
            fine_error=0.25,
            tolerance=1.0,
            expected_order=0.0,
        )


def test_convergence_rejects_negative_errors():
    with pytest.raises(ValueError):
        validate_convergence(
            coarse_error=-1.0,
            medium_error=0.5,
            fine_error=0.25,
            tolerance=1.0,
        )


def test_convergence_detects_nonconverging_solution():
    result = validate_convergence(
        coarse_error=0.1,
        medium_error=0.2,
        fine_error=0.3,
        tolerance=0.001,
    )

    assert not result.passed


def test_validation_report_passes_when_all_scenarios_pass():
    first = validate_circular_orbit(
        radius=EARTH_RADIUS + 400_000.0,
        actual_velocity=circular_orbital_velocity(
            EARTH_RADIUS + 400_000.0
        ),
    )

    second = validate_circular_orbit_energy(
        radius=EARTH_RADIUS + 400_000.0,
        velocity=circular_orbital_velocity(
            EARTH_RADIUS + 400_000.0
        ),
    )

    report = build_validation_report(
        scenarios=(first, second)
    )

    assert isinstance(report, ValidationReport)
    assert report.passed
    assert report.scenario_count == 2
    assert report.passed_scenarios == 2
    assert report.failed_scenarios == 0


def test_validation_report_detects_failure():
    passing = validate_circular_orbit(
        radius=EARTH_RADIUS + 400_000.0,
        actual_velocity=circular_orbital_velocity(
            EARTH_RADIUS + 400_000.0
        ),
    )

    failing = validate_circular_orbit(
        radius=EARTH_RADIUS + 400_000.0,
        actual_velocity=1.0,
        tolerance=1e-9,
    )

    report = build_validation_report(
        scenarios=(passing, failing)
    )

    assert not report.passed
    assert report.scenario_count == 2
    assert report.passed_scenarios == 1
    assert report.failed_scenarios == 1


def test_empty_validation_report_is_successful():
    report = build_validation_report(
        scenarios=()
    )

    assert report.passed
    assert report.scenario_count == 0
    assert report.metric_count == 0


def test_orbital_period_reference_is_reasonable():
    radius = EARTH_RADIUS + 400_000.0

    period = orbital_period(radius)

    assert 5_000.0 < period < 6_000.0


def test_escape_velocity_is_sqrt_two_times_circular_velocity():
    radius = EARTH_RADIUS + 400_000.0

    circular = circular_orbital_velocity(radius)
    escape = escape_velocity(radius)

    assert escape == pytest.approx(
        circular * math.sqrt(2.0)
    )


def test_finite_thrust_reference_mass_flow():
    model = ThrustModel(
        thrust=1_000.0,
        specific_impulse=300.0,
    )

    expected = (
        1_000.0
        / (300.0 * 9.80665)
    )

    assert model.mass_flow_rate == pytest.approx(
        expected
    )


def test_reference_scenario_tolerances_exist():
    for scenario in all_reference_scenarios():
        assert set(
            scenario.expected_values
        ) == set(
            scenario.tolerances
        )


def test_reference_scenario_values_are_finite():
    for scenario in all_reference_scenarios():
        for value in scenario.expected_values.values():
            assert math.isfinite(value)


def test_reference_scenario_tolerances_are_nonnegative():
    for scenario in all_reference_scenarios():
        for tolerance in scenario.tolerances.values():
            assert tolerance >= 0.0
