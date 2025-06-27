import time
import os
import sys
import wx
from functools import partial

from wxutils import (Button, CEN, Check, Choice, EditableListBox, OkCancel,
                     FRAMESTYLE, FileOpen, FileSave, FloatCtrl, FloatSpin,
                     Font, COLORS, set_color, GridPanel, LabeledTextCtrl, HLine,
                     HyperText, LEFT, MenuItem, Popup, RIGHT, RowPanel,
                     SimpleText, TextCtrl, get_icon, pack,
                     BitmapButton, ToggleButton, YesNo, NumericCombo,
                     make_steps)

from wxutils.passwords import PasswordCheckDialog, PasswordSetDialog

class PWFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'wxutil password demo',
                          style=wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER)
        self.SetTitle('wx password demo')

        self.pwhash = None

        self.Bind(wx.EVT_CLOSE, self.onExit)
        panel = GridPanel(self)

        self.set_btn = Button(panel, label='Set Password',
                             size=(175, -1), action=self.onSetPW)

        self.check_btn = Button(panel, label='Check Password',
                           size=(175, -1), action=self.onCheckPW)

        self.check_btn.Disable()

        panel.AddText(' Set: ', style=LEFT)
        panel.Add(self.set_btn)

        panel.AddText(' Check: ', style=LEFT, newrow=True)
        panel.Add(self.check_btn)

        panel.pack()

        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add(panel, 0, LEFT|wx.EXPAND)
        pack(self, fsizer)
        self.Refresh()

    def onCheckPW(self, evt=None):
        dlg = PasswordCheckDialog(self, self.pwhash)
        valid = dlg.GetResponse()
        dlg.Destroy()
        print("Password Valid? ", valid)

    def onSetPW(self, evt=None):
        dlg = PasswordSetDialog(self, self.pwhash)
        pwhash = dlg.GetResponse()
        dlg.Destroy()
        if len(pwhash) > 30:
            self.check_btn.Enable()
            self.pwhash = pwhash
            print(f"Password hash: {pwhash}")
        else:
             self.pwhash = ''

    def onExit(self, event=None):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    PWFrame().Show()
    app.MainLoop()
