import sys
import types
import unittest
from unittest.mock import patch

from test_curve_points import fake_mathutils

sys.modules.setdefault("mathutils", fake_mathutils)

from freebird_curve_editor.constants import ADD_POINT_TOOL  # noqa: E402
from freebird_curve_editor.patches import add_point_tool  # noqa: E402
from freebird_curve_editor.patching import PatchRegistry  # noqa: E402


class AddPointToolRegistrationTests(unittest.TestCase):
    def test_custom_tool_resolves_without_changing_existing_tools(self):
        select_module = object()
        tools = types.SimpleNamespace(
            _get_modules=lambda tool_name: [select_module] if tool_name == "select" else None,
        )
        freebird = types.ModuleType("freebird")
        freebird.tools = tools
        registry = PatchRegistry()

        with patch.dict(sys.modules, {"freebird": freebird}):
            add_point_tool.install(registry)
            self.assertEqual(tools._get_modules(ADD_POINT_TOOL), [add_point_tool])
            self.assertEqual(tools._get_modules("select"), [select_module])
            registry.restore()

        self.assertEqual(tools._get_modules("select"), [select_module])
        self.assertIsNone(tools._get_modules(ADD_POINT_TOOL))


if __name__ == "__main__":
    unittest.main()
