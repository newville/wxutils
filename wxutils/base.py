import wx


class EnableControl(wx.Control):
    """Base class that ensures the control is repainted whenever the enabled state changes."""

    def Enable(self, enable=True):
        "Enables/disables the control."
        result = super().Enable(enable)
        self._onEnable(bool(enable))
        return result

    def Disable(self):
        "Disables the control, (same as Enable(False))."
        return self.Enable(False)

    def _onEnable(self, enabled):
        "Called after Enable(). By default it repaints the control. Override to extend."
        self.Refresh()
