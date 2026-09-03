import sys
import types
import unittest
from unittest.mock import patch

from test_curve_points import CurveObject, Point, Spline, Vector, fake_mathutils

sys.modules.setdefault("mathutils", fake_mathutils)

from freebird_curve_editor.curve_segments import (  # noqa: E402
    SegmentHit,
    find_nearest_segment,
    inserted_point_index,
    segment_indices,
    subdivide_segment,
)


class InvertibleIdentityMatrix:
    def __matmul__(self, value):
        return Vector(value)

    def inverted(self):
        return self

    def to_3x3(self):
        return self


class CurveSegmentTests(unittest.TestCase):
    def test_open_and_cyclic_segment_indices(self):
        points = [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0)]
        self.assertEqual(list(segment_indices(Spline(points))), [(0, 1), (1, 2)])
        self.assertEqual(list(segment_indices(Spline(points, cyclic=True))), [(0, 1), (1, 2), (2, 0)])

    def test_finds_nearest_segment_across_splines(self):
        far = Spline([Point(0, 2, 0), Point(2, 2, 0)])
        near = Spline([Point(0, 0, 0), Point(2, 0, 0)])
        ob = CurveObject([far, near])
        ob.matrix_world = InvertibleIdentityMatrix()

        hit = find_nearest_segment(ob, (0.75, 0.05, 0), 0.1)

        self.assertIsNotNone(hit)
        self.assertEqual(hit.spline_index, 1)
        self.assertAlmostEqual(hit.factor, 0.375)
        self.assertAlmostEqual(hit.world_position.x, 0.75)

    def test_endpoint_margin_prevents_duplicate_points(self):
        ob = CurveObject([Spline([Point(0, 0, 0), Point(1, 0, 0)])])
        ob.matrix_world = InvertibleIdentityMatrix()
        self.assertIsNone(find_nearest_segment(ob, (0.02, 0, 0), 0.1, endpoint_margin=0.08))

    def test_hidden_segment_is_ignored(self):
        start = Point(0, 0, 0)
        start.hide = True
        ob = CurveObject([Spline([start, Point(1, 0, 0)])])
        ob.matrix_world = InvertibleIdentityMatrix()
        self.assertIsNone(find_nearest_segment(ob, (0.5, 0, 0), 0.1))

    def test_inserted_index_follows_open_and_cyclic_segment_order(self):
        open_hit = SegmentHit(0, 1, 2, 0.5, 0.0, None, None)
        cyclic_hit = SegmentHit(0, 3, 0, 0.5, 0.0, None, None)
        self.assertEqual(inserted_point_index(open_hit, 4), 2)
        self.assertEqual(inserted_point_index(cyclic_hit, 4), 4)

    def test_subdivide_places_and_selects_interpolated_point(self):
        start = Point(0, 0, 0)
        start.radius = 1.0
        start.tilt = 0.2
        end = Point(2, 0, 0)
        end.radius = 3.0
        end.tilt = 1.0
        spline = Spline([start, end])
        ob = CurveObject([spline])
        ob.data.update_tag = lambda: None

        other_point = Point(0, 3, 0)
        other_point.select = True
        other = CurveObject([Spline([other_point, Point(1, 3, 0)])])
        other.type = "CURVE"

        def subdivide(number_cuts):
            self.assertEqual(number_cuts, 1)
            self.assertTrue(start.select and end.select)
            inserted = Point(1, 0, 0)
            spline.points.insert(1, inserted)
            return {"FINISHED"}

        fake_bpy = types.SimpleNamespace(
            context=types.SimpleNamespace(objects_in_mode_unique_data=[ob, other]),
            ops=types.SimpleNamespace(curve=types.SimpleNamespace(subdivide=subdivide)),
        )
        hit = SegmentHit(0, 0, 1, 0.25, 0.0, Vector((0.5, 0, 0)), Vector((0.5, 0, 0)))

        with patch.dict(sys.modules, {"bpy": fake_bpy}):
            inserted = subdivide_segment(ob, hit)

        self.assertEqual(tuple(inserted.co[:3]), (0.5, 0.0, 0.0))
        self.assertAlmostEqual(inserted.radius, 1.5)
        self.assertAlmostEqual(inserted.tilt, 0.4)
        self.assertTrue(inserted.select)
        self.assertFalse(start.select or end.select)
        self.assertTrue(other_point.select)


if __name__ == "__main__":
    unittest.main()
