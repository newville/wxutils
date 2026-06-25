import wx
from dataclasses import dataclass
from typing import Optional


@dataclass
class ColorTheme:
    """Terminal-style color theme that drives all flat widget colors.

    Modelled on the standard 16-color palette so any theme
    (Tokyo Night, Solarized, Dracula, ...) maps directly.

    Widgets mappings, e.g.:
      background       -> widget surface
      bright_black     -> elevated surface, disabled bg, border
      foreground       -> primary text
      white            -> secondary text
      blue             -> accent / highlight / selection
      bright_blue      -> accent hover
      red              -> danger / error
      green            -> success / progress fill
      bright_black     -> comment fg in editor
      ...
    """

    # base
    foreground: wx.Colour
    background: wx.Colour

    # cursor (also used for inverted text in selections)
    cursor_fg: wx.Colour
    cursor_bg: wx.Colour

    # selection
    selection_fg: wx.Colour
    selection_bg: wx.Colour

    # normal
    black: wx.Colour
    red: wx.Colour
    green: wx.Colour
    yellow: wx.Colour
    blue: wx.Colour
    magenta: wx.Colour
    cyan: wx.Colour
    white: wx.Colour

    # bright
    bright_black: wx.Colour
    bright_red: wx.Colour
    bright_green: wx.Colour
    bright_yellow: wx.Colour
    bright_blue: wx.Colour
    bright_magenta: wx.Colour
    bright_cyan: wx.Colour
    bright_white: wx.Colour


def light_theme() -> ColorTheme:
    """Built-in light ColorTheme."""
    return ColorTheme(
        foreground=wx.Colour(30, 30, 30),
        background=wx.Colour(240, 240, 230),
        cursor_fg=wx.Colour(240, 240, 230),
        cursor_bg=wx.Colour(30, 30, 30),
        selection_fg=wx.Colour(30, 30, 30),
        selection_bg=wx.Colour(165, 205, 255),
        black=wx.Colour(255, 255, 255),
        red=wx.Colour(200, 30, 30),
        green=wx.Colour(10, 140, 10),
        yellow=wx.Colour(160, 120, 10),
        blue=wx.Colour(70, 100, 220),
        magenta=wx.Colour(120, 0, 120),
        cyan=wx.Colour(0, 100, 160),
        white=wx.Colour(150, 150, 140),
        bright_black=wx.Colour(215, 215, 205),
        bright_red=wx.Colour(200, 30, 30),
        bright_green=wx.Colour(30, 160, 30),
        bright_yellow=wx.Colour(200, 160, 40),
        bright_blue=wx.Colour(100, 130, 240),
        bright_magenta=wx.Colour(140, 30, 140),
        bright_cyan=wx.Colour(0, 130, 190),
        bright_white=wx.Colour(255, 255, 255),
    )


def dark_theme() -> ColorTheme:
    """Built-in dark ColorTheme."""
    return ColorTheme(
        foreground=wx.Colour(255, 255, 255),
        background=wx.Colour(20, 20, 20),
        cursor_fg=wx.Colour(20, 20, 20),
        cursor_bg=wx.Colour(255, 255, 255),
        selection_fg=wx.Colour(255, 255, 255),
        selection_bg=wx.Colour(49, 79, 120),
        black=wx.Colour(15, 16, 30),
        red=wx.Colour(240, 120, 120),
        green=wx.Colour(120, 240, 120),
        yellow=wx.Colour(224, 175, 104),
        blue=wx.Colour(120, 120, 250),
        magenta=wx.Colour(187, 154, 247),
        cyan=wx.Colour(125, 207, 255),
        white=wx.Colour(169, 177, 214),
        bright_black=wx.Colour(65, 72, 104),
        bright_red=wx.Colour(247, 118, 142),
        bright_green=wx.Colour(158, 206, 106),
        bright_yellow=wx.Colour(224, 175, 104),
        bright_blue=wx.Colour(53, 134, 255),
        bright_magenta=wx.Colour(187, 154, 247),
        bright_cyan=wx.Colour(125, 207, 255),
        bright_white=wx.Colour(192, 202, 245),
    )


_ACTIVE_THEME: Optional[ColorTheme] = None


def set_theme(theme: ColorTheme) -> None:
    """Set the global ColorTheme used by all flat widgets."""
    global _ACTIVE_THEME
    _ACTIVE_THEME = theme


def get_theme() -> ColorTheme:
    """Return the active ColorTheme."""
    if _ACTIVE_THEME is not None:
        return _ACTIVE_THEME
    from .colors import is_dark_theme
    return dark_theme() if is_dark_theme() else light_theme()
