#!/usr/bin/env python
"""
Code for floating point controls
"""
import sys
from functools import partial
import wx
from wx.lib.agw import floatspin as fspin

from .icons import get_icon

HAS_NUMPY = False
try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    pass


def make_steps(prec=3, tmin=0, tmax=10, base=10, steps=(1, 2, 5)):
    """make a list of 'steps' to use for a numeric ComboBox
    returns a list of floats, such as
        [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00...]
    """
    steplist = []
    power = -prec
    step = tmin
    while True:
        decade = base**power
        for step in (j*decade for j in steps):
            if step > 0.99*tmin and step <= tmax and step not in steplist:
                steplist.append(step)
        if step >= tmax:
            break
        power += 1
    return steplist

def set_float(val, default=0):
    """ utility to set a floating value,
    useful for converting from strings """
    out = None
    if not val in (None, ''):
        try:
            out = float(val)
        except ValueError:
            return None
        if HAS_NUMPY:
            if numpy.isnan(out):
                out = default
        else:
            if not(out > 0) and not(out<0) and not(out==0):
                out = default
    return out

class FloatCtrl(wx.TextCtrl):
    """ Numerical Float Control::
    wx.TextCtrl that allows only numerical input

    takes a precision argument
    and optional upper / lower bounds
    options:
     action             callback on Enter (or lose focus)
     act_on_losefocus   boolean (default False) to act on lose focus events
     action_kws         keyword args for action

    """
    def __init__(self, parent, value='', minval=None, maxval=None,
                 precision=3, odd_only=False, even_only=False,
                 bell_on_invalid = True,
                 act_on_losefocus=False, gformat=False,
                 action=None, action_kws=None, **kws):

        self.__digits = '0123456789.-e'
        self.__prec   = precision
        self.odd_only = odd_only
        self.even_only = even_only
        if precision is None:
            self.__prec = 0
        self.format   = '%%.%if' % self.__prec
        self.gformat  = gformat
        if gformat:
            self.__prec = max(8, self.__prec)
            self.format = '%%.%ig' % self.__prec

        self.is_valid = True
        self.__val = set_float(value)
        self.__max = set_float(maxval)
        self.__min = set_float(minval)
        self.__bound_val = None
        self.__mark = None
        self.__action = None

        self.fgcol_valid   = "Black"
        self.bgcol_valid   = "White"
        self.fgcol_invalid = "Red"
        self.bgcol_invalid = (254, 254, 80)
        self.bell_on_invalid = bell_on_invalid
        self.act_on_losefocus = act_on_losefocus

        # set up action
        if action_kws is None:
            action_kws = {}
        self.SetAction(action, **action_kws)

        this_sty =  wx.TE_PROCESS_ENTER|wx.TE_RIGHT
        if 'style' in kws:
            this_sty = this_sty | kws['style']
        kws['style'] = this_sty

        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, **kws)

        self.__CheckValid(self.__val)
        self.SetValue(self.__val)

        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_TEXT, self.OnText)

        self.Bind(wx.EVT_SET_FOCUS,  self.OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.__GetMark()

    def SetAction(self, action, **kws):
        "set callback action"
        if hasattr(action,'__call__'):
            self.__action = partial(action, **kws)

    def SetPrecision(self, prec=0, gformat=None):
        "set precision"
        self.__prec = prec
        if gformat is not None:
            self.gformat = gformat
        if self.gformat:
            self.__prec = max(8, self.__prec)
            self.format = '%%.%ig' % self.__prec
        else:
            self.format = '%%.%if' % prec

    def __GetMark(self):
        " keep track of cursor position within text"
        try:
            self.__mark = min(wx.TextCtrl.GetSelection(self)[0],
                              len(wx.TextCtrl.GetValue(self).strip()))
        except:
            self.__mark = 0

    def __SetMark(self, mark=None):
        "set mark for later"
        if mark is None:
            mark = self.__mark
        self.SetSelection(mark, mark)

    def SetValue(self, value=None, act=True):
        " main method to set value "
        if value is None:
            value = wx.TextCtrl.GetValue(self).strip()
        self.__CheckValid(value)
        self.__GetMark()
        value = set_float(value)
        if value is not None:
            wx.TextCtrl.SetValue(self, self.format % value)

        if self.is_valid and hasattr(self.__action, '__call__') and act:
            self.__action(value=self.__val)
        elif not self.is_valid and self.bell_on_invalid:
            wx.Bell()

        self.__SetMark()

    def OnKillFocus(self, event):
        "focus lost"
        self.__GetMark()
        if self.act_on_losefocus and hasattr(self.__action, '__call__'):
            self.__action(value=self.__val)
        event.Skip()

    def OnSetFocus(self, event):
        "focus gained - resume editing from last mark point"
        self.__SetMark()
        event.Skip()

    def OnChar(self, event):
        """ on Character event"""
        key   = event.GetKeyCode()
        entry = wx.TextCtrl.GetValue(self).strip()
        pos   = wx.TextCtrl.GetSelection(self)[0]
        # really, the order here is important:
        # 1. return sends to ValidateEntry
        if key == wx.WXK_RETURN:
            if not self.is_valid:
                wx.TextCtrl.SetValue(self, self.format % set_float(self.__bound_val))
            else:
                self.SetValue(entry)
            return

        # 2. other non-text characters are passed without change
        if (key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255):
            event.Skip()
            return

        # 3. check for multiple '.' and out of place '-' signs and ignore these
        #    note that chr(key) will now work due to return at #2
        ckey = chr(key)
        if ((ckey == '.' and (self.__prec == 0 or '.' in entry)) or
            (ckey != '-' and pos == 0 and entry.startswith('-'))):
            return
        if 'e' in entry:
            if ckey == 'e':
                return
            ind_e = entry.index('e')
            if (ckey == '-' and pos not in (0, ind_e+1)):
                return
        elif (ckey == '-' and '-' in entry):
            return
        # allow 'inf' and '-inf', but very restricted
        if ckey in ('i', 'n', 'f'):
            has_num = any([x in entry for x in self.__digits[:11]])
            if ((ckey in entry) or has_num or
                entry not in ('', '-', '-i', 'i', '-n', 'n', '-f', 'f',
                              '-in', 'in', '-if', 'if',
                             '-nf', 'nf', '-inf', 'inf')):
                return
        elif (ckey != '-' and ckey in self.__digits and
              any([x in ('i', 'n', 'f') for x in entry])):
            return

        # 4. allow digits or +/-inf but not other characters
        if ckey in self.__digits or ckey in ('i', 'n', 'f'):
            event.Skip()

    def OnText(self, event=None):
        "text event"
        try:
            if event.GetString() != '':
                self.__CheckValid(event.GetString())
        except:
            pass
        event.Skip()

    def GetValue(self):
        if self.__prec > 0:
            return set_float("%%.%if" % (self.__prec) % (self.__val))
        else:
            return int(self.__val)

    def GetMin(self):
        "return min value"
        return self.__min

    def GetMax(self):
        "return max value"
        return self.__max

    def SetMin(self, val):
        "set min value"
        self.__min = set_float(val)

    def SetMax(self, val):
        "set max value"
        self.__max = set_float(val)

    def __CheckValid(self, value):
        "check for validity of value"
        val = self.__val
        self.is_valid = True
        try:
            val = set_float(value)
            if self.__min is not None and (val < self.__min):
                self.is_valid = False
                val = self.__min
            if self.__max is not None and (val > self.__max):
                self.is_valid = False
                val = self.__max
            if self.__prec == 0:
                if self.odd_only and (val % 2 == 0):
                    self.is_valid = False
                    val = val + 1
                elif self.even_only and (val %2 == 1):
                    self.is_valid = False
                    val = val + 1
        except:
            self.is_valid = False
        self.__bound_val = self.__val = val
        fgcol, bgcol = self.fgcol_valid, self.bgcol_valid
        if not self.is_valid:
            fgcol, bgcol = self.fgcol_invalid, self.bgcol_invalid

        self.SetForegroundColour(fgcol)
        self.SetBackgroundColour(bgcol)
        self.Refresh()


def FloatSpin(parent, value=0, action=None, tooltip=None, size=(100, -1),
              digits=1, increment=1, use_gtk3=False, **kws):
    """FloatSpin with action and tooltip"""
    if value is None:
        value = 0

    # need to work this out better for GTK3 - lots of small
    # differences with GTK2, but this one is the biggest headache.
    # SpinCtrlDouble is like FloatSpin, but with every option
    # having a slightly different name...
    if use_gtk3 and 'gtk3' in wx.PlatformInfo:
        maxval = kws.pop('max_val', None)
        minval = kws.pop('min_val', None)
        fmt = "%%%df" % digits
        fs = wx.SpinCtrlDouble(parent, -1, value=fmt % value,
                               size=(size[0]+40, size[1]),
                               inc=increment, **kws)
        fs.SetDigits(digits)
        if minval is not None:
            fs.SetMin(minval)
        if maxval is not None:
            fs.SetMax(maxval)

        if action is not None:
            fs.Bind(wx.EVT_SPINCTRLDOUBLE, action)

    else:
        fs = fspin.FloatSpin(parent, -1, size=size, value=value,
                             digits=digits, increment=increment, **kws)

        if action is not None:
            fs.Bind(fspin.EVT_FLOATSPIN, action)
    if tooltip is not None:
        fs.SetToolTip(tooltip)
    return fs


def FloatSpinWithPin(parent, value=0, pin_action=None,
                     tooltip='select point from plot', **kws):
    """create a FloatSpin with Pin button with action"""
    fspin = FloatSpin(parent, value=value, **kws)
    bmbtn = wx.BitmapButton(parent, id=-1, bitmap=get_icon('pin'),
                            size=(25, 25))
    if pin_action is not None:
        parent.Bind(wx.EVT_BUTTON, pin_action, bmbtn)
    bmbtn.SetToolTip(tooltip)
    return fspin, bmbtn

class NumericCombo(wx.ComboBox):
    """
    Numeric Combo: ComboBox with numeric-only choices
    """
    def __init__(self, parent, choices, precision=3, fmt=None,
                 init=0, default_val=None, width=80):

        self.fmt = fmt
        if fmt is None:
            self.fmt = "%%.%if" % precision

        self.choices  = choices
        schoices = [self.fmt % i for i in self.choices]
        wx.ComboBox.__init__(self, parent, -1, '', (-1, -1), (width, -1),
                             schoices, wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)

        init = min(init, len(self.choices))
        if default_val is not None:
            if default_val in schoices:
                self.SetStringSelection(default_val)
            else:
                self.add_choice(default_val, select=True)
        else:
            self.SetStringSelection(schoices[init])
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

    def OnEnter(self, event=None):
        self.add_choice(float(event.GetString()))

    def add_choice(self, val, select=True):
        if val not in self.choices:
            self.choices.append(val)
            self.choices.sort()
        self.choices.reverse()
        self.Clear()
        self.AppendItems([self.fmt % x for x in self.choices])
        if select:
            self.SetSelection(self.choices.index(val))
