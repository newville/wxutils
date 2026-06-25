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
                     default_color_scheme, default_disabled_scheme, default_check_scheme, default_text_scheme, default_combo_scheme, default_scrollbar_scheme, default_splitter_scheme, default_radio_scheme, default_toggle_scheme, default_icon_scheme, default_progress_scheme, default_dialog_scheme, default_tab_scheme, default_menu_bar_scheme,
                     ColorScheme, DisabledColorScheme, CheckedColorScheme, TextScheme, ComboScheme, ScrollBarScheme, SplitterScheme, RadioDotScheme, ToggleScheme, IconScheme, ProgressScheme, DialogScheme, TabScheme, MenuBarScheme)

from .base import EnableBase, EnableControl, EnablePanel

from .buttons import Button, ToggleButton, BitmapButton, FlatButton, FlatRadioButton, FlatToggleButton, FlatIconButton
from .inputs import FlatCheckBox, FlatTextCtrl, FlatCombo
from .scrollbars import FlatScrollBar, FlatHScrollBar
from .splitter import FlatSplitter
from .display import StatusField, SectionDivider, FlatProgressBar, FlatTabbedPanel
from .menubar import FlatMenuBar
from .choice import Choice, YesNo, FlatMessageDialog, FlatConfirmDialog, FlatWaitDialog
from .dates import hms, DateTimeCtrl
from .text import SimpleText, TextCtrl, LabeledTextCtrl, HyperText
from .dialogs import OkCancel, FileOpen, FileSave, SelectWorkdir, SavedParameterDialog
from .filechecklist import FileCheckList, FileDropTarget
from .listbox import EditableListBox
from .gridpanel import GridPanel, RowPanel
from .icons import (get_icon,
                    draw_plus, draw_cross, draw_check,
                    draw_chevron_left, draw_chevron_right, draw_chevron_up, draw_chevron_down,
                    draw_refresh, draw_arrow_up, draw_arrow_down,
                    draw_cog, draw_folder, draw_folder_open, draw_search, draw_trash)
from .floats import (make_steps, set_float, FloatCtrl, NumericCombo,
                     FloatSpin, FloatSpinWithPin)

from .notebooks import flatnotebook
from .periodictable import  PeriodicTablePanel
from .passwords import (random_salt, hash_password, password_rules,
                        PasswordSetDialog, PasswordCheckDialog)
from .paths import (platform, nativepath, get_homedir, get_configfile,
                    save_configfile, get_cwd)
