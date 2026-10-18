"""Mission-level feasibility checks for ASTRA Hohmann transfers."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

from astra.physics.constants import EARTH_RADIUS
from astra.physics.transfers import hohmann_transfer


@dataclass(frozen=True)
class MissionRequirements:
    """Mission constraints expressed in SI units."""

    initial_altitude_m: float
    target_altitude_m: float
    max_delta_v_m_s: float
    max_transfer_time_s: float


@dataclass(frozen=True)
class MissionCheck:
    """One independently inspectable mission constraint result."""

    name: str
    passed: bool
    actual_value: float
    limit_value: float
    units: str
    message: str


@dataclass(frozen=True)
class MissionValidationResult:
    """Calculated transfer results and mission feasibility decision."""

    feasible: bool
    total_delta_v_m_s: float
    transfer_time_s: float
    checks: tuple[MissionCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "feasible": self.feasible,
            "total_delta_v_m_s": self.total_delta_v_m_s,
            "transfer_time_s": self.transfer_time_s,
            "checks": [asdict(check) for check in self.checks],
        }


def _positive_finite(name: str, value: float) -> float:
    """Validate a strictly positive finite numeric input."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a numeric value.")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return result


def _altitude(name: str, value: float) -> float:
    """Validate a finite non-negative altitude above Earth's surface."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a numeric value.")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")
    return result


def validate_hohmann_mission(
    requirements: MissionRequirements,
) -> MissionValidationResult:
    """Evaluate a circular-to-circular Earth Hohmann transfer.

    This is an ideal two-body analytical assessment. It does not model
    atmospheric drag, launch injection errors, plane changes, finite burns,
    third-body perturbations, or operational reserve policies.
    """
    if not isinstance(requirements, MissionRequirements):
        raise TypeError("requirements must be a MissionRequirements instance.")

    initial_altitude = _altitude(
        "initial_altitude_m", requirements.initial_altitude_m
    )
    target_altitude = _altitude(
        "target_altitude_m", requirements.target_altitude_m
    )
    delta_v_limit = _positive_finite(
        "max_delta_v_m_s", requirements.max_delta_v_m_s
    )
    time_limit = _positive_finite(
        "max_transfer_time_s", requirements.max_transfer_time_s
    )

    if initial_altitude == target_altitude:
        raise ValueError(
            "Initial and target altitudes must differ for a transfer."
        )

    initial_radius = EARTH_RADIUS + initial_altitude
    target_radius = EARTH_RADIUS + target_altitude
    transfer = hohmann_transfer(initial_radius, target_radius)

    total_delta_v = float(transfer.total_delta_v)
    transfer_time = float(transfer.transfer_time)

    if (
        not math.isfinite(total_delta_v)
        or total_delta_v <= 0
        or not math.isfinite(transfer_time)
        or transfer_time <= 0
    ):
        raise ArithmeticError("Transfer engine returned invalid results.")

    delta_v_passed = total_delta_v <= delta_v_limit
    time_passed = transfer_time <= time_limit

    checks = (
        MissionCheck(
            name="delta_v_budget",
            passed=delta_v_passed,
            actual_value=total_delta_v,
            limit_value=delta_v_limit,
            units="m/s",
            message=(
                "Transfer fits within the delta-v budget."
                if delta_v_passed
                else "Transfer exceeds the available delta-v budget."
            ),
        ),
        MissionCheck(
            name="transfer_time",
            passed=time_passed,
            actual_value=transfer_time,
            limit_value=time_limit,
            units="s",
            message=(
                "Transfer meets the mission time limit."
                if time_passed
                else "Transfer exceeds the mission time limit."
            ),
        ),
    )

    return MissionValidationResult(
        feasible=all(check.passed for check in checks),
        total_delta_v_m_s=total_delta_v,
        transfer_time_s=transfer_time,
        checks=checks,
    )
