from mathutils import Vector

from ..constants import (
    ADD_POINT_DRAG_THRESHOLD,
    ADD_POINT_ENDPOINT_MARGIN,
    ADD_POINT_HIT_RADIUS_MIN,
    ADD_POINT_MIN_SPACING,
    ADD_POINT_TOOL,
)
from ..curve_segments import find_nearest_segment, subdivide_segment
from ..state import runtime


def _active_edit_curve():
    import bpy

    ob = bpy.context.view_layer.objects.active
    if ob is None or ob.type != "CURVE" or ob.mode != "EDIT":
        return None
    return ob


def _viewer_scale():
    from bl_xr import xr_session

    return max(1.0e-6, float(xr_session.viewer_scale))


def _hit_radius():
    import bl_xr

    scale = _viewer_scale()
    return max(float(bl_xr.selection_size) * scale, ADD_POINT_HIT_RADIUS_MIN * scale)


def on_add_point_start(_, event_name, event):
    runtime.reset_add_point()
    if _active_edit_curve() is None or event.position is None:
        return
    runtime.add_point_start_position = Vector(event.position)


def on_add_point_press(_, event_name, event):
    ob = _active_edit_curve()
    if ob is None or runtime.add_point_start_position is None or event.position is None:
        return

    position = Vector(event.position)
    scale = _viewer_scale()
    hit_radius = _hit_radius()
    drag_threshold = max(ADD_POINT_DRAG_THRESHOLD * scale, hit_radius * 0.25)
    if (position - runtime.add_point_start_position).length < drag_threshold:
        return

    hit = find_nearest_segment(ob, position, hit_radius, endpoint_margin=ADD_POINT_ENDPOINT_MARGIN)
    if hit is None:
        return

    spacing = max(ADD_POINT_MIN_SPACING * scale, hit_radius * 0.75)
    if (
        runtime.add_point_last_position is not None
        and (hit.world_position - runtime.add_point_last_position).length < spacing
    ):
        return

    event.stop_propagation = True
    inserted = subdivide_segment(ob, hit)
    if inserted is None:
        return

    runtime.add_point_last_position = Vector(hit.world_position)
    runtime.add_point_count += 1
    runtime.reset_transform()


def on_add_point_end(_, event_name, event):
    if runtime.add_point_count:
        from freebird.utils import log

        log.info(f"Curve Editor: added {runtime.add_point_count} control point(s)")
    runtime.reset_add_point()


def enable_tool():
    from bl_xr import root

    root.add_event_listener("trigger_main_start", on_add_point_start)
    root.add_event_listener("trigger_main_press", on_add_point_press)
    root.add_event_listener("trigger_main_end", on_add_point_end)


def disable_tool():
    from bl_xr import root

    root.remove_event_listener("trigger_main_start", on_add_point_start)
    root.remove_event_listener("trigger_main_press", on_add_point_press)
    root.remove_event_listener("trigger_main_end", on_add_point_end)
    runtime.reset_add_point()


def install(registry):
    from freebird import tools

    original_get_modules = tools._get_modules

    def get_modules(tool_name):
        if tool_name == ADD_POINT_TOOL:
            return [__import__(__name__, fromlist=["enable_tool"])]
        return original_get_modules(tool_name)

    registry.replace_attribute(tools, "_get_modules", get_modules)


def deactivate():
    from freebird import tools

    if tools.active_tool == ADD_POINT_TOOL:
        tools.disable_tool(ADD_POINT_TOOL)
