#!/usr/bin/env python
# from distutils.core import setup
from setuptools import setup

long_desc = """A library of convenience functions for wxPython.  The aim
here is to simplify code, reduce boiler-plate, and prevent repeating code
across several projects.

These are primarily simplified widgets with common attributes, such as
      b = button(parent, label, action=action, **kws)

which attaches a callback to a wx.Button, corresponding to
      b = wx.Button(parent, label=label, **kws)
      if hasattr(action, '__call__'):
          parent.Bind(wx.EVT_BUTTON, action, b)

Yes, this is merely a convenience, but covers a remarkably common pattern.
There are several similar widgets.  In addition, there are more complex
widgets, such as:
     FloatCtrl  wx.TextCrtl, allowing numerical input only. Precision,
                upper bound, and lower bound can be set, and a callback
                can be bound to the control.
     NumericCombo  wx.ComboBox with a FloatCtrl
     YesNo      a wx.Choice of only 'No' and 'Yes'

"""

setup(name = 'wxutils',
      version = '0.2.2',
      author = 'Matthew Newville',
      author_email = 'newville@cars.uchicago.edu',
      url          = 'http://newville.github.com/wxutils/',
      download_url = 'http://newville.github.com/wxutils/',
      license = 'BSD',
      description = "Utilities and convenience classes and functions for wxPython",
      long_description = long_desc,
      platforms = ('Windows', 'Linux', 'Mac OS X'),
      classifiers=['Programming Language :: Python'],
      package_dir = {'wxutils': 'lib'},
      packages   = ['wxutils'],
      )
