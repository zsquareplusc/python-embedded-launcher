import wx

def main():
    app = wx.App(redirect=True)
    top = wx.Frame(None, title="Hello World", size=(300, 200))

    # close the console window as soon as the main window shows
    try:
        import launcher
    except ImportError:
        pass # ignore this when testing and running this file directly
    else:
        launcher.close_console()

    top.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()