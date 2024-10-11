import numpy as np
from pyroll.core import ThreeRollPass, Hook

from .helpers import calculate_three_roll_pass_bulged_section_polygon

ThreeRollPass.OutProfile.bulge_radius = Hook[float]()


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_round_round_byon(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "round" in self.roll_pass.in_profile.classifiers and "round" in self.roll_pass.classifiers:
        bulge_radius = self.width / 2

        return bulge_radius


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_oval_oval_byon(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "oval" in self.roll_pass.in_profile.classifiers and "oval" in self.roll_pass.classifiers:
        bulge_radius = self.width / 2
        return bulge_radius


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_round_oval_byon(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    eccentricity = 3.133 * self.roll_pass.displaced_cross_section.area / self.roll_pass.in_profile.cross_section.area * self.roll_pass.in_profile.width / 2

    if "round" in self.roll_pass.in_profile.classifiers and "oval" in self.roll_pass.classifiers:
        bulge_radius = np.abs(self.width / 2 - eccentricity)
        return bulge_radius


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_oval_round_byon(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    eccentricity = 3.133 * self.roll_pass.displaced_cross_section.area / self.roll_pass.in_profile.cross_section.area * self.roll_pass.in_profile.width / 2

    if "oval" in self.roll_pass.in_profile.classifiers and "round" in self.roll_pass.classifiers:
        bulge_radius = self.roll_pass.inscribed_circle_diameter / 2 + eccentricity
        return bulge_radius


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_round_flat_min(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "round" in self.roll_pass.in_profile.classifiers and "flat" in self.roll_pass.classifiers:
        eccentricity = 2.40 * self.roll_pass.displaced_cross_section.area / self.roll_pass.in_profile.cross_section.area * self.roll_pass.in_profile.width / 2
        bulge_radius = np.abs(self.width / 2 - eccentricity)
        return bulge_radius


@ThreeRollPass.OutProfile.bulge_radius
def bulge_radius_flat_flat_min(self: ThreeRollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "flat" in self.roll_pass.in_profile.classifiers and "flat" in self.roll_pass.classifiers:
        eccentricity = 2.40 * self.roll_pass.displaced_cross_section.area / self.roll_pass.in_profile.cross_section.area * self.roll_pass.in_profile.width / 2
        bulge_radius = np.abs(self.width - eccentricity)
        return bulge_radius


@ThreeRollPass.OutProfile.cross_section
def cross_section(self: ThreeRollPass.OutProfile):

    bulged_cross_section = calculate_three_roll_pass_bulged_section_polygon(profile=self)

    return bulged_cross_section
