from .constants import DRAW_RADIUS_MAX, DRAW_RADIUS_MIN, DRAW_RADIUS_STEP, PLUGIN_ID
from .icon_paths import launcher_icon
from .math_utils import clamp
from .state import runtime

_BUTTON_IDS = ("draw", "edit", "falloff", "radius_down", "radius_value", "radius_up")


def _log():
    from freebird.utils import log

    return log


def _active_or_target_curve():
    import bpy

    active = bpy.context.view_layer.objects.active
    if active is not None and active.type == "CURVE":
        return active
    target = runtime.draw_target
    try:
        if target is not None and target.type == "CURVE" and target.name in bpy.data.objects:
            return target
    except ReferenceError:
        pass
    return None


def activate_draw_mode():
    import bpy
    from freebird.settings_manager import settings
    from freebird.utils import set_mode, set_tool

    target = _active_or_target_curve()
    if target is None:
        _log().warning("Curve Editor: select a Curve object before entering DRAW mode")
        return

    if bpy.context.view_layer.objects.active is not target:
        bpy.context.view_layer.objects.active = target
    target.select_set(True)
    set_tool("select")
    if target.mode != "OBJECT" and not set_mode("OBJECT"):
        return
    if settings["stroke.type"] == "annotation":
        settings["stroke.type"] = "pen"
    settings["stroke.extend"] = False
    runtime.draw_target = target
    runtime.draw_into_active_curve = True
    set_tool("draw.stroke")
    _log().info(f"Curve Editor: drawing new splines into {target.name}; radius {runtime.draw_radius:.3f}x")


def activate_edit_mode():
    import bpy
    from freebird.utils import set_mode, set_tool

    target = _active_or_target_curve()
    if target is None:
        _log().warning("Curve Editor: no Curve object is available for EDIT mode")
        return

    runtime.draw_into_active_curve = False
    if bpy.context.view_layer.objects.active is not target:
        bpy.context.view_layer.objects.active = target
    target.select_set(True)
    set_tool("select")
    if target.mode != "EDIT":
        set_mode("EDIT")
    _log().info(f"Curve Editor: editing {target.name}")


def toggle_falloff():
    import bpy

    tool_settings = bpy.context.scene.tool_settings
    tool_settings.use_proportional_edit = not tool_settings.use_proportional_edit
    runtime.reset_transform()
    refresh_buttons()
    state = "enabled" if tool_settings.use_proportional_edit else "disabled"
    _log().info(f"Curve Editor: falloff {state}")


def decrease_draw_radius():
    runtime.draw_radius = clamp(runtime.draw_radius / DRAW_RADIUS_STEP, DRAW_RADIUS_MIN, DRAW_RADIUS_MAX)
    refresh_buttons()
    _log().info(f"Curve Editor: new spline radius {runtime.draw_radius:.3f}x")


def increase_draw_radius():
    runtime.draw_radius = clamp(runtime.draw_radius * DRAW_RADIUS_STEP, DRAW_RADIUS_MIN, DRAW_RADIUS_MAX)
    refresh_buttons()
    _log().info(f"Curve Editor: new spline radius {runtime.draw_radius:.3f}x")


def report_draw_radius():
    _log().info(f"Curve Editor: new spline radius {runtime.draw_radius:.3f}x")


def refresh_buttons():
    import bpy
    from freebird.api import add_launcher_button

    falloff_enabled = bpy.context.scene.tool_settings.use_proportional_edit
    falloff = "ON" if falloff_enabled else "OFF"
    entries = (
        ("draw", "DRAW IN", activate_draw_mode, launcher_icon("draw")),
        ("edit", "EDIT", activate_edit_mode, launcher_icon("edit")),
        ("falloff", f"FALLOFF {falloff}", toggle_falloff, launcher_icon("falloff", falloff_enabled)),
        ("radius_down", "RADIUS -", decrease_draw_radius, launcher_icon("radius_down")),
        ("radius_value", f"R {runtime.draw_radius:.2f}x", report_draw_radius, launcher_icon("radius_value")),
        ("radius_up", "RADIUS +", increase_draw_radius, launcher_icon("radius_up")),
    )
    for button_id, label, callback, icon in entries:
        add_launcher_button(PLUGIN_ID, button_id, label, callback, icon=icon)


def unregister_buttons():
    from freebird.api import remove_launcher_button

    for button_id in _BUTTON_IDS:
        remove_launcher_button(PLUGIN_ID, button_id)
