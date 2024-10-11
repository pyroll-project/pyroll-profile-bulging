from pyroll.core import RollPass, Hook

from .helpers import calculate_bulged_cross_section_polygon_round_oval_round, \
    calculate_bulged_cross_section_polygon_square_diamond_square, \
    calculate_bulged_cross_section_polygon_square_oval_square

RollPass.OutProfile.bulge_radius = Hook[float]()


@RollPass.OutProfile.bulge_radius
def bulge_radius_round_oval_lee(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass
    weight = (rp.roll.groove.usable_width - self.width) / (rp.roll.groove.usable_width - rp.in_profile.width)

    if "round" in rp.in_profile.classifiers and "oval" in rp.classifiers:
        usable_radius = (rp.roll.groove.r2 * rp.height - (rp.roll.groove.usable_width ** 2 + rp.height ** 2) / 4) / (
                2 * rp.roll.groove.r2 - rp.roll.groove.usable_width)

        bulge_radius = rp.in_profile.equivalent_radius * weight + usable_radius * (1 - weight)
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_oval_round_lee(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass
    weight = (rp.roll.groove.usable_width - self.width) / (rp.roll.groove.usable_width - rp.in_profile.width)

    if "oval" in rp.in_profile.classifiers and "round" in rp.classifiers:

        oval_radius = rp.prev_of(RollPass).roll.groove.r2

        if rp.height == 2 * rp.roll.groove.r2:
            usable_radius = 2 * rp.roll.groove.r2
        else:
            usable_radius = rp.roll.groove.r2 + (rp.height - 2 * rp.roll.groove.r2)

        bulge_radius = oval_radius * weight + usable_radius * (1 - weight)
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_square_diamond_schmidt(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass
    half_roll_pass_height = rp.height / 2
    half_profile_width = self.width / 2
    bulge_radius = (
                           half_roll_pass_height ** 2 + half_profile_width ** 2 - 2 * rp.roll.groove.r2 * half_roll_pass_height) / (
                           2 * (half_profile_width - rp.roll.groove.r2))

    if "square" in rp.in_profile.classifiers and "diamond" in rp.classifiers:
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_diamond_square_schmidt(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass
    half_roll_pass_height = rp.height / 2
    half_profile_width = self.width / 2
    bulge_radius = (
                           half_roll_pass_height ** 2 + half_profile_width ** 2 - 2 * rp.roll.groove.r2 * half_roll_pass_height) / (
                           2 * (half_profile_width - rp.roll.groove.r2))

    if "diamond" in rp.in_profile.classifiers and "square" in rp.classifiers:
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_oval_square_oval_schmidt(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass
    half_roll_pass_height = rp.height / 2
    half_profile_width = self.width / 2
    bulge_radius = (
                           half_roll_pass_height ** 2 + half_profile_width ** 2 - 2 * rp.roll.groove.r2 * half_roll_pass_height) / (
                           2 * (half_profile_width - rp.roll.groove.r2))

    if "oval" in rp.in_profile.classifiers and "square" in rp.classifiers:
        return bulge_radius

    if "square" in rp.in_profile.classifiers and "oval" in rp.classifiers:
        return bulge_radius


@RollPass.OutProfile.cross_section
def cross_section(self: RollPass.OutProfile):
    rp = self.roll_pass

    if "square" in rp.in_profile.classifiers and "diamond" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_square_diamond_square(profile=self)

    elif "diamond" in rp.in_profile.classifiers and "square" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_square_diamond_square(profile=self)

    elif "round" in rp.in_profile.classifiers and "oval" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_round_oval_round(profile=self)

    elif "oval" in rp.in_profile.classifiers and "round" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_round_oval_round(profile=self)

    elif "square" in rp.in_profile.classifiers and "oval" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_square_diamond_square(profile=self)

    elif "oval" in rp.in_profile.classifiers and "square" in rp.classifiers:
        bulged_cross_section = calculate_bulged_cross_section_polygon_square_oval_square(profile=self)

    else:
        bulged_cross_section = self.cross_section

    return bulged_cross_section
