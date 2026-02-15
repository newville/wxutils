#!/usr/bin/env python
"""
panel and frame for image display
"""
import wx

class ImagePanel(wx.Panel):
    def __init__(self, parent, image_path=None, size=(700, 500), **kws):
        wx.Panel.__init__(self, parent, **kws)
        self.iw = size[0]
        self.ih = size[1]
        self.image_path = None
        bitmap = wx.Bitmap(self.iw-10, self.ih-10, depth=24)
        self.static_bitmap = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
        if image_path is not None:
            self.showfile(image_path)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.static_bitmap, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizerAndFit(sizer)

    def showfile(self, image_path, title=None):
        self.image_path = image_path
        try:
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            w, h = img.GetSize()
            scale = min((self.iw-5)/(w+1.0), (self.ih-5)/(h+1))
            self.img = img.Scale(int(scale*w-5), int(scale*h-5), wx.IMAGE_QUALITY_HIGH)
            self.static_bitmap.SetBitmap(wx.Bitmap(self.img))
        except:
            wx.MessageBox(f"Cannot load image file '{image_path}'", "Error", wx.OK | wx.ICON_ERROR)
        if title is not None:
            self.SetTitle(title)

    def onSize(self, evt):
        self.iw, self.ih = evt.GetSize()
        if self.image_path is not None:
            self.showfile(self.image_path)
        evt.Skip()

class ImageFrame(wx.Frame):
    def __init__(self, image_path=None, size=(700, 500), pad=5, **kws):
        wx.Frame.__init__(self, None, -1, 'hello', size=size,
                          style=wx.DEFAULT_FRAME_STYLE, **kws)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.image_path = image_path
        self.pad = pad
        self.iw = size[0]
        self.ih = size[1]
        bitmap = wx.Bitmap(self.iw-pad, self.ih-pad, depth=24)
        self.static_bitmap = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        sizer.Add(self.static_bitmap, 1, wx.ALL|wx.EXPAND|wx.GROW, 5)
        self.SetSizerAndFit(sizer)
        self.Layout()
        self.Show()
        self.Bind(wx.EVT_SIZE,  self.onSize)
        self.SetMinSize((self.iw//4, self.ih//4))
        if image_path is not None:
            self.showfile(image_path)

    def showfile(self, image_path, title=None):
        self.image_path = image_path
        try:
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            w, h = img.GetSize()
            scale = min((self.iw-self.pad)/(w+1.0), (self.ih-self.pad)/(h+1))
            self.img = img.Scale(int(scale*w-self.pad), int(scale*h-self.pad), wx.IMAGE_QUALITY_HIGH)
            self.static_bitmap.SetBitmap(wx.Bitmap(self.img))
        except:
            wx.MessageBox(f"Cannot load image file '{image_path}'", "Error", wx.OK | wx.ICON_ERROR)
        if title is not None:
            self.SetTitle(title)


    def onSize(self, evt):
        self.iw, self.ih = evt.GetSize()
        if self.image_path is not None:
            self.showfile(self.image_path)
        evt.Skip()


if __name__ == '__main__':
    app = wx.App()

    frame = ImageFrame(image_path='test.png')
    frame.Show(True)
    frame.Raise()
    app.MainLoop()
