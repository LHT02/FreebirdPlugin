from math import atan2, exp, sqrt


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def signed_twist_angle(quaternion_wxyz, axis_xyz):
    """Return the signed quaternion twist around a normalized axis."""
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
