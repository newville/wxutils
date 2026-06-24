#!/usr/bin/env python
"""
  simplified wx widgets and utilities
"""
from .version import version as __version__
__author__  = 'Matthew Newville'

import sys
import wx

if sys.platform.lower() == 'darwin':
    wx.PyApp.IsDisplayAvailable = lambda _: True

from . import utils

from .utils import (gcd, ExceptionPopup, set_sizer, pack, panel_pack,
                    set_widget_value, get_widget_value,
                    show_wxsizes, SetTip, Font, HLine, Check, MenuItem, Popup,
                    RIGHT, LEFT, CEN , LCEN, RCEN, CCEN, LTEXT, FRAMESTYLE)

from .colors import (COLORS, GUI_COLORS, GUIColors,
                     get_color, set_color, DARK_THEME, is_dark_theme,
                     register_darkdetect, use_darkdetect,
                     default_color_scheme, default_disabled_scheme, default_check_scheme, default_text_scheme, default_combo_scheme, default_scrollbar_scheme, default_splitter_scheme,
                     ColorScheme, DisabledColorScheme, CheckedColorScheme, TextScheme, ComboScheme, ScrollBarScheme, SplitterScheme)

from .base import EnableBase, EnableControl, EnablePanel

from .buttons import Button, ToggleButton, BitmapButton, FlatButton
from .inputs import FlatCheckBox, FlatTextCtrl, FlatCombo
from .scrollbars import FlatScrollBar, FlatHScrollBar
from .splitter import FlatSplitter
from .display import StatusField, SectionDivider
from .choice import Choice, YesNo
from .dates import hms, DateTimeCtrl
from .dialogs import (OkCancel, FileOpen, FileSave, SelectWorkdir,
                      SavedParameterDialog)
from .text import SimpleText, TextCtrl, LabeledTextCtrl, HyperText
from .filechecklist import FileCheckList, FileDropTarget
from .listbox import EditableListBox
from .gridpanel import GridPanel, RowPanel
from .icons import get_icon
from .floats import (make_steps, set_float, FloatCtrl, NumericCombo,
                     FloatSpin, FloatSpinWithPin)

from .notebooks import flatnotebook
from .periodictable import  PeriodicTablePanel
from .passwords import (random_salt, hash_password, password_rules,
                        PasswordSetDialog, PasswordCheckDialog)
from .paths import (platform, nativepath, get_homedir, get_configfile,
                    save_configfile, get_cwd)
