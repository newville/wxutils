import wx

import wx.lib.agw.flatnotebook as flat_nb
from .colors import get_color, register_darkdetect

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_NODRAG

def flatnotebook(parent, paneldict=None, panelkws={},
                 on_change=None, selection=0, style=None, with_dropdown=False,
                 with_nav_buttons=False, with_smart_tabs=False, **kws):
    if style is None:
        style = FNB_STYLE
    if with_dropdown:
        style |= flat_nb.FNB_DROPDOWN_TABS_LIST
    if not with_nav_buttons:
        style |= flat_nb.FNB_NO_NAV_BUTTONS
    if with_smart_tabs:
        style |= flat_nb.FNB_SMART_TABS

    nb = flat_nb.FlatNotebook(parent, agwStyle=style, **kws)
    nb.SetTabAreaColour(get_color('nb_area'))
    nb.SetActiveTabColour(get_color('nb_active'))
    nb.SetNonActiveTabTextColour(get_color('nb_text'))
    nb.SetActiveTabTextColour(get_color('nb_activetext'))

    def onDarkTheme(is_dark=None):
        nb.SetTabAreaColour(get_color('nb_area', dark=is_dark))
        nb.SetActiveTabColour(get_color('nb_active', dark=is_dark))
        nb.SetNonActiveTabTextColour(get_color('nb_text', dark=is_dark))
        nb.SetActiveTabTextColour(get_color('nb_activetext', dark=is_dark))
        wx.CallAfter(nb.Refresh)

    register_darkdetect(onDarkTheme)

    nb.SetPadding(wx.Size(5, 5))

    nb.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))

    nb.DeleteAllPages()
    nb.pagelist = []
    grandparent = parent.GetParent()
    if grandparent is None:
        grandparent = parent
    if paneldict is not None:
        for name, creator in paneldict.items():
            _page = creator(parent=grandparent, **panelkws)
            nb.AddPage(_page,f" {name} ", True)
            nb.pagelist.append(_page)

    if callable(on_change):
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, on_change)


    nb.SetSelection(selection)
    return nb
