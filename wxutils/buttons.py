import wx

from typing import Callable, Optional

from .base import EnableControl
from .colors import register_darkdetect
from .themes import get_theme


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
        color_scheme = None,
        disabled_scheme = None,
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

        self._custom_scheme = color_scheme
        self._custom_disabled = disabled_scheme

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

    def SetColorScheme(self, color_scheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = color_scheme
        self._resolve_colors()
        self.Refresh()

    def SetDisabledScheme(self, disabled_scheme) -> None:
        """Replace the disabled color scheme and repaint."""
        self._custom_disabled = disabled_scheme
        self._resolve_colors()
        self.Refresh()

    def SetLabel(self, label: str) -> None:
        """Update the button label and repaint."""
        self._label = label
        self.Refresh()

    def _resolve_colors(self) -> None:
        """Compute the active color tuples from the scheme or the active theme."""
        theme = get_theme()
        if self._custom_scheme is not None:
            self._idle_bg, self._hover_bg, self._press_bg, self._idle_fg, self._hover_fg = self._custom_scheme
        else:
            self._idle_bg = theme.bright_black
            self._hover_bg = theme.white
            self._press_bg = theme.blue
            self._idle_fg = theme.foreground
            self._hover_fg = theme.foreground

        if self._custom_disabled is not None:
            self._disabled_bg, self._disabled_fg = self._custom_disabled
        else:
            self._disabled_bg = theme.bright_black
            self._disabled_fg = theme.white

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        """Registered with darkdetect; rebuilds default colors on theme change."""
        self._resolve_colors()
        wx.CallAfter(self.Refresh)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Refresh()
        event.Skip()

    def DoGetBestSize(self) -> wx.Size:
        dc = wx.ClientDC(self)
        dc.SetFont(self._font if self._font is not None else self.GetFont())
        tw, th = dc.GetTextExtent(self._label)
        return wx.Size(tw + 24, max(th + 10, 28))

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


class FlatRadioButton(EnableControl):
    """Flat custom-painted radio button with optional theme.

    parent: parent wx window
    value: initial selected state (default False)
    tooltip: optional tooltip string
    radio_scheme: optional four-color tuple (bg, ring_fill, accent, inactive_ring)
    dot_size: diameter of the dot in pixels (default 16)
    """

    def __init__(
        self,
        parent: wx.Window,
        value: bool = False,
        tooltip: str = "",
        radio_scheme = None,
        dot_size: int = 16,
    ) -> None:
        pad = 8
        super().__init__(parent, size=wx.Size(dot_size + pad, dot_size + pad), style=wx.BORDER_NONE)
        self._value = value
        self._hovered = False
        self._size = dot_size
        self._scheme = radio_scheme
        self._callback: Optional[Callable[[], None]] = None
        self._resolve_colors()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        if tooltip:
            self.SetToolTip(tooltip)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        if radio_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetValue(self, value: bool) -> None:
        if value != self._value:
            self._value = value
            self.Refresh()

    def GetValue(self) -> bool:
        return self._value

    def SetAction(self, callback: Callable[[], None]) -> None:
        self._callback = callback

    def _resolve_colors(self) -> None:
        if self._scheme is not None:
            self._bg, self._ring_fill, self._accent, self._inactive = self._scheme
        else:
            theme = get_theme()
            self._bg = theme.background
            self._ring_fill = theme.bright_black
            self._accent = theme.blue
            self._inactive = theme.white

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(lambda: self and self.Refresh())

    def _on_enter(self, event: wx.MouseEvent) -> None:
        self._hovered = True
        self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        self._hovered = False
        self.Refresh()
        event.Skip()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        gc.SetBrush(wx.Brush(self._bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        cx, cy = w / 2, h / 2
        r = self._size / 2
        ring_colour = self._accent if (self._value or self._hovered) else self._inactive
        gc.SetPen(wx.Pen(ring_colour, 2))
        gc.SetBrush(wx.Brush(self._ring_fill))
        gc.DrawEllipse(cx - r, cy - r, self._size, self._size)

        if self._value:
            inner = self._size * 0.45
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush(self._accent))
            gc.DrawEllipse(cx - inner / 2, cy - inner / 2, inner, inner)

    def _on_click(self, event: wx.MouseEvent) -> None:
        if not self._value:
            self._value = True
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_RADIOBUTTON, self.GetId())
            evt.SetEventObject(self)
            self.ProcessEvent(evt)
            if self._callback is not None:
                self._callback()
        event.Skip()


class FlatToggleButton(EnableControl):
    """Flat toggle button with on/off states and optional theme.

    parent: parent wx window
    label: button text
    value: initial on/off state (default False)
    action: optional callback accepting a wx.CommandEvent
    toggle_scheme: optional four-color tuple (off_colour, off_hover, on_colour, on_hover)
    font: optional wx.Font to use for the label
    corner_radius: rounded-rectangle corner radius in pixels (default 4)
    """

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        value: bool = False,
        action: Optional[Callable[[wx.CommandEvent], None]] = None,
        toggle_scheme = None,
        font: Optional[wx.Font] = None,
        corner_radius: int = 4,
        **kws,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE | wx.WANTS_CHARS, **kws)
        self._label = label
        self._value = value
        self._hovered = False
        self._font = font
        self._corner_radius = corner_radius
        self._custom_scheme = toggle_scheme
        self._resolve_colors()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, 26))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_UP, self._on_release)
        if action is not None:
            self.SetAction(action)
        if toggle_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetValue(self, value: bool) -> None:
        """Set the on/off state without firing an event."""
        if value != self._value:
            self._value = value
            self.Refresh()

    def GetValue(self) -> bool:
        """Return the current on/off state."""
        return self._value

    def SetAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Bind action to EVT_TOGGLEBUTTON."""
        self.Bind(wx.EVT_TOGGLEBUTTON, action)

    def RemoveAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Unbind a previously set action."""
        self.Unbind(wx.EVT_TOGGLEBUTTON, handler=action)

    def SetLabel(self, label: str) -> None:
        """Update the button label and repaint."""
        self._label = label
        self.Refresh()

    def SetColorScheme(self, toggle_scheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = toggle_scheme
        self._resolve_colors()
        self.Refresh()

    def _resolve_colors(self) -> None:
        if self._custom_scheme is not None:
            self._off, self._off_hover, self._on, self._on_hover = self._custom_scheme
        else:
            theme = get_theme()
            self._off = theme.white
            self._off_hover = theme.bright_black
            self._on = theme.blue
            on = theme.bright_blue
            self._on_hover = on

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(lambda: self and self.Refresh())

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Refresh()
        event.Skip()

    def DoGetBestSize(self) -> wx.Size:
        dc = wx.ClientDC(self)
        dc.SetFont(self._font if self._font is not None else self.GetFont())
        tw, th = dc.GetTextExtent(self._label)
        return wx.Size(tw + 24, max(th + 10, 28))

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        enabled = self.IsEnabled()

        if not enabled:
            colour = self._off
        elif self._value:
            colour = self._on_hover if self._hovered else self._on
        else:
            colour = self._off_hover if self._hovered else self._off

        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        gc.SetPen(wx.Pen(colour, 1))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, self._corner_radius)

        font = self._font if self._font is not None else self.GetFont()
        gc.SetFont(font, colour)
        tw, th = gc.GetTextExtent(self._label)
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)

    def _on_enter(self, event: wx.MouseEvent) -> None:
        self._hovered = True
        self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        self._hovered = False
        self.Refresh()
        event.Skip()

    def _on_release(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        self._value = not self._value
        self.Refresh()
        evt = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON, self.GetId())
        evt.SetEventObject(self)
        self.ProcessEvent(evt)
        event.Skip()


class FlatIconButton(EnableControl):
    """Flat icon button with hover/press background states.

    parent: parent wx window
    draw_fn: callable(gc: wx.GraphicsContext, size: int) that draws the icon
    icon_size: icon pixel size (default 20); widget is icon_size + 8 square
    tooltip: optional tooltip string
    action: optional callback accepting a wx.CommandEvent
    icon_scheme: optional three-color tuple (idle_bg, hover_bg, press_bg)
    corner_radius: background rounded-rectangle corner radius (default 4)
    """

    def __init__(
        self,
        parent: wx.Window,
        draw_fn: Callable,
        icon_size: int = 20,
        tooltip: str = "",
        action: Optional[Callable[[wx.CommandEvent], None]] = None,
        icon_scheme = None,
        corner_radius: int = 4,
        **kws,
    ) -> None:
        sz = icon_size + 8
        super().__init__(parent, size=wx.Size(sz, sz), style=wx.BORDER_NONE, **kws)
        self._draw_fn = draw_fn
        self._icon_size = icon_size
        self._corner_radius = corner_radius
        self._hovered = False
        self._pressed = False
        self._custom_scheme = icon_scheme
        self._resolve_colors()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        if tooltip:
            self.SetToolTip(tooltip)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)
        self.Bind(wx.EVT_LEFT_UP, self._on_release)
        if action is not None:
            self.SetAction(action)
        if icon_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Bind action to EVT_BUTTON."""
        self.Bind(wx.EVT_BUTTON, action)

    def RemoveAction(self, action: Callable[[wx.CommandEvent], None]) -> None:
        """Unbind a previously set action."""
        self.Unbind(wx.EVT_BUTTON, handler=action)

    def SetDrawFn(self, draw_fn: Callable) -> None:
        """Replace the icon draw function and repaint."""
        self._draw_fn = draw_fn
        self.Refresh()

    def SetColorScheme(self, icon_scheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = icon_scheme
        self._resolve_colors()
        self.Refresh()

    def set_hovered(self, hovered: bool) -> None:
        """Externally drive the hover state (useful for overlay parents)."""
        if hovered != self._hovered:
            self._hovered = hovered
            if not hovered:
                self._pressed = False
            self.Refresh()

    def _resolve_colors(self) -> None:
        if self._custom_scheme is not None:
            self._idle_bg, self._hover_bg, self._press_bg = self._custom_scheme
        else:
            theme = get_theme()
            self._idle_bg = theme.background
            self._hover_bg = theme.bright_black
            self._press_bg = theme.blue

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(lambda: self and self.Refresh())

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Refresh()
        event.Skip()

    def DoGetBestSize(self) -> wx.Size:
        sz = self._icon_size + 8
        return wx.Size(sz, sz)

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        enabled = self.IsEnabled()

        if not enabled:
            bg = self._idle_bg
        elif self._pressed:
            bg = self._press_bg
        elif self._hovered:
            bg = self._hover_bg
        else:
            bg = self._idle_bg

        parent_bg = self._idle_bg
        gc.SetBrush(wx.Brush(parent_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, w, h, self._corner_radius)

        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
        offset = (w - self._icon_size) / 2
        gc.Translate(offset, offset)
        if not enabled:
            gc.BeginLayer(0.35)
        self._draw_fn(gc, self._icon_size)
        if not enabled:
            gc.EndLayer()

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
        if self._pressed:
            self._pressed = False
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_BUTTON, self.GetId())
            evt.SetEventObject(self)
            self.ProcessEvent(evt)
        event.Skip()
