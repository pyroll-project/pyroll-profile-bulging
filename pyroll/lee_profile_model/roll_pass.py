from shapely import Point, unary_union
from pyroll.core import RollPass, Hook

RollPass.OutProfile.bulge_radius = Hook[float]()


@RollPass.OutProfile.bulge_radius
def bulge_radius_round_oval(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "round" in self.roll_pass.in_profile.classifiers and "oval" in self.roll_pass.classifiers:
        rp = self.roll_pass
        weight = (rp.roll.groove.usable_width - self.width) / (
                    rp.roll.groove.usable_width - rp.in_profile.width)

        usable_radius = (rp.roll.groove.r2 * rp.height - 1 / 4 * (self.width ** 2 + rp.height ** 2)) / (
                2 * rp.roll.groove.r2 - rp.roll.groove.usable_width)

        return rp.in_profile.equvalent_radius * weight + usable_radius * (1 - weight)


@RollPass.OutProfile.bulge_radius
def bulge_radius_oval_round(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    if "oval" in self.roll_pass.in_profile.classifiers and "round" in self.roll_pass.classifiers:
        rp = self.roll_pass
        oval_radius = rp.prev_of(RollPass).roll.groove.r2

        weight = (2 * rp.roll.groove.r2 - self.width) / (2 * rp.roll.groove.r2 - rp.in_profile.width)

        return oval_radius * weight + rp.roll.groove.r2 * (1 - weight)


@RollPass.OutProfile.cross_section
def cross_section(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None

    cs = self.cross_section

    if self.has_set_or_cached("bulge_radius"):
        circle_center = self.width / 2 - self.bulge_radius
        p = Point(circle_center, 0).buffer(self.bulge_radius)

        return unary_union([cs, p])
    return cs
