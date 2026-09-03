from ..state import runtime


def _valid_target():
    import bpy

    target = runtime.draw_target
    try:
        return target if target is not None and target.type == "CURVE" and target.name in bpy.data.objects else None
    except ReferenceError:
        return None


def install(registry):
    from mathutils import Vector
    from freebird import tools
    from freebird.settings_manager import settings
    from freebird.tools import draw_stroke
    from freebird.utils import ui_utils

    original_curve_class = draw_stroke.NURBSCurve
    original_enable_tool = tools.enable_tool

    class ActiveObjectCurveStroke(original_curve_class):
        def _local_position(self, world_position):
            target = _valid_target()
            return target.matrix_world.inverted() @ Vector(world_position)

        def _radius(self, pressure):
            if settings["stroke.fixed_thickness"]:
                return runtime.draw_radius
            return max(0.0, pressure) * runtime.draw_radius

        def start(self, stroke_pt, pressure):
            target = _valid_target()
            if not runtime.draw_into_active_curve or target is None:
                runtime.draw_into_active_curve = False
                return super().start(stroke_pt, pressure)

            local_point = self._local_position(stroke_pt)
            pressure = self._radius(pressure)
            self.point_co_size = 4
            self.extended_stroke = False
            self._reversed_for_extend = False
            self.cu = target.data
            spline_type = "POLY" if settings["stroke.straight_line"] else "NURBS"
            self.curve = self.cu.splines.new(spline_type)
            self.update_pt(local_point, pressure)

            if settings["stroke.straight_line"]:
                self.add_pt()
                self.update_pt(local_point, pressure)
                return

            for _ in range(4):
                self.add_pt()
                self.update_pt(local_point, pressure)

        def stroke(self, stroke_pt, pressure):
            target = _valid_target()
            if not runtime.draw_into_active_curve or target is None:
                return super().stroke(stroke_pt, pressure)

            stroke_pt = self._local_position(stroke_pt)
            pressure = self._radius(pressure)
            if not settings["stroke.straight_line"]:
                point = Vector(self.curve.points[-1].co[:-1])
                point_world = target.matrix_world @ point
                previous_world = target.matrix_world @ self.prev_pt
                distance = (point_world - previous_world).length
                distance /= draw_stroke.xr_session.viewer_scale
                direction_change = self.is_direction_change(stroke_pt)
                if distance > settings["stroke.min_stroke_distance"] or direction_change:
                    self.add_pt()
                self.update_pt(stroke_pt, pressure, index=-3)
                self.update_pt(stroke_pt, pressure, index=-2)

            self.update_pt(stroke_pt, pressure, index=-1)

    def enable_tool(tool_name):
        if tool_name != "draw.stroke":
            runtime.draw_into_active_curve = False
        return original_enable_tool(tool_name)

    registry.replace_attribute(draw_stroke, "NURBSCurve", ActiveObjectCurveStroke)
    registry.replace_attribute(tools, "enable_tool", enable_tool)
    registry.replace_attribute(ui_utils, "enable_tool", enable_tool)
