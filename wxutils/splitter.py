import wx
from typing import Optional

from .colors import register_darkdetect
from .themes import get_theme


class FlatSplitter(wx.SplitterWindow):
    """SplitterWindow with a palette-driven sash overlay and hover highlight."""

    def __init__(
        self,
        parent: wx.Window,
        orientation: int = wx.SPLIT_VERTICAL,
        splitter_scheme = None,
    ) -> None:
        super().__init__(parent, style=wx.SP_LIVE_UPDATE)
        self._custom_scheme = splitter_scheme
        self._resolve_colors()

        cursor = wx.CURSOR_SIZEWE if orientation == wx.SPLIT_VERTICAL else wx.CURSOR_SIZENS
        self._overlay = wx.Panel(self, style=wx.BORDER_NONE)
        self._overlay.SetBackgroundColour(self._sash)
        self._overlay.SetCursor(wx.Cursor(cursor))
        self._overlay.Bind(wx.EVT_ENTER_WINDOW, self._on_sash_enter)
        self._overlay.Bind(wx.EVT_LEAVE_WINDOW, self._on_sash_leave)
        self._overlay.Bind(wx.EVT_LEFT_DOWN, self._on_sash_down)

        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._reposition_overlay)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self._reposition_overlay)
        self.Bind(wx.EVT_SIZE, self._reposition_overlay)

        if splitter_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetSplitterScheme(self, scheme) -> None:
        self._custom_scheme = scheme
        self._resolve_colors()
        self._overlay.SetBackgroundColour(self._sash)
        self._overlay.Refresh()

    def _resolve_colors(self) -> None:
        if self._custom_scheme is not None:
            self._sash, self._sash_hover = self._custom_scheme
        else:
            theme = get_theme()
            self._sash = theme.bright_black
            self._sash_hover = theme.blue

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        self._overlay.SetBackgroundColour(self._sash)
        wx.CallAfter(self._overlay.Refresh)

    def _reposition_overlay(self, event: wx.Event | None = None) -> None:
        if event is not None:
            event.Skip()
        pos = self.GetSashPosition()
        if pos <= 0:
            self._overlay.Hide()
            return
        _, h = self.GetClientSize()
        sash_w = self.GetSashSize()
        self._overlay.SetSize(pos, 0, sash_w, h)
        self._overlay.Raise()
        self._overlay.Show()

    def _on_sash_enter(self, event: wx.MouseEvent) -> None:
        self._overlay.SetBackgroundColour(self._sash_hover)
        self._overlay.Refresh()
        event.Skip()

    def _on_sash_leave(self, event: wx.MouseEvent) -> None:
        self._overlay.SetBackgroundColour(self._sash)
        self._overlay.Refresh()
        event.Skip()

    def _on_sash_down(self, event: wx.MouseEvent) -> None:
        pt = self._overlay.ClientToScreen(event.GetPosition())
        pt = self.ScreenToClient(pt)
        new_event = wx.MouseEvent(wx.wxEVT_LEFT_DOWN)
        new_event.SetPosition(pt)
        wx.PostEvent(self, new_event)
        event.Skip()
