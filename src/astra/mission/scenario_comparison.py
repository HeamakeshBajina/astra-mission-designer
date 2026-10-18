"""Compare and rank ideal Earth Hohmann mission scenarios."""
from dataclasses import asdict, dataclass
import math
from typing import Any, Iterable, Literal
from astra.validation.mission_constraints import MissionRequirements, validate_hohmann_mission

RankingObjective = Literal["lowest_delta_v", "shortest_time"]

@dataclass(frozen=True)
class MissionScenario:
    """Candidate transfer; altitudes are kilometres above Earth's surface."""
    name: str
    initial_altitude_km: float
    target_altitude_km: float

@dataclass(frozen=True)
class ScenarioResult:
    name: str
    initial_altitude_km: float
    target_altitude_km: float
    total_delta_v_m_s: float
    transfer_time_s: float
    feasible: bool
    delta_v_passed: bool
    time_passed: bool
    rank: int
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ScenarioComparison:
    objective: RankingObjective
    max_delta_v_m_s: float
    max_transfer_time_s: float
    results: tuple[ScenarioResult, ...]
    def to_dict(self) -> dict[str, Any]:
        return {
            "model": "ideal_two_body_earth_hohmann_transfer",
            "ranking_objective": self.objective,
            "max_delta_v_m_s": self.max_delta_v_m_s,
            "max_transfer_time_s": self.max_transfer_time_s,
            "scenario_count": len(self.results),
            "feasible_count": sum(r.feasible for r in self.results),
            "results": [r.to_dict() for r in self.results],
            "limitations": [
                "Ideal circular-to-circular Earth Hohmann transfer",
                "No drag, injection errors, plane changes, finite burns,",
                "third-body perturbations, or operational reserves",
                "Not flight-qualified software",
            ],
        }

def compare_mission_scenarios(
    scenarios: Iterable[MissionScenario], *, max_delta_v_m_s: float,
    max_transfer_time_s: float,
    objective: RankingObjective = "lowest_delta_v",
) -> ScenarioComparison:
    """Evaluate candidates; feasible scenarios rank before infeasible ones."""
    if objective not in ("lowest_delta_v", "shortest_time"):
        raise ValueError("Invalid ranking objective.")
    def positive_limit(name, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric.")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive.")
        return value
    dv_limit = positive_limit("max_delta_v_m_s", max_delta_v_m_s)
    time_limit = positive_limit("max_transfer_time_s", max_transfer_time_s)
    scenarios = tuple(scenarios)
    if not scenarios:
        raise ValueError("Provide at least one scenario.")
    names, evaluated = set(), []
    for s in scenarios:
        if not isinstance(s, MissionScenario):
            raise TypeError("Each item must be a MissionScenario.")
        if not isinstance(s.name, str) or not s.name.strip():
            raise ValueError("Scenario names cannot be empty.")
        if s.name in names:
            raise ValueError(f"Duplicate scenario name: {s.name}")
        names.add(s.name)
        for field, value in (("initial altitude", s.initial_altitude_km),
                             ("target altitude", s.target_altitude_km)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be numeric.")
            if not math.isfinite(float(value)) or value < 0:
                raise ValueError(f"{field} must be finite and non-negative.")
        if s.initial_altitude_km == s.target_altitude_km:
            raise ValueError(f"{s.name}: initial and target altitudes must differ.")
        result = validate_hohmann_mission(MissionRequirements(
            initial_altitude_m=float(s.initial_altitude_km) * 1000,
            target_altitude_m=float(s.target_altitude_km) * 1000,
            max_delta_v_m_s=dv_limit,
            max_transfer_time_s=time_limit,
        ))
        checks = {c.name: c.passed for c in result.checks}
        evaluated.append(dict(
            name=s.name, initial_altitude_km=float(s.initial_altitude_km),
            target_altitude_km=float(s.target_altitude_km),
            total_delta_v_m_s=result.total_delta_v_m_s,
            transfer_time_s=result.transfer_time_s, feasible=result.feasible,
            delta_v_passed=checks["delta_v_budget"],
            time_passed=checks["transfer_time"],
        ))
    def key(r):
        primary = r["total_delta_v_m_s"] if objective == "lowest_delta_v" else r["transfer_time_s"]
        return (not r["feasible"], primary, r["total_delta_v_m_s"],
                r["transfer_time_s"], r["name"].casefold())
    evaluated.sort(key=key)
    ranked = tuple(ScenarioResult(rank=i, **r) for i, r in enumerate(evaluated, 1))
    return ScenarioComparison(objective, dv_limit, time_limit, ranked)
