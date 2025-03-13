import numpy as np

from data import OrekitInitializer
from src.orbits import OrbitUtils
from src.orbits.KeplerianOrbitFactory import KeplerianOrbitFactory
from src.propagation.PropagationPostProcessing import PropagationPostProcessing
from src.propagation.PropagatorFactory import PropagatorFactory

from org.orekit.bodies import CelestialBodyFactory
from org.orekit.orbits import PositionAngleType
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.utils import Constants

print("Main script starting\n")

# Orekit is an open-source astrodynamics toolbox offering several useful classes and methods which can be used here
# Originally in Java, the Python wrapper used here needs to initialize an Orekit context
print("Initializing Orekit context...\n")
OrekitInitializer.initialize()

# Celestial bodies physical characteristics and ephemeris are taken from publicized international standards such as JPL and IAU
moon = CelestialBodyFactory.getMoon()
mu_moon = moon.getGM()

# The initial orbit here is an elliptical orbit of 100 x 10 000 km.
# Let's assume at first that the initial state is at periapsis with true anomaly = 0deg
initial_epoch = AbsoluteDate(2025, 1, 23, 0, 0, 0.0, TimeScalesFactory.getUTC())  # Start simulation on my birthday
rp = 100 * 1000 + Constants.MOON_EQUATORIAL_RADIUS
ra = 10000 * 1000 + Constants.MOON_EQUATORIAL_RADIUS
semi_major_axis = (rp + ra) / 2.
eccentricity = (ra - rp) / (ra + rp)
inclination = float(np.deg2rad(90.)) # Let's assume a polar orbit which has the advantage of covering all latitudes and have well-defined nodes
argument_of_periapsis = float(np.deg2rad(0.))
raan = float(np.deg2rad(0.))
true_anomaly = float(np.deg2rad(0.))

print("Initial orbit parameters are:")
print("\t - Initial epoch = ", initial_epoch)
print("\t - Semi major axis (km) = ", semi_major_axis/1000)
print("\t - Eccentricity = ", eccentricity)
print("\t - Inclination (deg) = ", np.rad2deg(inclination))
print("\t - Argument of Periapsis (deg) = ", np.rad2deg(argument_of_periapsis))
print("\t - Right Ascension of Ascending Node (deg) = ", np.rad2deg(raan))
print("\t - True Anomaly (deg) = ", np.rad2deg(true_anomaly))

lunar_orbit_factory = KeplerianOrbitFactory(PositionAngleType.TRUE, moon.getInertiallyOrientedFrame(), mu_moon)

initial_orbit_primary = lunar_orbit_factory.create_keplerian_orbit(initial_epoch, semi_major_axis, eccentricity,
                                                                   inclination,
                                                                   argument_of_periapsis, raan, true_anomaly)

# Compute the Keplerian period
keplerian_period = OrbitUtils.keplerian_period_equation(mu_moon, semi_major_axis)
print("\nInitial keplerian period is: ", keplerian_period, " s")

# Compute initial orbit speed at periapsis since this is where the maximum orbital velocity is reached
velocity_at_periapsis = initial_orbit_primary.getPVCoordinates().getVelocity().getNorm()
print("\nInitial orbit velocity at periapsis = ", velocity_at_periapsis, " m/s")
print("Initial orbit velocity at apoapsis = ", OrbitUtils.live_forces_equation(mu_moon, ra, semi_major_axis), " m/s")

# First assuming linear behaviour around periapsis, create initial guess of period difference needed to achieve 10km separation in relative distance at periapsis.

# The hypothesis here is that a phasing difference in revolution period will be used to create an in-plane separation
# Since a phasing difference is efficiently achieved by a tangential deltaV, as opposed to a normal to the plane or radial separation,
# this will be the preferred method here to achieve the required separation of 10km.

# Note that this is very dependent on the actual separation need. For anti-collision purposes, it might be worth investigating a radial separation instead
period_difference = 10000 / velocity_at_periapsis
target_keplerian_period = keplerian_period + period_difference
target_semi_major_axis = float(np.cbrt(mu_moon * np.square(target_keplerian_period / (2 * np.pi))))
print("\nTarget semi-major axis = ", target_semi_major_axis/1000, " km")

# Using the live forces equation to compute deltaV needed at periapsis to achieve this semi major axis
target_delta_V_at_periapsis = (OrbitUtils.live_forces_equation(mu_moon, rp, target_semi_major_axis) -
                               OrbitUtils.live_forces_equation(mu_moon, rp, semi_major_axis))
print("Target deltaV at periapsis = ", target_delta_V_at_periapsis, " m/s")

# Compare with performing the same maneuver at apoapsis. The target period difference would of course be greater at apogee since orbital speed is at its minimum.
# So the required deltaV would also be greater. Here the interesting metric is the required deltaV to perform the same change in semi-major axis as the periapsis case.
target_delta_V_at_apoapsis = (OrbitUtils.live_forces_equation(mu_moon, ra, target_semi_major_axis) -
                              OrbitUtils.live_forces_equation(mu_moon, ra, semi_major_axis))
print("Target deltaV at apoapsis = ", target_delta_V_at_apoapsis, " m/s")

# So to achieve the same change in semi-major axis, which wouldn't even be enough to create the required phase difference,
# a deltaV performed at apoapsis would be less efficient

# The above problem assumes that the deltaV is instantaneous. However, propulsion systems do not have infinite thrust.
# In order to check if the gravity losses should be considered for a spread-out burn, the burn duration/orbital period is studied.

# Physical characteristics now have to be detailed a bit more. Let's assume the maneuvering spacecraft looks like Hakuto-R lander from Mission 1.
# Total mass is from Nasa website. Isp and thrust are typical values for attitude thrusters chemical propulsion system as I don't have detailed specs.
burn_duration = OrbitUtils.rocket_equation_duration_from_delta_v(1000, 240, 20, target_delta_V_at_periapsis)
print("\nBurn duration = ", burn_duration, " s")
print("Burn duration represents  ", burn_duration/keplerian_period*100, " % of total revolution period")
# Since the burn duration is very small, let's assume impulsive maneuver to simplify the problem.

# The initial orbit of the secondary takes this into account by assuming instantaneous change in semi-major axis at initial epoch
# Eccentricity would also vary, but it is assumed fixed since the point of interest is the periapsis of both objects
initial_orbit_secondary = lunar_orbit_factory.create_keplerian_orbit(initial_epoch, target_semi_major_axis,
                                                                     eccentricity,inclination,
                                                                     argument_of_periapsis, raan, true_anomaly)

# So to reach the same target semi-major axis, a deltaV performed at periapsis is more efficient.
# Given our assumption of period difference, we can check that the relative distance between the two satellites is
# more than 10km after one revolution by actually performing a numerical propagation of the two objects states

# About propagation: since the notion of separation makes more sense from an osculating orbit point of view,
# a numerical propagation will be used to compare the relative distances between the primary and secondary object.

# However, since we are only interested in a single revolution, the force model can be simplified to only take into
# account the major orbital perturbations around the Moon and not the second-order ones
# (such as the SRP where we would need to define an object surface and radiation coefficient)
print("\nPropagating primary and secondary spacecrafts...\n")

add_geopotential = True  # Only 3/3 should cover the majority of geopotential accelerations
add_earth_third_body = True
add_sun_third_body = True
end_epoch = initial_epoch.shiftedBy(float(keplerian_period))

# Note that this is where using an open-source well known library such as Orekit comes in handy.
# There is no need to re-code a heavy-duty propagation, just to set it up with the required parameters.
propagator_factory = PropagatorFactory(add_geopotential, add_earth_third_body, add_sun_third_body)

primary_propagator = propagator_factory.create_propagator(initial_orbit_primary)
primary_handler = propagator_factory.add_fixed_step_handler(primary_propagator)
primary_propagator.propagate(initial_epoch, end_epoch)

secondary_propagator = propagator_factory.create_propagator(initial_orbit_secondary)
secondary_handler = propagator_factory.add_fixed_step_handler(secondary_propagator)
secondary_propagator.propagate(initial_epoch, end_epoch)

print("Propagation duration = ", end_epoch.durationFrom(initial_epoch), " s")

# Once propagation is done for both objects, this is where the outputs can be created.
# Here there are only a couple of plots generated but a lot more metrics could be observed from the states ephemeris
print("Post-processing...")
post_processor = PropagationPostProcessing(initial_epoch)
post_processor.post_process(primary_handler.states, secondary_handler.states)

# Achieved relative distance after one revolution is indeed 10 km!

print("\nAll done!\n")
