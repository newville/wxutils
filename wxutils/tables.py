import wx
from typing import Optional

from .colors import get_color
from .themes import get_theme
from .scrollbars import FlatScrollBar


class FlatTableHeader(wx.Panel):
    """Painted column header bar. Labels are centered in each column. Column dividers run full height.

    parent: parent window
    labels: column label strings; empty string = no text drawn
    proportions: relative integer widths per column (e.g. [6, 3, 1])
    height: row height in px; None derives from font
    scheme: TableScheme; None uses palette default at paint time
    """

    def __init__(
        self,
        parent: wx.Window,
        labels: list[str],
        proportions: list[int],
        height: Optional[int] = None,
        scheme = None,
    ) -> None:
        h = height if height is not None else self._default_height(parent)
        super().__init__(parent, size=(-1, h), style=wx.BORDER_NONE)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._labels = labels
        self._proportions = proportions
        self._custom_scheme = scheme
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda _e: self.Refresh())

    @staticmethod
    def _default_height(parent: wx.Window) -> int:
        dc = wx.ScreenDC()
        dc.SetFont(parent.GetFont())
        _, fh = dc.GetTextExtent("Ag")
        return max(28, fh + 14)

    def _scheme(self):
        if self._custom_scheme is not None:
            return self._custom_scheme
        theme = get_theme()
        return (theme.bright_black, theme.bright_black, theme.foreground)

    def _col_widths(self, total: int) -> list[int]:
        total_parts = sum(self._proportions)
        if total_parts == 0:
            return [0] * len(self._proportions)
        widths = [total * p // total_parts for p in self._proportions]
        widths[-1] += total - sum(widths)
        return widths

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        s = self._scheme()
        header_bg, border_color, label_color = s[0], s[1], s[2]

        gc.SetBrush(wx.Brush(header_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        font = self.GetFont().Bold()
        gc.SetFont(gc.CreateFont(font, label_color))
        gc.SetPen(wx.Pen(border_color, 1))

        widths = self._col_widths(w)
        x = 0
        for i, (label, cw) in enumerate(zip(self._labels, widths)):
            if label:
                tw, th = gc.GetTextExtent(label)
                gc.DrawText(label, x + (cw - tw) / 2, (h - th) / 2)
            if i < len(widths) - 1:
                gc.StrokeLine(x + cw, 0, x + cw, h)
            x += cw

        gc.StrokeLine(0, h - 1, w, h - 1)


class FlatTableRow(wx.Panel):
    """Base for a table row with absolute-positioned controls.

    parent: parent window
    proportions: relative column widths matching the header
    height: row height in px; None derives from font
    scheme: TableScheme for border color; None uses palette default at paint time
    """

    def __init__(
        self,
        parent: wx.Window,
        proportions: list[int],
        height: Optional[int] = None,
        scheme = None,
    ) -> None:
        h = height if height is not None else self._default_height(parent)
        super().__init__(parent, size=(-1, h), style=wx.BORDER_NONE)
        self._row_height = h
        self._pad = max(4, h // 7)
        self.SetBackgroundColour(self._row_bg())
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._proportions = proportions
        self._custom_scheme = scheme
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _row_bg(self) -> wx.Colour:
        return wx.Colour(*get_color('pt_bg'))

    def _apply_row_bg(self) -> None:
        """Push row background to self and all children."""
        bg = self._row_bg()
        self.SetBackgroundColour(bg)
        for child in self.GetChildren():
            child.SetBackgroundColour(bg)

    @staticmethod
    def _default_height(parent: wx.Window) -> int:
        dc = wx.ScreenDC()
        dc.SetFont(parent.GetFont())
        _, fh = dc.GetTextExtent("Ag")
        return max(28, fh + 10)

    def _scheme(self):
        if self._custom_scheme is not None:
            return self._custom_scheme
        theme = get_theme()
        return (theme.bright_black, theme.bright_black, theme.foreground)

    def _col_widths(self, total: int) -> list[int]:
        total_parts = sum(self._proportions)
        if total_parts == 0:
            return [0] * len(self._proportions)
        widths = [total * p // total_parts for p in self._proportions]
        widths[-1] += total - sum(widths)
        return widths

    def _reposition(self) -> None:
        """Override in subclasses to position child controls."""

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        border_color = self._scheme()[1]
        bg = self._row_bg()

        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # keep children in sync in case theme changed since AddRow
        for child in self.GetChildren():
            if child.GetBackgroundColour() != bg:
                child.SetBackgroundColour(bg)
                child.Refresh()

        gc.SetPen(wx.Pen(border_color, 1))
        gc.StrokeLine(0, h - 1, w, h - 1)
        widths = self._col_widths(w)
        x = 0
        for cw in widths[:-1]:
            x += cw
            gc.StrokeLine(x, 0, x, h)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self._reposition()
        self.Refresh()
        event.Skip()

    def _place(self, ctrl: wx.Window, x: int, col_width: int) -> None:
        """Place a control inside a column with consistent inset padding."""
        ctrl.SetSize(x + self._pad, self._pad, col_width - self._pad * 2, self._row_height - self._pad * 2)


class FlatScrolledPanel(wx.Panel):
    """Viewport + FlatScrollBar container for vertically stacked children.

    parent: parent window
    scroll_step: pixels to scroll per mouse-wheel click (default: 28)
    bg: background color; None uses the palette 'bg' color
    scrollbar_scheme: ScrollBarScheme; None uses the palette default
    header: optional header window to pin above the viewport
    """

    def __init__(
        self,
        parent: wx.Window,
        scroll_step: int = 28,
        bg: Optional[wx.Colour] = None,
        scrollbar_scheme = None,
        header: Optional[wx.Window] = None,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._scroll_step = scroll_step
        self._custom_bg = bg
        self._offset: int = 0

        self._apply_bg()

        self._viewport = wx.Panel(self, style=wx.BORDER_NONE)
        self._apply_bg(self._viewport)

        self.rows_sizer = wx.BoxSizer(wx.VERTICAL)
        self._content = wx.Panel(self._viewport, style=wx.BORDER_NONE)
        self._apply_bg(self._content)
        self._content.SetSizer(self.rows_sizer)

        self._scrollbar = FlatScrollBar(
            self,
            on_scroll=self._on_sb_scroll,
            scrollbar_scheme=scrollbar_scheme,
        )

        # left column: optional header above the scrollable viewport
        left = wx.BoxSizer(wx.VERTICAL)
        if header is not None:
            header.Reparent(self)
            left.Add(header, 0, wx.EXPAND)
        left.Add(self._viewport, 1, wx.EXPAND)

        outer = wx.BoxSizer(wx.HORIZONTAL)
        outer.Add(left, 1, wx.EXPAND)
        outer.Add(self._scrollbar, 0, wx.EXPAND)
        self.SetSizer(outer)

        self._viewport.Bind(wx.EVT_SIZE, self._on_viewport_size)
        self._viewport.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self._content.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)

    def _resolve_bg(self) -> wx.Colour:
        return self._custom_bg if self._custom_bg is not None else wx.Colour(*get_color('bg'))

    def _apply_bg(self, window: Optional[wx.Window] = None) -> None:
        target = window if window is not None else self
        target.SetBackgroundColour(self._resolve_bg())

    def AddRow(self, row: wx.Window) -> None:
        if isinstance(row, FlatTableRow):
            row._apply_row_bg()
        self.rows_sizer.Add(row, 0, wx.EXPAND)
        self._content.Layout()
        self._sync()

    def RemoveRow(self, row: wx.Window) -> None:
        self.rows_sizer.Detach(row)
        self._content.Layout()
        self._sync()

    def ClearRows(self) -> None:
        self.rows_sizer.Clear(delete_windows=False)
        self._content.Layout()
        self._sync()

    def BindMouseWheel(self, window: wx.Window) -> None:
        """Propagate mouse-wheel events from a child control into the panel."""
        window.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)

    def _content_height(self) -> int:
        return self._content.GetBestSize().height

    def _viewport_height(self) -> int:
        return self._viewport.GetClientSize().height

    def _max_offset(self) -> int:
        return max(0, self._content_height() - self._viewport_height())

    def _apply_offset(self) -> None:
        self._offset = max(0, min(self._offset, self._max_offset()))
        w = self._viewport.GetClientSize().width
        h = max(self._content_height(), self._viewport_height())
        self._content.SetSize(0, -self._offset, w, h)
        self._sync_scrollbar()

    def _sync_scrollbar(self) -> None:
        total = self._content_height()
        visible = self._viewport_height()
        if total <= visible:
            self._scrollbar.Update(0.0, 1.0)
        else:
            self._scrollbar.Update(self._offset / (total - visible), visible / total)

    def _sync(self) -> None:
        self._apply_offset()

    def _on_sb_scroll(self, fraction: float) -> None:
        self._offset = int(fraction * self._max_offset())
        self._apply_offset()

    def _on_viewport_size(self, event: wx.SizeEvent) -> None:
        event.Skip()
        self._apply_offset()

    def _on_wheel(self, event: wx.MouseEvent) -> None:
        delta = event.GetWheelRotation() // event.GetWheelDelta()
        self._offset = max(0, min(self._offset - delta * self._scroll_step, self._max_offset()))
        self._apply_offset()
        event.Skip()
