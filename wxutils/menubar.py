import wx
from typing import Callable, Optional

from .colors import MenuBarScheme, default_menu_bar_scheme


class _FlatMenuDropdown(wx.PopupTransientWindow):
    """Dropdown for FlatMenuBar. Supports None separator entries."""

    def __init__(self, parent: wx.Window, items: list[Optional[str]], shortcuts: list[Optional[str]], on_select: Callable[[int], None], scheme: MenuBarScheme) -> None:
        super().__init__(parent, flags=wx.BORDER_SIMPLE | wx.PU_CONTAINS_CONTROLS)
        self._items = items
        self._shortcuts = shortcuts
        self._on_select = on_select
        self._scheme = scheme
        self._hover_index: int = -1
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)

    def _font_metrics(self) -> tuple[int, int]:
        """Return (item_h, sep_h) from the current font height."""
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        _, fh = dc.GetTextExtent("Ag")
        item_h = fh + max(8, fh // 2)
        sep_h = max(6, fh // 2)
        return item_h, sep_h

    def _row_height(self, i: int, item_h: int, sep_h: int) -> int:
        return sep_h if self._items[i] is None else item_h

    def _index_at(self, py: int) -> int:
        item_h, sep_h = self._font_metrics()
        y = 4
        for i, item in enumerate(self._items):
            h = self._row_height(i, item_h, sep_h)
            if item is not None and y <= py < y + h:
                return i
            y += h
        return -1

    def PopupBelow(self, screen_pt: wx.Point) -> None:
        item_h, sep_h = self._font_metrics()
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        items = [i for i in self._items if i is not None]
        shortcuts = [sc for sc in self._shortcuts if sc is not None]
        label_w = max((dc.GetTextExtent(i)[0] for i in items), default=0)
        short_w = max((dc.GetTextExtent(sc)[0] for sc in shortcuts), default=0) if shortcuts else 0
        gap = item_h * 2 if short_w else item_h
        width = max(160, label_w + short_w + gap)
        height = 8 + sum(
            self._row_height(i, item_h, sep_h) for i in range(len(self._items))
        )
        self.SetSize(width, height)
        self.Position(screen_pt, (0, 0))
        self.Popup()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        s = self._scheme
        item_h, sep_h = self._font_metrics()
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        gc.SetBrush(wx.Brush(s[6]))   # popup_bg
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        font = self.GetFont()
        small_font = wx.Font(font)
        small_font.SetPointSize(max(7, font.GetPointSize() - 1))
        y = 4
        for i, item in enumerate(self._items):
            rh = self._row_height(i, item_h, sep_h)
            if item is None:
                cy = y + rh / 2
                gc.SetPen(wx.Pen(s[10], 1))   # popup_sep
                gc.StrokeLine(8, cy, w - 8, cy)
            else:
                if i == self._hover_index:
                    gc.SetBrush(wx.Brush(s[7]))   # popup_hover_bg
                    gc.SetPen(wx.TRANSPARENT_PEN)
                    gc.DrawRectangle(0, y, w, rh)
                gc.SetFont(gc.CreateFont(font, s[8]))   # popup_fg
                _, th = gc.GetTextExtent(item)
                gc.DrawText(item, 12, y + (rh - th) / 2)
                sc = self._shortcuts[i]
                if sc:
                    gc.SetFont(gc.CreateFont(small_font, s[9]))   # popup_secondary_fg
                    sw, _ = gc.GetTextExtent(sc)
                    gc.DrawText(sc, w - sw - 12, y + (rh - th) / 2)
            y += rh

    def _on_motion(self, event: wx.MouseEvent) -> None:
        idx = self._index_at(event.GetY())
        if idx != self._hover_index:
            self._hover_index = idx
            self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self._hover_index != -1:
            self._hover_index = -1
            self.Refresh()
        event.Skip()

    def _on_left_up(self, event: wx.MouseEvent) -> None:
        idx = self._index_at(event.GetY())
        if idx >= 0:
            self.Dismiss()
            wx.CallAfter(self._on_select, idx)
        else:
            event.Skip()


class _FlatMenuButton(wx.Control):
    """Single title button in the FlatMenuBar strip."""

    def __init__(self, parent: wx.Window, label: str, height: int) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._label = label
        self._height = height
        self._hovered = False
        self._active = False
        self._scheme: Optional[MenuBarScheme] = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)

    def SetScheme(self, scheme: MenuBarScheme) -> None:
        self._scheme = scheme
        self.Refresh()

    def SetActive(self, active: bool) -> None:
        self._active = active
        self.Refresh()

    def DoGetBestSize(self) -> wx.Size:
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        tw, fh = dc.GetTextExtent(self._label)
        pad = max(8, fh // 2)
        return wx.Size(tw + pad * 2, self._height)

    def Enable(self, enable: bool = True) -> bool:
        result = super().Enable(enable)
        self.Refresh()
        return result

    def _on_paint(self, _: wx.PaintEvent) -> None:
        s = self._scheme if self._scheme is not None else default_menu_bar_scheme()
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        if self._active:
            bg = s[2]   # btn_active_bg
        elif self._hovered:
            bg = s[1]   # btn_hover_bg
        else:
            bg = s[0]   # bar_bg
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        fg = s[4] if not self.IsEnabled() else s[3]   # btn_disabled_fg : btn_fg
        gc.SetFont(gc.CreateFont(self.GetFont(), fg))
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

    def _on_press(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        wx.PostEvent(self, wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId()))
        event.Skip()


class FlatMenuBar(wx.Panel):
    """Menu bar with dropdown support, light/dark aware.

    parent:  parent window
    height:  bar height in pixels (default 28); scales button hit area
    scheme:  optional MenuBarScheme; if None, palette colours are resolved at
             paint time so dark/light switching works automatically

    Usage::

        bar = FlatMenuBar(parent)
        bar.AppendMenu(
            title="File",
            items=["Open", "Save", None, "Exit"],
            shortcuts=["Ctrl+O", "Ctrl+S", None, "Ctrl+Q"],
            callbacks=[open_fn, save_fn, None, exit_fn],
        )
        bar.AppendAction("Settings", settings_fn)
    """

    def __init__(
        self,
        parent: wx.Window,
        height: int = 28,
        scheme: Optional[MenuBarScheme] = None,
    ) -> None:
        super().__init__(parent, size=(-1, height), style=wx.BORDER_NONE)
        self._height = height
        self._custom_scheme = scheme
        self._menus: list[tuple[_FlatMenuButton, list, list, list]] = []
        self._btn_count: int = 0
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._sizer)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self._apply_scheme()

    def _scheme(self) -> MenuBarScheme:
        return self._custom_scheme if self._custom_scheme is not None else default_menu_bar_scheme()

    def _apply_scheme(self) -> None:
        s = self._scheme()
        for btn, _, _, _ in self._menus:
            btn.SetScheme(s)

    def SetColorScheme(self, scheme: MenuBarScheme) -> None:
        """Replace the colour scheme at runtime."""
        self._custom_scheme = scheme
        self._apply_scheme()
        self.Refresh()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        s = self._scheme()
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        gc.SetBrush(wx.Brush(s[0]))   # bar_bg
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
        gc.SetPen(wx.Pen(s[5], 1))   # sep_colour
        gc.StrokeLine(0, h - 1, w, h - 1)

    def Enable(self, enable: bool = True) -> bool:
        for btn, _, _, _ in self._menus:
            btn.Enable(enable)
        return True

    def AppendMenu(
        self,
        title: str,
        items: list[Optional[str]],
        shortcuts: list[Optional[str]],
        callbacks: list[Optional[Callable[[], None]]],
    ) -> None:
        """Add a menu title that opens a dropdown on click."""
        btn = _FlatMenuButton(self, title, self._height)
        btn.SetScheme(self._scheme())
        idx = len(self._menus)
        btn.Bind(wx.EVT_BUTTON, lambda e, i=idx: self._open_menu(i))
        self._menus.append((btn, items, shortcuts, callbacks))
        self._sizer.Insert(self._btn_count, btn, 0, wx.EXPAND)
        self._btn_count += 1
        self.Layout()

    def AppendAction(self, title: str, callback: Callable[[], None]) -> None:
        """Add a button that fires callback directly — no dropdown."""
        btn = _FlatMenuButton(self, title, self._height)
        btn.SetScheme(self._scheme())

        def _on_click(_event: wx.CommandEvent) -> None:
            btn.SetActive(True)
            callback()
            btn.SetActive(False)

        btn.Bind(wx.EVT_BUTTON, _on_click)
        self._menus.append((btn, [], [], []))
        self._sizer.Insert(self._btn_count, btn, 0, wx.EXPAND)
        self._btn_count += 1
        self.Layout()

    def _open_menu(self, menu_idx: int) -> None:
        btn, items, shortcuts, callbacks = self._menus[menu_idx]
        s = self._scheme()
        btn.SetActive(True)

        def on_select(item_idx: int) -> None:
            btn.SetActive(False)
            cb = callbacks[item_idx]
            if cb is not None:
                cb()

        def on_dismiss() -> None:
            btn.SetActive(False)

        popup = _FlatMenuDropdown(self, items, shortcuts, on_select, s)
        popup.Bind(wx.EVT_SHOW, lambda e: on_dismiss() if not e.IsShown() else None)
        pos = btn.ClientToScreen(wx.Point(0, btn.GetSize().height))
        popup.PopupBelow(pos)
