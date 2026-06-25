import wx
import wx.stc as stc
from typing import Callable, Optional

from .colors import SyntaxScheme, default_python_scheme, default_color_scheme, default_disabled_scheme
from .buttons import FlatButton
from .scrollbars import FlatScrollBar, FlatHScrollBar

_MONO_FACE = "Consolas" if wx.Platform == "__WXMSW__" else "Menlo"


def apply_python_highlighting(
    ed: stc.StyledTextCtrl,
    scheme: SyntaxScheme,
    font_size: int,
    mono_face: str,
) -> None:
    """Apply Python syntax highlighting to a StyledTextCtrl using the given scheme."""
    (editor_bg, editor_fg, gutter_bg, gutter_fg, _sel_bg,
     keyword_fg, keyword2_fg, string_fg, comment_fg,
     number_fg, operator_fg, decorator_fg, defname_fg) = scheme

    ed.SetLexer(stc.STC_LEX_PYTHON)

    ed.StyleSetBackground(stc.STC_STYLE_DEFAULT, editor_bg)
    ed.StyleSetForeground(stc.STC_STYLE_DEFAULT, editor_fg)
    ed.StyleSetFaceName(stc.STC_STYLE_DEFAULT, mono_face)
    ed.StyleSetSize(stc.STC_STYLE_DEFAULT, font_size)
    ed.StyleClearAll()

    ed.StyleSetBackground(stc.STC_STYLE_LINENUMBER, gutter_bg)
    ed.StyleSetForeground(stc.STC_STYLE_LINENUMBER, gutter_fg)
    ed.StyleSetFaceName(stc.STC_STYLE_LINENUMBER, mono_face)
    ed.StyleSetSize(stc.STC_STYLE_LINENUMBER, max(7, font_size - 1))

    def _s(num, fg, bold=False):
        ed.StyleSetForeground(num, fg)
        ed.StyleSetBackground(num, editor_bg)
        if bold:
            ed.StyleSetBold(num, True)

    _s(stc.STC_P_DEFAULT,      editor_fg)
    _s(stc.STC_P_COMMENTLINE,  comment_fg)
    _s(stc.STC_P_NUMBER,       number_fg)
    _s(stc.STC_P_STRING,       string_fg)
    _s(stc.STC_P_CHARACTER,    string_fg)
    _s(stc.STC_P_WORD,         keyword_fg,   bold=True)
    _s(stc.STC_P_TRIPLE,       string_fg)
    _s(stc.STC_P_TRIPLEDOUBLE, string_fg)
    _s(stc.STC_P_CLASSNAME,    defname_fg,   bold=True)
    _s(stc.STC_P_DEFNAME,      defname_fg)
    _s(stc.STC_P_OPERATOR,     operator_fg)
    _s(stc.STC_P_IDENTIFIER,   editor_fg)
    _s(stc.STC_P_COMMENTBLOCK, comment_fg)
    _s(stc.STC_P_STRINGEOL,    string_fg)
    _s(stc.STC_P_WORD2,        keyword2_fg)
    _s(stc.STC_P_DECORATOR,    decorator_fg)

    ed.SetKeyWords(
        0,
        "False None True and as assert async await break class continue def del "
        "elif else except finally for from global if import in is lambda nonlocal "
        "not or pass raise return try while with yield",
    )
    ed.SetKeyWords(
        1,
        "abs all any bin bool bytearray bytes callable chr classmethod compile "
        "complex delattr dict dir divmod enumerate eval exec filter float format "
        "frozenset getattr globals hasattr hash help hex id input int isinstance "
        "issubclass iter len list locals map max min next object oct open ord pow "
        "print property range repr reversed round set setattr slice sorted "
        "staticmethod str sum super tuple type vars zip self cls __name__ __file__",
    )


class FlatScriptEditorDialog(wx.Frame):
    """Resizable Python script editor dialog with syntax highlighting and flat scrollbars.

    parent:      parent window
    title:       dialog title bar string
    font_size:   editor font point size (default 11)
    mono_face:   monospace font face name (default Consolas/Menlo)
    syntax_scheme: SyntaxScheme for token colours; defaults to VS Code Dark+
    btn_scheme:  ColorScheme for the Save button; defaults to palette default
    save_label:  label on the save button (default "Save")
    """

    def __init__(
        self,
        parent: wx.Window,
        title: str = "Script Editor",
        font_size: int = 11,
        mono_face: Optional[str] = None,
        syntax_scheme: Optional[SyntaxScheme] = None,
        btn_scheme=None,
        scrollbar_scheme=None,
        save_label: str = "Save",
    ) -> None:
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._syntax_scheme = syntax_scheme
        self._font_size = font_size
        self._mono_face = mono_face if mono_face is not None else _MONO_FACE
        self._on_save_cb: Optional[Callable[[str], None]] = None

        editor_bg = self._syntax_scheme[0] if self._syntax_scheme is not None else default_python_scheme()[0]
        self.SetBackgroundColour(editor_bg)

        self._container = wx.Panel(self, style=wx.BORDER_NONE)
        self._container.SetBackgroundColour(editor_bg)

        self._editor = stc.StyledTextCtrl(self._container, style=wx.BORDER_NONE)
        self._setup_editor()

        # Scrollbar width scales with font: ~half a character width, min 8px
        dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(font_size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=self._mono_face))
        char_w, _ = dc.GetTextExtent("M")
        sb_w = max(8, char_w // 2)

        self._vscrollbar = FlatScrollBar(self._container, on_scroll=self._on_vsb_scroll, scrollbar_scheme=scrollbar_scheme)
        self._hscrollbar = FlatHScrollBar(self._container, on_scroll=self._on_hsb_scroll, scrollbar_scheme=scrollbar_scheme)

        _corner = wx.Panel(self._container, size=(sb_w, sb_w))
        _corner.SetBackgroundColour(editor_bg)

        editor_row = wx.BoxSizer(wx.HORIZONTAL)
        editor_row.Add(self._editor, 1, wx.EXPAND)
        editor_row.Add(self._vscrollbar, 0, wx.EXPAND)

        scroll_row = wx.BoxSizer(wx.HORIZONTAL)
        scroll_row.Add(self._hscrollbar, 1, wx.EXPAND)
        scroll_row.Add(_corner, 0)

        sep = wx.Panel(self, size=(-1, 1))
        sep.SetBackgroundColour(wx.Colour(*[max(0, c + 20) for c in editor_bg.Get()[:3]]))

        self._status_label = wx.StaticText(self, label="")
        self._status_label.SetBackgroundColour(editor_bg)

        s = btn_scheme if btn_scheme is not None else default_color_scheme()
        dis = default_disabled_scheme()
        self._save_btn = FlatButton(self, save_label, color_scheme=s, disabled_scheme=dis)
        self._save_btn.SetMinSize((-1, 28))
        self._save_btn.SetAction(self._on_save_clicked)

        container_sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer.Add(editor_row, 1, wx.EXPAND)
        container_sizer.Add(scroll_row, 0, wx.EXPAND)
        self._container.SetSizer(container_sizer)

        bottom = wx.BoxSizer(wx.HORIZONTAL)
        bottom.Add(self._status_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        bottom.Add(self._save_btn, 0, wx.RIGHT | wx.TOP | wx.BOTTOM, 6)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self._container, 1, wx.EXPAND)
        outer.Add(sep, 0, wx.EXPAND)
        outer.Add(bottom, 0, wx.EXPAND)
        self.SetSizer(outer)

        self.SetSize(920, 720)
        self.SetMinSize((580, 460))
        self.CentreOnParent()

        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _setup_editor(self) -> None:
        s = self._syntax_scheme if self._syntax_scheme is not None else default_python_scheme()
        self._syntax_scheme = s
        ed = self._editor
        editor_bg, editor_fg = s[0], s[1]
        sel_bg = s[4]

        apply_python_highlighting(ed, s, self._font_size, self._mono_face)

        ed.SetCaretForeground(editor_fg)
        ed.SetSelBackground(True, sel_bg)
        ed.SetSelForeground(False, editor_fg)

        ed.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        ed.SetMarginWidth(0, 44)
        ed.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        ed.SetMarginWidth(1, 4)
        ed.SetMarginBackground(1, editor_bg)

        ed.SetTabWidth(4)
        ed.SetUseTabs(False)
        ed.SetIndent(4)
        ed.SetTabIndents(True)
        ed.SetBackSpaceUnIndents(True)
        ed.SetIndentationGuides(stc.STC_IV_LOOKBOTH)

        ed.SetEOLMode(stc.STC_EOL_LF)
        ed.SetViewEOL(False)
        ed.SetViewWhiteSpace(stc.STC_WS_INVISIBLE)
        ed.SetScrollWidth(1)
        ed.SetScrollWidthTracking(True)

        ed.SetUseVerticalScrollBar(False)
        ed.SetUseHorizontalScrollBar(False)

        ed.Bind(stc.EVT_STC_CHARADDED, self._on_char_added)
        ed.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)
        ed.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        ed.Bind(wx.EVT_SIZE, self._on_editor_size)

    def _on_update_ui(self, event: stc.StyledTextEvent) -> None:
        ed = self._editor
        total = ed.GetLineCount()
        visible = ed.LinesOnScreen()
        first = ed.GetFirstVisibleLine()
        if total <= visible:
            self._vscrollbar.Update(0.0, 1.0)
        else:
            scrollable = total - visible
            self._vscrollbar.Update(first / scrollable, visible / total)

        scroll_width = ed.GetScrollWidth()
        client_width = ed.GetClientSize().width
        x_offset = ed.GetXOffset()
        if scroll_width <= client_width:
            self._hscrollbar.Update(0.0, 1.0)
        else:
            scrollable_w = scroll_width - client_width
            self._hscrollbar.Update(
                min(x_offset / scrollable_w, 1.0),
                client_width / scroll_width,
            )
        event.Skip()

    def _on_vsb_scroll(self, fraction: float) -> None:
        ed = self._editor
        total = ed.GetLineCount()
        visible = ed.LinesOnScreen()
        scrollable = max(1, total - visible)
        ed.ScrollToLine(round(fraction * scrollable))

    def _on_hsb_scroll(self, fraction: float) -> None:
        ed = self._editor
        scroll_width = ed.GetScrollWidth()
        client_width = ed.GetClientSize().width
        scrollable_w = max(1, scroll_width - client_width)
        ed.SetXOffset(round(fraction * scrollable_w))

    def _on_editor_size(self, event: wx.SizeEvent) -> None:
        self._on_update_ui(stc.StyledTextEvent(stc.wxEVT_STC_UPDATEUI))
        event.Skip()

    def _on_wheel(self, event: wx.MouseEvent) -> None:
        ed = self._editor
        delta = event.GetWheelRotation() // event.GetWheelDelta()
        ed.ScrollToLine(max(0, ed.GetFirstVisibleLine() - delta * 3))
        self._on_update_ui(stc.StyledTextEvent(stc.wxEVT_STC_UPDATEUI))

    def _on_char_added(self, event: stc.StyledTextEvent) -> None:
        if event.GetKey() == ord("\n"):
            self._auto_indent()
        event.Skip()

    def _auto_indent(self) -> None:
        ed = self._editor
        line = ed.GetCurrentLine()
        if line == 0:
            return
        prev = ed.GetLine(line - 1)
        indent = len(prev) - len(prev.lstrip())
        if prev.rstrip().endswith(":"):
            indent += 4
        ed.SetLineIndentation(line, indent)
        ed.GotoPos(ed.GetLineIndentPosition(line))

    def bind_save(self, callback: Callable[[str], None]) -> None:
        self._on_save_cb = callback

    def load_source(self, source: str) -> None:
        self._editor.SetValue(source)
        self._editor.EmptyUndoBuffer()
        self._editor.GotoPos(0)
        self.set_status("")

    def get_source(self) -> str:
        return self._editor.GetValue()

    def set_status(
        self,
        text: str,
        ok_color: Optional[wx.Colour] = None,
        error_color: Optional[wx.Colour] = None,
        error: bool = False,
    ) -> None:
        """Update the status bar text.

        ok_color:    color when text is non-empty and not an error (default: green)
        error_color: color when error=True (default: red)
        """
        if ok_color is None:
            ok_color = wx.Colour(106, 190, 130)
        if error_color is None:
            error_color = wx.Colour(210, 80, 80)
        fg = self._syntax_scheme[1]  # editor_fg (dim)
        color = error_color if error else (ok_color if text else fg)
        self._status_label.SetLabel(text)
        self._status_label.SetForegroundColour(color)
        self._status_label.Refresh()

    def _on_save_clicked(self, _e=None) -> None:
        if self._on_save_cb is not None:
            self._on_save_cb(self._editor.GetValue())

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Hide()
        else:
            event.Skip()
