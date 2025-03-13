import numpy as np
import matplotlib.pyplot as plt
from org.orekit.propagation import SpacecraftState
from typing import List
from org.orekit.utils import Constants

from org.orekit.time import AbsoluteDate

class PropagationPostProcessing:
    DATE_TOLERANCE = 1e-9
    HOUR = 3600.
    KILOMETER_TO_METER = 1000.

    def __init__(self, initial_epoch: AbsoluteDate):
        self.initial_epoch = initial_epoch

    def post_process(self, states_primary: List[SpacecraftState], states_secondary: List[SpacecraftState]):
        self.check_time_steps(states_primary, states_secondary)

        print("\nDisplaying relative distance vs time plot...")
        self.plot_relative_distance_vs_time(states_primary, states_secondary)

        print("\nDisplaying 3D trajectories plot...")
        self.plot_3d_trajectories_with_moon(states_primary, states_secondary)

    def extract_positions(self, states_primary: List[SpacecraftState]):
        x_values = [(state.getPosition().getX() / self.KILOMETER_TO_METER) for state in states_primary]
        y_values = [(state.getPosition().getY() / self.KILOMETER_TO_METER) for state in states_primary]
        z_values = [(state.getPosition().getZ() / self.KILOMETER_TO_METER) for state in states_primary]
        return x_values, y_values, z_values

    def plot_relative_distance_vs_time(self, states_primary, states_secondary):
        states_difference = [(state1.getDate(), self.compute_relative_distance(state1, state2)) for state1, state2 in
                             zip(states_primary, states_secondary) if self.check_time_step(state1, state2)]

        elapsed_time = [(date.durationFrom(self.initial_epoch) / self.HOUR) for date, _ in states_difference]
        relative_distances = [(relative_distance / self.KILOMETER_TO_METER) for _, relative_distance in
                              states_difference]

        print("Final achieved relative distance = ", relative_distances[-1], "km")

        plt.plot(elapsed_time, relative_distances, label="Relative distance")
        plt.xlabel("Elapsed Time (hours)")
        plt.ylabel("Relative Distance (km)")
        plt.title("Relative Distance vs Time")
        plt.grid(True)
        plt.legend()
        plt.show()

    def compute_relative_distance(self, state1: SpacecraftState, state2: SpacecraftState):
        return state1.getPosition().subtract(state2.getPosition()).getNorm()

    def check_time_steps(self, states_primary: List[SpacecraftState], states_secondary: List[SpacecraftState]) -> None:
        if len(states_primary) != len(states_secondary):
            raise ValueError(
                "Primary and secondary object ephemeris size mismatch: {} vs {}.".format(len(states_primary),
                                                                                         len(states_secondary)))

        for index, (state1, state2) in enumerate(zip(states_primary, states_secondary)):
            if not self.check_time_step(state1, state2):
                raise ValueError("Time step mismatch at index {}: {} vs {}.".format(
                    index, state1.getDate(), state2.getDate()
                ))

    def check_time_step(self, state1: SpacecraftState, state2: SpacecraftState):
        return abs(state1.getDate().durationFrom(state2.getDate())) < self.DATE_TOLERANCE

    def plot_3d_trajectories_with_moon(self, states_primary, states_secondary):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        x_primary, y_primary, z_primary = self.extract_positions(states_primary)
        ax.plot(x_primary, y_primary, z_primary, label="Primary Trajectory", color='b')
        x_secondary, y_secondary, z_secondary = self.extract_positions(states_secondary)
        ax.plot(x_secondary, y_secondary, z_secondary, label="Secondary Trajectory", color='r')
        x_moon, y_moon, z_moon = self.create_moon_sphere()
        ax.plot_surface(x_moon, y_moon, z_moon, color='gray', alpha=0.6, rstride=2, cstride=2)
        ax.set_xlabel("X (km)")
        ax.set_ylabel("Y (km)")
        ax.set_zlabel("Z (km)")
        ax.set_title("Lunar separation at perigee between primary and secondary object")
        ax.legend()
        max_range = np.ptp([x_primary, y_primary, z_primary])
        min_limit = np.min([np.min(x_primary), np.min(y_primary), np.min(z_primary)])
        ax.set_xlim([min_limit, min_limit + max_range])
        ax.set_ylim([min_limit, min_limit + max_range])
        ax.set_zlim([min_limit, min_limit + max_range])
        plt.show()

    def create_moon_sphere(self):
        moon_radius = Constants.MOON_EQUATORIAL_RADIUS / self.KILOMETER_TO_METER
        sides_number = 50
        az = np.linspace(0, 2 * np.pi, sides_number)
        el = np.linspace(0, np.pi, sides_number)
        x_sphere = moon_radius * np.outer(np.cos(az), np.sin(el))
        y_sphere = moon_radius * np.outer(np.sin(az), np.sin(el))
        z_sphere = moon_radius * np.outer(np.ones_like(az), np.cos(el))
        return x_sphere, y_sphere, z_sphere
