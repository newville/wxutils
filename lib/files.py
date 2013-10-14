#!/usr/bin/env python
"""
file utilities
"""
import os
import wx
from string import maketrans

def fix_filename(fname):
    """
    fix string to be a 'good' filename. This may be a more
    restrictive than the OS, but avoids nasty cases.
    """
    badchars = ' <>:"\'\\\t\r\n/|?*!%$'
    out = fname.translate(maketrans(badchars, '_'*len(badchars)))
    if out[0] in '-,;[]{}()~`@#':
        out = '_%s' % out
    return out

def FileOpen(parent, message, default_dir=None, default_file=None,
             multiple=False, wildcard=None):
    """File Open dialog wrapper.
    returns full path on OK or None on Cancel
    """
    out = None
    if default_dir is None:
        default_dir = os.getcwd()
    if wildcard is None:
        wildcard = 'All files (*.*)|*.*'

    style = wx.OPEN|wx.CHANGE_DIR
    if multiple:
        style = style|wx.MULTIPLE
    dlg = wx.FileDialog(parent, message=message, wildcard=wildcard,
                        defaultFile=default_file,
                        defaultDir=default_dir,
                        style=style)

    out = None
    if dlg.ShowModal() == wx.ID_OK:
        out = os.path.abspath(dlg.GetPath())
    dlg.Destroy()
    return out

def FileSave(parent, message, default_file=None,
             default_dir=None,  wildcard=None):
    "File Save dialog"
    out = None
    if wildcard is None:
        wildcard = 'All files (*.*)|*.*'

    if default_dir is None:
        default_dir = os.getcwd()

    dlg = wx.FileDialog(parent, message=message, wildcard=wildcard,
                        defaultFile=default_file,
                        style=wx.SAVE|wx.CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        out = os.path.abspath(dlg.GetPath())
    dlg.Destroy()
    return out

def SelectWorkdir(parent,  message='Select Working Folder...'):
    "prompt for and change into a working directory "
    dlg = wx.DirDialog(parent, message,
                       style=wx.DD_DEFAULT_STYLE|wx.DD_CHANGE_DIR)

    path = os.path.abspath(os.curdir)
    dlg.SetPath(path)
    if  dlg.ShowModal() == wx.ID_CANCEL:
        return None
    path = os.path.abspath(dlg.GetPath())
    dlg.Destroy()
    os.chdir(path)
    return path
