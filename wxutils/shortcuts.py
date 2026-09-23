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

def create_shortcut(app_config, public=False, folder=None, desktop=None, macos_app=True):
    """Create a platform-native application shortcut."""
    extension = {"darwin": "icns", "win": "ico"}.get(uname, "png")
    icon = app_config.icon_path(extension)

    if uname == "win":
        script = Path(sys.prefix, "Scripts", f"{app_config.slug}.exe")
    else:
        script = Path(sys.prefix, "bin", app_config.slug)

    if not script.is_file():
        raise FileNotFoundError(f"Application launcher was not found: {script}!")

    if desktop is None:
        desktop = (uname != 'darwin')

    return make_shortcut(
        str(script),
        name=app_config.name,
        description=app_config.description or app_config.name,
        icon=str(icon),
        terminal=False,
        public=public,
        folder=folder,
        desktop=desktop,
        macos_app=(uname=='darwin'))
    )


def add_shortcut_arguments(parser):
    """Adds shortcut options to an argument parser."""
    group = parser.add_argument_group("shortcut options")
    group.add_argument("-m", "--make-icon", action="store_true", help="create an application shortcut")
    group.add_argument("-p", "--public", action="store_true", help="create the shortcut for all users")
    group.add_argument("-f", "--folder", nargs="?", help="optional shortcut subfolder")
    return parser


def handle_shortcut_arguments(parser, args, app_config):
    """Handles the shortcut arguments and returns true if a shortcut was created."""
    if args.public and not args.make_icon:
        parser.error("-p/--public requires -m/--make-icon flag")

    if args.folder and not args.make_icon:
        parser.error("-f/--folder requires -m/--make-icon flag")

    if not args.make_icon:
        return False

    create_shortcut(app_config, public=args.public, folder=args.folder)

    return True
