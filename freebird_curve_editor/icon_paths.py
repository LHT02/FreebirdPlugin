from pathlib import Path


_ICON_ROOT = Path(__file__).resolve().parent / "assets" / "icons"

_BUTTON_ICON_NAMES = {
    "draw": "draw_in.png",
    "edit": "edit_curve.png",
    "add_point": "add_point.png",
    "falloff_on": "falloff_on.png",
    "falloff_off": "falloff_off.png",
    "radius_down": "radius_down.png",
    "radius_value": "radius_value.png",
    "radius_up": "radius_up.png",
}


def launcher_icon(button_id, falloff_enabled=False):
    icon_id = f"falloff_{'on' if falloff_enabled else 'off'}" if button_id == "falloff" else button_id
    return str((_ICON_ROOT / _BUTTON_ICON_NAMES[icon_id]).resolve())
