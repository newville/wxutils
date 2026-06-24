import wx
from typing import Callable, Optional

from .base import EnablePanel
from .colors import register_darkdetect, default_scrollbar_scheme, ScrollBarScheme


class _ScrollBarBase(EnablePanel):
    """Base class for FlatScrollBar and FlatHScrollBar."""

    def __init__(
        self,
        parent: wx.Window,
        on_scroll: Callable[[float], None],
        size: wx.Size,
        thickness: int,
        corner_radius: int,
        min_thumb: int,
        scrollbar_scheme: Optional[ScrollBarScheme],
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE, size=size)
        self._on_scroll = on_scroll
        self._thickness = thickness
        self._corner_radius = corner_radius
        self._min_thumb = min_thumb
        self._custom_scheme = scrollbar_scheme
        self._thumb_pos: float = 0.0
        self._thumb_size: float = 1.0
        self._dragging = False
        self._drag_start_event_pos: int = 0
        self._drag_start_thumb_pos: float = 0.0
        self._hovered = False

        self._resolve_colors()

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)

        if scrollbar_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def Update(self, thumb_pos: float, thumb_size: float) -> None:
        """Set thumb position and size as fractions of the track (0.0–1.0)."""
        self._thumb_pos = max(0.0, min(thumb_pos, 1.0 - thumb_size))
        self._thumb_size = max(0.0, min(thumb_size, 1.0))
        self.Refresh()

    @property
    def visible(self) -> bool:
        """True when the thumb does not fill the full track."""
        return self._thumb_size < 1.0

    def SetScrollBarScheme(self, scheme: ScrollBarScheme) -> None:
        self._custom_scheme = scheme
        self._resolve_colors()
        self.Refresh()

    def _resolve_colors(self) -> None:
        scheme = self._custom_scheme if self._custom_scheme is not None else default_scrollbar_scheme()
        self._track_colour, self._thumb_colour, self._thumb_hover_colour = scheme

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(self.Refresh)

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        gc.SetBrush(wx.Brush(self._track_colour))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        if not self.visible:
            return
        x, y, tw, th = self._thumb_rect()
        colour = self._thumb_hover_colour if (self._hovered or self._dragging) else self._thumb_colour
        gc.SetBrush(wx.Brush(colour))
        gc.DrawRoundedRectangle(x, y, tw, th, self._corner_radius)

    def _on_mouse_down(self, event: wx.MouseEvent) -> None:
        x, y, tw, th = self._thumb_rect()
        ep = self._event_pos(event)
        thumb_start, thumb_span = self._thumb_range(x, y, tw, th)
        if thumb_start <= ep <= thumb_start + thumb_span:
            self._dragging = True
            self._drag_start_event_pos = ep
            self._drag_start_thumb_pos = self._thumb_pos
            self.CaptureMouse()
        else:
            track = self._track_length()
            pos = max(0.0, min((ep - 1) / track - self._thumb_size / 2, 1.0 - self._thumb_size))
            self._thumb_pos = pos
            self.Refresh()
            self._on_scroll(self._thumb_pos)
        event.Skip()

    def _on_mouse_up(self, event: wx.MouseEvent) -> None:
        if self._dragging and self.HasCapture():
            self.ReleaseMouse()
        self._dragging = False
        self.Refresh()
        event.Skip()

    def _on_motion(self, event: wx.MouseEvent) -> None:
        if self._dragging:
            track = self._track_length()
            delta = self._event_pos(event) - self._drag_start_event_pos
            pos = max(0.0, min(self._drag_start_thumb_pos + delta / track, 1.0 - self._thumb_size))
            self._thumb_pos = pos
            self.Refresh()
            self._on_scroll(self._thumb_pos)
        else:
            x, y, tw, th = self._thumb_rect()
            ep = self._event_pos(event)
            thumb_start, thumb_span = self._thumb_range(x, y, tw, th)
            hovered = thumb_start <= ep <= thumb_start + thumb_span
            if hovered != self._hovered:
                self._hovered = hovered
                self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self._hovered:
            self._hovered = False
            self.Refresh()
        event.Skip()


class FlatScrollBar(_ScrollBarBase):
    """Vertical scrollbar."""

    def __init__(
        self,
        parent: wx.Window,
        on_scroll: Callable[[float], None],
        thickness: int = 8,
        corner_radius: int = 4,
        min_thumb: int = 20,
        scrollbar_scheme: Optional[ScrollBarScheme] = None,
    ) -> None:
        super().__init__(
            parent, on_scroll,
            size=wx.Size(thickness, -1),
            thickness=thickness,
            corner_radius=corner_radius,
            min_thumb=min_thumb,
            scrollbar_scheme=scrollbar_scheme,
        )

    def _track_length(self) -> int:
        return self.GetClientSize().y - 2

    def _event_pos(self, event: wx.MouseEvent) -> int:
        return event.GetY()

    def _thumb_rect(self) -> tuple[int, int, int, int]:
        track = self._track_length()
        ty = 1 + int(self._thumb_pos * track)
        th = min(max(self._min_thumb, int(self._thumb_size * track)), track - (ty - 1))
        return 1, ty, self._thickness - 2, th

    def _thumb_range(self, x, y, tw, th) -> tuple[int, int]:
        return y, th


class FlatHScrollBar(_ScrollBarBase):
    """Horizontal scrollbar."""

    def __init__(
        self,
        parent: wx.Window,
        on_scroll: Callable[[float], None],
        thickness: int = 8,
        corner_radius: int = 4,
        min_thumb: int = 20,
        scrollbar_scheme: Optional[ScrollBarScheme] = None,
    ) -> None:
        super().__init__(
            parent, on_scroll,
            size=wx.Size(-1, thickness),
            thickness=thickness,
            corner_radius=corner_radius,
            min_thumb=min_thumb,
            scrollbar_scheme=scrollbar_scheme,
        )

    def _track_length(self) -> int:
        return self.GetClientSize().x - 2

    def _event_pos(self, event: wx.MouseEvent) -> int:
        return event.GetX()

    def _thumb_rect(self) -> tuple[int, int, int, int]:
        track = self._track_length()
        tx = 1 + int(self._thumb_pos * track)
        tw = min(max(self._min_thumb, int(self._thumb_size * track)), track - (tx - 1))
        return tx, 1, tw, self._thickness - 2

    def _thumb_range(self, x, y, tw, th) -> tuple[int, int]:
        return x, tw
