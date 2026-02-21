# wxutils

wxutils is a Python library with a collection utilities and
convenience functions for wxPython.  It is by no means comprehensive,
but aims to simplify wxPython code, reduce boiler-plate, make wxPython
coding a bit more python-like.


## convenience functions

A large share of the classes in wxutils are simplified versions of wxPython
widgets with common programming attributes and patterns.  For example,
a commmon pattern to create a Button in wxPython

```
import wx
btn = wx.Button(parent, label=label, **kws)
btn.Bind(wx.EVT_BUTTON, onButtonPress)
```

becomes

```
import wxutils
btn = wxutils.Button(parent, label,  action=action, **kws)
`

Yes, this can be viewed as merely a convenience, and not a completely
general solution. But it is a remarkably common pattern, and the
wxutils form hides the ugliest parts of wxPython.

There are several similar convenience widgets, including Check, Choice, and
SimpleText (a simplified variant of StaticText), MenuItem, Font, HLine,
OkCancel, HyperText.

In addition, there are more complex widgets:

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


## colors and dark mode

wxPython supports switching between Dark Mode and Light Mode, and will
automatically make this switch when the system setting changes.  While
a nice development, this means that any code that explicitly sets
colors of some widget properties would either have to set colors for
everything attribute (ignoring the system mode) or select and change
colors based on the mode.

The `wxutils.color` module tries to help with this in a few
ways. First, it uses the `darkdetect` module to identify Dark mode,
and to allow callbacks to run when the mode changes.  Second, it
provides dictionaryes colors for both dark and light mode
(`COLORS_DARK` and `COLORS_LIGHT`) using names for their usage
(`'text'`, `'text_bg'`, `'nb_text'`, and so on) that can be used as
DARK-mode aware values.  The `wxutils.colors.COLORS` attribute will be
either `wxutils.colors.COLORS_DARK` or `wxutils.colors.COLORS_LIGHT`
depending on the mode.  All the `wxutils` classes and functions will
use these, and so respond to changes in the dark mode.  A number of
utility functions in `wxutils.colors` are provided:

* `add_named_color(name, light, dark)`  to add a named color to both
  `COLORS_LIGHT` and `COLORS_DARK`, using either RGB or RGBA tuples.
* `set_color(widget, colorname, bg=None)` to set the foreground (and
  optionally background) color by name in the `COLORS` dictionaries.
* `get_color(name)` to get the color value by name.
* `register_darkdetect(callback)` to define a callback to be run when
  a change in Dark mode is detected.
