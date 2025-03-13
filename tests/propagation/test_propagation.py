import orekit
orekit.initVM()
import pytest
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.orbits import PositionAngleType
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from src.orbits.KeplerianOrbitFactory import KeplerianOrbitFactory
from src.propagation.PropagatorFactory import PropagatorFactory


def test_propagator_creation_and_propagation():
    moon = CelestialBodyFactory.getMoon()
    propagator_factory = PropagatorFactory(True, True, True)
    lunar_orbit_factory = KeplerianOrbitFactory(PositionAngleType.TRUE, moon.getInertiallyOrientedFrame(), moon.getGM())

    initial_epoch = AbsoluteDate(2025, 1, 1, 0, 0, 0.0, TimeScalesFactory.getUTC())
    duration = 3600.
    initial_orbit = lunar_orbit_factory.create_keplerian_orbit(initial_epoch, 10000., 0.,
                                                               0., 0., 0., 0.)

    propagator = propagator_factory.create_propagator(initial_orbit)
    propagator.propagate(initial_epoch, initial_epoch.shiftedBy(duration))
    handler = propagator_factory.add_fixed_step_handler(propagator)

    assert handler.states[-1].getDate().durationFrom(initial_epoch) == pytest.approx(duration, 1e-9)
