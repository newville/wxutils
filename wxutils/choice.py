import wx
from typing import Optional

from .colors import DialogScheme, default_dialog_scheme
from .buttons import FlatButton


def _dlg_sep(parent: wx.Window, colour: wx.Colour) -> wx.Panel:
    line = wx.Panel(parent, size=(-1, 1))
    line.SetBackgroundColour(colour)
    return line


class Choice(wx.Choice):
    """Simple Choice with default and bound action
    c = Choice(panel, choices, default=0, action=None, **kws)
    """
    def __init__(self, parent, choices=None, default=0,
                 action=None, **kws):
        if choices is None:
            choices = []
        wx.Choice.__init__(self, parent, -1,  choices=choices, **kws)
        self.Select(default)
        self.Bind(wx.EVT_CHOICE, action)

    def SetChoices(self, choices):
        index = 0
        try:
            current = self.GetStringSelection()
            if current in choices:
                index = choices.index(current)
        except:
            pass
        self.Clear()
        self.AppendItems(choices)
        self.SetStringSelection(choices[index])


class YesNo(wx.Choice):
    """
    A simple wx.Choice with choices set to ('No', 'Yes')
    c = YesNo(parent, defaultyes=True, choices=('No', 'Yes'))

    has methods SetChoices(self, choices) and Select(choice)
    """
    def __init__(self, parent, defaultyes=True,
                 choices=('No', 'Yes'), size=(60, -1)):
        wx.Choice.__init__(self, parent, -1, size=size)
        self.choices = choices
        self.Clear()
        self.SetItems(self.choices)
        try:
            default = int(defaultyes)
        except:
            default = 0
        self.SetSelection(default)

    def SetChoices(self, choices):
        self.Clear()
        self.SetItems(choices)
        self.choices = choices

    def Select(self, choice):
        if isinstance(choice, int):
            self.SetSelection(0)
        elif choice in self.choices:
            self.SetSelection(self.choices.index(choice))


class FlatMessageDialog(wx.Dialog):
    """Flat themed message dialog with a single OK button.

    parent: parent wx window
    message: body text
    title: window title bar text
    ok_label: label for the OK button (default 'OK')
    wrap: pixel width to wrap message text at (default 380)
    scheme: optional DialogScheme; defaults to palette colours
    """

    def __init__(
        self,
        parent: wx.Window,
        message: str,
        title: str,
        ok_label: str = 'OK',
        wrap: int = 380,
        scheme: Optional[DialogScheme] = None,
    ) -> None:
        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE)
        s = scheme if scheme is not None else default_dialog_scheme()
        self.SetBackgroundColour(s[0])

        outer = wx.BoxSizer(wx.VERTICAL)

        msg = wx.StaticText(self, label=message)
        msg.SetForegroundColour(s[1])
        msg.SetBackgroundColour(s[0])
        msg.Wrap(wrap)
        outer.Add(msg, 0, wx.ALL, 20)

        outer.Add(_dlg_sep(self, s[3]), 0, wx.EXPAND)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddStretchSpacer()
        btn_ok = FlatButton(self, ok_label, color_scheme=s[4], disabled_scheme=s[5])
        btn_ok.SetMinSize((80, 28))
        btn_ok.SetAction(lambda _e: self.EndModal(wx.ID_OK))
        btn_row.Add(btn_ok, 0, wx.ALL, 8)
        outer.Add(btn_row, 0, wx.EXPAND)

        self.SetSizer(outer)
        self.Fit()
        self.CentreOnParent()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

    def _on_key(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_ESCAPE):
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()


class FlatConfirmDialog(wx.Dialog):
    """Flat themed two-button confirmation dialog.

    parent: parent wx window
    message: body text
    title: window title bar text
    yes_label: label for the affirmative button (default 'Yes')
    no_label: label for the negative button (default 'No')
    yes_scheme: ColorScheme for the affirmative button; defaults to palette
    wrap: pixel width to wrap message text at (default 380)
    scheme: optional DialogScheme; defaults to palette colours
    """

    def __init__(
        self,
        parent: wx.Window,
        message: str,
        title: str,
        yes_label: str = 'Yes',
        no_label: str = 'No',
        yes_scheme=None,
        wrap: int = 380,
        scheme: Optional[DialogScheme] = None,
    ) -> None:
        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE)
        s = scheme if scheme is not None else default_dialog_scheme()
        self.SetBackgroundColour(s[0])

        outer = wx.BoxSizer(wx.VERTICAL)

        msg = wx.StaticText(self, label=message)
        msg.SetForegroundColour(s[1])
        msg.SetBackgroundColour(s[0])
        msg.Wrap(wrap)
        outer.Add(msg, 0, wx.ALL, 20)

        outer.Add(_dlg_sep(self, s[3]), 0, wx.EXPAND)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddStretchSpacer()

        affirm_scheme = yes_scheme if yes_scheme is not None else s[4]
        btn_yes = FlatButton(self, yes_label, color_scheme=affirm_scheme, disabled_scheme=s[5])
        btn_yes.SetMinSize((80, 28))
        btn_yes.SetAction(lambda _e: self.EndModal(wx.ID_YES))

        btn_no = FlatButton(self, no_label, color_scheme=s[4], disabled_scheme=s[5])
        btn_no.SetMinSize((80, 28))
        btn_no.SetAction(lambda _e: self.EndModal(wx.ID_NO))

        btn_row.Add(btn_yes, 0, wx.ALL, 8)
        btn_row.Add(btn_no, 0, wx.TOP | wx.BOTTOM | wx.RIGHT, 8)
        outer.Add(btn_row, 0, wx.EXPAND)

        self.SetSizer(outer)
        self.Fit()
        self.CentreOnParent()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

    def _on_key(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_NO)
        else:
            event.Skip()


class FlatWaitDialog(wx.Dialog):
    """Flat themed blocking dialog for long-running operations.

    Shows a title, body message, and a mutable status line. The OK button
    is disabled until Ready() is called. Disables the parent window while
    open and re-enables it on close.

    parent: parent wx window
    title: window title bar text
    message: static body text (explains what is happening)
    status: initial status line text (default 'Please wait…')
    ok_label: label for the OK button (default 'OK')
    title_colour: optional wx.Colour for the title label; defaults to fg
    wrap: pixel width to wrap message text at (default 400)
    scheme: optional DialogScheme; defaults to palette colours
    """

    def __init__(
        self,
        parent: wx.Window,
        title: str,
        message: str,
        status: str = 'Please wait\u2026',
        ok_label: str = 'OK',
        title_colour: Optional[wx.Colour] = None,
        wrap: int = 400,
        scheme: Optional[DialogScheme] = None,
    ) -> None:
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE & ~wx.CLOSE_BOX,
        )
        s = scheme if scheme is not None else default_dialog_scheme()
        self.SetBackgroundColour(s[0])

        outer = wx.BoxSizer(wx.VERTICAL)

        title_lbl = wx.StaticText(self, label=title)
        title_lbl.SetForegroundColour(title_colour if title_colour else s[1])
        title_lbl.SetBackgroundColour(s[0])
        title_lbl.SetFont(self.GetFont().Bold())
        outer.Add(title_lbl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 20)

        msg_lbl = wx.StaticText(self, label=message)
        msg_lbl.SetForegroundColour(s[2])
        msg_lbl.SetBackgroundColour(s[0])
        msg_lbl.Wrap(wrap)
        outer.Add(msg_lbl, 0, wx.LEFT | wx.RIGHT, 20)

        self._status_lbl = wx.StaticText(self, label='\n' + status)
        self._status_lbl.SetForegroundColour(s[2])
        self._status_lbl.SetBackgroundColour(s[0])
        outer.Add(self._status_lbl, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 20)

        outer.Add(_dlg_sep(self, s[3]), 0, wx.EXPAND)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddStretchSpacer()
        self._ok_btn = FlatButton(self, ok_label, color_scheme=s[4], disabled_scheme=s[5])
        self._ok_btn.SetMinSize((80, 28))
        self._ok_btn.Enable(False)
        self._ok_btn.SetAction(self._on_ok)
        btn_row.Add(self._ok_btn, 0, wx.ALL, 8)
        outer.Add(btn_row, 0, wx.EXPAND)

        self.SetSizer(outer)
        self.Fit()
        self.CentreOnParent()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_CLOSE, lambda _e: None)

        if parent:
            parent.Enable(False)

    def Ready(self, status: str = 'Done.') -> None:
        """Enable the OK button and update the status line."""
        if self:
            self._status_lbl.SetLabel('\n' + status)
            self._ok_btn.Enable(True)
            self._ok_btn.SetFocus()

    def SetStatus(self, status: str) -> None:
        """Update the status line without enabling the OK button."""
        if self:
            self._status_lbl.SetLabel('\n' + status)

    def _on_ok(self, _e=None) -> None:
        parent = self.GetParent()
        if parent:
            parent.Enable(True)
            parent.Raise()
        self.Destroy()

    def _on_key(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_ESCAPE) and self._ok_btn.IsEnabled():
            self._on_ok()
        else:
            event.Skip()
