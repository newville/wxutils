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


class GridPanel(wx.Panel):
    """A simple panel with a GridBagSizer
    """
    def __init__(self, parent, nrows=10, ncols=10, **kws):
        wx.Panel.__init__(self, parent, **kws)
        self.sizer = wx.GridBagSizer(nrows, ncols)
        self.irow = 0
        self.icol = 0

    def Add(self, item, irow=None, icol=None, drow=1, dcol=1,
            style=wx.ALIGN_CENTER, newrow=False, pad=0, **kws):
        """add item with default values for col, row, and size"""
        if newrow: self.NewRow()
        if irow is None: irow = self.irow
        if icol is None: icol = self.icol
        self.sizer.Add(item, (irow, icol), (drow, dcol), style, pad, **kws)
        self.icol = self.icol + dcol


    def AddMany(self, items, newrow=False, **kws):
        """add items"""
        if newrow: self.NewRow()
        for item in items:
            self.Add(item, **kws)

    def AddManyText(self, items, newrow=False, **kws):
        """add items"""
        if newrow: self.NewRow()
        for item in items:
            self.AddText(item, **kws)

    def NewRow(self):
        "advance row, set col # = 0"
        self.irow += 1
        self.icol = 0

    def AddText(self, label, newrow=False, dcol=1, style=None, **kws):
        """add a Simple StaticText item"""
        if style is None:
            style = CCEN
        self.Add(SimpleText(self, label, style=style, **kws),
                 dcol=dcol, style=style, newrow=newrow)
        
    def pack(self):
        tsize = self.GetSize()
        msize = self.GetMinSize()

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        nsize = (10*int(1.1*(max(msize[0], tsize[0])/10)),
                 10*int(1.1*(max(msize[1], tsize[1])/10.)))
        self.SetSize(nsize)

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


def Popup(parent, message, title, style=None, **kws):
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

class LabeledTextCtrl(TextCtrl):
    """
    simple extension of TextCtrl with a .label attribute holding a SimpleText
    Typical usage:
      entry = LabeledTextCtrl(self, value='22', labeltext='X:')
      row   = wx.BoxSizer(wx.HORIZONTAL)
      row.Add(entry.label, 1,wx.ALIGN_LEFT|wx.EXPAND)
      row.Add(entry,    1,wx.ALIGN_LEFT|wx.EXPAND)
    """
    def __init__(self, parent, value, font=None, action=None,
                 action_kws=None, act_on_losefocus=True, size=(-1, -1),
                 bgcolour=None, colour=None, style=None,
                 labeltext=None, labelsize=(-1, -1),
                 labelcolour=None, labelbgcolour=None, **kws):

        if labeltext is not None:
            self.label = SimpleText(parent, labeltext, size=labelsize,
                                    font=font, style=style,
                                    colour=labelcolour,
                                    bgcolour=labelbgcolour)

        try:
            value = str(value)
        except:
            value = ' '

        TextCtrl.__init__(self, parent, value, font=font,
                          colour=colour, bgcolour=bgcolour,
                          style=stye, size=size,
                          action=action, action_kws=action_kws,
                          act_on_losefocus=act_on_losefocus, **kws)


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


class EditableListBox(wx.ListBox):
    """
    A ListBox with pop-up menu to arrange order of
    items and remove items from list
    supply select_action for EVT_LISTBOX selection action
    """
    def __init__(self, parent, select_action, right_click=True,
                 remove_action=None, **kws):
        wx.ListBox.__init__(self, parent, **kws)

        self.SetBackgroundColour(wx.Colour(248, 248, 235))
        self.Bind(wx.EVT_LISTBOX,  select_action)
        self.remove_action = remove_action
        if right_click:
            self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
            for item in ('popup_up1', 'popup_dn1',
                         'popup_upall', 'popup_dnall', 'popup_remove'):
                setattr(self, item,  wx.NewId())
                self.Bind(wx.EVT_MENU, self.onRightEvent,
                          id=getattr(self, item))

    def onRightClick(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.popup_up1,    "Move up")
        menu.Append(self.popup_dn1,    "Move down")
        menu.Append(self.popup_upall,  "Move to top")
        menu.Append(self.popup_dnall,  "Move to bottom")
        menu.Append(self.popup_remove, "Remove from list")
        self.PopupMenu(menu)
        menu.Destroy()

    def onRightEvent(self, event=None):
        idx = self.GetSelection()
        if idx < 0: # no item selected
            return
        wid   = event.GetId()
        names = self.GetItems()
        this  = names.pop(idx)
        if wid == self.popup_up1 and idx > 0:
            names.insert(idx-1, this)
        elif wid == self.popup_dn1 and idx < len(names):
            names.insert(idx+1, this)
        elif wid == self.popup_upall:
            names.insert(0, this)
        elif wid == self.popup_dnall:
            names.append(this)
        elif wid == self.popup_remove and self.remove_action is not None:
            self.remove_action(this)

        self.Clear()
        for name in names:
            self.Append(name)
