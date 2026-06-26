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
btn = wxutils.Button(parent, label,  action=onButtonPress, **kws)
```

While this can be viewed as merely a convenience, and not a completely
general solution. But it is a very common pattern, and the
wxutils version hides the ugliest parts of wxPython.

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


## dedicated widgets for working with passwords

The `wxutils.passwords` module has dedicated code and wx widgets for
dealing with Password dialogs, including 'show and hide password'
icons.  These methods can enforce common password rules like length
and number of specials and can generate a "password hash" (which
includes a salt and a number of iterations for the pbkdf2 algorithm)
which is safe to store on disk, and methods to check the password
against an existing hash.  Methods in this module include

* `hash_password()` to convert a password into a safe-to-store
  hash.bimum number of lowercase, upper case,
  digits, special characters.
* `PasswordPanel` which includes a Password TextCtrl that can be
  toggled to show or hide plain text password.
* `PasswordCheckDialog` a dialog to challenge for a password to match an
  existing hash.
* `PasswordSetDialog` a dialog to set a Password, checking that
  password rules are satisfied.


## flat widgets

The `Flat*` family is a set of theme-aware widgets that look consistent across platforms. 
All colors are resolved at paint time from the active `ColorTheme`, so switching the theme 
causes every widget to repaint correctly without re-initialization.

The flat widgets available are:

* ``FlatButton`` a push simple button.
  Accepts an optional ``color_scheme`` 5-tuple ``(idle_bg, hover_bg,
  press_bg, idle_fg, hover_fg)`` and ``disabled_scheme`` 2-tuple ``(bg, fg)``
  to override the theme for that instance.  Use ``SetAction(fn)`` to bind
  a click handler.

* ``FlatIconButton`` a square button that draws a vector icon supplied as
  a ``draw_fn(gc, size)`` callable.  Built-in draw functions: ``draw_plus``,
  ``draw_cross``, ``draw_refresh``, ``draw_cog``, ``draw_folder``,
  ``draw_folder_open``, ``draw_search``, ``draw_trash``,
  ``draw_chevron_left``, ``draw_chevron_right``, ``draw_arrow_up``.

* ``FlatToggleButton`` a two-state toggle that fires ``wx.EVT_TOGGLEBUTTON``.
  ``GetValue()`` returns the current bool state.

* ``FlatRadioButton`` a circular radio dot.

* ``FlatCheckBox`` a themed check box.  ``SetAction(fn)`` receives the new
  ``bool`` value on every change.

* ``FlatTextCtrl`` a text field with placeholder text, optional float-only
  restriction (``SetRestrictToFloat(True)``), centered mode, and an error
  highlight (``SetError(True)``).

* ``FlatCombo`` a themed drop-down selector.  ``SetAction(fn)`` receives the
  selected string.

* ``FlatScrollBar`` and ``FlatHScrollBar`` thin vertical and horizontal
  scrollbars.  The ``on_scroll`` callback receives a float position in
  ``[0, 1]``.  Call ``Update(pos, size)`` to move the thumb programmatically.

* ``FlatSplitter`` a resizable themed split pane.  Accepts an ``orientation`` 
  parameter (``wx.SPLIT_VERTICAL`` by default).

* ``FlatProgressBar`` a labeled progress bar.  ``Update(fraction, label,
  sublabel)`` sets progress.  ``SetElapsed(seconds)`` shows a formatted
  elapsed time; ``ClearElapsed()`` hides it.  ``Reset()`` returns to zero.

* ``FlatTabbedPanel`` a themed tab bar.  Add pages with
  ``AddPage(title, panel)`` and switch with ``SetSelection(index)``.

* ``FlatMenuBar`` a fully painted menu bar.  ``AppendMenu(title, items,
  shortcuts, callbacks)`` adds a dropdown (``None`` entries become
  separators).  ``AppendAction(title, callback)`` adds a single-action item.

* ``FlatTableHeader``, ``FlatTableRow``, ``FlatScrolledPanel`` a scrollable
  table with a fixed header.

* ``FlatScriptEditorDialog`` a syntax-highlighted Python editor in a
  resizable frame.

* ``FlatMessageDialog``, ``FlatConfirmDialog``, ``FlatWaitDialog`` themed
  modal dialogs.

* ``SectionDivider`` a horizontal rule with a centered label, useful for
  grouping widgets in a panel.

* ``StatusField`` a read-only display box with centered text.


## color themes

All Flat widgets resolve their colors from a global ``ColorTheme`` at paint
time.  Switching the theme causes every widget in the application to repaint
correctly without re-initialization.

``ColorTheme`` is a dataclass with terminal-style color fields — the same
layout used by terminal emulator themes: ``foreground``, ``background``,
``cursor_fg``, ``cursor_bg``, ``selection_fg``, ``selection_bg``, and the
standard 8 normal + 8 bright colors.

Two built-in themes are provided, `light_theme()` and `dark_theme()`.

By default wxutils selects the appropriate built-in automatically based on
the OS setting via `darkdetect`.  To override, call ``set_theme()`` once
after ``wx.App()`` is created and before any widgets are constructed:

```
from wxutils import set_theme, dark_theme
set_theme(dark_theme())
```

To supply a custom theme, construct a ``ColorTheme`` with all fields and
pass it to ``set_theme()``.  ``get_theme()`` returns the currently active
theme anywhere in your code.

Every Flat widget also accepts an optional per-instance scheme parameter
that overrides the theme colors for that widget only.  When the scheme is
``None`` (the default) the widget falls back to ``get_theme()`` at every
paint, so theme switches automatically.  The shape of each scheme
tuple is documented in the widget's constructor.


