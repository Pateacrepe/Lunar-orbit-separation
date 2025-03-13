import orekit
from org.orekit.frames import Frame
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate


class KeplerianOrbitFactory:

    def __init__(self, anomaly_type: PositionAngleType, frame: Frame, central_body_mu: float) -> None:
        self.anomaly_type: PositionAngleType = anomaly_type
        self.frame: Frame = frame
        self.central_body_mu: float = central_body_mu

    def create_keplerian_orbit(self, epoch: AbsoluteDate, semi_major_axis: float, eccentricity: float,
                               inclination: float, argument_of_periapsis: float, raan: float, true_anomaly: float):
        return KeplerianOrbit(semi_major_axis, eccentricity, inclination, argument_of_periapsis, raan, true_anomaly,
                              self.anomaly_type, self.frame, epoch, self.central_body_mu)