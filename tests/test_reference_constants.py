"""Check ASTRA Earth constants against published reference values.

References:
- NASA Earth Fact Sheet:
  https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
- JPL Astrodynamic Parameters (DE440):
  https://ssd.jpl.nasa.gov/astro_par.html

The gravitational parameter tolerance allows for small differences between
adopted Earth reference models. It is not a claim of exact DE440 equivalence.
"""

import pytest

from astra.physics.constants import EARTH_MU, EARTH_RADIUS


JPL_DE440_EARTH_MU_M3_S2 = 398600.435507 * 1_000_000_000
NASA_EARTH_MEAN_RADIUS_M = 6_371_000.0


def test_earth_gravitational_parameter_is_consistent_with_jpl_reference():
    assert EARTH_MU == pytest.approx(
        JPL_DE440_EARTH_MU_M3_S2,
        rel=2e-8,
    )


def test_earth_radius_matches_nasa_volumetric_mean_radius():
    assert EARTH_RADIUS == pytest.approx(
        NASA_EARTH_MEAN_RADIUS_M,
        abs=0.0,
    )
