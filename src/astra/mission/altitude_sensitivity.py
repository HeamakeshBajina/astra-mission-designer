"""Target-altitude sensitivity analysis for ideal Earth Hohmann transfers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from astra.validation.mission_constraints import (
    MissionRequirements,
    validate_hohmann_mission,
)


@dataclass(frozen=True)
class AltitudeSensitivityPoint:
    target_altitude_km: float
    total_delta_v_m_s: float
    transfer_time_s: float
    delta_v_passed: bool
    time_passed: bool
    feasible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AltitudeSensitivityReport:
    initial_altitude_km: float
    minimum_target_altitude_km: float
    maximum_target_altitude_km: float
    sample_count: int
    max_delta_v_m_s: float
    max_transfer_time_s: float
    points: tuple[AltitudeSensitivityPoint, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": "ideal_two_body_earth_hohmann_transfer",
            "initial_altitude_km": self.initial_altitude_km,
            "minimum_target_altitude_km": self.minimum_target_altitude_km,
            "maximum_target_altitude_km": self.maximum_target_altitude_km,
            "sample_count": self.sample_count,
            "max_delta_v_m_s": self.max_delta_v_m_s,
            "max_transfer_time_s": self.max_transfer_time_s,
            "feasible_count": sum(point.feasible for point in self.points),
            "points": [point.to_dict() for point in self.points],
            "limitations": [
                "Ideal circular-to-circular Earth Hohmann transfer",
                "Two-body gravity; no atmospheric drag or injection errors",
                "No plane changes, finite-duration burns, or third-body effects",
                "No operational reserves; not flight-qualified software",
                "Only the specified uniformly spaced target altitudes are sampled",
            ],
        }


def _finite_number(name: str, value: float, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")
    result = float(value)
    if not math.isfinite(result) or result < 0 or (positive and result <= 0):
        qualifier = "finite and positive" if positive else "finite and non-negative"
        raise ValueError(f"{name} must be {qualifier}.")
    return result


def analyze_altitude_sensitivity(
    *,
    initial_altitude_km: float,
    minimum_target_altitude_km: float,
    maximum_target_altitude_km: float,
    sample_count: int = 21,
    max_delta_v_m_s: float,
    max_transfer_time_s: float,
) -> AltitudeSensitivityReport:
    """Sweep target altitude while holding initial altitude and limits fixed."""
    initial = _finite_number("initial_altitude_km", initial_altitude_km)
    minimum = _finite_number(
        "minimum_target_altitude_km", minimum_target_altitude_km
    )
    maximum = _finite_number(
        "maximum_target_altitude_km", maximum_target_altitude_km
    )
    dv_limit = _finite_number(
        "max_delta_v_m_s", max_delta_v_m_s, positive=True
    )
    time_limit = _finite_number(
        "max_transfer_time_s", max_transfer_time_s, positive=True
    )

    if isinstance(sample_count, bool) or not isinstance(sample_count, int):
        raise ValueError("sample_count must be an integer from 2 to 500.")
    if not 2 <= sample_count <= 500:
        raise ValueError("sample_count must be an integer from 2 to 500.")
    if maximum <= minimum:
        raise ValueError("Maximum target altitude must exceed the minimum.")

    targets = [
        minimum + (maximum - minimum) * i / (sample_count - 1)
        for i in range(sample_count)
    ]
    if any(target == initial for target in targets):
        raise ValueError(
            "The sampled target altitudes must not equal the initial altitude."
        )

    points = []
    for target in targets:
        result = validate_hohmann_mission(
            MissionRequirements(
                initial_altitude_m=initial * 1000.0,
                target_altitude_m=target * 1000.0,
                max_delta_v_m_s=dv_limit,
                max_transfer_time_s=time_limit,
            )
        )
        checks = {check.name: check.passed for check in result.checks}
        points.append(
            AltitudeSensitivityPoint(
                target_altitude_km=target,
                total_delta_v_m_s=result.total_delta_v_m_s,
                transfer_time_s=result.transfer_time_s,
                delta_v_passed=checks["delta_v_budget"],
                time_passed=checks["transfer_time"],
                feasible=result.feasible,
            )
        )

    return AltitudeSensitivityReport(
        initial_altitude_km=initial,
        minimum_target_altitude_km=minimum,
        maximum_target_altitude_km=maximum,
        sample_count=sample_count,
        max_delta_v_m_s=dv_limit,
        max_transfer_time_s=time_limit,
        points=tuple(points),
    )
