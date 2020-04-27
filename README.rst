wxutils
=======

wxutils provides wxPython utilities and convenience functions.  The wxutils
library is a small collection of functions and classes, and is by no means
comprehensive.

The aim is to simplify code, reduce boiler-plate, make wxPython coding a
bit more python-like, and prevent repeating code across several projects.

The largest share of classes in wxutils are simplified versions of wxPython
widgets with limited but common attributes and patterns.  For example::

   btn = wxutils.Button(parent, label, action=action, **kws)

binds a callback function (the "action") to a wx.Button, corresponding to::

   b = wx.Button(parent, label=label, **kws)
   if callable(action):
       parent.Bind(wx.EVT_BUTTON, action, b)

Yes, this can be viewed as merely a convenience, and not completely
general.  But it is a remarkably common pattern (at least in my code),
replaces 3 lines with 1, and hides the ugliest parts of wxPython.

There are several similar convenience widgets, including Check, Choice, and
SimpleText (a simplified variant of StaticText), MenuItem, Font, HLine,
OkCancel, HyperText.

In addition, there are more complex widgets, such as

* ``FloatCtrl`` a wx.TextCrtl that allows numerical input only. Precision,
  upper bound, and lower bound can be set, and a callback can be bound to
  the control.

* ``NumericCombo`` wx.ComboBox with a FloatCtrl

* ``EditableListBox`` a list box with a built-in popup menu to arrange order of
  the items with "move up/down, to top, to bottom"

* ``YesNo`` a wx.Choice of only 'No' and 'Yes'

* ``GridPanel`` a combined GridBagSizer and Panel that simplifies adding
  widgets to a GridBagSizer.

* ``FileOpen``, ``FileSave`` wrappers (supporting wildcards) to FileDialog.

And some other miscellaneous stuff as well.  Yeah, it's sort of a motley collection.
