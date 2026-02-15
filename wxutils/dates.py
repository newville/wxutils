#!/usr/bin/env python
# epics/wx/utils.py
"""
date utilities and widgets
"""
import os
from datetime import timedelta

import wx
import wx.adv as wxadv
from .utils import pack

def hms(secs):
    "format time in seconds to H:M:S"
    return str(timedelta(seconds=int(secs)))

class DateTimeCtrl(wx.Panel):
    """
    Simple Combined date/time control
    """
    def __init__(self, parent, name='datetimectrl', use_now=None):
        self.name = name
        wx.Panel.__init__(self, parent)
        datestyle = wxadv.DP_DROPDOWN|wxadv.DP_SHOWCENTURY|wxadv.DP_ALLOWNONE
        now = wx.DateTime.Now()

        self.datectrl = wxadv.DatePickerCtrl(self, size=(120, -1), dt=now, style=datestyle)
        self.timectrl = wxadv.TimePickerCtrl(self, size=(120, -1), dt=now)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.datectrl, 0, wx.ALIGN_CENTER)
        sizer.Add(self.timectrl, 0, wx.ALIGN_CENTER)
        pack(self, sizer)

    def GetValue(self):
        return {'date': self.datectrl.GetValue(),
                'time': self.timectrl.GetValue()}
