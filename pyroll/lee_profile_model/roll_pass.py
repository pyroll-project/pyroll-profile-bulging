from shapely import Point, unary_union
from pyroll.core import RollPass, Hook

RollPass.OutProfile.bulge_radius = Hook[float]()


@RollPass.OutProfile.bulge_radius
def bulge_radius_round_oval(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    rp = self.roll_pass

    if "round" in rp.in_profile.classifiers and "oval" in rp.classifiers:
        weight = (rp.roll.groove.usable_width - self.width) / (rp.roll.groove.usable_width - rp.in_profile.width)
        usable_radius = (rp.roll.groove.r2 * rp.height - 1 / 4 * (
                rp.roll.groove.usable_width ** 2 + rp.height ** 2)) / (
                                2 * rp.roll.groove.r2 - rp.roll.groove.usable_width)
        bulge_radius = rp.in_profile.equvalent_radius * weight + usable_radius * (1 - weight)
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_oval_round(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None
    rp = self.roll_pass

    if "oval" in rp.in_profile.classifiers and "round" in rp.classifiers:

        oval_radius = rp.prev_of(RollPass).roll.groove.r2
        weight = (rp.roll.groove.usable_width - self.width) / (rp.roll.groove.usable_width - rp.in_profile.width)

        if rp.height == 2 * rp.roll.groove.r2:
            usable_radius = 2 * rp.roll.groove.r2
        else:
            usable_radius = rp.roll.groove.r2 + (rp.height - 2 * rp.roll.groove.r2)

        return oval_radius * weight + usable_radius * (1 - weight)


@RollPass.OutProfile.cross_section
def cross_section(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    cs = self.cross_section

    if self.has_value("bulge_radius"):
        circle_center = self.width / 2 - self.bulge_radius
        left_circle = Point(circle_center, 0).buffer(self.bulge_radius)
        right_circle = Point(-circle_center, 0).buffer(self.bulge_radius)
        return unary_union([left_circle, cs, right_circle])
    return cs
