import math
import logging
import numpy as np

from shapely import Point, intersection, unary_union
from pyroll.core import Hook, Unit, Profile as BaseProfile, SymmetricRollPass
from pyroll.core.roll_pass.hookimpls.helpers import out_cross_section, out_cross_section3

SymmetricRollPass.OutProfile.bulge_radius = Hook[float]()


class BulgingModel(Unit):
    def __init__(self, symmetric_roll_pass: SymmetricRollPass):
        self.symmetric_roll_pass = symmetric_roll_pass
        super().__init__(label=f"Bulging Model for {self.symmetric_roll_pass}")

    def two_roll_bulge_radius_round_oval_lee(self, profile: BaseProfile):

        weight = (self.symmetric_roll_pass.roll.groove.usable_width - profile.width) / (
                self.symmetric_roll_pass.roll.groove.usable_width - self.symmetric_roll_pass.in_profile.width)
        usable_radius = (self.symmetric_roll_pass.roll.groove.r2 * self.symmetric_roll_pass.height - (
                self.symmetric_roll_pass.roll.groove.usable_width ** 2 + self.symmetric_roll_pass.height ** 2) / 4) / (
                                2 * self.symmetric_roll_pass.roll.groove.r2 - self.symmetric_roll_pass.roll.groove.usable_width)
        return self.symmetric_roll_pass.in_profile.equivalent_radius * weight + usable_radius * (1 - weight)


    def two_roll_bulge_radius_oval_round_lee(self, profile: BaseProfile):

        weight = (self.symmetric_roll_pass.roll.groove.usable_width - profile.width) / (
                self.symmetric_roll_pass.roll.groove.usable_width - self.symmetric_roll_pass.in_profile.width)
        oval_radius = self.symmetric_roll_pass.prev_of(SymmetricRollPass).roll.groove.r2

        if self.symmetric_roll_pass.height == 2 * self.symmetric_roll_pass.roll.groove.r2:
            usable_radius = 2 * self.symmetric_roll_pass.roll.groove.r2
        else:
            usable_radius = self.symmetric_roll_pass.roll.groove.r2 + (
                    self.symmetric_roll_pass.height - 2 * self.symmetric_roll_pass.roll.groove.r2)

        return oval_radius * weight + usable_radius * (1 - weight)

    def two_roll_bulge_radius_model_schmidt(self, profile: BaseProfile):
        return (
                self.symmetric_roll_pass.height / 2 ** 2 + profile.width / 2 ** 2 - 2 * self.symmetric_roll_pass.roll.groove.r2 * self.symmetric_roll_pass.height / 2) / (
                2 * (profile.width / 2 - self.symmetric_roll_pass.roll.groove.r2))

    def three_roll_bulge_radius_round_round_and_oval_oval_byon(self, profile: BaseProfile):
        return profile.width / 2

    def three_roll_bulge_radius_round_oval_byon(self, profile: BaseProfile):
        eccentricity = 3.133 * self.symmetric_roll_pass.displaced_cross_section.area / self.symmetric_roll_pass.in_profile.cross_section.area * self.symmetric_roll_pass.in_profile.width / 2
        return np.abs(profile.width / 2 - eccentricity)

    def three_roll_bulge_radius_oval_round_byon(self, profile: BaseProfile):
        eccentricity = 3.133 * self.symmetric_roll_pass.displaced_cross_section.area / self.symmetric_roll_pass.in_profile.cross_section.area * self.symmetric_roll_pass.in_profile.width / 2
        return self.symmetric_roll_pass.inscribed_circle_diameter / 2 + eccentricity

    def three_roll_bulge_radius_model_min(self, profile: BaseProfile):
        eccentricity = 2.40 * self.symmetric_roll_pass.displaced_cross_section.area / self.symmetric_roll_pass.in_profile.cross_section.area * self.symmetric_roll_pass.in_profile.width / 2
        return np.abs(profile.width - eccentricity)

    def bulge_radius(self, profile: BaseProfile):

        if not "3fold" in self.symmetric_roll_pass.classifiers:
            if "round" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_round_oval_lee(profile)
            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_oval_round_lee(profile)
            elif "square" in self.symmetric_roll_pass.in_profile.classifiers and "diamond" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_model_schmidt(profile)
            elif "diamond" in self.symmetric_roll_pass.in_profile.classifiers and "square" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_model_schmidt(profile)
            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "square" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_model_schmidt(profile)
            elif "square" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulge_radius_model_schmidt(profile)

        elif "3fold" in self.symmetric_roll_pass.classifiers:
            if "round" in self.symmetric_roll_pass.in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_round_round_and_oval_oval_byon(profile)
            elif "round" in self.symmetric_roll_pass.in_profile.classifiers and "flat" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_model_min(profile)
            elif "round" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_round_oval_byon(profile)
            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_round_round_and_oval_oval_byon(profile)
            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_oval_round_byon(profile)
            elif "flat" in self.symmetric_roll_pass.in_profile.classifiers and "flat" in self.symmetric_roll_pass.classifiers:
                return self.three_roll_bulge_radius_model_min(profile)

    def two_roll_bulged_cross_section_polygon_round_oval_round(self, profile: BaseProfile):
        circle_center = profile.width / 2 - profile.bulge_radius
        right_circle = Point(circle_center, 0).buffer(profile.bulge_radius)
        left_circle = Point(-circle_center, 0).buffer(profile.bulge_radius)
        max_cross_section = out_cross_section(profile.roll_pass, math.inf)
        intersection_points = max_cross_section.boundary.intersection(right_circle.boundary)

        if intersection_points.is_empty:
            logging.getLogger(__name__).info("No intersection point found. Continuing without bulging.")
            return None

        elif (profile.bulge_radius * 2) > (
                abs(max_cross_section.bounds[0]) + max_cross_section.bounds[2]):
            circle_intersection = intersection(left_circle, right_circle)
            return intersection(circle_intersection, max_cross_section)

        else:
            intersection_points = list(intersection_points.geoms)
            first_intersection_point = min(intersection_points, key=lambda point: abs(point.y))
            cross_section_till_intersection = out_cross_section(profile.roll_pass,
                                                                abs(first_intersection_point.x) * 2)
            left_side_cross_section = intersection(max_cross_section, left_circle)
            right_side_cross_section = intersection(max_cross_section, right_circle)
            bulged_cross_section = unary_union(
                [left_side_cross_section, cross_section_till_intersection, right_side_cross_section])

            return bulged_cross_section

    def two_roll_bulged_cross_section_polygon_square_diamond_square(self, profile: BaseProfile):

        separation_point_angle = np.arcsin(
            (profile.width / 2 - profile.bulge_radius) / (
                    self.symmetric_roll_pass.roll.groove.r2 - profile.bulge_radius))
        separation_point_z_coordinate = self.symmetric_roll_pass.roll.groove.r2 * np.sin(separation_point_angle)

        left_bulge = Point(
            -profile.width / 2 + profile.bulge_radius,
            0).buffer(profile.bulge_radius)
        right_bulge = Point(
            profile.width / 2 - profile.bulge_radius,
            0).buffer(profile.bulge_radius)
        intersection_cross_section = out_cross_section(self.symmetric_roll_pass,
                                                       2 * np.abs(separation_point_z_coordinate))

        if (2 * profile.bulge_radius) < self.symmetric_roll_pass.height:
            bulged_cross_section = unary_union([left_bulge, intersection_cross_section, right_bulge])
            return bulged_cross_section

        else:
            helper_cs = out_cross_section(self.symmetric_roll_pass, profile.width)
            left_bulge_with_intersection = left_bulge.intersection(helper_cs)
            right_bulge_with_intersection = right_bulge.intersection(helper_cs)
            bulged_cross_section = unary_union([left_bulge_with_intersection, right_bulge_with_intersection])
            return bulged_cross_section

    def two_roll_bulged_cross_section_polygon_square_oval_square(self, profile: BaseProfile):

        separation_point_angle = np.arcsin(
            (profile.width / 2 - profile.bulge_radius) / (
                    self.symmetric_roll_pass.roll.groove.r2 - profile.bulge_radius))
        separation_point_z_coordinate = self.symmetric_roll_pass.roll.groove.r2 * np.sin(separation_point_angle)

        left_bulge = Point(
            -profile.width / 2 + profile.bulge_radius,
            0).buffer(profile.bulge_radius)
        right_bulge = Point(
            profile.width / 2 - profile.bulge_radius,
            0).buffer(profile.bulge_radius)
        intersection_cross_section = out_cross_section(self.symmetric_roll_pass,
                                                       2 * np.abs(separation_point_z_coordinate))

        if (2 * profile.bulge_radius) < self.symmetric_roll_pass.height:
            bulged_cross_section = unary_union([left_bulge, intersection_cross_section, right_bulge])
            return bulged_cross_section

        else:
            helper_cs = out_cross_section(self.symmetric_roll_pass, profile.width)
            left_bulge_with_intersection = left_bulge.intersection(helper_cs)
            right_bulge_with_intersection = right_bulge.intersection(helper_cs)
            bulged_cross_section = left_bulge_with_intersection.intersection(right_bulge_with_intersection)
            return bulged_cross_section

    def three_roll_pass_bulged_cross_section(self, profile: BaseProfile):
        in_profile = self.symmetric_roll_pass.in_profile

        offset_distance = profile.width / 2 - profile.bulge_radius

        x_offset_lower_right = offset_distance * np.cos(np.deg2rad(-30))
        y_offset_lower_right = offset_distance * np.sin(np.deg2rad(-30))

        x_offset_lower_left = offset_distance * np.cos(np.deg2rad(210))
        y_offset_lower_left = offset_distance * np.sin(np.deg2rad(210))

        upper_bulge = Point(0,
                            profile.width / 2 - profile.bulge_radius).buffer(
            profile.bulge_radius)
        lower_right_bulge = Point(x_offset_lower_right, y_offset_lower_right).buffer(
            profile.bulge_radius)
        lower_left_bulge = Point(x_offset_lower_left, y_offset_lower_left).buffer(
            profile.bulge_radius)

        upper_with_bulge = profile.cross_section.intersection(upper_bulge)
        lower_left_with_bulge = profile.cross_section.intersection(lower_left_bulge)
        lower_right_with_bulge = profile.cross_section.intersection(lower_right_bulge)

        if "round" in in_profile.classifiers and "flat" in self.symmetric_roll_pass.classifiers:
            intermediate_cs = out_cross_section3(self.symmetric_roll_pass,
                                                 profile.width * 0.7)
            bulged_cross_section = unary_union(
                [intermediate_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

        elif "flat" in in_profile.classifiers and "flat" in self.symmetric_roll_pass.classifiers:
            intermediate_cs = upper_with_bulge.intersection(lower_left_with_bulge)
            bulged_cross_section = intermediate_cs.intersection(lower_right_with_bulge)

        elif "round" in in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
            helper_cs = out_cross_section3(self.symmetric_roll_pass, profile.width * 0.9)
            bulged_cross_section = unary_union(
                [helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

        elif "round" in in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
            helper_cs = out_cross_section3(self.symmetric_roll_pass, profile.width * 0.9)
            bulged_cross_section = unary_union(
                [helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

        elif "oval" in in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
            helper_cs = out_cross_section3(self.symmetric_roll_pass, profile.width * 0.9)
            bulged_cross_section = unary_union(
                [helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

        elif "oval" in in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
            intermediate_cs = upper_with_bulge.intersection(lower_left_with_bulge)
            bulged_cross_section = intermediate_cs.intersection(lower_right_with_bulge)
        else:
            bulged_cross_section = profile.cross_section
        return bulged_cross_section

    def cross_section(self, profile: BaseProfile):

        if not "3fold" in self.symmetric_roll_pass.classifiers:
            if "square" in self.symmetric_roll_pass.in_profile.classifiers and "diamond" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_square_diamond_square(profile)

            elif "diamond" in self.symmetric_roll_pass.in_profile.classifiers and "square" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_square_diamond_square(profile)

            elif "round" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_round_oval_round(profile)

            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "round" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_round_oval_round(profile)

            elif "square" in self.symmetric_roll_pass.in_profile.classifiers and "oval" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_square_oval_square(profile)

            elif "oval" in self.symmetric_roll_pass.in_profile.classifiers and "square" in self.symmetric_roll_pass.classifiers:
                return self.two_roll_bulged_cross_section_polygon_square_oval_square(profile)
            else:
                return profile.cross_section
        elif "3fold" in self.symmetric_roll_pass.classifiers:
            return self.three_roll_pass_bulged_cross_section(profile)

    def solve(self, in_profile: BaseProfile) -> BaseProfile:
        in_profile.bulge_radius = self.bulge_radius(profile=in_profile)
        in_profile.cross_section = self.cross_section(profile=in_profile)
        return in_profile


SymmetricRollPass.post_processors.append(BulgingModel)
