import wx


class EnableBase:
    """Base class that repaints the widget whenever its enabled state changes. Must be used alongside a wx.Window subclass (wx.Control, wx.Panel, etc.)."""

    def Enable(self, enable=True):
        "Enables/disables the widget."
        result = super().Enable(enable)
        self._onEnable(bool(enable))
        return result

    def Disable(self):
        "Disables the widget, (same as Enable(False))."
        return self.Enable(False)

    def _onEnable(self, enabled):
        "Called after Enable(). By default it repaints. Override to extend."
        self.Refresh()


class EnableControl(EnableBase, wx.Control):
    """EnableBase for native-control-based owner-drawn widgets."""
    ...

class EnablePanel(EnableBase, wx.Panel):
    """EnableBase for panel-based owner-drawn widgets."""
    ...

