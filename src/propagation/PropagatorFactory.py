from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel, ThirdBodyAttraction
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.orbits import KeplerianOrbit
from org.orekit.propagation import SpacecraftState, Propagator
from org.orekit.propagation.numerical import NumericalPropagator

from src.propagation.EphemerisStepHandler import EphemerisStepHandler


class PropagatorFactory:
    DEFAULT_MIN_STEP = 1.
    DEFAULT_MAX_STEP = 1000.
    DEFAULT_ABSOLUTE_TOLERANCE = 1e-8
    DEFAULT_RELATIVE_TOLERANCE = 1e-10

    DEFAULT_GEOPOTENTIAL_DEGREE = 3
    DEFAULT_GEOPOTENTIAL_ORDER = 3

    DEFAULT_HANDLER_STEP = 60.

    def __init__(self, is_geopotential_added: bool, is_earth_added: bool, is_sun_added: bool) -> None:
        self.is_geopotential_added: bool = is_geopotential_added
        self.is_earth_added: bool = is_earth_added
        self.is_sun_added: bool = is_sun_added

    def create_propagator(self, initial_orbit: KeplerianOrbit):
        numerical_propagator = NumericalPropagator(self.create_integrator())
        numerical_propagator.setInitialState(SpacecraftState(initial_orbit))

        self.is_geopotential_added and numerical_propagator.addForceModel(self.create_lunar_geopotential())
        self.is_earth_added and numerical_propagator.addForceModel(self.create_earth_third_body_attraction())
        self.is_sun_added and numerical_propagator.addForceModel(self.create_sun_third_body_attraction())
        return numerical_propagator

    def create_integrator(self, min_step=DEFAULT_MIN_STEP, max_step=DEFAULT_MAX_STEP,
                          abs_tolerance=DEFAULT_ABSOLUTE_TOLERANCE, relative_tolerance=DEFAULT_RELATIVE_TOLERANCE):
        return DormandPrince853Integrator(min_step, max_step, abs_tolerance, relative_tolerance)

    def create_lunar_geopotential(self, degree=DEFAULT_GEOPOTENTIAL_DEGREE, order=DEFAULT_GEOPOTENTIAL_ORDER):
        gravity_provider = GravityFieldFactory.getNormalizedProvider(degree, order)
        return HolmesFeatherstoneAttractionModel(CelestialBodyFactory.getMoon().getInertiallyOrientedFrame(),
                                                 gravity_provider)

    def create_sun_third_body_attraction(self):
        return ThirdBodyAttraction(CelestialBodyFactory.getSun())

    def create_earth_third_body_attraction(self):
        return ThirdBodyAttraction(CelestialBodyFactory.getEarth())

    def add_fixed_step_handler(self, propagator: NumericalPropagator):
        handler = EphemerisStepHandler()
        Propagator.cast_(propagator).setStepHandler(self.DEFAULT_HANDLER_STEP, handler)
        return handler
