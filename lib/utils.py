#!/usr/bin/env python
# epics/wx/utils.py
"""
This is a collection of general purpose utility functions and classes,
especially useful for wx functionality
"""
import os
import wx
from string import maketrans
from array import array
from functools import partial

# some common abbrevs for wx ALIGNMENT styles
RIGHT = wx.ALIGN_RIGHT
LEFT  = wx.ALIGN_LEFT
CEN   = wx.ALIGN_CENTER
LCEN  = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT
RCEN  = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
CCEN  = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER
LTEXT = wx.ST_NO_AUTORESIZE|wx.ALIGN_CENTER
FRAMESTYLE = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL

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

def HLineText(panel, text, colour='#222288'):
    """draw an Horizontal line, then SimpleText underneath
    HLineText(panel, text, **kws)
    keywords are passed to SimpleText
    """
    p = wx.Panel(panel)
    s = wx.BoxSizer(wx.HORIZONTAL)
    s.Add(wx.StaticLine(p, size=(50, 5), style=wx.LI_HORIZONTAL), 0, LCEN, 5)
    s.Add(SimpleText(p, text,  **kws),  0, LCEN, 5)
    pack(p, s)
    return p

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


class GUIColors(object):
    """a container for colour attributes
         bg
         nb_active
         nb_area
         nb_text
         nb_activetext
         title
         pvname
    """
    def __init__(self):
        self.bg        = wx.Colour(240,240,230)
        self.nb_active = wx.Colour(254,254,195)
        self.nb_area   = wx.Colour(250,250,245)
        self.nb_text   = wx.Colour(10,10,180)
        self.nb_activetext = wx.Colour(80,10,10)
        self.title     = wx.Colour(80,10,10)
        self.pvname    = wx.Colour(10,10,80)

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

class Check(wx.CheckBox):
    """Simple Checkbox
    c = Check(parent, default=True, label=None, **kws)
    kws passed to wx.CheckBox
    """
    def __init__(self, parent, default=True, label=None, **kws):
        wx.CheckBox.__init__(self, parent, -1, **kws)
        self.SetValue(default)
        if label is not None:
            self.SetLabel(label)

def Button(parent, label, action=None, **kws):
    """Simple button with bound action
    b = Button(parent, label, action=None, **kws)

    """
    thisb = wx.Button(parent, label=label, **kws)
    if hasattr(action, '__call__'):
        parent.Bind(wx.EVT_BUTTON, action, thisb)
    return thisb

def MenuItem(parent, menu, label='', longtext='', action=None):
    """Add Item to a Menu, with action
    m = Menu(parent, menu, label, longtext, action=None)
    """
    wid = wx.NewId()
    menu.Append(wid, label, longtext)
    if hasattr(action, '__call__'):
        wx.EVT_MENU(parent, wid, action)

def Choice(panel, choices, default=0, action=None, **kws):
    """Simple Choice with default and bound action
    c = Choice(panel, choices, default=0, action=None, **kws)
    """
    c = wx.Choice(panel, -1,  choices=choices, **kws)
    c.Select(default)
    c.Bind(wx.EVT_CHOICE, action)
    return c

def Popup(parent, message, title, style=None):
    """Simple popup message dialog
    p = Popup(parent, message, title, **kws)
    returns output of MessageDialog.ShowModal()
    """
    if style is None:
        style = wx.OK|wx.ICON_INFORMATION
    dlg = wx.MessageDialog(parent, message, title, **kws)
    ret = dlg.ShowModal()
    dlg.Destroy()
    return ret

def HLine(parent, size=(700, 3)):
    """Simple horizontal line
    h = HLine(parent, size=(700, 3)
    """
    return wx.StaticLine(parent, size=size, style=wx.LI_HORIZONTAL|wx.GROW)

def EmptyBitmap(width, height, value=255):
    """an empty BitMap of a specifc width and height
    b = EmptyBitmap(width, heigh, value=255)
    """
    data = array.array('B', [value]*3*width*height)
    return wx.BitmapFromBuffer(width, height, data)

class TextCtrl(wx.TextCtrl):
    """simple TextCtrl
    t = TextCtrl(parent, value, font=None
                 colour=None, bgcolour=None,
                 action=None, action_kws=None,
                 act_on_losefocus=True, **kws)
    has a method SetAction(action, action_kws)
    for setting action on RETURN (and optionally LoseFocus)
    """
    def __init__(self, parent, value, font=None,
                 colour=None, bgcolour=None,
                 action=None, action_kws=None,
                 act_on_losefocus=True, **kws):

        self.id = wx.Id()
        self.act_on_losefocus = act_on_losefocus

        this_sty =  wx.TE_PROCESS_ENTER|wx.ALIGN_CENTRE
        if 'style' in kws:
            this_sty = this_sty | kws['style']
        kws['style'] = this_sty
        wx.TextCtrl.__init__(self, parent, self.id, **kws)
        self.SetValue(value)
        if font is not None:
            self.SetFont(font)
        if colour is not None:
            self.SetForegroundColour(colour)
        if bgcolour is not None:
            self.SetBackgroundColour(colour)

        self.SetAction(action, **action_kws)

        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.onFocus)

    def SetAction(self, action, **kws):
        "set action callback"
        self.__act = None
        if hasattr(action,'__call__'):
            self.__act = partial(action, **kws)

    def onFocus(self, evt=None):
        "focus events -- may act on KillFocus"
        if self.act_on_losefocus and self.__act is not None:
            self.__act(self.GetValue())
        evt.Skip()

    def onChar(self, evt=None):
        "character events -- may act on RETURN"
        if evt.GetKeyCode() == wx.WXK_RETURN and self.__act is not None:
            self.__act(self.GetValue())
        evt.Skip()

class SimpleText(wx.StaticText):
    "simple static text wrapper"
    def __init__(self, parent, label, minsize=None,
                 font=None, colour=None, bgcolour=None,
                 style=wx.ALIGN_CENTRE,  **kws):

        wx.StaticText.__init__(self, parent, -1,
                               label=label, style=style, **kws)

        if minsize is not None:
            self.SetMinSize(minsize)
        if font is not None:
            self.SetFont(font)
        if colour is not None:
            self.SetForegroundColour(colour)
        if bgcolour is not None:
            self.SetBackgroundColour(colour)

class HyperText(wx.StaticText):
    """HyperText is a simple extension of wx.StaticText that

       1. adds an underscore to the label to appear to be a hyperlink
       2. performs the supplied action on Left-Up button events
    """
    def  __init__(self, parent, label, action=None,
                  action_kws = None, colour=(50, 50, 180), **kws):
        self.action = action
        if action_kws is None: action_kws = {}
        self.action_kws = action_kws

        wx.StaticText.__init__(self, parent, -1, label=label, **kws)
        font  = self.GetFont()
        try:
            font.SetUnderlined(True)
        except:
            pass
        self.SetFont(font)
        self.SetForegroundColour(colour)
        self.Bind(wx.EVT_LEFT_UP, self.OnSelect)

    def OnSelect(self, event=None):
        "Left-Up Event Handler"
        if hasattr(self.action,'__call__'):
            self.action(self.GetLabel(), event=event, **action_kws)
        event.Skip()

