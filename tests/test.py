import wx

def test_1():
    import wxutils

    assert('Check' in dir(wxutils))

    from wxutils import (Button, CEN, Check, Choice, EditableListBox,
                         FRAMESTYLE, FileOpen, FileSave, FloatCtrl, Font,
                         GUIColors, GridPanel, HLine, HyperText, LCEN,
                         LEFT, MenuItem, Popup, RCEN, RIGHT, RowPanel,
                         SimpleText, TextCtrl, fix_filename, get_icon,
                         pack)
