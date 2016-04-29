import wx
try:
    import launcher
except ImportError:
    launcher = None

class SampleFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Hello World", size=(300, 200))
        self.button_error = wx.Button(self, -1, "Raise Exception")
        self.button_error.Bind(wx.EVT_BUTTON, self.raise_exception)
        self.button_show = wx.Button(self, -1, "Show console window")
        self.button_show.Bind(wx.EVT_BUTTON, self.show_console)
        self.button_hide = wx.Button(self, -1, "Hide console window")
        self.button_hide.Bind(wx.EVT_BUTTON, self.hide_console)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.button_error)
        sizer.Add(self.button_show)
        sizer.Add(self.button_hide)
        self.SetSizer(sizer)
        self.Fit()

    def raise_exception(self, event):
        raise ValueError('intentionally generated error')

    def show_console(self, event):
        launcher.hide_console(False)

    def hide_console(self, event):
        launcher.hide_console(True)


def main():
    app = wx.App()
    top = SampleFrame()
    top.Show()

    # close the console window as soon as the main window shows
    try:
        import launcher
    except ImportError:
        pass # ignore this when testing and running this file directly
    else:
        #~ launcher.close_console()
        launcher.hide_console_until_error()
        top.SetFocus()

    app.MainLoop()

if __name__ == '__main__':
    main()