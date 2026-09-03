import argparse
import ast
import json
from pathlib import Path


EXPECTED_VERSION = (2, 14, 2)
EXPECTED_COMMIT = "dd3cb84"

REQUIRED_SYMBOLS = {
    "freebird/api.py": {"add_launcher_button", "remove_launcher_button"},
    "freebird/gizmos/auto_keyframe_transforms.py": {"add_edit_nurbs_keyframe"},
    "freebird/gizmos/proportional_edit_cursor.py": {"ProportionalEditSphere"},
    "freebird/tools/draw_stroke.py": {"NURBSCurve"},
    "freebird/tools/erase.py": {"on_erase_edit_curve"},
    "freebird/tools/select.py": {"get_selection_state", "toggle_edit_curve_selections"},
    "freebird/tools/transform_common.py": {
        "get_selected_elements",
        "on_joystick_vertical",
        "on_transform_edit_curve",
    },
    "freebird/tools/__init__.py": {"_get_modules", "disable_tool", "enable_tool"},
    "freebird/utils/selection_utils.py": {"set_select_state", "set_select_state_all"},
    "freebird/navigate.py": {"on_strafe_move", "on_yaw_move"},
    "bl_xr/events/bind_and_dispatch.py": {"remove_dead_subtargets"},
    "bl_xr/utils/intersection_utils.py": {"intersects_edit_curve"},
}


def top_level_symbols(source_path):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def top_level_function_parameters(source_path, function_name):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
        ),
        None,
    )
    if function is None:
        return set()
    return {
        argument.arg
        for argument in (*function.args.args, *function.args.kwonlyargs)
    }


def verify(root):
    version_path = root / "version.json"
    version_data = json.loads(version_path.read_text(encoding="utf-8"))
    version = tuple(version_data["version"])
    commit = version_data["commit"]
    if version != EXPECTED_VERSION or commit != EXPECTED_COMMIT:
        raise RuntimeError(
            f"expected Freebird {EXPECTED_VERSION}/{EXPECTED_COMMIT}, found {version}/{commit}"
        )

    for relative_path, expected in REQUIRED_SYMBOLS.items():
        source_path = root / relative_path
        if not source_path.is_file():
            raise RuntimeError(f"missing Freebird source file: {source_path}")
        missing = expected - top_level_symbols(source_path)
        if missing:
            raise RuntimeError(f"missing symbols in {source_path}: {sorted(missing)}")

    api_path = root / "freebird/api.py"
    if "icon" not in top_level_function_parameters(api_path, "add_launcher_button"):
        raise RuntimeError("Freebird add_launcher_button no longer accepts the icon parameter")

    print(f"FREEBIRD_SOURCE_OK version={'.'.join(map(str, version))} commit={commit}")
    print(f"FREEBIRD_ROOT={root}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("freebird_root", type=Path)
    args = parser.parse_args()
    verify(args.freebird_root.resolve())


if __name__ == "__main__":
    main()
