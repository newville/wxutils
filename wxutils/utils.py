#!/usr/bin/env python

"""
A collection of wx utility functions,
mostly simplified wrappers around existing widgets.
"""
import wx

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
