"""Externally sourced, reproducible analytical orbital benchmarks.

Reference model:
- Earth GM: JPL DE440, 398600.435507 km^3/s^2.
- Earth radius: NASA volumetric mean radius, 6371.000 km.
- Model: ideal two-body dynamics; circular orbits and impulsive Hohmann transfer.

The output values below are derived from these published constants and the
standard analytical equations. They are not claimed to be directly published
NASA/JPL trajectory results.
"""

from __future__ import annotations

from astra.physics.orbital import (
    circular_orbital_velocity,
    escape_velocity,
    orbital_period,
)
from astra.physics.transfers import hohmann_transfer
from astra.validation.benchmark_report import (
    BenchmarkReference,
    build_benchmark_report,
)
from astra.validation.mission_report import MissionValidationReport


JPL_DE440_GM_URL = "https://ssd.jpl.nasa.gov/astro_par.html"
NASA_EARTH_FACTSHEET_URL = (
    "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"
)

REFERENCE_EARTH_MU_M3_S2 = 398600.435507e9
REFERENCE_EARTH_RADIUS_M = 6_371_000.0

ALTITUDE_400_KM_M = 400_000.0
ALTITUDE_800_KM_M = 800_000.0

RADIUS_400_KM_M = REFERENCE_EARTH_RADIUS_M + ALTITUDE_400_KM_M
RADIUS_800_KM_M = REFERENCE_EARTH_RADIUS_M + ALTITUDE_800_KM_M

# These values are independently derived using the documented reference
# constants and analytical equations, then frozen as regression targets.
ORBITAL_BENCHMARKS: tuple[BenchmarkReference, ...] = (
    BenchmarkReference(
        benchmark_id="leo400.circular_speed",
        name="Circular orbital speed at 400 km altitude",
        reference_value=7672.598587818517,
        unit="m/s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="leo400.escape_speed",
        name="Escape speed at 400 km altitude",
        reference_value=10850.692981537604,
        unit="m/s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="leo400.orbital_period",
        name="Circular orbital period at 400 km altitude",
        reference_value=5544.8551397511565,
        unit="s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=NASA_EARTH_FACTSHEET_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="hohmann400_800.first_burn",
        name="Hohmann transfer first burn, 400 km to 800 km",
        reference_value=109.28621273260796,
        unit="m/s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="hohmann400_800.second_burn",
        name="Hohmann transfer second burn, 400 km to 800 km",
        reference_value=107.72909396489285,
        unit="m/s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="hohmann400_800.total_delta_v",
        name="Hohmann transfer total delta-v, 400 km to 800 km",
        reference_value=217.01530669750082,
        unit="m/s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.02,
        relative_tolerance=2e-6,
    ),
    BenchmarkReference(
        benchmark_id="hohmann400_800.transfer_time",
        name="Hohmann transfer time, 400 km to 800 km",
        reference_value=2896.167077658511,
        unit="s",
        source_name="JPL DE440 Earth GM + NASA Earth radius; derived",
        source_url=JPL_DE440_GM_URL,
        absolute_tolerance=0.05,
        relative_tolerance=2e-6,
    ),
)


def calculate_core_orbital_values() -> dict[str, float]:
    """Run ASTRA's production calculations for the frozen benchmark cases."""
    orbit_speed = circular_orbital_velocity(RADIUS_400_KM_M)
    orbit_escape_speed = escape_velocity(RADIUS_400_KM_M)
    orbit_period = orbital_period(RADIUS_400_KM_M)

    transfer = hohmann_transfer(RADIUS_400_KM_M, RADIUS_800_KM_M)

    return {
        "leo400.circular_speed": orbit_speed,
        "leo400.escape_speed": orbit_escape_speed,
        "leo400.orbital_period": orbit_period,
        "hohmann400_800.first_burn": transfer.first_burn_delta_v,
        "hohmann400_800.second_burn": transfer.second_burn_delta_v,
        "hohmann400_800.total_delta_v": transfer.total_delta_v,
        "hohmann400_800.transfer_time": transfer.transfer_time,
    }


def build_core_orbital_benchmark_report(
    *,
    mission_name: str = "ASTRA Core Orbital Benchmarks",
    created_at: str,
    software_version: str,
) -> MissionValidationReport:
    """Compare ASTRA results with the fixed external-reference benchmark set."""
    actual_values = calculate_core_orbital_values()

    return build_benchmark_report(
        mission_name=mission_name,
        created_at=created_at,
        software_version=software_version,
        benchmarks=ORBITAL_BENCHMARKS,
        actual_values=actual_values,
        inputs={
            "reference_earth_mu_m3_s2": REFERENCE_EARTH_MU_M3_S2,
            "reference_earth_radius_m": REFERENCE_EARTH_RADIUS_M,
            "initial_altitude_m": ALTITUDE_400_KM_M,
            "final_altitude_m": ALTITUDE_800_KM_M,
            "model": "ideal two-body dynamics",
            "transfer_model": "impulsive Hohmann transfer",
        },
        assumptions=(
            "Reference Earth GM is taken from JPL DE440.",
            "Reference Earth radius is NASA's volumetric mean radius.",
            "Benchmark outputs are independently derived from the cited constants.",
            "The model assumes ideal two-body dynamics and impulsive maneuvers.",
            "Tolerances are numerical regression thresholds, not mission uncertainty bounds.",
            "ASTRA does not independently authenticate the cited source.",
            "Passing checks do not demonstrate flight readiness or spacecraft safety.",
        ),
        notes=(
            "The reference values are derived analytical targets, not direct "
            "measurements or published mission trajectory results.",
            "Atmospheric drag, oblateness, third-body perturbations, and finite "
            "burn duration are not included in these benchmark cases.",
        ),
    )
