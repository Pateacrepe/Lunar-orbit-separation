import orekit
import numpy as np
from org.orekit.utils import Constants


def live_forces_equation(mu: float, radius: float, semi_major_axis: float):
    return np.sqrt(mu* (2/radius - 1/semi_major_axis))

def keplerian_period_equation(mu: float, semi_major_axis: float):
    return 2 * np.pi * np.sqrt(np.power(semi_major_axis,3)/mu)

def rocket_equation_duration_from_delta_v(initial_mass: float, isp: float, thrust:float, delta_v:float):
    moon_standard_acceleration = Constants.JPL_SSD_MOON_GM / Constants.MOON_EQUATORIAL_RADIUS**2
    exhaust_velocity = moon_standard_acceleration * isp
    return initial_mass*exhaust_velocity/thrust*(1-np.exp(-delta_v/exhaust_velocity))