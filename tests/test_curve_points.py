import math
import sys
import types
import unittest


class Vector:
    def __init__(self, values=()):
        if isinstance(values, Vector):
            values = values.values
        self.values = [float(value) for value in values]

    def __getitem__(self, index):
        return self.values[index]

    def __iter__(self):
        return iter(self.values)

    def __add__(self, other):
        return Vector(a + b for a, b in zip(self, other))

    def __sub__(self, other):
        return Vector(a - b for a, b in zip(self, other))

    def __mul__(self, scalar):
        return Vector(value * scalar for value in self)

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]

    @property
    def z(self):
        return self.values[2]

    @property
    def length_squared(self):
        return sum(value * value for value in self)

    @property
    def length(self):
        return math.sqrt(self.length_squared)

    def normalize(self):
        length = self.length
        self.values = [value / length for value in self]

    def to_tuple(self):
        return tuple(self.values)


fake_mathutils = types.ModuleType("mathutils")
fake_mathutils.Vector = Vector
sys.modules.setdefault("mathutils", fake_mathutils)

from freebird_curve_editor.curve_points import (  # noqa: E402
    build_falloff_entries,
    capture_point_tangents,
    iter_curve_points,
    point_key,
    point_world_tangent,
)


class IdentityMatrix:
    def __matmul__(self, value):
        return Vector(value)

    def to_3x3(self):
        return self


class Point:
    _next_id = 1

    def __init__(self, x, y, z):
        self.co = [x, y, z, 1.0]
        self.hide = False
        self.select = False
        self.radius = 1.0
        self.tilt = 0.0
        self._id = Point._next_id
        Point._next_id += 1

    def as_pointer(self):
        return self._id


class Spline:
    def __init__(self, points, cyclic=False):
        self.type = "NURBS"
        self.points = points
        self.use_cyclic_u = cyclic


class Curve:
    def __init__(self, splines):
        self.splines = splines


class CurveObject:
    def __init__(self, splines):
        self.data = Curve(splines)
        self.matrix_world = IdentityMatrix()


class CurvePointTests(unittest.TestCase):
    def test_iterates_every_spline(self):
        first = Spline([Point(0, 0, 0), Point(1, 0, 0)])
        second = Spline([Point(2, 0, 0)])
        curve = Curve([first, second])
        self.assertEqual(len(list(iter_curve_points(curve))), 3)

    def test_connected_falloff_does_not_cross_splines(self):
        selected = Point(0, 0, 0)
        neighbor = Point(1, 0, 0)
        other_spline = Point(0.25, 0, 0)
        ob = CurveObject([Spline([selected, neighbor]), Spline([other_spline])])

        entries = build_falloff_entries(ob, [selected], 2.0, "LINEAR", connected=True)
        self.assertAlmostEqual(entries[point_key(neighbor)][1], 0.5)
        self.assertNotIn(point_key(other_spline), entries)

    def test_tangent_uses_both_neighbors(self):
        left = Point(0, 0, 0)
        center = Point(1, 0, 0)
        right = Point(2, 1, 0)
        ob = CurveObject([Spline([left, center, right])])

        tangent = point_world_tangent(ob, center)
        expected_length = math.sqrt(5.0)
        self.assertAlmostEqual(tangent.x, 2.0 / expected_length)
        self.assertAlmostEqual(tangent.y, 1.0 / expected_length)

    def test_captured_tangent_does_not_flip_when_endpoint_crosses_neighbor(self):
        endpoint = Point(0, 0, 0)
        neighbor = Point(1, 0, 0)
        ob = CurveObject([Spline([endpoint, neighbor])])
        key = point_key(endpoint)

        captured = capture_point_tangents(ob, {key: (endpoint, 1.0)})
        endpoint.co[:3] = [2.0, 0.0, 0.0]
        live = point_world_tangent(ob, endpoint)

        self.assertAlmostEqual(captured[key].x, 1.0)
        self.assertAlmostEqual(live.x, -1.0)


if __name__ == "__main__":
    unittest.main()
