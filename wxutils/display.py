import wx
from typing import Optional

from .colors import register_darkdetect, get_color, is_dark_theme
from .themes import get_theme



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


class StatusField(wx.Control):
    """Read-only value display, centered on both axes."""

    def __init__(
        self,
        parent: wx.Window,
        value: str = "",
        bg: Optional[wx.Colour] = None,
        fg: Optional[wx.Colour] = None,
        font: Optional[wx.Font] = None,
        corner_radius: int = 3,
        height: int = 28,
    ) -> None:
        super().__init__(parent, size=wx.Size(-1, height), style=wx.BORDER_NONE)
        self._value = value
        self._custom_bg = bg
        self._custom_fg = fg
        self._font = font
        self._corner_radius = corner_radius
        self._resolve_colors()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        if bg is None or fg is None:
            register_darkdetect(self._on_dark_theme)

    def SetValue(self, value: str) -> None:
        self._value = value
        self.Refresh()

    def GetValue(self) -> str:
        return self._value

    def _resolve_colors(self) -> None:
        theme = get_theme()
        dis_bg = theme.bright_black
        dis_fg = theme.white
        self._bg = self._custom_bg if self._custom_bg is not None else dis_bg
        self._fg = self._custom_fg if self._custom_fg is not None else dis_fg

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(self.Refresh)

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        # paint the full rect with the parent bg so rounded corners are clean
        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        gc.SetBrush(wx.Brush(self._bg))
        gc.DrawRoundedRectangle(0, 0, w, h, self._corner_radius)
        if not self._value:
            return
        font = self._font if self._font is not None else self.GetFont().Bold()
        gc.SetFont(font, self._fg)
        tw, th = gc.GetTextExtent(self._value)
        gc.DrawText(self._value, (w - tw) / 2, (h - th) / 2)


class FlatProgressBar(wx.Panel):
    """Flat progress bar with optional text overlay and elapsed time.

    parent: parent wx window
    height: bar height in pixels (default 28)
    corner_radius: rounded-rectangle corner radius (default 4)
    progress_scheme: optional (track_bg, fill_bg) tuple; defaults to palette colours
    """

    def __init__(
        self,
        parent: wx.Window,
        height: int = 28,
        corner_radius: int = 4,
        progress_scheme = None,
    ) -> None:
        super().__init__(parent, size=(-1, height), style=wx.BORDER_NONE)
        self._custom_scheme = progress_scheme
        self._corner_radius = corner_radius
        self._fraction: float = 0.0
        self._label: str = ""
        self._sublabel: str = ""
        self._elapsed: str = ""
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda _e: self.Refresh())

    def Update(self, fraction: float, label: str = "", sublabel: str = "") -> None:
        """Set progress fraction (0.0 – 1.0) and optional text labels. """
        self._fraction = max(0.0, min(1.0, fraction))
        self._label = label
        self._sublabel = sublabel
        self.Refresh()

    def SetElapsed(self, elapsed_seconds: float) -> None:
        """Display a right-aligned elapsed time string (HH:MM:SS)."""
        h = int(elapsed_seconds) // 3600
        m = (int(elapsed_seconds) % 3600) // 60
        s = int(elapsed_seconds) % 60
        self._elapsed = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        self.Refresh()

    def ClearElapsed(self) -> None:
        """Remove the elapsed time display."""
        self._elapsed = ""
        self.Refresh()

    def Reset(self) -> None:
        """Reset progress to zero and clear all text."""
        self._fraction = 0.0
        self._label = ""
        self._sublabel = ""
        self._elapsed = ""
        self.Refresh()

    def SetColorScheme(self, scheme) -> None:
        """Replace the track/fill colours at runtime."""
        self._custom_scheme = scheme
        self.Refresh()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        r = self._corner_radius

        theme = get_theme()
        scheme = self._custom_scheme if self._custom_scheme is not None else (theme.black, theme.blue)
        track_bg = scheme[0]
        fill_bg = scheme[1]

        # clear to parent background first to avoid corner bleed
        parent_bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(wx.Brush(parent_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # track
        gc.SetBrush(wx.Brush(track_bg))
        gc.DrawRoundedRectangle(0, 0, w, h, r)

        # fill
        fill_w = int(w * self._fraction)
        if fill_w > 0:
            gc.SetBrush(wx.Brush(fill_bg))
            gc.DrawRoundedRectangle(0, 0, fill_w, h, r)

        # primary + secondary label, centred
        if self._label:
            fg = wx.Colour(*get_color('pt_fg'))
            fg_sub = wx.Colour(*get_color('graytext'))
            bold = self.GetFont().Bold()
            norm = self.GetFont()
            full = self._label + self._sublabel
            gc.SetFont(gc.CreateFont(bold, fg))
            tw, th = gc.GetTextExtent(full)
            tx = (w - tw) / 2
            ty = (h - th) / 2
            if self._sublabel:
                lw, _ = gc.GetTextExtent(self._label)
                gc.DrawText(self._label, tx, ty)
                gc.SetFont(gc.CreateFont(norm, fg_sub))
                gc.DrawText(self._sublabel, tx + lw, ty)
            else:
                gc.DrawText(self._label, tx, ty)

        # elapsed, right-aligned
        if self._elapsed:
            fg_sub = wx.Colour(*get_color('graytext'))
            norm = self.GetFont()
            gc.SetFont(gc.CreateFont(norm, fg_sub))
            ew, eh = gc.GetTextExtent(self._elapsed)
            gc.DrawText(self._elapsed, w - ew - 6, (h - eh) / 2)


class _FlatTabBar(wx.Control):
    """Tab strip for FlatTabbedPanel."""

    def __init__(self, parent: wx.Window, height: int, scheme = None) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._height = height
        self._custom_scheme = scheme
        self._labels: list[str] = []
        self._selection: int = 0
        self._hover: int = -1
        self._on_select: Optional[callable] = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, height))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_UP, self._on_click)

    def SetLabels(self, labels: list[str]) -> None:
        self._labels = list(labels)
        self.Refresh()

    def SetSelection(self, idx: int) -> None:
        if 0 <= idx < len(self._labels):
            self._selection = idx
            self.Refresh()

    def SetOnSelect(self, callback) -> None:
        self._on_select = callback

    def _scheme(self):
        if self._custom_scheme is not None:
            return self._custom_scheme
        theme = get_theme()
        return (theme.background, theme.bright_black, theme.black, theme.foreground, theme.white, theme.blue, theme.bright_black)

    def _tab_rects(self) -> list[tuple[int, int, int, int]]:
        dc = wx.ClientDC(self)
        font = self.GetFont().Bold()
        dc.SetFont(font)
        _, fh = dc.GetTextExtent("Ag")
        pad_x = max(8, fh // 2)
        _, h = self.GetClientSize()
        rects = []
        x = 0
        for label in self._labels:
            tw, _ = dc.GetTextExtent(label)
            w = tw + pad_x * 2
            rects.append((x, 0, w, h))
            x += w
        return rects

    def _index_at(self, px: int, py: int) -> int:
        for i, (x, y, w, h) in enumerate(self._tab_rects()):
            if x <= px < x + w and y <= py < y + h:
                return i
        return -1

    def _on_paint(self, _: wx.PaintEvent) -> None:
        s = self._scheme()
        bar_bg, active_bg, hover_bg, active_fg, inactive_fg, underline, sep = s
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        gc.SetBrush(wx.Brush(bar_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        font = self.GetFont().Bold()
        for i, (tx, ty, tw, th) in enumerate(self._tab_rects()):
            active = i == self._selection
            hovered = i == self._hover
            if active:
                bg = active_bg
            elif hovered:
                bg = hover_bg
            else:
                bg = bar_bg
            gc.SetBrush(wx.Brush(bg))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(tx, ty, tw, th)
            fg = active_fg if (active or hovered) else inactive_fg
            gc.SetFont(gc.CreateFont(font, fg))
            label = self._labels[i]
            ltw, lth = gc.GetTextExtent(label)
            gc.DrawText(label, tx + (tw - ltw) / 2, (th - lth) / 2)
            if active:
                gc.SetBrush(wx.Brush(underline))
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.DrawRectangle(tx, th - 2, tw, 2)
        gc.SetPen(wx.Pen(sep, 1))
        gc.StrokeLine(0, h - 1, w, h - 1)

    def _on_motion(self, event: wx.MouseEvent) -> None:
        idx = self._index_at(event.GetX(), event.GetY())
        if idx != self._hover:
            self._hover = idx
            self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self._hover != -1:
            self._hover = -1
            self.Refresh()
        event.Skip()

    def _on_click(self, event: wx.MouseEvent) -> None:
        idx = self._index_at(event.GetX(), event.GetY())
        if idx >= 0 and idx != self._selection:
            self._selection = idx
            self.Refresh()
            if self._on_select is not None:
                self._on_select(idx)
        event.Skip()


class FlatTabbedPanel(wx.Panel):
    """Tabbed container. Pages can be added via AddPage().

    parent: parent wx window
    tab_height: height of the tab bar in pixels (default 30)
    scheme: optional TabScheme; defaults to palette colors at paint time
    """

    def __init__(self, parent: wx.Window, tab_height: int = 30, scheme = None) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._custom_scheme = scheme
        self._tab_bar = _FlatTabBar(self, tab_height, scheme)
        self._tab_bar.SetOnSelect(self._on_tab_selected)
        self._content = wx.Panel(self, style=wx.BORDER_NONE)
        self._content.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._content.Bind(wx.EVT_PAINT, self._on_content_paint)
        self._content.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self._content_sizer = wx.BoxSizer(wx.VERTICAL)
        self._content.SetSizer(self._content_sizer)
        self._pages: list[tuple[str, wx.Window]] = []
        self._selection: int = -1
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tab_bar, 0, wx.EXPAND)
        sizer.Add(self._content, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self._apply_bg()

    def _apply_bg(self) -> None:
        if self._custom_scheme is not None:
            bg = self._custom_scheme[0]
            self.SetBackgroundColour(bg)
            self._content.SetBackgroundColour(bg)

    def SetColorScheme(self, scheme) -> None:
        """Replace the color scheme at runtime and repaint."""
        self._custom_scheme = scheme
        self._tab_bar._custom_scheme = scheme
        self._apply_bg()
        self._tab_bar.Refresh()
        self.Refresh()

    def AddPage(self, label: str, page: wx.Window) -> None:
        """Add a page with a tab label. First page added becomes active."""
        page.Reparent(self._content)
        self._pages.append((label, page))
        self._content_sizer.Add(page, 1, wx.EXPAND)
        self._tab_bar.SetLabels([lbl for lbl, _ in self._pages])
        if self._selection == -1:
            self.SetSelection(0)
        else:
            page.Show(False)
            self._content.Layout()

    def SetSelection(self, idx: int) -> None:
        """Show the page at idx, hide all others."""
        if not (0 <= idx < len(self._pages)) or idx == self._selection:
            return
        self._selection = idx
        for i, (_, page) in enumerate(self._pages):
            page.Show(i == idx)
        self._tab_bar.SetSelection(idx)
        self._content.Layout()

    def GetPage(self, idx: int) -> wx.Window:
        return self._pages[idx][1]

    def _on_content_paint(self, _: wx.PaintEvent) -> None:
        theme = get_theme()
        s = self._custom_scheme if self._custom_scheme is not None else (
            theme.background,
            theme.bright_black,
            theme.black,
            theme.foreground,
            theme.white,
            theme.blue,
            theme.bright_black
        )
        dc = wx.AutoBufferedPaintDC(self._content)
        dc.SetBackground(wx.Brush(s[0]))
        dc.Clear()

    def _on_tab_selected(self, idx: int) -> None:
        self.SetSelection(idx)
