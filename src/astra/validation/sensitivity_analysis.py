"""One-at-a-time sensitivity analysis for ideal orbital mechanics."""

from __future__ import annotations

from dataclasses import dataclass
import math

from astra.physics.constants import EARTH_MU, EARTH_RADIUS


@dataclass(frozen=True)
class SensitivityResult:
    """Metric response to a single perturbed input."""

    parameter: str
    perturbation_percent: float
    metric: str
    baseline_value: float
    perturbed_value: float
    absolute_change: float
    relative_change_percent: float


def _validate_positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive number.")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a finite positive number.")
    return result


def _calculate_metrics(
    initial_radius_m: float,
    final_radius_m: float,
    mu_m3_s2: float,
) -> dict[str, float]:
    """Calculate metrics from analytical equations, independent of ASTRA APIs."""
    initial_radius_m = _validate_positive_finite(
        initial_radius_m, "initial_radius_m"
    )
    final_radius_m = _validate_positive_finite(
        final_radius_m, "final_radius_m"
    )
    mu_m3_s2 = _validate_positive_finite(mu_m3_s2, "mu_m3_s2")

    if math.isclose(initial_radius_m, final_radius_m):
        raise ValueError("Initial and final radii must differ.")

    circular_speed = math.sqrt(mu_m3_s2 / initial_radius_m)
    orbital_period = 2.0 * math.pi * math.sqrt(
        initial_radius_m**3 / mu_m3_s2
    )

    transfer_axis = (initial_radius_m + final_radius_m) / 2.0
    initial_circular_speed = math.sqrt(mu_m3_s2 / initial_radius_m)
    final_circular_speed = math.sqrt(mu_m3_s2 / final_radius_m)

    transfer_speed_at_initial = math.sqrt(
        mu_m3_s2 * (2.0 / initial_radius_m - 1.0 / transfer_axis)
    )
    transfer_speed_at_final = math.sqrt(
        mu_m3_s2 * (2.0 / final_radius_m - 1.0 / transfer_axis)
    )

    first_burn = abs(transfer_speed_at_initial - initial_circular_speed)
    second_burn = abs(final_circular_speed - transfer_speed_at_final)
    total_delta_v = first_burn + second_burn
    transfer_time = math.pi * math.sqrt(transfer_axis**3 / mu_m3_s2)

    return {
        "circular_speed_m_s": circular_speed,
        "orbital_period_s": orbital_period,
        "hohmann_total_delta_v_m_s": total_delta_v,
        "hohmann_transfer_time_s": transfer_time,
    }


def run_sensitivity_analysis(
    *,
    initial_altitude_m: float = 400_000.0,
    final_altitude_m: float = 800_000.0,
    earth_mu_m3_s2: float = EARTH_MU,
    perturbations_percent: tuple[float, ...] = (-5.0, -1.0, 1.0, 5.0),
) -> tuple[SensitivityResult, ...]:
    """Perturb each input independently and quantify metric responses.

    Radius parameters mean the initial orbital radius, final orbital radius,
    or gravitational parameter. Altitudes are converted to geocentric radii
    using the configured Earth radius.

    This is a deterministic analytical study, not a physical uncertainty model.
    """
    initial_altitude_m = _validate_positive_finite(
        initial_altitude_m, "initial_altitude_m"
    )
    final_altitude_m = _validate_positive_finite(
        final_altitude_m, "final_altitude_m"
    )
    earth_mu_m3_s2 = _validate_positive_finite(
        earth_mu_m3_s2, "earth_mu_m3_s2"
    )

    initial_radius = EARTH_RADIUS + initial_altitude_m
    final_radius = EARTH_RADIUS + final_altitude_m

    if math.isclose(initial_radius, final_radius):
        raise ValueError("Initial and final orbital radii must differ.")
    if not perturbations_percent:
        raise ValueError("At least one perturbation is required.")

    perturbations = tuple(perturbations_percent)
    for perturbation in perturbations:
        if isinstance(perturbation, bool) or not isinstance(
            perturbation, (int, float)
        ):
            raise ValueError("Perturbations must be finite numbers.")
        if not math.isfinite(perturbation) or perturbation <= -100.0:
            raise ValueError(
                "Perturbations must be finite and greater than -100%."
            )

    baseline = _calculate_metrics(
        initial_radius, final_radius, earth_mu_m3_s2
    )
    results: list[SensitivityResult] = []

    for parameter in ("initial_radius", "final_radius", "earth_mu"):
        for perturbation in perturbations:
            factor = 1.0 + perturbation / 100.0
            perturbed_initial = initial_radius
            perturbed_final = final_radius
            perturbed_mu = earth_mu_m3_s2

            if parameter == "initial_radius":
                perturbed_initial *= factor
            elif parameter == "final_radius":
                perturbed_final *= factor
            else:
                perturbed_mu *= factor

            if math.isclose(perturbed_initial, perturbed_final):
                raise ValueError(
                    "A perturbation makes the initial and final radii equal."
                )

            changed = _calculate_metrics(
                perturbed_initial, perturbed_final, perturbed_mu
            )

            for metric, baseline_value in baseline.items():
                perturbed_value = changed[metric]
                absolute_change = perturbed_value - baseline_value
                relative_change_percent = (
                    absolute_change / baseline_value * 100.0
                )

                results.append(
                    SensitivityResult(
                        parameter=parameter,
                        perturbation_percent=float(perturbation),
                        metric=metric,
                        baseline_value=baseline_value,
                        perturbed_value=perturbed_value,
                        absolute_change=absolute_change,
                        relative_change_percent=relative_change_percent,
                    )
                )

    return tuple(results)
