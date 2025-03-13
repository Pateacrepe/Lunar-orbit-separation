import orekit
import pytest

from src.orbits import OrbitUtils

EARTH_MU = 3.986004e14 #m^3/s^2
EARTH_AVERAGE_RADIUS = 6371. * 1000 # m
ISS_ALTITUDE = 400. * 1000 # m

def test_live_forces_equation():
    iss_semi_major_axis = EARTH_AVERAGE_RADIUS + ISS_ALTITUDE
    assert OrbitUtils.live_forces_equation(EARTH_MU, iss_semi_major_axis, iss_semi_major_axis) == pytest.approx(
        7672.5982, 1e-3)

def test_keplerian_period():
    iss_semi_major_axis = EARTH_AVERAGE_RADIUS + ISS_ALTITUDE
    assert OrbitUtils.keplerian_period_equation(EARTH_MU,iss_semi_major_axis) == pytest.approx(5544.855, 1e-3)

def test_rocket_equation():
    assert OrbitUtils.rocket_equation_duration_from_delta_v(1.,1.,1.,1.) == pytest.approx(1.,1.)