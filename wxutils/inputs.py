import wx

from typing import Callable, Optional

from .base import EnableControl, EnablePanel
from .colors import register_darkdetect, default_check_scheme, default_disabled_scheme, default_text_scheme, CheckedColorScheme, DisabledColorScheme, TextScheme


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
        check_scheme: Optional[CheckedColorScheme] = None,
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

    def SetCheckScheme(self, check_scheme: CheckedColorScheme) -> None:
        """Replace the active color scheme and repaint."""
        self._custom_scheme = check_scheme
        self._resolve_colors()
        self.Refresh()

    def SetDisabledScheme(self, disabled_scheme: DisabledColorScheme) -> None:
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
        text_scheme: Optional[TextScheme] = None,
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


    def _resolve_scheme(self) -> TextScheme:
        return self._text_scheme if self._text_scheme is not None else default_text_scheme()

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

    def SetTextScheme(self, scheme: TextScheme) -> None:
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
