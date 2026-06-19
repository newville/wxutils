import wx

from typing import Callable, Optional

from .base import EnableControl
from .colors import register_darkdetect, default_check_scheme, default_disabled_scheme

# CheckScheme: (box_bg, hover_bg, check_color, label_fg)
CheckScheme = tuple[wx.Colour, wx.Colour, wx.Colour, wx.Colour]


class FlatCheckBox(EnableControl):
    """Flat custom-painted checkbox with hover state and optional theme.

    parent: parent wx window
    label: text displayed to the right of the box
    value: initial checked state (default False)
    action: optional callback accepting (bool) — called on toggle
    check_scheme: optional four-color tuple (box_bg, hover_bg, check_color, label_fg)
    disabled_scheme: optional two-color tuple (disabled_bg, disabled_fg)
    box_size: side length of the checkbox square in pixels (default 13)
    font: optional wx.Font for the label
    corner_radius: corner radius of the checkbox square in pixels (default 2)
    """

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        value: Optional[bool] = False,
        action: Optional[Callable[[bool], None]] = None,
        check_scheme: Optional[CheckScheme] = None,
        disabled_scheme=None,
        box_size: Optional[int] = 13,
        font: Optional[wx.Font] = None,
        corner_radius: Optional[int] = 2,
        **kws,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE, **kws)
        self._label = label
        self._value = value
        self._hovered = False
        self._box_size = box_size
        self._corner_radius = corner_radius
        self._font = font
        self._margin = 4

        self._custom_scheme = check_scheme
        self._custom_disabled = disabled_scheme

        self._resolve_colors()

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, self._box_size + 8))

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_UP, self._on_click)

        if action is not None:
            self.SetAction(action)

        if check_scheme is None or disabled_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetAction(self, action: Callable[[bool], None]) -> None:
        """Bind a callback that receives the new bool value on toggle."""
        self._action = action

    def RemoveAction(self) -> None:
        """Remove the current action callback."""
        self._action = None

    def GetValue(self) -> bool:
        """Return the current checked state."""
        return self._value

    def SetValue(self, value: bool) -> None:
        """Set the checked state without firing the action callback."""
        self._value = value
        self.Refresh()

    def SetLabel(self, label: str) -> None:
        """Update the label text and repaint."""
        self._label = label
        self.InvalidateBestSize()
        self.Refresh()

    def SetCheckScheme(self, check_scheme: CheckScheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = check_scheme
        self._resolve_colors()
        self.Refresh()

    def SetDisabledScheme(self, disabled_scheme) -> None:
        """Replace the disabled color scheme and repaint."""
        self._custom_disabled = disabled_scheme
        self._resolve_colors()
        self.Refresh()

    def _resolve_colors(self) -> None:
        if self._custom_scheme is not None:
            self._box_bg, self._hover_bg, self._check_color, self._label_fg = self._custom_scheme
        else:
            self._box_bg, self._hover_bg, self._check_color, self._label_fg = default_check_scheme()

        if self._custom_disabled is not None:
            self._disabled_bg, self._disabled_fg = self._custom_disabled
        else:
            self._disabled_bg, self._disabled_fg = default_disabled_scheme()

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(self.Refresh)

    def DoGetBestSize(self) -> wx.Size:
        """Report the natural size to the sizer: left maring + box + gap + label text + right maring."""
        dc = wx.ClientDC(self)
        dc.SetFont(self._font if self._font is not None else self.GetFont())
        text_w, text_h = dc.GetTextExtent(self._label)
        return wx.Size(self._margin + self._box_size + 8 + text_w + self._margin, self._box_size + 8)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Refresh()
        event.Skip()

    def _on_enter(self, event: wx.MouseEvent) -> None:
        self._hovered = True
        self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        self._hovered = False
        self.Refresh()
        event.Skip()

    def _on_click(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        self._value = not self._value
        self.Refresh()
        action = getattr(self, '_action', None)
        if action is not None:
            action(self._value)
        event.Skip()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        enabled = self.IsEnabled()

        # Background — inherit from parent
        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        cy = h / 2
        bx = float(self._margin)
        by = cy - self._box_size / 2

        if not enabled:
            box_fill   = self._disabled_bg
            tick_color = self._disabled_fg
        elif self._value:
            box_fill   = self._check_color
            tick_color = wx.Colour(255, 255, 255)
        else:
            box_fill   = self._hover_bg if self._hovered else self._box_bg
            tick_color = None

        gc.SetBrush(wx.Brush(box_fill))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(bx, by, self._box_size, self._box_size, self._corner_radius)

        if self._value and tick_color is not None:
            gc.SetPen(wx.Pen(tick_color, 2))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            # Tick mark expressed as fractions of box dimensions:
            #   start  — left side, vertically centred
            #   elbow  — lower-left of the L, where the short stroke meets the long one
            #   end    — upper-right corner
            elbow_x = bx + self._box_size * 0.35
            elbow_y = by + self._box_size * 0.72
            path = gc.CreatePath()
            path.MoveToPoint(bx + self._box_size * 0.15, by + self._box_size * 0.50)
            path.AddLineToPoint(elbow_x, elbow_y)
            path.AddLineToPoint(bx + self._box_size * 0.82, by + self._box_size * 0.22)
            gc.StrokePath(path)

        font = self._font if self._font is not None else self.GetFont()
        fg = self._disabled_fg if not enabled else self._label_fg
        gc.SetFont(font, fg)
        _, text_h = gc.GetTextExtent(self._label)
        gc.DrawText(self._label, bx + self._box_size + 8, cy - text_h / 2)
