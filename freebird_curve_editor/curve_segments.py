from dataclasses import dataclass

from mathutils import Vector

from .curve_points import (
    is_bezier_point,
    point_is_hidden,
    point_position,
    set_point_position,
    set_point_selected,
    spline_points,
)


@dataclass(frozen=True)
class SegmentHit:
    spline_index: int
    start_index: int
    end_index: int
    factor: float
    distance: float
    world_position: object
    local_position: object


def segment_indices(spline):
    points = spline_points(spline)
    count = len(points)
    if count < 2 or getattr(spline, "point_count_v", 1) > 1:
        return

    for index in range(count - 1):
        yield index, index + 1

    if getattr(spline, "use_cyclic_u", False) and count > 2:
        yield count - 1, 0


def find_nearest_segment(ob, world_position, max_distance, endpoint_margin=0.08):
    position = Vector(world_position)
    best = None
    matrix_world = ob.matrix_world
    matrix_world_inv = matrix_world.inverted()

    for spline_index, spline in enumerate(ob.data.splines):
        points = spline_points(spline)
        for start_index, end_index in segment_indices(spline):
            start_point = points[start_index]
            end_point = points[end_index]
            if point_is_hidden(start_point) or point_is_hidden(end_point):
                continue

            start = matrix_world @ point_position(start_point)
            end = matrix_world @ point_position(end_point)
            segment = end - start
            length_squared = segment.length_squared
            if length_squared <= 1.0e-12:
                continue

            factor = sum((position[axis] - start[axis]) * segment[axis] for axis in range(3)) / length_squared
            if factor <= endpoint_margin or factor >= 1.0 - endpoint_margin:
                continue

            nearest = start + segment * factor
            distance = (position - nearest).length
            if distance > max_distance or (best is not None and distance >= best.distance):
                continue

            best = SegmentHit(
                spline_index=spline_index,
                start_index=start_index,
                end_index=end_index,
                factor=factor,
                distance=distance,
                world_position=nearest,
                local_position=matrix_world_inv @ nearest,
            )

    return best


def inserted_point_index(hit, point_count_before):
    cyclic_wrap = hit.start_index == point_count_before - 1 and hit.end_index == 0
    return point_count_before if cyclic_wrap else hit.start_index + 1


def _selection_value(point):
    if is_bezier_point(point):
        return (point.select_control_point, point.select_left_handle, point.select_right_handle)
    return point.select


def _restore_selection(point, value):
    if is_bezier_point(point):
        point.select_control_point, point.select_left_handle, point.select_right_handle = value
    else:
        point.select = value


def _other_edit_curve_selections(bpy, active_object):
    snapshots = []
    for candidate in getattr(bpy.context, "objects_in_mode_unique_data", ()):
        if candidate is active_object or getattr(candidate, "type", None) != "CURVE":
            continue
        points = [point for spline in candidate.data.splines for point in spline_points(spline)]
        snapshots.append((points, [_selection_value(point) for point in points]))
        for point in points:
            set_point_selected(point, False)
    return snapshots


def _restore_other_selections(snapshots):
    for points, selections in snapshots:
        for point, selection in zip(points, selections):
            _restore_selection(point, selection)


def subdivide_segment(ob, hit):
    """Subdivide one legacy Curve segment and move the new point to the hit."""
    import bpy

    spline = ob.data.splines[hit.spline_index]
    points = spline_points(spline)
    count_before = len(points)
    start = points[hit.start_index]
    end = points[hit.end_index]
    start_radius, end_radius = start.radius, end.radius
    start_tilt, end_tilt = start.tilt, end.tilt
    start_softbody = getattr(start, "weight_softbody", None)
    end_softbody = getattr(end, "weight_softbody", None)

    for curve_spline in ob.data.splines:
        for point in spline_points(curve_spline):
            set_point_selected(point, False)
    set_point_selected(start, True)
    set_point_selected(end, True)

    other_selections = _other_edit_curve_selections(bpy, ob)
    try:
        result = bpy.ops.curve.subdivide(number_cuts=1)
    finally:
        _restore_other_selections(other_selections)

    if "FINISHED" not in result:
        return None

    spline = ob.data.splines[hit.spline_index]
    points = spline_points(spline)
    if len(points) != count_before + 1:
        raise RuntimeError("Curve subdivision inserted an unexpected number of points")

    inserted = points[inserted_point_index(hit, count_before)]
    set_point_position(inserted, hit.local_position)
    inserted.radius = start_radius + (end_radius - start_radius) * hit.factor
    inserted.tilt = start_tilt + (end_tilt - start_tilt) * hit.factor
    if start_softbody is not None and end_softbody is not None:
        inserted.weight_softbody = start_softbody + (end_softbody - start_softbody) * hit.factor

    for curve_spline in ob.data.splines:
        for point in spline_points(curve_spline):
            set_point_selected(point, False)
    set_point_selected(inserted, True)
    ob.data.update_tag()
    return inserted
