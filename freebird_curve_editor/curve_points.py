from mathutils import Vector

from .math_utils import falloff_weight


def is_bezier_point(point):
    return hasattr(point, "select_control_point")


def point_key(point):
    try:
        return point.as_pointer()
    except Exception:
        return id(point)


def spline_points(spline):
    collection = spline.bezier_points if spline.type == "BEZIER" else spline.points
    return list(collection)


def iter_curve_points(curve):
    for spline in curve.splines:
        for index, point in enumerate(spline_points(spline)):
            yield spline, index, point


def point_position(point):
    return Vector(point.co[:3])


def set_point_position(point, position):
    position = Vector(position)
    if is_bezier_point(point):
        delta = position - Vector(point.co)
        left = Vector(point.handle_left) + delta
        right = Vector(point.handle_right) + delta
        point.co = position
        point.handle_left = left
        point.handle_right = right
        return

    weight = point.co[3]
    point.co = position.to_tuple() + (weight,)


def point_is_hidden(point):
    return bool(getattr(point, "hide", False))


def point_is_selected(point):
    if is_bezier_point(point):
        return bool(point.select_control_point or point.select_left_handle or point.select_right_handle)
    return bool(point.select)


def set_point_selected(point, selected):
    if is_bezier_point(point):
        point.select_control_point = selected
        point.select_left_handle = selected
        point.select_right_handle = selected
        return
    point.select = selected


def curve_contains_point(curve, target):
    target_key = point_key(target)
    return any(point_key(point) == target_key for _, _, point in iter_curve_points(curve))


def find_point_context(curve, target):
    target_key = point_key(target)
    for spline, index, point in iter_curve_points(curve):
        if point_key(point) == target_key:
            return spline, index, point
    return None


def _neighbor_tangent(spline, index, points):
    count = len(points)
    if count < 2:
        return Vector()

    cyclic = bool(getattr(spline, "use_cyclic_u", False))
    if cyclic:
        previous = point_position(points[(index - 1) % count])
        following = point_position(points[(index + 1) % count])
        return following - previous
    if index == 0:
        return point_position(points[1]) - point_position(points[0])
    if index == count - 1:
        return point_position(points[-1]) - point_position(points[-2])
    return point_position(points[index + 1]) - point_position(points[index - 1])


def point_world_tangent(ob, target):
    context = find_point_context(ob.data, target)
    if context is None:
        return Vector()

    spline, index, point = context
    points = spline_points(spline)
    tangent = Vector()
    if is_bezier_point(point):
        tangent = Vector(point.handle_right) - Vector(point.handle_left)
    if tangent.length_squared <= 1.0e-12:
        tangent = _neighbor_tangent(spline, index, points)
    if tangent.length_squared <= 1.0e-12:
        return Vector()

    tangent = ob.matrix_world.to_3x3() @ tangent
    if tangent.length_squared > 1.0e-12:
        tangent.normalize()
    return tangent


def _world_positions(ob, points):
    return [ob.matrix_world @ point_position(point) for point in points]


def _connected_distances(ob, spline, points, selected_indices):
    positions = _world_positions(ob, points)
    count = len(points)
    cumulative = [0.0]
    for index in range(1, count):
        cumulative.append(cumulative[-1] + (positions[index] - positions[index - 1]).length)

    cyclic = bool(getattr(spline, "use_cyclic_u", False)) and count > 1
    total = cumulative[-1]
    if cyclic:
        total += (positions[0] - positions[-1]).length

    distances = []
    for index in range(count):
        best = min(abs(cumulative[index] - cumulative[selected]) for selected in selected_indices)
        if cyclic and total > 0.0:
            best = min(best, total - best)
        distances.append(best)
    return distances


def build_falloff_entries(ob, selected_points, radius, falloff_type, connected=True):
    if not selected_points:
        return {}

    selected_keys = {point_key(point) for point in selected_points}
    selected_world = [ob.matrix_world @ point_position(point) for point in selected_points]
    entries = {}

    for spline in ob.data.splines:
        points = spline_points(spline)
        selected_indices = [index for index, point in enumerate(points) if point_key(point) in selected_keys]
        if connected and not selected_indices:
            continue

        if connected:
            distances = _connected_distances(ob, spline, points, selected_indices)
        else:
            positions = _world_positions(ob, points)
            distances = [min((position - selected).length for selected in selected_world) for position in positions]

        for point, distance in zip(points, distances):
            weight = 1.0 if point_key(point) in selected_keys else falloff_weight(distance, radius, falloff_type)
            if weight > 0.0:
                entries[point_key(point)] = (point, weight)

    return entries
