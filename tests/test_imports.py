import wx
import time
import unittest
import pytest

from wxutils import (Button, CEN, Check, Choice, EditableListBox,
                     FRAMESTYLE, FileOpen, FileSave, FloatCtrl, Font,
                     GUIColors, GridPanel, HLine, HyperText, LCEN, LEFT,
                     MenuItem, Popup, RCEN, RIGHT, RowPanel, SimpleText,
                     TextCtrl, fix_filename, get_icon, pack)

class TestCase(unittest.TestCase):
    def test_imports(self):
        import wxutils

        assert('Check' in dir(wxutils))

if __name__ == '__main__':
    pytest.main(['-v', '-x', '-s'])
