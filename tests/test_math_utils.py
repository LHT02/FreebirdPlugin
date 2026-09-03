import math
import unittest

from freebird_curve_editor.math_utils import falloff_weight, joystick_scale_factor, signed_twist_angle


class SignedTwistAngleTests(unittest.TestCase):
    def test_extracts_rotation_around_matching_axis(self):
        angle = math.pi / 2.0
        quaternion = (math.cos(angle / 2.0), math.sin(angle / 2.0), 0.0, 0.0)
        self.assertAlmostEqual(signed_twist_angle(quaternion, (1.0, 0.0, 0.0)), angle)

    def test_rejects_rotation_around_perpendicular_axis(self):
        angle = math.pi / 2.0
        quaternion = (math.cos(angle / 2.0), math.sin(angle / 2.0), 0.0, 0.0)
        self.assertAlmostEqual(signed_twist_angle(quaternion, (0.0, 1.0, 0.0)), 0.0)

    def test_preserves_negative_direction(self):
        angle = -math.pi / 3.0
        quaternion = (math.cos(angle / 2.0), 0.0, 0.0, math.sin(angle / 2.0))
        self.assertAlmostEqual(signed_twist_angle(quaternion, (0.0, 0.0, 1.0)), angle)


class JoystickScaleTests(unittest.TestCase):
    def test_deadzone_is_neutral(self):
        self.assertEqual(joystick_scale_factor(0.1, 1.0, 2.0, 0.15), 1.0)

    def test_opposite_inputs_are_reciprocal(self):
        up = joystick_scale_factor(1.0, 0.5, 2.0, 0.15)
        down = joystick_scale_factor(-1.0, 0.5, 2.0, 0.15)
        self.assertAlmostEqual(up * down, 1.0)


class FalloffTests(unittest.TestCase):
    def test_selected_point_has_full_weight(self):
        self.assertEqual(falloff_weight(0.0, 1.0, "SMOOTH"), 1.0)

    def test_point_at_radius_has_no_weight(self):
        self.assertEqual(falloff_weight(1.0, 1.0, "SMOOTH"), 0.0)

    def test_linear_midpoint(self):
        self.assertAlmostEqual(falloff_weight(0.5, 1.0, "LINEAR"), 0.5)


if __name__ == "__main__":
    unittest.main()
