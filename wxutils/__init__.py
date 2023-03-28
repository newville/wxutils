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
                    show_wxsizes, SetTip, Font, HLine, Check, MenuItem, Popup,
                    RIGHT, LEFT, CEN , LCEN, RCEN, CCEN, LTEXT, FRAMESTYLE)

from .buttons import Button, ToggleButton, BitmapButton
from .choice import Choice, YesNo
from .dates import hms, DateTimeCtrl
from .dialogs import (OkCancel, FileOpen, FileSave, SelectWorkdir,
                      SavedParameterDialog, fix_filename)
from .text import SimpleText, TextCtrl, LabeledTextCtrl, HyperText
from .filechecklist import FileCheckList, FileDropTarget
from .listbox import EditableListBox
from .gridpanel import GridPanel, RowPanel
from .icons import get_icon
from .floats import (make_steps, set_float, FloatCtrl, NumericCombo,
                     FloatSpin, FloatSpinWithPin)

from .notebooks import flatnotebook
from .periodictable import  PeriodicTablePanel

from .paths import (platform, nativepath, get_homedir, get_configfile,
                    save_configfile, get_cwd)

from .colors import GUIColors, COLORS, set_color
