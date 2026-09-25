"""Keep user data outside executable bundles and source installations."""

from pathlib import Path
import os
import sys


PACKAGE_DIR = Path(__file__).resolve().parent


def data_directory() -> Path:
    if os.environ.get("KET_STUDIO_DATA_DIR"):
        path = Path(os.environ["KET_STUDIO_DATA_DIR"]).expanduser().resolve()
    elif sys.platform == "win32":
        path = (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
            / "KETWordStudio"
        )
    elif sys.platform == "darwin":
        path = Path.home() / "Library/Application Support/KETWordStudio"
    else:
        path = (
            Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
            / "KETWordStudio"
        )
    path.mkdir(parents=True, exist_ok=True)
    return path
