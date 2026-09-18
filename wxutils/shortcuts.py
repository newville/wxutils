"""
Create platform-native application shortcuts.

Application icons must be named after the application slug:
    <slug>.icns - macOS
    <slug>.ico  - Windows
    <slug>.png  - Linux
"""

import sys
from pathlib import Path

from pyshortcuts import make_shortcut, uname


def create_shortcut(app_config, public=False, folder=None):
    """Create a platform-native application shortcut."""
    extension = {"darwin": "icns", "win": "ico"}.get(uname, "png")
    icon = app_config.icon_path(extension)

    if uname == "win":
        script = Path(sys.prefix, "Scripts", f"{app_config.slug}.exe")
    else:
        script = Path(sys.prefix, "bin", app_config.slug)

    if not script.is_file():
        raise FileNotFoundError(f"Application launcher was not found: {script}!")

    platform_opts = {}
    if uname == "darwin":
        platform_opts["macos_app"] = True
        platform_opts["desktop"] = False

    return make_shortcut(
        str(script),
        name=app_config.name,
        description=app_config.description or app_config.name,
        icon=str(icon),
        terminal=False,
        public=public,
        folder=folder,
        **platform_opts,
    )
