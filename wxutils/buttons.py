import wx

from typing import Callable, Optional

from .base import EnableControl
from .colors import register_darkdetect, default_color_scheme, default_disabled_scheme, ColorScheme, DisabledColorScheme


class Button(wx.Button):
    """Simple button with bound action
    b = Button(parent, label, action=None, **kws)

    """
    def __init__(self, parent: wx.Window, label: str, action: Optional[Callable] = None, **kws) -> None:
        super(Button, self).__init__(parent=parent, label=label, **kws)
        if action is not None:
            self.SetAction(action)

    def SetAction(self, action: Callable) -> None:
        self.Bind(wx.EVT_BUTTON, handler=action)

    def RemoveAction(self, action: Callable) -> None:
        self.Unbind(wx.EVT_BUTTON, handler=action)


class BitmapButton(wx.BitmapButton):
    def __init__(
        self, parent: wx.Window, bmp: wx.Bitmap, action: Optional[Callable] = None, tooltip: Optional[str] = None, size: tuple[int, int] = (20, 20), **kws
    ) -> None:
        bitmap_arg = wx.BitmapBundle.FromBitmap(bmp) if isinstance(bmp, wx.Bitmap) else bmp
        super(BitmapButton, self).__init__(parent=parent, id=-1, bitmap=bitmap_arg, size=wx.Size(size[0], size[1]), **kws)

        if action is not None:
            self.SetAction(action)
        if tooltip is not None:
            self.SetToolTip(tooltip)

    def SetAction(self, action: Callable) -> None:
        self.Bind(wx.EVT_BUTTON, handler=action)

    def RemoveAction(self, action: Callable) -> None:
        self.Unbind(wx.EVT_BUTTON, handler=action)


def ToggleButton(parent, label, action=None, tooltip=None,
                 size=(25, 25), **kws):
    b = wx.ToggleButton(parent, -1, label, size=size, **kws)
    if action is not None:
        b.Bind(wx.EVT_TOGGLEBUTTON, action)
    if tooltip is not None:
        b.SetToolTip(tooltip)
    return b


class FlatButton(EnableControl):
    """Flat custom-painted button with hover/press states and optional theme.

    parent: parent wx window
    label: button text
    action: optional callback accepting a wx.CommandEvent
    color_scheme: optional five-color tuple (idle_bg, hover_bg, press_bg, idle_fg, hover_fg)
    disabled_scheme: optional two-color tuple (disabled_bg, disabled_fg)
    font: optional wx.Font to use for the label
    corner_radius: rounded-rectangle corner radius in pixels (default 4)
    """

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        action: Optional[Callable[[wx.CommandEvent], None]] = None,
        color_scheme: Optional[ColorScheme] = None,
        disabled_scheme: Optional[DisabledColorScheme] = None,
        font: Optional[wx.Font] = None,
        corner_radius: int = 4,
        **kws,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE | wx.WANTS_CHARS, **kws)
        self._label = label
        self._hovered = False
        self._pressed = False
        self._font = font
        self._corner_radius = corner_radius

        self._custom_scheme: Optional[ColorScheme] = color_scheme
        self._custom_disabled: Optional[DisabledColorScheme] = disabled_scheme

        self._resolve_colors()

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, 26))

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)
        self.Bind(wx.EVT_LEFT_UP, self._on_release)

        if action is not None:
            self.SetAction(action)

        # Only register for automatic updates when using default colors.
        if color_scheme is None or disabled_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Bind action to EVT_BUTTON."""
        self.Bind(wx.EVT_BUTTON, action)

    def RemoveAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Unbind a previously set action."""
        self.Unbind(wx.EVT_BUTTON, handler=action)

    def SetColorScheme(self, color_scheme: ColorScheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = color_scheme
        self._resolve_colors()
        self.Refresh()

    def SetDisabledScheme(self, disabled_scheme: DisabledColorScheme) -> None:
        """Replace the disabled color scheme and repaint."""
        self._custom_disabled = disabled_scheme
        self._resolve_colors()
        self.Refresh()

    def SetLabel(self, label: str) -> None:
        """Update the button label and repaint."""
        self._label = label
        self.Refresh()

    def _resolve_colors(self) -> None:
        """Compute the active color tuples from the scheme or the palette."""
        if self._custom_scheme is not None:
            self._idle_bg, self._hover_bg, self._press_bg, self._idle_fg, self._hover_fg = self._custom_scheme
        else:
            scheme = default_color_scheme()
            self._idle_bg, self._hover_bg, self._press_bg, self._idle_fg, self._hover_fg = scheme

        if self._custom_disabled is not None:
            self._disabled_bg, self._disabled_fg = self._custom_disabled
        else:
            ds = default_disabled_scheme()
            self._disabled_bg, self._disabled_fg = ds

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        """Registered with darkdetect; rebuilds default colors on theme change."""
        self._resolve_colors()
        wx.CallAfter(self.Refresh)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Refresh()
        event.Skip()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        enabled = self.IsEnabled()

        if not enabled:
            bg = self._disabled_bg
        elif self._pressed:
            bg = self._press_bg
        elif self._hovered:
            bg = self._hover_bg
        else:
            bg = self._idle_bg

        # Paint the parent's background first
        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        gc.SetBrush(wx.Brush(bg))
        gc.DrawRoundedRectangle(0, 0, w, h, self._corner_radius)

        font = self._font if self._font is not None else self.GetFont()
        fg = self._disabled_fg if not enabled else (
            self._hover_fg if (self._hovered or self._pressed) else self._idle_fg
        )
        gc.SetFont(font, fg)
        tw, th = gc.GetTextExtent(self._label)
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)

    def _on_enter(self, event: wx.MouseEvent) -> None:
        self._hovered = True
        self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        self._hovered = False
        self._pressed = False
        self.Refresh()
        event.Skip()

    def _on_press(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        self._pressed = True
        self.Refresh()
        event.Skip()

    def _on_release(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        was_pressed = self._pressed
        self._pressed = False
        self.Refresh()
        event.Skip()
        if was_pressed:
            # Fire EVT_BUTTON so both SetAction() and Bind() receive the event
            evt = wx.CommandEvent(wx.wxEVT_BUTTON, self.GetId())
            evt.SetEventObject(self)
            self.ProcessEvent(evt)
