from ..curve_points import (
    curve_contains_point,
    iter_curve_points,
    point_is_hidden,
    point_is_selected,
    point_position,
    set_point_selected,
)


def install(registry):
    import bpy
    import importlib
    import bl_xr.utils as bl_xr_utils
    import freebird.utils as freebird_utils
    from bl_xr.utils import intersection_utils
    from freebird.tools import erase as erase_module
    from freebird.tools import select as select_module
    from freebird.tools import transform as transform_module
    from freebird.tools import transform_common
    from freebird.tools import transform_trigger
    from freebird.utils import selection_utils

    bind_and_dispatch = importlib.import_module("bl_xr.events.bind_and_dispatch")

    original_remove_dead = bind_and_dispatch.remove_dead_subtargets
    original_set_all = selection_utils.set_select_state_all
    original_set = selection_utils.set_select_state
    original_selection_state = select_module.get_selection_state
    original_selected_elements = transform_common.get_selected_elements

    def intersects_edit_curve(ob, center, shape, size):
        intersections = []
        for _, _, point in iter_curve_points(ob.data):
            if point_is_hidden(point):
                continue
            world_position = ob.matrix_world @ point_position(point)
            if (world_position - center).length <= size:
                intersections.append(point)
        return intersections or None

    def remove_dead_subtargets(ob, sub_targets):
        if not sub_targets:
            return None
        if isinstance(ob, bpy.types.Object) and ob.type == "CURVE":
            valid = {point for point in sub_targets if curve_contains_point(ob.data, point)}
            return valid or None
        return original_remove_dead(ob, sub_targets)

    def set_select_state_all(state):
        ob = bpy.context.view_layer.objects.active
        if ob is not None and ob.mode in ("EDIT", "POSE") and ob.type == "CURVE":
            for _, _, point in iter_curve_points(ob.data):
                set_point_selected(point, state)
            return None
        return original_set_all(state)

    def set_select_state(elements, state):
        ob = bpy.context.view_layer.objects.active
        if ob is not None and ob.mode in ("EDIT", "POSE") and ob.type == "CURVE":
            for point in elements:
                set_point_selected(point, state)
            return None
        return original_set(elements, state)

    def get_selection_state():
        ob = bpy.context.view_layer.objects.active
        if ob is not None and ob.mode in ("EDIT", "POSE") and ob.type == "CURVE":
            return select_module.np.array(
                [point_is_selected(point) for _, _, point in iter_curve_points(ob.data)], dtype=bool
            )
        return original_selection_state()

    def toggle_edit_curve_selections(event):
        if event.sub_targets is None:
            return
        for point in event.sub_targets:
            if point in select_module.elements_toggled_this_selection:
                continue
            set_point_selected(point, not point_is_selected(point))
            select_module.elements_toggled_this_selection.add(point)

    def get_selected_elements(elements=None, active_ob=None):
        ob = bpy.context.view_layer.objects.active if active_ob is None else active_ob
        if ob is not None and ob.mode == "EDIT" and ob.type == "CURVE":
            candidates = elements
            if candidates is None:
                candidates = [point for _, _, point in iter_curve_points(ob.data)]
            return {point for point in candidates if point_is_selected(point)}
        return original_selected_elements(elements, active_ob)

    def on_erase_edit_curve(self, event_name, event):
        event.stop_propagation = True
        for _, _, point in iter_curve_points(self.data):
            set_point_selected(point, False)
        for point in event.sub_targets or ():
            set_point_selected(point, True)
        bpy.ops.curve.delete(type="VERT")
        erase_module.has_erased_elements = True

    registry.replace_attribute(intersection_utils, "intersects_edit_curve", intersects_edit_curve)
    registry.replace_attribute(bl_xr_utils, "intersects_edit_curve", intersects_edit_curve)
    registry.replace_attribute(bind_and_dispatch, "remove_dead_subtargets", remove_dead_subtargets)

    registry.replace_attribute(selection_utils, "set_select_state_all", set_select_state_all)
    registry.replace_attribute(selection_utils, "set_select_state", set_select_state)
    registry.replace_attribute(freebird_utils, "set_select_state_all", set_select_state_all)
    registry.replace_attribute(freebird_utils, "set_select_state", set_select_state)
    registry.replace_attribute(select_module, "set_select_state_all", set_select_state_all)
    registry.replace_attribute(select_module, "get_selection_state", get_selection_state)
    registry.replace_attribute(select_module, "toggle_edit_curve_selections", toggle_edit_curve_selections)

    registry.replace_attribute(transform_common, "get_selected_elements", get_selected_elements)
    registry.replace_attribute(transform_module, "get_selected_elements", get_selected_elements)
    registry.replace_attribute(transform_trigger, "get_selected_elements", get_selected_elements)
    registry.replace_attribute(transform_module, "set_select_state", set_select_state)
    registry.replace_attribute(transform_trigger, "set_select_state", set_select_state)
    registry.replace_attribute(erase_module, "on_erase_edit_curve", on_erase_edit_curve)
