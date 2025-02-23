import wx


DARK_THEME = False
try:
    import darkdetect
    DARK_THEME = darkdetect.isDark()
except ImportError:
    pass

COLORS = {'text': wx.Colour(0, 0, 0),
          'text_bg': wx.Colour(255, 255, 255),
          'text_invalid': wx.Colour(240, 0, 10),
          'text_invalid_bg': wx.Colour(253, 253, 90),
          'bg': wx.Colour(240,240,230),
          'hyperlink': wx.Colour(0, 0, 60),
          'nb_active': wx.Colour(254,254,195),
          'nb_area': wx.Colour(250,250,245),
          'nb_text': wx.Colour(10,10,180),
          'nb_activetext': wx.Colour(80,10,10),
          'title': wx.Colour(80,10,10),
          'pvname': wx.Colour(10,10,80),
          'list_bg': wx.Colour(255, 255, 250),
          'list_fg': wx.Colour(5, 5, 25),
          'hline': wx.Colour(80, 80, 200),
          'pt_frame_bg':  wx.Colour(253, 253, 250),
          'pt_fg':  wx.Colour( 20,  20, 120),
          'pt_bg': wx.Colour(253, 253, 250),
          'pt_fgsel': wx.Colour(200,   0,   0),
          'pt_bgsel': wx.Colour(250, 250, 200),
        }

if DARK_THEME:
    COLORS = {'text': wx.Colour(255, 255, 255),
             'text_bg': wx.Colour(25, 25, 25),
             'text_invalid': wx.Colour(240, 0, 10),
             'text_invalid_bg': wx.Colour(220, 220, 60),
             'bg': wx.Colour(20, 20, 20),
             'hyperlink': wx.Colour(200, 200, 255),
             'nb_active': wx.Colour(50, 50, 20),
             'nb_area': wx.Colour(10,10,2),
             'nb_text': wx.Colour(10,10,180),
             'nb_activetext': wx.Colour(100,10,10),
             'title': wx.Colour(80,10,10),
             'pvname': wx.Colour(10,10,80),
             'list_bg': wx.Colour(5, 5, 0),
             'list_fg': wx.Colour(5, 5, 125),
             'hline': wx.Colour(220, 220, 250),
             'pt_frame_bg':  wx.Colour(10, 10, 10),
             'pt_fg':  wx.Colour(180,  200, 250),
             'pt_bg': wx.Colour(10, 10, 10),
             'pt_fgsel': wx.Colour(250, 180,  200),
             'pt_bgsel': wx.Colour(30, 20, 80),
    }


# attribitue interface
class GUIColors(object):
    def __init__(self):
        for key, rgb in COLORS.items():
            setattr(self, key,rgb)

GUI_COLORS = GUIColors()

def set_color(widget, color, bg=None):
    if color not in COLORS:
        color = 'text'
    widget.SetForegroundColour(COLORS[color])
    if bg is not None:
        if bg not in COLORS:
            color = 'bg'
        method = widget.SetBackgroundColour(COLORS[bg])
