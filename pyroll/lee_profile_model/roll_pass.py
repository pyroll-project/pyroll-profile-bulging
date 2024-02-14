import math
import logging
import numpy as np
from shapely import Point, unary_union, intersection
from pyroll.core import RollPass, Hook
from pyroll.core.roll_pass.hookimpls.helpers import out_cross_section

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
        bulge_radius = rp.in_profile.equivalent_radius * weight + usable_radius * (1 - weight)
        return bulge_radius


@RollPass.OutProfile.bulge_radius
def bulge_radius_oval_round(self: RollPass.OutProfile, cycle: bool):
    if cycle:
        return None
    rp = self.roll_pass

    if "oval" in rp.in_profile.classifiers and "round" in rp.classifiers:

        oval_radius = rp.prev_of(RollPass).roll.groove.r2
        weight = (rp.roll.groove.usable_width - self.width) / (
                rp.roll.groove.usable_width - rp.in_profile.width)

        if rp.height == 2 * rp.roll.groove.r2:
            usable_radius = 2 * rp.roll.groove.r2
        else:
            usable_radius = rp.roll.groove.r2 + (rp.height - 2 * rp.roll.groove.r2)

        return oval_radius * weight + usable_radius * (1 - weight)


@RollPass.OutProfile.cross_section
def cross_section(self: RollPass.OutProfile):
    if self.has_value("bulge_radius"):
        circle_center = self.width / 2 - self.bulge_radius
        right_circle = Point(circle_center, 0).buffer(self.bulge_radius)
        left_circle = Point(-circle_center, 0).buffer(self.bulge_radius)
        max_cross_section = out_cross_section(self.roll_pass, math.inf)
        intersection_points = max_cross_section.boundary.intersection(right_circle.boundary)

        if intersection_points.is_empty:
            logging.getLogger(__name__).info("No intersection point found. Continuing without bulging.")
            return None

        elif (self.bulge_radius * 2) > (abs(max_cross_section.bounds[0]) + max_cross_section.bounds[2]):
            circle_intersection = intersection(left_circle, right_circle)
            return intersection(circle_intersection, max_cross_section)

        else:
            intersection_points = list(intersection_points.geoms)
            first_intersection_point = min(intersection_points, key=lambda point: abs(point.y))
            cross_section_till_intersection = out_cross_section(self.roll_pass, abs(first_intersection_point.x) * 2)
            left_side_cross_section = intersection(max_cross_section, left_circle)
            right_side_cross_section = intersection(max_cross_section, right_circle)

            return unary_union([left_side_cross_section, cross_section_till_intersection, right_side_cross_section])
