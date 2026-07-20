import wx

from typing import Callable, Optional

from .base import EnableControl, EnablePanel
from .colors import register_darkdetect
from .themes import get_theme


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
        check_scheme = None,
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

    def SetCheckScheme(self, check_scheme) -> None:
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
            theme = get_theme()
            self._box_bg = theme.bright_black
            self._hover_bg = theme.blue
            self._check_color = theme.blue
            self._label_fg = theme.foreground

        if self._custom_disabled is not None:
            self._disabled_bg, self._disabled_fg = self._custom_disabled
        else:
            theme = get_theme()
            self._disabled_bg = theme.bright_black
            self._disabled_fg = theme.white

    def _on_dark_theme(self, is_dark: bool = True) -> None:
        self._resolve_colors()
        wx.CallAfter(lambda: self and self.Refresh())

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


class FlatTextCtrl(EnablePanel):
    """Flat custom-painted editable text field with placeholder, validation, and theme support.

    parent: parent wx window
    value: initial text value (default "")
    placeholder: hint text shown when empty and not editing (default "")
    centered: center the text horizontally (default False)
    font: optional wx.Font for the value text; falls back to system font
    placeholder_font: optional wx.Font for placeholder text; falls back to font italic
    text_scheme: optional TextScheme (bg, fg, placeholder_fg, disabled_bg, disabled_fg, error_bg)
    corner_radius: corner radius of the field in pixels (default 2)
    """

    def __init__(
        self,
        parent: wx.Window,
        value: str = "",
        placeholder: str = "",
        centered: bool = False,
        font: Optional[wx.Font] = None,
        placeholder_font: Optional[wx.Font] = None,
        text_scheme = None,
        corner_radius: int = 2,
        size: wx.Size = wx.DefaultSize,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE, size=size)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self._value = value
        self._placeholder = placeholder
        self._centered = centered
        self._font = font
        self._placeholder_font = placeholder_font
        self._corner_radius = corner_radius
        self._text_scheme = text_scheme

        self._editing = False
        self._error = False
        self._limit_error = False
        self._validator: Callable[[str], str] | None = None
        self._restrict_to_float = False
        self._callback_enter: Callable | None = None
        self._callback_kill: Callable | None = None

        ctrl_style = wx.TE_PROCESS_ENTER | wx.BORDER_NONE
        if centered:
            ctrl_style |= wx.TE_CENTRE
        self._ctrl = wx.TextCtrl(self, value=value, style=ctrl_style)
        self._ctrl.EnableVisibleFocus(False)
        self._ctrl.Hide()
        self._apply_scheme()

        if placeholder:
            self._ctrl.SetHint(placeholder)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._start_edit)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self._ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_enter)
        self._ctrl.Bind(wx.EVT_KILL_FOCUS, self._on_kill)

        if text_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def _on_dark_theme(self, _is_dark: bool = True) -> None:
        def _update():
            if self:
                self._apply_scheme()
                self._ctrl.Refresh()
                self.Refresh()
        wx.CallAfter(_update)

    def _resolve_scheme(self):
        if self._text_scheme is not None:
            return self._text_scheme
        theme = get_theme()
        return (theme.black, theme.foreground, theme.white, theme.bright_black, theme.white, theme.red)

    def _apply_scheme(self) -> None:
        bg, fg, _, _, _, _ = self._resolve_scheme()
        font = self._font if self._font is not None else self.GetFont()
        self._ctrl.SetBackgroundColour(bg)
        self._ctrl.SetForegroundColour(fg)
        self._ctrl.SetFont(font)

    def GetValue(self) -> str:
        return self._ctrl.GetValue() if self._editing else self._value

    def SetValue(self, value: str) -> None:
        self._value = value
        self._ctrl.SetValue(value)
        self.Refresh()

    def SetPlaceholder(self, text: str) -> None:
        self._placeholder = text
        self._ctrl.SetHint(text)
        self.Refresh()

    def SetTextScheme(self, scheme) -> None:
        """Replace the color scheme and repaint."""
        self._text_scheme = scheme
        self._apply_scheme()
        self.Refresh()

    def Enable(self, enable: bool = True) -> bool:
        if not enable and self._editing:
            self._ctrl.Hide()
            self._editing = False
        return super().Enable(enable)

    def SetError(self, error: bool) -> None:
        if error != self._error:
            self._error = error
            _, _, _, _, _, error_bg = self._resolve_scheme()
            bg, _, _, _, _, _ = self._resolve_scheme()
            self._ctrl.SetBackgroundColour(error_bg if error else bg)
            self.Refresh()

    def SetLimitError(self, error: bool) -> None:
        if error != self._limit_error:
            self._limit_error = error
            self.Refresh()

    def SetValidator(self, validator: Callable[[str], str] | None) -> None:
        """Set an optional validator called on commit; raise any exception to signal an error."""
        self._validator = validator

    def SetRestrictToFloat(self, restrict: bool) -> None:
        """When True, keystroke filtering allows only digits, one '.', and '-' at position 0."""
        if restrict and not self._restrict_to_float:
            self._ctrl.Bind(wx.EVT_CHAR, self._on_char_float)
        elif not restrict and self._restrict_to_float:
            self._ctrl.Unbind(wx.EVT_CHAR, handler=self._on_char_float)
        self._restrict_to_float = restrict

    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        if event == wx.EVT_KEY_DOWN:
            self._ctrl.Bind(event, handler)
        elif event == wx.EVT_KILL_FOCUS:
            self._callback_kill = handler
        elif event == wx.EVT_TEXT_ENTER:
            self._callback_enter = handler
        else:
            super().Bind(event, handler, source, id, id2)

    def _reposition_ctrl(self) -> None:
        w, h = self.GetClientSize()
        _, th = self._ctrl.GetTextExtent("0")
        ctrl_h = th + 4
        self._ctrl.SetSize(0, (h - ctrl_h) // 2, w, ctrl_h)

    def _commit(self, raw: str) -> None:
        """Validate raw, update internal state, and mark error on failure."""
        if self._validator is not None:
            try:
                canonical = self._validator(raw)
                self._value = canonical
                self._ctrl.SetValue(canonical)
                self.SetError(False)
            except Exception:
                self._ctrl.SetValue(self._value)
                self.SetError(True)
        else:
            self._value = raw

    def _on_size(self, event: wx.SizeEvent) -> None:
        self._reposition_ctrl()
        self.Refresh()
        event.Skip()

    def _start_edit(self, event: wx.MouseEvent) -> None:
        if not self.IsEnabled():
            return
        self._editing = True
        self._ctrl.SetValue(self._value)
        self._reposition_ctrl()
        self._apply_scheme()
        self._ctrl.Show()
        self._ctrl.SetFocus()
        self._ctrl.SelectAll()
        self.Refresh()
        event.Skip()

    def _on_enter(self, event: wx.Event) -> None:
        raw = self._ctrl.GetValue()
        self._commit(raw)
        self._ctrl.Hide()
        self._editing = False
        self.Refresh()
        if self._callback_enter:
            self._callback_enter(event)

    def _on_kill(self, event: wx.FocusEvent) -> None:
        raw = self._ctrl.GetValue()
        self._commit(raw)
        self._ctrl.Hide()
        self._editing = False
        self.Refresh()
        if self._callback_kill:
            self._callback_kill(event)
        event.Skip()

    def _on_char_float(self, event: wx.KeyEvent) -> None:
        if not self.IsEnabled():
            return
        key  = event.GetKeyCode()
        char = chr(key) if 32 <= key < 127 else None

        if key < 32 or event.ControlDown():
            event.Skip()
            return
        if char is None:
            return

        current = self._ctrl.GetValue()
        insert_pos = self._ctrl.GetInsertionPoint()
        sel_from, sel_to = self._ctrl.GetSelection()
        has_selection = sel_from != sel_to
        after_replace = current[:sel_from] + current[sel_to:] if has_selection else current

        if char == "-":
            effective_pos = sel_from if has_selection else insert_pos
            if effective_pos == 0 and not after_replace.startswith("-"):
                event.Skip()
            return
        if char == ".":
            if "." not in after_replace:
                event.Skip()
            return
        if char.isdigit():
            event.Skip()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        bg, fg, placeholder_fg, dis_bg, dis_fg, error_bg = self._resolve_scheme()

        # Parent background
        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # Field background
        if not self.IsEnabled():
            field_bg = dis_bg
        elif self._error:
            field_bg = error_bg
        else:
            field_bg = bg
        gc.SetBrush(wx.Brush(field_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, w, h, self._corner_radius)

        if self._editing:
            return

        # Text
        x_pad = 6
        font = self._font if self._font is not None else self.GetFont()
        ph_font = self._placeholder_font if self._placeholder_font is not None else font

        if self._value:
            text_fg = dis_fg if not self.IsEnabled() else (fg if not self._limit_error else error_bg)
            gc.SetFont(font, text_fg)
            text_w, text_h = gc.GetTextExtent(self._value)
            tx = (w - text_w) / 2 if self._centered else x_pad
            gc.DrawText(self._value, tx, (h - text_h) / 2)
        elif self._placeholder and self.IsEnabled():
            gc.SetFont(ph_font, placeholder_fg)
            text_w, text_h = gc.GetTextExtent(self._placeholder)
            tx = (w - text_w) / 2 if self._centered else x_pad
            gc.DrawText(self._placeholder, tx, (h - text_h) / 2)


class _FlatComboPopup(wx.PopupTransientWindow):
    """Dropdown list used by FlatCombo."""

    def __init__(
        self,
        parent: wx.Window,
        choices: list[str],
        selection: int,
        on_select: Callable[[int], None],
        choice_colours: dict[str, wx.Colour] | None,
        popup_bg: wx.Colour,
        popup_hover: wx.Colour,
        fg: wx.Colour,
        font: Optional[wx.Font],
        row_height: int,
        max_visible: int,
        sb_width: int,
        sb_radius: int,
    ) -> None:
        super().__init__(parent, wx.BORDER_SIMPLE)
        self._choices = list(choices)
        self._selection = selection
        self._hover_index = -1
        self._scroll_offset = 0
        self._visible_rows = min(max_visible, len(self._choices))
        self._needs_sb = len(self._choices) > self._visible_rows
        self._row_height = row_height
        self._sb_width = sb_width
        self._sb_radius = sb_radius
        self._on_select = on_select
        self._choice_colours = choice_colours or {}
        self._dismissed = False
        self._popup_bg = popup_bg
        self._popup_hover = popup_hover
        self._fg = fg
        self._font = font
        # scrollbar drag state
        self._sb_dragging = False
        self._sb_drag_start_y: int = 0
        self._sb_drag_start_offset: int = 0
        self.SetBackgroundColour(popup_bg)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self._hover_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_hover_tick, self._hover_timer)
        self._hover_timer.Start(16)

    def popup_below(self, screen_pt: wx.Point, min_width: int) -> None:
        dc = wx.ClientDC(self)
        dc.SetFont(self._font if self._font is not None else self.GetFont())
        text_w = max((dc.GetTextExtent(c)[0] for c in self._choices), default=0)
        extra = self._sb_width + 4 if self._needs_sb else 0
        width = max(min_width, text_w + 24 + extra)
        height = self._row_height * self._visible_rows + 4
        self.SetSize(width, height)
        self._scroll_to(self._selection)
        self.SetPosition(screen_pt)
        self.Popup()

    def _list_w(self, total_w: int) -> int:
        """Width of the row list area."""
        return total_w - self._sb_width if self._needs_sb else total_w

    def _sb_thumb_rect(self, total_h: int) -> tuple[int, int, int, int]:
        """x, y, w, h of the scrollbar thumb."""
        n = len(self._choices)
        track_h = total_h - 4
        thumb_h = max(20, int(self._visible_rows / n * track_h))
        max_offset = n - self._visible_rows
        thumb_y = 2 + int(self._scroll_offset / max_offset * (track_h - thumb_h)) if max_offset > 0 else 2
        return 0, thumb_y, self._sb_width - 2, thumb_h

    def _scroll_to(self, idx: int) -> None:
        if idx < 0:
            return
        if idx < self._scroll_offset:
            self._scroll_offset = idx
        elif idx >= self._scroll_offset + self._visible_rows:
            self._scroll_offset = idx - self._visible_rows + 1
        self._scroll_offset = max(0, min(self._scroll_offset, max(0, len(self._choices) - self._visible_rows)))

    def _row_at(self, x: int, y: int) -> int:
        """Return choice index under (x, y), or -1 if on scrollbar or out of range."""
        w, _ = self.GetClientSize()
        if self._needs_sb and x >= self._list_w(w):
            return -1
        idx = self._scroll_offset + (y - 2) // self._row_height
        return int(idx) if 0 <= idx < len(self._choices) else -1

    def _on_sb_scroll_to_y(self, y: int) -> None:
        _, h = self.GetClientSize()
        track_h = h - 4
        n = len(self._choices)
        max_offset = n - self._visible_rows
        _, _, _, thumb_h = self._sb_thumb_rect(h)
        frac = max(0.0, min((y - 2) / (track_h - thumb_h), 1.0)) if track_h > thumb_h else 0.0
        self._scroll_offset = round(frac * max_offset)
        self.Refresh()

    def ProcessLeftDown(self, event: wx.MouseEvent) -> bool:
        return False

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        list_w = self._list_w(w)

        # background
        gc.SetBrush(wx.Brush(self._popup_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # rows
        font = self._font if self._font is not None else self.GetFont()
        for slot in range(self._visible_rows):
            i = self._scroll_offset + slot
            if i >= len(self._choices):
                break
            label = self._choices[i]
            y = 2 + slot * self._row_height
            if i == self._hover_index:
                gc.SetBrush(wx.Brush(self._popup_hover))
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.DrawRectangle(0, y, list_w, self._row_height)
            colour = self._choice_colours.get(label, self._fg)
            gc.SetFont(font, colour)
            _, text_h = gc.GetTextExtent(label)
            gc.DrawText(label, 10, y + (self._row_height - text_h) / 2)

        # scrollbar
        if self._needs_sb:
            sb_x = list_w
            track_colour = wx.Colour(
                max(0, self._popup_bg.Red() - 15),
                max(0, self._popup_bg.Green() - 15),
                max(0, self._popup_bg.Blue() - 15),
            )
            gc.SetBrush(wx.Brush(track_colour))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(sb_x, 0, self._sb_width, h)
            tx, ty, tw, th = self._sb_thumb_rect(h)
            thumb_colour = wx.Colour(
                min(255, self._popup_bg.Red() + 60),
                min(255, self._popup_bg.Green() + 60),
                min(255, self._popup_bg.Blue() + 60),
            )
            gc.SetBrush(wx.Brush(thumb_colour))
            gc.DrawRoundedRectangle(sb_x + tx, ty, tw, th, self._sb_radius)

    def _on_left_down(self, event: wx.MouseEvent) -> None:
        if not self._needs_sb:
            event.Skip()
            return
        w, h = self.GetClientSize()
        x, y = event.GetX(), event.GetY()
        if x >= self._list_w(w):
            tx, ty, tw, th = self._sb_thumb_rect(h)
            if ty <= y <= ty + th:
                self._sb_dragging = True
                self._sb_drag_start_y = y
                self._sb_drag_start_offset = self._scroll_offset
                self.CaptureMouse()
            else:
                self._on_sb_scroll_to_y(y)
        else:
            event.Skip()

    def _on_hover_tick(self, _: wx.TimerEvent) -> None:
        """Poll actual mouse position to update hover. Bypasses event routing issues."""
        screen_pt = wx.GetMousePosition()
        client_pt = self.ScreenToClient(screen_pt)
        x, y = client_pt.x, client_pt.y
        w, h = self.GetClientSize()
        if 0 <= x <= w and 0 <= y <= h:
            idx = self._row_at(x, y)
        else:
            idx = -1
        if idx != self._hover_index:
            self._hover_index = idx
            self.Refresh()

    def _on_left_up(self, event: wx.MouseEvent) -> None:
        if self._sb_dragging:
            if self.HasCapture():
                self.ReleaseMouse()
            self._sb_dragging = False
            return
        x, y = event.GetX(), event.GetY()
        idx = self._row_at(x, y)
        if idx >= 0 and not self._dismissed:
            self._dismissed = True
            self._hover_timer.Stop()
            self.Dismiss()
            wx.CallAfter(self._on_select, idx)

    def _on_motion(self, event: wx.MouseEvent) -> None:
        if self._sb_dragging:
            _, h = self.GetClientSize()
            dy = event.GetY() - self._sb_drag_start_y
            track_h = h - 4
            n = len(self._choices)
            max_offset = n - self._visible_rows
            _, _, _, thumb_h = self._sb_thumb_rect(h)
            frac = dy / (track_h - thumb_h) if track_h > thumb_h else 0.0
            new_offset = round(self._sb_drag_start_offset + frac * max_offset)
            self._scroll_offset = max(0, min(new_offset, max_offset))
            self.Refresh()
            return
        idx = self._row_at(event.GetX(), event.GetY())
        if idx != self._hover_index:
            self._hover_index = idx
            self.Refresh()
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self._hover_index != -1:
            self._hover_index = -1
            self.Refresh()

    def _on_wheel(self, event: wx.MouseEvent) -> None:
        delta = -1 if event.GetWheelRotation() > 0 else 1
        new_offset = max(0, min(self._scroll_offset + delta, max(0, len(self._choices) - self._visible_rows)))
        if new_offset != self._scroll_offset:
            self._scroll_offset = new_offset
            self._hover_index = -1
            self.Refresh()


class FlatCombo(EnablePanel):
    """Flat owner-drawn read-only dropdown with a themed popup list.

    parent: parent wx window
    choices: list of option strings
    selection: initial selected index (default 0)
    choice_colours: optional per-label wx.Colour overrides
    font: optional wx.Font; falls back to system font
    combo_scheme: optional ComboScheme tuple; falls back to default_combo_scheme()
    size: explicit size; defaults to wx.DefaultSize (expands to fill sizer slot)
    corner_radius: corner radius of the field in pixels (default 4)
    """

    def __init__(
        self,
        parent: wx.Window,
        choices: list[str],
        selection: int = 0,
        choice_colours: dict[str, wx.Colour] | None = None,
        font: Optional[wx.Font] = None,
        combo_scheme = None,
        size: wx.Size = wx.DefaultSize,
        corner_radius: int = 4,
        row_height: int = 26,
        max_visible: int = 16,
        popup_sb_width: int = 8,
        popup_sb_radius: int = 3,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE, size=size)
        self._choices = list(choices)
        self._selection = selection
        self._choice_colours = choice_colours or {}
        self._font = font
        self._custom_scheme = combo_scheme
        self._corner_radius = corner_radius
        self._row_height = row_height
        self._max_visible = max_visible
        self._popup_sb_width = popup_sb_width
        self._popup_sb_radius = popup_sb_radius
        self._hovered = False
        self._callback: Callable[[str], None] | None = None

        self._resolve_colors()

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)

        if combo_scheme is None:
            register_darkdetect(self._on_dark_theme)

    def SetAction(self, action: Callable[[str], None]) -> None:
        """Bind a callback that receives the selected string on change."""
        self._callback = action

    def GetStringSelection(self) -> str:
        """Return the currently selected string."""
        return self._choices[self._selection] if self._choices else ""

    def GetSelection(self) -> int:
        """Return the currently selected index."""
        return self._selection

    def SetSelection(self, idx: int) -> None:
        """Set the selected index and repaint."""
        self._selection = idx
        self.Refresh()

    def SetChoices(self, choices: list[str], selection: int = 0) -> None:
        """Replace the choice list and repaint."""
        self._choices = list(choices)
        self._selection = max(0, min(selection, len(self._choices) - 1)) if self._choices else 0
        self.InvalidateBestSize()
        self.Refresh()

    def SetComboScheme(self, scheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = scheme
        self._resolve_colors()
        self.Refresh()

    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        """Maps EVT_CHOICE to internal callback"""
        if event == wx.EVT_CHOICE:
            self._callback = handler
        else:
            super().Bind(event, handler, source, id, id2)

    def DoGetBestSize(self) -> wx.Size:
        dc = wx.ClientDC(self)
        dc.SetFont(self._font if self._font is not None else self.GetFont())
        max_w = max((dc.GetTextExtent(c)[0] for c in self._choices), default=60)
        return wx.Size(max_w + 40, 28)

    def _resolve_colors(self) -> None:
        if self._custom_scheme is not None:
            (self._bg, self._hover_bg, self._fg, self._border, self._arrow,
             self._disabled_bg, self._disabled_fg, self._popup_bg, self._popup_hover) = self._custom_scheme
        else:
            theme = get_theme()
            self._bg = theme.bright_black
            self._hover_bg = theme.bright_black
            self._fg = theme.foreground
            self._border = theme.bright_black
            self._arrow = theme.white
            self._disabled_bg = theme.bright_black
            self._disabled_fg = theme.white
            self._popup_bg = theme.black
            self._popup_hover = theme.bright_black

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

    def _on_click(self, event: wx.MouseEvent) -> None:
        if not self._choices or not self.IsEnabled():
            return
        popup = _FlatComboPopup(
            self,
            self._choices,
            self._selection,
            on_select=self._select,
            choice_colours=self._choice_colours,
            popup_bg=self._popup_bg,
            popup_hover=self._popup_hover,
            fg=self._fg,
            font=self._font,
            row_height=self._row_height,
            max_visible=self._max_visible,
            sb_width=self._popup_sb_width,
            sb_radius=self._popup_sb_radius,
        )
        w, h = self.GetSize()
        popup.popup_below(self.ClientToScreen(wx.Point(0, h)), w)

    def _select(self, idx: int) -> None:
        self._selection = idx
        self.Refresh()
        if self._callback is not None:
            self._callback(self.GetStringSelection())

    def _on_paint(self, _: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        enabled = self.IsEnabled()

        # Parent background
        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # Field background
        if not enabled:
            field_bg = self._disabled_bg
        elif self._hovered:
            field_bg = self._hover_bg
        else:
            field_bg = self._bg
        border_colour = self._disabled_fg if not enabled else self._border
        gc.SetBrush(wx.Brush(field_bg))
        gc.SetPen(wx.Pen(border_colour, 1))
        gc.DrawRoundedRectangle(0, 0, w, h, self._corner_radius)

        # Label
        font = self._font if self._font is not None else self.GetFont()
        label = self.GetStringSelection()
        label_colour = self._disabled_fg if not enabled else self._choice_colours.get(label, self._fg)
        gc.SetFont(font, label_colour)
        _, text_h = gc.GetTextExtent(label)
        gc.DrawText(label, 8, (h - text_h) / 2)

        # Arrow
        arrow_colour = self._disabled_fg if not enabled else self._arrow
        arrow_x = w - 16
        arrow_y = h / 2
        gc.SetPen(wx.Pen(arrow_colour, 1))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        path = gc.CreatePath()
        path.MoveToPoint(arrow_x - 4, arrow_y - 2)
        path.AddLineToPoint(arrow_x, arrow_y + 2)
        path.AddLineToPoint(arrow_x + 4, arrow_y - 2)
        gc.StrokePath(path)
