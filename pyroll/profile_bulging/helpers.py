import math
import logging
import numpy as np
from pyroll.core import RollPass
from shapely import Point, intersection, unary_union
from pyroll.core.roll_pass.hookimpls.helpers import out_cross_section, out_cross_section3


def calculate_bulged_cross_section_polygon_round_oval_round(profile: RollPass.OutProfile):
    circle_center = profile.width / 2 - profile.bulge_radius
    right_circle = Point(circle_center, 0).buffer(profile.bulge_radius)
    left_circle = Point(-circle_center, 0).buffer(profile.bulge_radius)
    max_cross_section = out_cross_section(profile.roll_pass, math.inf)
    intersection_points = max_cross_section.boundary.intersection(right_circle.boundary)

    if intersection_points.is_empty:
        logging.getLogger(__name__).info("No intersection point found. Continuing without bulging.")
        return None

    elif (profile.bulge_radius * 2) > (abs(max_cross_section.bounds[0]) + max_cross_section.bounds[2]):
        circle_intersection = intersection(left_circle, right_circle)
        return intersection(circle_intersection, max_cross_section)

    else:
        intersection_points = list(intersection_points.geoms)
        first_intersection_point = min(intersection_points, key=lambda point: abs(point.y))
        cross_section_till_intersection = out_cross_section(profile.roll_pass, abs(first_intersection_point.x) * 2)
        left_side_cross_section = intersection(max_cross_section, left_circle)
        right_side_cross_section = intersection(max_cross_section, right_circle)
        bulged_cross_section = unary_union(
            [left_side_cross_section, cross_section_till_intersection, right_side_cross_section])

        return bulged_cross_section


def calculate_bulged_cross_section_polygon_square_diamond_square(profile: RollPass.OutProfile):
    rp = profile.roll_pass

    separation_point_angle = np.arcsin(
        (profile.width / 2 - profile.bulge_radius) / (rp.roll.groove.r2 - profile.bulge_radius))
    separation_point_z_coordinate = rp.roll.groove.r2 * np.sin(separation_point_angle)

    left_bulge = Point(-profile.width / 2 + profile.bulge_radius, 0).buffer(profile.bulge_radius)
    right_bulge = Point(profile.width / 2 - profile.bulge_radius, 0).buffer(profile.bulge_radius)
    intersection_cross_section = out_cross_section(rp, 2 * np.abs(separation_point_z_coordinate))

    if (2 * profile.bulge_radius) < rp.height:
        bulged_cross_section = unary_union([left_bulge, intersection_cross_section, right_bulge])
        return bulged_cross_section

    else:
        helper_cs = out_cross_section(rp, profile.width)
        left_bulge_with_intersection = left_bulge.intersection(helper_cs)
        right_bulge_with_intersection = right_bulge.intersection(helper_cs)
        bulged_cross_section = unary_union([left_bulge_with_intersection, right_bulge_with_intersection])
        return bulged_cross_section


def calculate_bulged_cross_section_polygon_square_oval_square(profile: RollPass.OutProfile):
    rp = profile.roll_pass

    separation_point_angle = np.arcsin(
        (profile.width / 2 - profile.bulge_radius) / (rp.roll.groove.r2 - profile.bulge_radius))
    separation_point_z_coordinate = rp.roll.groove.r2 * np.sin(separation_point_angle)

    left_bulge = Point(-profile.width / 2 + profile.bulge_radius, 0).buffer(profile.bulge_radius)
    right_bulge = Point(profile.width / 2 - profile.bulge_radius, 0).buffer(profile.bulge_radius)
    intersection_cross_section = out_cross_section(rp, 2 * np.abs(separation_point_z_coordinate))

    if (2 * profile.bulge_radius) < rp.height:
        bulged_cross_section = unary_union([left_bulge, intersection_cross_section, right_bulge])
        return bulged_cross_section

    else:

        helper_cs = out_cross_section(rp, profile.width)
        left_bulge_with_intersection = left_bulge.intersection(helper_cs)
        right_bulge_with_intersection = right_bulge.intersection(helper_cs)
        bulged_cross_section = left_bulge_with_intersection.intersection(right_bulge_with_intersection)
        return bulged_cross_section


def calculate_three_roll_pass_bulged_section_polygon(profile: RollPass.OutProfile):
    roll_pass = profile.roll_pass
    in_profile = roll_pass.in_profile

    offset_distance = profile.width / 2 - profile.bulge_radius

    x_offset_lower_right = offset_distance * np.cos(np.deg2rad(-30))
    y_offset_lower_right = offset_distance * np.sin(np.deg2rad(-30))

    x_offset_lower_left = offset_distance * np.cos(np.deg2rad(210))
    y_offset_lower_left = offset_distance * np.sin(np.deg2rad(210))

    upper_bulge = Point(0, profile.width / 2 - profile.bulge_radius).buffer(profile.bulge_radius)
    lower_right_bulge = Point(x_offset_lower_right, y_offset_lower_right).buffer(profile.bulge_radius)
    lower_left_bulge = Point(x_offset_lower_left, y_offset_lower_left).buffer(profile.bulge_radius)

    upper_with_bulge = profile.cross_section.intersection(upper_bulge)
    lower_left_with_bulge = profile.cross_section.intersection(lower_left_bulge)
    lower_right_with_bulge = profile.cross_section.intersection(lower_right_bulge)

    if "round" in in_profile.classifiers and "flat" in roll_pass.classifiers:
        intermediate_cs = out_cross_section3(profile.roll_pass, profile.width * 0.7)
        bulged_cross_section = unary_union(
            [intermediate_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

    elif "flat" in in_profile.classifiers and "flat" in roll_pass.classifiers:
        intermediate_cs = upper_with_bulge.intersection(lower_left_with_bulge)
        bulged_cross_section = intermediate_cs.intersection(lower_right_with_bulge)

    elif "round" in in_profile.classifiers and "oval" in roll_pass.classifiers:
        helper_cs = out_cross_section3(profile.roll_pass, profile.width * 0.9)
        bulged_cross_section = unary_union([helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

    elif "round" in in_profile.classifiers and "round" in roll_pass.classifiers:
        helper_cs = out_cross_section3(profile.roll_pass, profile.width * 0.9)
        bulged_cross_section = unary_union([helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

    elif "oval" in in_profile.classifiers and "oval" in roll_pass.classifiers:
        helper_cs = out_cross_section3(profile.roll_pass, profile.width * 0.9)
        bulged_cross_section = unary_union([helper_cs, upper_with_bulge, lower_left_with_bulge, lower_right_with_bulge])

    elif "oval" in in_profile.classifiers and "round" in roll_pass.classifiers:
        intermediate_cs = upper_with_bulge.intersection(lower_left_with_bulge)
        bulged_cross_section = intermediate_cs.intersection(lower_right_with_bulge)
    else:
        bulged_cross_section = profile.cross_section
    return bulged_cross_section
