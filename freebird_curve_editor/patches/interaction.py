from math import isclose
from time import monotonic

from ..constants import (
    JOYSTICK_DEADZONE,
    JOYSTICK_RADIUS_RATE,
    MAX_TILT,
    POINT_RADIUS_MAX,
    POINT_RADIUS_MIN,
)
from ..curve_points import build_falloff_entries, point_key, point_world_tangent, set_point_position
from ..math_utils import clamp, joystick_scale_factor, signed_twist_angle
from ..state import runtime


def _is_curve_transform_active(transform_state):
    ob = transform_state.get("object_to_transform")
    return bool(
        transform_state.get("is_transforming")
        and transform_state.get("is_transforming_from_grab")
        and ob is not None
        and getattr(ob, "type", None) == "CURVE"
        and getattr(ob, "mode", None) == "EDIT"
    )


def _delta_seconds(channel):
    now = monotonic()
    previous = runtime.joystick_timestamps.get(channel)
    runtime.joystick_timestamps[channel] = now
    if previous is None or now - previous > 0.1:
        return 1.0 / 60.0
    return max(1.0 / 240.0, min(0.05, now - previous))


def _scale_component(scale):
    try:
        if not isclose(scale.x, 1.0):
            return scale.x
        if not isclose(scale.y, 1.0):
            return scale.y
        return scale.z
    except AttributeError:
        return scale


def _prepare_entries(ob, transform_elements):
    import bpy

    selected = list(transform_elements or ())
    session = (ob.as_pointer(), frozenset(point_key(point) for point in selected))
    if runtime.falloff_session == session:
        return

    runtime.falloff_session = session
    runtime.joystick_timestamps.clear()
    tool_settings = bpy.context.scene.tool_settings
    if not tool_settings.use_proportional_edit:
        runtime.falloff_entries = {point_key(point): (point, 1.0) for point in selected}
        return

    size_name = "proportional_distance" if hasattr(tool_settings, "proportional_distance") else "proportional_size"
    radius = getattr(tool_settings, size_name)
    connected = bool(getattr(tool_settings, "use_proportional_connected", True))
    runtime.falloff_entries = build_falloff_entries(
        ob,
        selected,
        radius,
        tool_settings.proportional_edit_falloff,
        connected=connected,
    )


def _weighted_pose(pose_delta, weight):
    from bl_xr import Pose
    from mathutils import Quaternion, Vector

    rotation = Quaternion().slerp(pose_delta.rotation, weight)
    scale = pose_delta.scale_factor
    if isinstance(scale, Vector):
        scale = Vector([1.0 + (component - 1.0) * weight for component in scale])
    else:
        scale = 1.0 + (scale - 1.0) * weight
    return Pose(position=pose_delta.position * weight, rotation=rotation, scale_factor=scale)


def install(registry):
    import bpy
    from bl_xr import Pose, root
    from mathutils import Quaternion, Vector
    from freebird import navigate
    from freebird.gizmos import auto_keyframe_transforms
    from freebird.gizmos import proportional_edit_cursor
    from freebird.tools import transform as transform_module
    from freebird.tools import transform_common
    from freebird.tools import transform_trigger

    original_joystick = transform_common.on_joystick_vertical
    original_yaw_move = navigate.on_yaw_move
    original_strafe_move = navigate.on_strafe_move
    original_cursor_update = proportional_edit_cursor.ProportionalEditSphere.update
    original_keyframe_point = auto_keyframe_transforms.add_edit_nurbs_keyframe
    transform_state = transform_common.transform_state

    def on_transform_edit_curve(ob, event_name, event):
        if event_name == "drag_start":
            runtime.falloff_session = None
        _prepare_entries(ob, transform_state.get("transform_elements"))

        pose_delta = event.pose_delta
        scale = _scale_component(pose_delta.scale_factor)
        single_hand = "both" not in (event.button_name or "")

        for point, weight in runtime.falloff_entries.values():
            tangent = point_world_tangent(ob, point)
            position = point.co[:3]
            pose = Pose(transform_state["transform_m"] @ Vector(position), Quaternion(), 1.0)
            pose.transform(_weighted_pose(pose_delta, weight), event.pivot_position)
            local_position = transform_state["transform_m_inv"] @ pose.position
            set_point_position(point, local_position)

            if not isclose(scale, 1.0):
                weighted_scale = 1.0 + (scale - 1.0) * weight
                point.radius = clamp(point.radius * weighted_scale, POINT_RADIUS_MIN, POINT_RADIUS_MAX)

            if (
                single_hand
                and transform_state.get("is_transforming_from_grab")
                and tangent.length_squared > 1.0e-12
            ):
                angle = signed_twist_angle(
                    (pose_delta.rotation.w, pose_delta.rotation.x, pose_delta.rotation.y, pose_delta.rotation.z),
                    (tangent.x, tangent.y, tangent.z),
                )
                point.tilt = clamp(point.tilt + angle * weight, -MAX_TILT, MAX_TILT)

        ob.data.update_tag()

    def guarded_proportional_joystick(self, event_name, event):
        if _is_curve_transform_active(transform_state):
            return
        return original_joystick(self, event_name, event)

    def on_curve_radius_joystick(self, event_name, event):
        if not _is_curve_transform_active(transform_state):
            runtime.joystick_timestamps.pop("radius", None)
            return

        value = float(event.value)
        if abs(value) <= JOYSTICK_DEADZONE:
            runtime.joystick_timestamps.pop("radius", None)
            return

        ob = transform_state["object_to_transform"]
        _prepare_entries(ob, transform_state.get("transform_elements"))
        factor = joystick_scale_factor(
            value,
            _delta_seconds("radius"),
            JOYSTICK_RADIUS_RATE,
            JOYSTICK_DEADZONE,
        )
        for point, weight in runtime.falloff_entries.values():
            point.radius = clamp(point.radius * (factor**weight), POINT_RADIUS_MIN, POINT_RADIUS_MAX)
        transform_state["has_transformed"] = True
        ob.data.update_tag()

    def guarded_yaw_move(self, event_name, event):
        if _is_curve_transform_active(transform_state) and "joystick_y_main" in event_name:
            return
        return original_yaw_move(self, event_name, event)

    def guarded_strafe_move(self, event_name, event):
        if _is_curve_transform_active(transform_state) and "joystick_y_alt" in event_name:
            return
        return original_strafe_move(self, event_name, event)

    def update_proportional_cursor(self):
        original_cursor_update(self)
        ob = bpy.context.view_layer.objects.active
        if (
            ob is not None
            and ob.mode == "EDIT"
            and ob.type == "CURVE"
            and bpy.context.scene.tool_settings.use_proportional_edit
        ):
            self.sphere.style["visible"] = True

    def keyframe_curve_point(point):
        original_keyframe_point(point)
        point.keyframe_insert(data_path="tilt")
        point.keyframe_insert(data_path="radius")
        if hasattr(point, "handle_left"):
            point.keyframe_insert(data_path="handle_left")
            point.keyframe_insert(data_path="handle_right")

    registry.replace_attribute(transform_common, "on_transform_edit_curve", on_transform_edit_curve)
    registry.replace_attribute(transform_module, "on_transform_edit_curve", on_transform_edit_curve)
    registry.replace_attribute(transform_trigger, "on_transform_edit_curve", on_transform_edit_curve)

    registry.replace_attribute(transform_common, "on_joystick_vertical", guarded_proportional_joystick)
    registry.replace_attribute(transform_module, "on_joystick_vertical", guarded_proportional_joystick)
    registry.replace_attribute(transform_trigger, "on_joystick_vertical", guarded_proportional_joystick)
    registry.replace_listener(root, "joystick_y_main_press", original_joystick, guarded_proportional_joystick)
    registry.add_listener(root, "joystick_y_main_press", on_curve_radius_joystick)

    registry.replace_attribute(navigate, "on_yaw_move", guarded_yaw_move)
    registry.replace_attribute(navigate, "on_strafe_move", guarded_strafe_move)
    registry.replace_listener(root, "joystick_y_main_press", original_yaw_move, guarded_yaw_move)
    registry.replace_listener(root, "joystick_y_alt_press", original_strafe_move, guarded_strafe_move)
    registry.replace_attribute(
        proportional_edit_cursor.ProportionalEditSphere,
        "update",
        update_proportional_cursor,
    )
    registry.replace_attribute(auto_keyframe_transforms, "add_edit_nurbs_keyframe", keyframe_curve_point)
