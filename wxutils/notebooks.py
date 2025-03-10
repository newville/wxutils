import wx

import wx.lib.agw.flatnotebook as flat_nb
from .colors import GUI_COLORS

FNB_STYLE = flat_nb.FNB_NO_X_BUTTON|flat_nb.FNB_NODRAG

def flatnotebook(parent, paneldict, panelkws={},
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
    nb.SetTabAreaColour(GUI_COLORS.nb_area)
    nb.SetActiveTabColour(GUI_COLORS.nb_active)
    nb.SetNonActiveTabTextColour(GUI_COLORS.nb_text)
    nb.SetActiveTabTextColour(GUI_COLORS.nb_activetext)
    nb.SetPadding(wx.Size(5, 5))

    nb.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))

    nb.DeleteAllPages()
    nb.pagelist = []
    grandparent = parent.GetParent()
    if grandparent is None:
        grandparent = parent
    for name, creator in paneldict.items():
        _page = creator(parent=grandparent, **panelkws)
        nb.AddPage(_page," %s " % name, True)
        nb.pagelist.append(_page)

    if callable(on_change):
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, on_change)


    nb.SetSelection(selection)
    return nb
