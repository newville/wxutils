import wx

from typing import Callable, Optional

class Button(wx.Button):
    """Simple button with bound action
    b = Button(parent, label, action=None, **kws)

    """
    def __init__(self, parent: wx.Window, label: str, action: Optional[Callable] = None, **kws) -> None:
        super(Button, self).__init__(parent=parent, label=label, **kws)
        if action is not None:
            self.SetAction(action)

    def SetAction(self, action: Callable) -> None:
        self.Bind(wx.EVT_BUTTON, handler=action)

    def RemoveAction(self, action: Callable) -> None:
        self.Unbind(wx.EVT_BUTTON, handler=action)


def BitmapButton(parent, bmp, action=None, tooltip=None, size=(20, 20), **kws):
    b = wx.BitmapButton(parent, id=-1, bitmap=bmp, size=size, **kws)
    if action is not None:
        parent.Bind(wx.EVT_BUTTON, action, b)
    if tooltip is not None:
        b.SetToolTip(tooltip)
    return b

def ToggleButton(parent, label, action=None, tooltip=None,
                 size=(25, 25), **kws):
    b = wx.ToggleButton(parent, -1, label, size=size, **kws)
    if action is not None:
        b.Bind(wx.EVT_TOGGLEBUTTON, action)
    if tooltip is not None:
        b.SetToolTip(tooltip)
    return b
