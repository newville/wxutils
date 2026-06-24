import wx
from typing import Optional

from .colors import register_darkdetect, get_color, is_dark_theme


class SectionDivider(wx.Control):
    """Horizontal rule with a centred label sitting on top of the line."""

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        font: Optional[wx.Font] = None,
        fg: Optional[wx.Colour] = None,
        line_colour: Optional[wx.Colour] = None,
        line_width: int = 2,
        padding: int = 10,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._label = label
        self._font = font
        self._custom_fg = fg
        self._custom_line = line_colour
        self._line_width = line_width
        self._padding = padding
        self._resolve_colors()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, 28))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        if fg is None or line_colour is None:
            register_darkdetect(self._on_dark_theme)

    def _resolve_colors(self, is_dark: bool | None = None) -> None:
        self._fg = self._custom_fg if self._custom_fg is not None else wx.Colour(*get_color('pt_fg'))
        base = wx.Colour(*get_color('info_bg'))
        offset = 30 if (is_dark if is_dark is not None else is_dark_theme()) else -30
        derived_line = wx.Colour(
            max(0, min(255, base.Red() + offset)),
            max(0, min(255, base.Green() + offset)),
            max(0, min(255, base.Blue() + offset)),
        )
        self._line = self._custom_line if self._custom_line is not None else derived_line

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors(is_dark)
        wx.CallAfter(self.Refresh)

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        font = self._font if self._font is not None else self.GetFont().Bold()
        gc.SetFont(font, self._fg)
        tw, th = gc.GetTextExtent(self._label)
        cy = h / 2
        tx = (w - tw) / 2
        ty = (h - th) / 2

        gc.SetPen(wx.Pen(self._line, self._line_width))
        gc.StrokeLine(self._padding, cy, tx - self._padding, cy)
        gc.StrokeLine(tx + tw + self._padding, cy, w - self._padding, cy)
        gc.DrawText(self._label, tx, ty)
