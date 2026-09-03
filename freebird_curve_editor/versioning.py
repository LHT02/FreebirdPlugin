import json
from pathlib import Path

from .constants import SUPPORTED_FREEBIRD_COMMIT, SUPPORTED_FREEBIRD_VERSION


def read_freebird_version():
    import freebird

    version_path = Path(freebird.__file__).resolve().parent.parent / "version.json"
    with version_path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    return tuple(data["version"]), data["commit"], version_path


def require_supported_freebird():
    version, commit, version_path = read_freebird_version()
    if version != SUPPORTED_FREEBIRD_VERSION or commit != SUPPORTED_FREEBIRD_COMMIT:
        expected = ".".join(str(part) for part in SUPPORTED_FREEBIRD_VERSION)
        actual = ".".join(str(part) for part in version)
        raise RuntimeError(
            f"Freebird Curve Editor requires Freebird {expected}/{SUPPORTED_FREEBIRD_COMMIT}, "
            f"but found {actual}/{commit} at {version_path}"
        )
    return version, commit
