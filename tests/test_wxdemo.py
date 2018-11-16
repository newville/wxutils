from __future__ import print_function

import time
import os
import sys
import wx

is_wxPhoenix = 'phoenix' in wx.PlatformInfo
if is_wxPhoenix:
    PyDeadObjectError = RuntimeError
else:
    from wx._core import PyDeadObjectError

from wxutils import (Button, CEN, Check, Choice, EditableListBox, FRAMESTYLE,
                     FileOpen, FileSave, FloatCtrl, FloatSpin, Font, GUIColors,
                     GridPanel, LabeledTextCtrl, HLine, HyperText, LCEN, LEFT,
                     MenuItem, Popup, RCEN, RIGHT, RowPanel, SimpleText,
                     TextCtrl, fix_filename, get_icon, pack)


class DemoFrame(wx.Frame):
    def __init__(self):

        wx.Frame.__init__(self, None, -1, 'wxutil demo',
                          style=wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL)
        self.SetTitle('wxutil demo')

        self.SetFont(Font(11))

        self.set_menu()
        self.statusbar = self.CreateStatusBar(2, 1)
        self.statusbar.SetStatusWidths([-2, -1])
        statusbar_fields = ['Initializing....', ' ']
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        self.Bind(wx.EVT_CLOSE, self.onExit)

        panel  = GridPanel(self, nrows=8, ncols=4)

        tctrl_name = TextCtrl(panel, value='', action=self.onName,
                              size=(250, -1))

        lctrl_addr = LabeledTextCtrl(self, value='<>', action=self.onAddr,
                                     labeltext=' Address: ', size=(250, -1))

        lab3 = HyperText(panel,' Float1: ', size=(100, -1), action=self.onHyperText)

        val3 = FloatCtrl(panel, '3', action=self.onFloat1, precision=2,
                         minval=0, maxval=1000, size=(250, -1))


        lab4 = HyperText(panel,' Float2: ', size=(100, -1), action=self.onHyperText)

        val4 = FloatSpin(panel, '12.2', action=self.onFloatSpin, digits=2,
                         increment=0.1, size=(250, -1))

        self.choice1 = Choice(panel, choices=['Apple', 'Banana', 'Cherry'],
                          size=(200, -1),
                         action=self.onChoice)

        check1 = Check(panel, label='enable? ',   action=self.onCheck)

        btn1 = Button(panel, label='Start', size=(100, -1), action=self.onStart)

        panel.AddText(' Name: ', style=LEFT)

        panel.Add(tctrl_name, dcol=2)
        panel.Add(lctrl_addr.label, newrow=True)
        panel.Add(lctrl_addr, dcol=2)

        panel.Add(lab3, newrow=True)
        panel.Add(val3, dcol=3)

        panel.Add(lab4, newrow=True)
        panel.Add(val4, dcol=3)
        panel.AddText(' Choice : ', newrow=True)
        panel.Add(check1)
        panel.Add(self.choice1)
        panel.Add(HLine(panel, size=(500, -1)), dcol=3, newrow=True)

        panel.Add(btn1, newrow=True)

        panel.pack()

        self.timer = wx.Timer(self)
        self.last_time = time.time()
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add(panel, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.EXPAND)
        wx.CallAfter(self.init_timer)
        pack(self, fsizer)
        self.Refresh()

    def init_timer(self):
        self.timer.Start(500)

    def onTimer(self, event):
        idle_time = (time.time() - self.last_time)
        msg = "Time remaining = %.1f sec" % (30 - idle_time)
        self.statusbar.SetStatusText(msg, 1)
        if (time.time() - self.last_time) > 30:
            print("quitting...")
            self.onExit()

    def report(self, reason, value):
        self.statusbar.SetStatusText("%s: %s" % (reason, value), 0)
        self.last_time = time.time()

    def set_menu(self):
        menu = wx.Menu()
        mexit = MenuItem(self, menu, "Q&uit", "Quit Program", self.onExit)

        menubar = wx.MenuBar()
        menubar.Append(menu, "&File");
        self.SetMenuBar(menubar)

    def onName(self, event=None):
        self.report("on Name: ", event)

    def onAddr(self, event=None):
        self.report("on Addr: ", event)

    def onHyperText(self, event=None, label=None):
        self.report("on HyperText ", label)

    def onFloat1(self, value=None):
        self.report("on Float1 ", value)

    def onFloatSpin(self, event=None):
        self.report("on FloatSpin ", event.GetString())

    def onChoice(self, event=None):
        self.report("on Choice ", event.GetString())

    def onCheck(self, event=None):
        self.report("on Check ", event.IsChecked())

        self.choice1.Enable(event.IsChecked())


    def onStart(self, event=None):
        self.report("on Start Button ", '')

    def onBrowseScript(self, event=None):
        wildcards = "%s|%s" % (PY_FILES, ALL_FILES)

        dlg = wx.FileDialog(self, message='Select Python Script file',
                            wildcard=wildcards,
                            style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = os.path.abspath(dlg.GetPath())
            self.txt_script.SetValue(path)

            _, name = os.path.split(path)
            name = fix_filename(name)
            if name.endswith('.py'):
                name = name[:-3]

            txt_name = self.txt_name.GetValue().strip()
            if len(txt_name) < 1:
                self.txt_name.SetValue(name)

            txt_desc = self.txt_desc.GetValue().strip()
            if len(txt_desc) < 1:
                self.txt_desc.SetValue(name)
        dlg.Destroy()

    def onExit(self, event=None):
        self.Destroy()


def test_wxdemo():
    app = wx.App()
    DemoFrame().Show(True)
    app.MainLoop()


if __name__ == '__main__':
    test_wxdemo()
