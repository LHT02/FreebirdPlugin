from math import atan2, exp, isfinite, sqrt


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def _canonical_quaternion(quaternion_wxyz):
    values = tuple(float(component) for component in quaternion_wxyz)
    if len(values) != 4 or not all(isfinite(component) for component in values):
        return None

    length = sqrt(sum(component * component for component in values))
    if length <= 1.0e-8:
        return None

    values = tuple(component / length for component in values)
    for component in values:
        if abs(component) <= 1.0e-8:
            continue
        if component < 0.0:
            values = tuple(-value for value in values)
        break
    return values


def _signed_twist_angle(quaternion_wxyz, axis_xyz):
    w, x, y, z = quaternion_wxyz
    ax, ay, az = axis_xyz
    axis_length = sqrt(ax * ax + ay * ay + az * az)
    if axis_length <= 1.0e-8:
        return 0.0

    ax /= axis_length
    ay /= axis_length
    az /= axis_length
    projected = x * ax + y * ay + z * az
    projected_length = sqrt(w * w + projected * projected)
    if projected_length <= 1.0e-8:
        return 0.0

    return 2.0 * atan2(projected / projected_length, w / projected_length)


def signed_twist_angle(quaternion_wxyz, axis_xyz):
    """Return shortest-arc quaternion twist, invariant to q/-q representation."""
    quaternion = _canonical_quaternion(quaternion_wxyz)
    if quaternion is None:
        return 0.0
    return _signed_twist_angle(quaternion, axis_xyz)


def safe_signed_twist_angle(quaternion_wxyz, axis_xyz, max_rotation_delta):
    """Return twist unless the whole frame delta looks like a tracking discontinuity."""
    quaternion = _canonical_quaternion(quaternion_wxyz)
    if quaternion is None:
        return 0.0

    w, x, y, z = quaternion
    rotation_angle = 2.0 * atan2(sqrt(x * x + y * y + z * z), w)
    if max_rotation_delta > 0.0 and rotation_angle > max_rotation_delta:
        return 0.0
    return _signed_twist_angle(quaternion, axis_xyz)


def joystick_scale_factor(value, delta_seconds, rate, deadzone):
    if abs(value) <= deadzone:
        return 1.0

    return exp(value * rate * max(0.0, delta_seconds))


def falloff_weight(distance, radius, falloff_type="SMOOTH"):
    if distance <= 0.0:
        return 1.0
    if radius <= 0.0 or distance >= radius:
        return 0.0

    t = distance / radius
    x = 1.0 - t
    falloff_type = (falloff_type or "SMOOTH").upper()

    if falloff_type == "CONSTANT":
        return 1.0
    if falloff_type == "LINEAR":
        return x
    if falloff_type == "SHARP":
        return x * x
    if falloff_type == "ROOT":
        return sqrt(x)
    if falloff_type == "SPHERE":
        return sqrt(max(0.0, 1.0 - t * t))
    if falloff_type == "INVERSE_SQUARE":
        return 1.0 - t * t

    return x * x * (3.0 - 2.0 * x)
