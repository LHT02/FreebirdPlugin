import struct
import unittest
from pathlib import Path

from freebird_curve_editor.icon_paths import launcher_icon


class LauncherIconTests(unittest.TestCase):
    def test_every_launcher_icon_is_an_absolute_png(self):
        paths = [
            launcher_icon("draw"),
            launcher_icon("edit"),
            launcher_icon("add_point"),
            launcher_icon("falloff", True),
            launcher_icon("falloff", False),
            launcher_icon("radius_down"),
            launcher_icon("radius_value"),
            launcher_icon("radius_up"),
        ]
        for value in paths:
            path = Path(value)
            self.assertTrue(path.is_absolute())
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.suffix.lower(), ".png")

    def test_icons_are_128_pixel_rgba_pngs(self):
        for name in ("draw", "edit", "add_point", "radius_down", "radius_value", "radius_up"):
            data = Path(launcher_icon(name)).read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
            self.assertEqual((width, height, bit_depth, color_type), (128, 128, 8, 6))
