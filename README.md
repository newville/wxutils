wxutils
=======

wxPython utilities and convenience functions

The  wxutils library is a small collection of convenience functions for
using wxPython.  It is by no means comprehensive.

The aim is to simplify code, reduce boiler-plate, and prevent repeating
code across several projects.

These are primarily simplified widgets with common attributes, such as
      b = button(parent, label, action=action, **kws)

which attaches a callback to a wx.Button, corresponding to
      b = wx.Button(parent, label=label, **kws)
      if hasattr(action, '__call__'):
          parent.Bind(wx.EVT_BUTTON, action, b)

Yes, this is merely a convenience, but covers a remarkably common pattern.
There are several similar widgets.  In addition, there are more complex
widgets, such as:
     FloatCtrl  wx.TextCrtl, allowing numerical input only. Precision,
                upper bound, and lower bound can be set, and a callback
                can be bound to the control.
     NumericCombo  wx.ComboBox with a FloatCtrl
     YesNo      a wx.Choice of only 'No' and 'Yes'

