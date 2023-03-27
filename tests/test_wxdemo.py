import time
import os
import sys
import wx
from functools import partial

from wxutils import (Button, CEN, Check, Choice, EditableListBox, OkCancel,
                     FRAMESTYLE, FileOpen, FileSave, FloatCtrl, FloatSpin,
                     Font, GUIColors, GridPanel, LabeledTextCtrl, HLine,
                     HyperText, LEFT, MenuItem, Popup, RIGHT, RowPanel,
                     SimpleText, TextCtrl, fix_filename, get_icon, pack,
                     BitmapButton, ToggleButton, YesNo, NumericCombo,
                     make_steps)
from wxutils.periodictable import PeriodicTablePanel, PTableFrame
from wxutils.filechecklist import FileCheckList

PY_FILES = "Python scripts (*.py)|*.py"
ALL_FILES = "All files (*.*)|*.*"

class DemoFrame(wx.Frame):
    def __init__(self, idletime=30.0):

        wx.Frame.__init__(self, None, -1, 'wxutil demo',
                          style=wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL)
        self.SetTitle('wxutil demo')

        self.SetFont(Font(11))
        self.idletime = idletime
        self.deadtime = time.time() + idletime

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

        lctrl_addr = LabeledTextCtrl(panel, value='<>', action=self.onAddr,
                                     labeltext=' Address: ', size=(250, -1))

        lab3 = HyperText(panel,' FloatCtrl: ', size=(100, -1), action=self.onHyperText)

        val3 = FloatCtrl(panel, '3', action=self.onFloat1, precision=2,
                         minval=0, maxval=1000, size=(250, -1))


        lab4 = HyperText(panel,' FloatSpin: ', size=(100, -1), action=self.onHyperText)
        val4 = FloatSpin(panel, '12.2', action=self.onFloatSpin, digits=2,
                         increment=0.1, size=(250, -1))

        labx = HyperText(panel,' NumericCombo: ', size=(100, -1), action=self.onHyperText)

        steps = make_steps(prec=1, tmin=0, tmax=100)
        valx = NumericCombo(panel, steps, precision=1)

        self.choice1 = Choice(panel, size=(200, -1),action=self.onChoice)
        self.choice1.SetChoices(['Apple', 'Banana', 'Cherry'])

        yesno = YesNo(panel)

        check1 = Check(panel, label='enable? ',   action=self.onCheck)

        btn1 = Button(panel, label='Start', size=(100, -1), action=self.onStart)

        pinbtn = BitmapButton(panel, get_icon('pin'), size=(50, -1),
                              action=partial(self.onBMButton, opt='pin1'),
                              tooltip='use last point selected from plot')

        togbtn = ToggleButton(panel, 'Press Me',
                              action=self.onToggleButton, size=(100, -1),
                              tooltip='do it, do it now, you will like it')


        browse_btn = Button(panel, 'Open File',
                            action=self.onFileOpen, size=(150, -1))


        okcancel = OkCancel(panel, onOK=self.onOK, onCancel=self.onCancel)

        ptable_btn = Button(panel, 'Show Periodic Table',
                            action=self.onPTable, size=(175, -1))


        edlist_btn = Button(panel, 'Show Editable Listbox',
                            action=self.onEdList, size=(175, -1))

        filelist_btn = Button(panel, 'Show File CheckList',
                            action=self.onFileList, size=(175, -1))


        panel.AddText(' Name: ', style=LEFT)

        panel.Add(tctrl_name, dcol=2)
        panel.Add(lctrl_addr.label, newrow=True)
        panel.Add(lctrl_addr, dcol=2)

        panel.Add(lab3, newrow=True)
        panel.Add(val3, dcol=3)

        panel.Add(lab4, newrow=True)
        panel.Add(val4, dcol=3)

        panel.Add(labx, newrow=True)
        panel.Add(valx, dcol=3)

        panel.AddText(' Choice : ', newrow=True)
        panel.Add(check1)
        panel.Add(self.choice1)
        panel.AddText(' Yes or No: ', newrow=True)
        panel.Add(yesno)
        panel.Add(HLine(panel, size=(500, -1)), dcol=3, newrow=True)

        panel.Add(btn1, newrow=True)
        panel.Add(pinbtn)
        panel.Add(togbtn)

        panel.Add(browse_btn, newrow=True)
        panel.Add(ptable_btn)
        panel.Add(edlist_btn, newrow=True)
        panel.Add(filelist_btn)

        panel.Add(okcancel, newrow=True)
        panel.pack()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

        fsizer = wx.BoxSizer(wx.VERTICAL)
        fsizer.Add(panel, 0, LEFT|wx.EXPAND)
        wx.CallAfter(self.init_timer)

        psize = panel.GetBestSize()
        self.SetSize((psize[0]+5, psize[1]+25))

        pack(self, fsizer)
        self.Refresh()

    def init_timer(self):
        self.timer.Start(100)

    def onTimer(self, event=None):
        time_remaining = self.deadtime  - time.time()

        msg = "Time remaining = %.1f sec" % (time_remaining)
        self.statusbar.SetStatusText(msg, 1)
        if time_remaining < 0:
            print("quitting...")
            self.onExit()

    def report(self, reason, value):
        self.statusbar.SetStatusText("%s: %s" % (reason, value), 0)
        self.deadtime = time.time() + self.idletime

    def set_menu(self):
        menu = wx.Menu()
        mexit = MenuItem(self, menu, "Q&uit", "Quit Program", self.onExit)

        menubar = wx.MenuBar()
        menubar.Append(menu, "&File");
        self.SetMenuBar(menubar)

    def onOK(self, event=None):
        self.report("on OK: ", '')

    def onCancel(self, event=None):
        self.report("on Cancel: ", '')

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

    def onBMButton(self, event=None, opt='xxx'):
        self.report("on Bitmap Button ", opt)

    def onToggleButton(self, event=None):
        self.report(" on Toggle Button %s " % event.GetString(), event.IsChecked())

    def onPTable(self, event=None):
        PTableFrame(fontsize=10).Show()
        self.report("on Periodic Table: ", '')

    def onEdList(self, event=None):
        frame = wx.Frame(self)
        edlist  = EditableListBox(frame, self.onEdListSelect)
        edlist.Append(" Item 1 ")
        edlist.Append(" Item 2 ")
        edlist.Append(" Next ")
        self.report("on Edit List: ", '')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(edlist, 1, wx.EXPAND|wx.ALL, 5)
        pack(frame, sizer)

        frame.Show()
        frame.Raise()

    def onEdListSelect(self, event=None, **kws):
        self.report(" Editable List selected ", event.GetString())

    def onFileList(self, event=None):
        frame = wx.Frame(self)
        edlist  = FileCheckList(frame, select_action=self.onFileListSelect)
        for i in range(8):
            edlist.Append("File.%3.3d" % (i+1))
        self.report("on File List: ", '')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(edlist, 1, wx.EXPAND|wx.ALL, 5)
        pack(frame, sizer)

        frame.Show()
        frame.Raise()

    def onFileListSelect(self, event=None, **kws):
        self.report(" File List selected ", event.GetString())

    def onFileOpen(self, event=None):
        wildcards = "%s|%s" % (PY_FILES, ALL_FILES)

        dlg = wx.FileDialog(self, message='Select File',
                            wildcard=wildcards,
                            style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = os.path.abspath(dlg.GetPath())
            self.report("file ",  path)
        dlg.Destroy()

    def onExit(self, event=None):
        self.Destroy()


def test_wxdemo(idletime=5.0):
    app = wx.App()
    DemoFrame(idletime=idletime).Show(True)
    app.MainLoop()

if __name__ == '__main__':
    test_wxdemo(idletime=30.0)
