"""
Reusable wx application configuration
"""

import ctypes
import re
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

import wx
from pyshortcuts import uname

from .utils import SetAppDisplayName, SetDockIcon


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Configuration for a wx application."""

    name: str
    assets: str
    description: str | None = None
    application_id: str | None = None

    @property
    def slug(self):
        """Returns a filesystem and command safe application name."""
        return re.sub(r"[^a-z0-9]+", "-", self.name.casefold()).strip("-")

    @property
    def assets_path(self):
        """Returns the validated assets directory."""
        if not self.assets.strip():
            raise ValueError("Assets directory can't be empty.")

        path = Path(self.assets).expanduser().resolve()
        if not path.is_dir():
            raise FileNotFoundError(f"Assets directory wasn't found: {path}.")

        return path

    def icon_path(self, extension):
        """Returns a validated platform specific icon."""
        icon = self.assets_path / f"{self.slug}.{extension}"

        if not icon.is_file():
            raise FileNotFoundError(f"Application icon was not found: {icon}.")

        return icon


class WxApplication(wx.App):
    """Configures and runs a wx application."""

    def __init__(self, app_config: AppConfig, *args, **kwargs):
        self.app_config = app_config
        self._configure_windows()
        super().__init__(*args, **kwargs)

    def OnInit(self):
        """Configure the application during wx initialization."""
        SetAppDisplayName(self.app_config.name)

        if uname == "darwin":
            SetDockIcon(self.app_config.icon_path("icns"))

        return True

    def run(self, window):
        """Displays the main application window and starts the main event loop."""
        self._set_window_icon(window)
        self.SetTopWindow(window)
        window.Show()
        wx.CallAfter(self._activate_window, window)

        self.MainLoop()

    def _configure_windows(self):
        """Configures Windows identity and DPI awareness."""
        if uname != "win":
            return

        if self.app_config.application_id:
            with suppress(Exception):
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.app_config.application_id)

        try:
            wx.App.SetDPIAwareness(wx.DPI_AWARENESS_CTX_PER_MONITOR_AWARE_V2)
        except AttributeError:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)

    @staticmethod
    def _activate_window(window):
        """Activates and raises the main application window."""
        if uname == "darwin":
            with suppress(Exception):
                from AppKit import NSApplication

                NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

        window.Raise()
