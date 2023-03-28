#!/usr/bin/env python

"""
A collection of wx utility functions,
mostly simplified wrappers around existing widgets.
"""
import os
import sys
from traceback import format_tb
import wx
from  wx.lib.dialogs import ScrolledMessageDialog

# some common abbrevs for wx ALIGNMENT styles
RIGHT = RCEN = wx.ALIGN_RIGHT
LEFT  = LCEN = wx.ALIGN_LEFT
CEN   = CCEN = wx.ALIGN_CENTER
LTEXT = wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTER
FRAMESTYLE = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL

def SetTip(wid, tip=''):
    wid.SetToolTip(tip)

def set_sizer(panel, sizer=None, style=wx.VERTICAL, fit=False):
    """ utility for setting wx Sizer  """
    if sizer is None:
        sizer = wx.BoxSizer(style)
    panel.SetAutoLayout(1)
    panel.SetSizer(sizer)
    if fit:
        sizer.Fit(panel)

def pack(window, sizer, expand=1.1):
    "simple wxPython pack function"
    tsize =  window.GetSize()
    msize =  window.GetMinSize()
    window.SetSizer(sizer)
    sizer.Fit(window)
    nsize = (10*int(expand*(max(msize[0], tsize[0])/10)),
             10*int(expand*(max(msize[1], tsize[1])/10.)))
    window.SetSize(nsize)

def Font(size, serif=False):
    """define a font by size and serif/ non-serif
    f = Font(10, serif=True)
    """
    family = wx.DEFAULT
    if not serif:
        family = wx.SWISS
    return wx.Font(size, family, wx.NORMAL, wx.BOLD, 0, "")

def SetChildrenFont(widget, font, dsize=None):
    "set font for a widget and all children"
    cfont = widget.GetFont()
    font.SetWeight(cfont.GetWeight())
    if dsize == None:
        dsize = font.PointSize - cfont.PointSize
    else:
        font.PointSize = cfont.PointSize + dsize
    widget.SetFont(font)
    for child in widget.GetChildren():
        set_font_with_children(child, font, dsize=dsize)

def HLine(parent, size=(700, 3)):
    """Simple horizontal line
    h = HLine(parent, size=(700, 3)
    """
    return wx.StaticLine(parent, size=size, style=wx.LI_HORIZONTAL|wx.GROW)

def HLineText(panel, text, colour='#222288'):
    """draw an Horizontal line, then SimpleText underneath
    HLineText(panel, text, **kws)
    keywords are passed to SimpleText
    """
    p = wx.Panel(panel)
    s = wx.BoxSizer(wx.HORIZONTAL)
    s.Add(wx.StaticLine(p, size=(50, 5), style=wx.LI_HORIZONTAL), 0, LEFT, 5)
    s.Add(SimpleText(p, text,  **kws),  0, LEFT, 5)
    pack(p, s)
    return p

class Check(wx.CheckBox):
    """Simple Checkbox
    c = Check(parent, default=True, label=None, **kws)
    kws passed to wx.CheckBox
    """
    def __init__(self, parent, label='', default=True, action=None, **kws):
        wx.CheckBox.__init__(self, parent, -1, label=label, **kws)
        self.SetValue({True: 1, False:0}[default])
        if action is not None:
            self.Bind(wx.EVT_CHECKBOX, action)

def MenuItem(parent, menu, label='', longtext='', action=None, kind='normal',
             checked=False):
    """Add Item to a Menu, with action
    m = Menu(parent, menu, label, longtext, action=None, kind='normal')
    """
    kinds_map = {'normal': wx.ITEM_NORMAL,
                 'radio': wx.ITEM_RADIO,
                 'check': wx.ITEM_CHECK}
    menu_kind = wx.ITEM_NORMAL
    if kind in kinds_map.values():
        menu_kind = kind
    elif kind in kinds_map:
        menu_kind = kinds_map[kind]

    item = menu.Append(-1, label, longtext, kind=menu_kind)
    if menu_kind == wx.ITEM_CHECK and checked:
        item.Check(True)

    if callable(action):
        parent.Bind(wx.EVT_MENU, action, item)
    return item


def Popup(parent, message, title, style=None, **kws):
    """Simple popup message dialog
    p = Popup(parent, message, title, **kws)
    returns output of MessageDialog.ShowModal()
    """
    if style is None:
        style = wx.OK|wx.ICON_INFORMATION
    dlg = wx.MessageDialog(parent, message, title, style=style, **kws)
    ret = dlg.ShowModal()
    dlg.Destroy()
    return ret



def ExceptionPopup(parent, title, lines, with_traceback=True,
                   style=None, **kws):
    """Modal message dialog with current Python Exception"""
    if style is None:
        style = wx.OK|wx.ICON_INFORMATION

    etype, exc, tb = sys.exc_info()
    if with_traceback:
        lines.append("Traceback (most recent calls last):")
        for tline in format_tb(tb):
            if tline.endswith('\n'): tline = tline[:-1]
            lines.append(tline)
    lines.append(f"{etype.__name__}: {exc}")

    message = '\n'.join(lines)
    dkws = {'size': (700, 350)}
    dkws.update(kws)
    dlg = ScrolledMessageDialog(parent, message, title, **dkws)
    dlg.ShowModal()
    dlg.Destroy()


def get_homedir():
    "determine home directory"
    homedir = None
    def check(method, s):
        "check that os.path.expanduser / expandvars gives a useful result"
        try:
            if method(s) not in (None, s):
                return method(s)
        except:
            pass
        return None

    # try expanding '~' -- should work on most Unixes
    homedir = check(os.path.expanduser, '~')

    # try the common environmental variables
    if homedir is  None:
        for var in ('$HOME', '$HOMEPATH', '$USERPROFILE', '$ALLUSERSPROFILE'):
            homedir = check(os.path.expandvars, var)
            if homedir is not None:
                break

    # For Windows, ask for parent of Roaming 'Application Data' directory
    if homedir is None and os.name == 'nt':
        try:
            from win32com.shell import shellcon, shell
            homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        except ImportError:
            pass

    # finally, use current folder
    if homedir is None:
        homedir = os.path.abspath('.')
    return homedir


def get_cwd():
    """get current working directory
    Note: os.getcwd() can fail with permission error.

    when that happens, this changes to the users `HOME` directory
    and returns that directory so that it always returns an existing
    and readable directory.
    """
    try:
        return os.getcwd()
    except:
        curdir = os.path.abspath('.')
        os.chdir(curdir)
        return home

def gcd(parent=None, **kws):
    """Directory Browser to Change Directory"""
    if parent is None:
        parent = wx.GetApp()

    dlg = wx.DirDialog(parent, 'Choose Directory',
                       defaultPath = get_cwd(),
                       style = wx.DD_DEFAULT_STYLE)

    if dlg.ShowModal() == wx.ID_OK:
        os.chdir(dlg.GetPath())
    dlg.Destroy()
    return get_cwd()


def panel_pack(window, panel, pad=10):
    """
    a simple method to pack a single panel to a single frame
    """
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(panel, 1, wx.LEFT, 5)
    window.SetSizer(sizer)
    sizer.Fit(window)
    w0, h0 = window.GetSize()
    w1, h1 = window.GetBestSize()
    window.SetSize((max(w0, w1)+pad, max(h0, h1)+pad))

def show_wxsizes(obj):
    """recursively show sizes of wxPython objects --
    useful for avoiding size<1 errors"""
    for child in obj.GetChildren():
        try:
            csize = child.GetSize()
            if csize[0] < 1 or csize[1] < 1:
                print(child, csize)
        except:
            pass
        try:
            show_wxsizes(child)
        except:
            pass
