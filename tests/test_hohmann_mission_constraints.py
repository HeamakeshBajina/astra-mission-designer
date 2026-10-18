import math

import pytest

from astra.validation.mission_constraints import (
    MissionRequirements,
    validate_hohmann_mission,
)


def requirements(**overrides):
    values = {
        "initial_altitude_m": 400_000.0,
        "target_altitude_m": 800_000.0,
        "max_delta_v_m_s": 2_000.0,
        "max_transfer_time_s": 20_000.0,
    }
    values.update(overrides)
    return MissionRequirements(**values)


def test_feasible_mission_passes_all_checks():
    result = validate_hohmann_mission(requirements())
    assert result.feasible
    assert len(result.checks) == 2
    assert all(check.passed for check in result.checks)
    assert result.total_delta_v_m_s > 0
    assert result.transfer_time_s > 0


def test_delta_v_budget_failure_marks_mission_infeasible():
    result = validate_hohmann_mission(requirements(max_delta_v_m_s=1.0))
    assert not result.feasible
    check = next(c for c in result.checks if c.name == "delta_v_budget")
    assert not check.passed
    assert check.actual_value > check.limit_value


def test_transfer_time_failure_marks_mission_infeasible():
    result = validate_hohmann_mission(requirements(max_transfer_time_s=1.0))
    assert not result.feasible
    check = next(c for c in result.checks if c.name == "transfer_time")
    assert not check.passed
    assert check.actual_value > check.limit_value


def test_each_constraint_is_evaluated_independently():
    result = validate_hohmann_mission(requirements(max_delta_v_m_s=1.0))
    assert [c.passed for c in result.checks] == [False, True]

    result = validate_hohmann_mission(requirements(max_transfer_time_s=1.0))
    assert [c.passed for c in result.checks] == [True, False]


def test_limits_are_inclusive_at_calculated_values():
    baseline = validate_hohmann_mission(requirements())
    exact = MissionRequirements(
        initial_altitude_m=400_000.0,
        target_altitude_m=800_000.0,
        max_delta_v_m_s=baseline.total_delta_v_m_s,
        max_transfer_time_s=baseline.transfer_time_s,
    )
    assert validate_hohmann_mission(exact).feasible


@pytest.mark.parametrize(
    "field,value",
    [
        ("initial_altitude_m", -1.0),
        ("initial_altitude_m", math.inf),
        ("target_altitude_m", math.nan),
        ("max_delta_v_m_s", 0.0),
        ("max_delta_v_m_s", -1.0),
        ("max_transfer_time_s", 0.0),
        ("max_transfer_time_s", math.inf),
    ],
)
def test_invalid_inputs_are_rejected(field, value):
    with pytest.raises(ValueError):
        validate_hohmann_mission(requirements(**{field: value}))


@pytest.mark.parametrize(
    "field",
    [
        "initial_altitude_m",
        "target_altitude_m",
        "max_delta_v_m_s",
        "max_transfer_time_s",
    ],
)
def test_boolean_inputs_are_rejected(field):
    with pytest.raises(ValueError):
        validate_hohmann_mission(requirements(**{field: True}))


def test_equal_altitudes_are_rejected():
    with pytest.raises(ValueError, match="must differ"):
        validate_hohmann_mission(requirements(target_altitude_m=400_000.0))


def test_non_requirements_argument_is_rejected():
    with pytest.raises(TypeError):
        validate_hohmann_mission(None)


def test_result_serialization_has_explicit_checks():
    payload = validate_hohmann_mission(requirements()).to_dict()
    assert payload["feasible"] is True
    assert len(payload["checks"]) == 2
    assert payload["checks"][0]["name"] == "delta_v_budget"
    assert payload["checks"][1]["name"] == "transfer_time"
    assert payload["checks"][0]["units"] == "m/s"
    assert payload["checks"][1]["units"] == "s"


def test_results_are_deterministic():
    assert (
        validate_hohmann_mission(requirements()).to_dict()
        == validate_hohmann_mission(requirements()).to_dict()
    )


def test_failed_check_includes_explanation():
    result = validate_hohmann_mission(requirements(max_delta_v_m_s=1.0))
    check = result.checks[0]
    assert not check.passed
    assert check.message
    assert check.actual_value > check.limit_value
