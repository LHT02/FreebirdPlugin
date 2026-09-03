from . import commands
from .patches import drawing, interaction, multi_spline
from .patching import PatchRegistry
from .state import runtime
from .versioning import require_supported_freebird

_registry = None


def register_plugin():
    global _registry
    if _registry is not None:
        return

    from freebird.utils import log

    version, commit = require_supported_freebird()
    registry = PatchRegistry()
    try:
        multi_spline.install(registry)
        drawing.install(registry)
        interaction.install(registry)
        commands.refresh_buttons()
    except Exception:
        commands.unregister_buttons()
        registry.restore()
        runtime.reset()
        raise

    _registry = registry
    log.info(
        "Freebird Curve Editor loaded for Freebird "
        + ".".join(str(part) for part in version)
        + f"/{commit}"
    )


def unregister_plugin():
    global _registry
    commands.unregister_buttons()
    if _registry is not None:
        _registry.restore()
        _registry = None
    runtime.reset()
