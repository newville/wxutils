#!/usr/bin/env python
"""
file utilities
"""
import os
import sys
import time
from pathlib import Path
from collections import namedtuple

import wx

from .gridpanel import GridPanel
from .paths import get_configfile, save_configfile, get_cwd, unixpath

def FileOpen(parent, message, default_dir=None, default_file='',
             multiple=False, wildcard=None):
    """File Open dialog wrapper.
    returns full path on OK or None on Cancel
    """
    out = None
    if default_file is None:
        default_file = ''
    if default_dir is None:
        default_dir = Path('.').absolute().as_posix()

    if wildcard is None:
        wildcard = 'All files (*.*)|*.*'

    style = wx.FD_OPEN|wx.FD_CHANGE_DIR
    if multiple:
        style = style|wx.FD_MULTIPLE
    dlg = wx.FileDialog(parent, message=message, wildcard=wildcard,
                        defaultFile=default_file,
                        defaultDir=default_dir, style=style)

    if dlg.ShowModal() == wx.ID_OK:
        if multiple:
            out = [Path(p).absolute().as_posix() for p in dlg.GetPaths()]
        else:
            out = Path(dlg.GetPath()).absolute().as_posix()
    dlg.Destroy()
    return out

def FileSave(parent, message, default_file=None,
             default_dir=None,  wildcard=None):
    "File Save dialog"
    out = None
    if wildcard is None:
        wildcard = 'All files (*.*)|*.*'

    if default_dir is None:
        default_dir = Path('.').absolute().as_posix()

    dlg = wx.FileDialog(parent, message=message, wildcard=wildcard,
                        defaultFile=default_file,
                        style=wx.FD_SAVE|wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        out = Path(dlg.GetPath()).absolute().as_posix()
    dlg.Destroy()
    return out

def SelectWorkdir(parent,  message='Select Working Folder...'):
    "prompt for and change into a working directory "
    dlg = wx.DirDialog(parent, message,
                       style=wx.DD_DEFAULT_STYLE|wx.DD_CHANGE_DIR)

    path = Path(os.curdir).absolute().as_posix()
    dlg.SetPath(path)
    if  dlg.ShowModal() == wx.ID_OK:
        path = Path(dlg.GetPath()).absolute().as_posix()
        os.chdir(path)
    dlg.Destroy()
    return path


def OkCancel(panel, onOK=None, onCancel=None):
    """Add OK / Cancel buttons
    OkCancel(panel, onOK=None, onCancel=None)
    returns a wx.StdDialogButtonSizer
    """
    btnsizer = wx.StdDialogButtonSizer()
    _ok = wx.Button(panel, wx.ID_OK)
    _no = wx.Button(panel, wx.ID_CANCEL)
    panel.Bind(wx.EVT_BUTTON, onOK,     _ok)
    panel.Bind(wx.EVT_BUTTON, onCancel, _no)
    _ok.SetDefault()
    btnsizer.AddButton(_ok)
    btnsizer.AddButton(_no)
    btnsizer.Realize()
    return btnsizer

class SavedParameterDialog(wx.Dialog):
    """dialog to prompt for string with
    read/write of previous value to config file

    dlg = SavedParameterDialog(label='Prefix',
                               title='Parameter Prompt',
                               configfile='.myparam.dat')
    res = dlg.GetResponse()
    dlg.Destroy()
    if res.ok:
        prefix = res.value

    """
    def __init__(self, label='Value:', title='Parameter Prompt',
                 configfile=None, **kws):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title=title)

        value = ''
        self.configfile = configfile
        if configfile is not None:
            cfile = get_configfile(configfile)
            if cfile is not None:
                with open(cfile, 'r') as fh:
                    for line in fh.readlines():
                        line = line.strip().replace('\n','').replace('\r','')
                        if line.startswith('#') or len(line)<1:
                            continue
                        value = line
                        break


        self.text = wx.TextCtrl(self, value=value, size=(250, -1))
        panel = GridPanel(self, ncols=3, nrows=4, pad=2)
        panel.Add(wx.StaticText(self, label=label), newrow=True)
        panel.Add(self.text)
        panel.Add(OkCancel(self), dcol=2, newrow=True)
        panel.pack()

    def GetResponse(self, master=None, gname=None, ynorm=True):
        self.Raise()
        response = namedtuple('Reponse', ('ok', 'value'))
        ok, value = False, None
        if self.ShowModal() == wx.ID_OK:
            value = self.text.GetValue()
            ok = True
        if ok and self.configfile is not None:
            tout = '# saved %s\n  %s   \n\n' % (time.ctime(), value)
            save_configfile(self.configfile, tout)
        return response(ok, value)
