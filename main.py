import wx
from Window import DoodleWindow

# noinspection PyAttributeOutsideInit,PyUnusedLocal
class DoodleFrame(wx.Frame):
    def __init__(self, parent=None):
        super(DoodleFrame, self).__init__(parent, title="Doodle Frame",
                                          size=(800, 640),
                                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.setup_menu()
        doodle = DoodleWindow(self)

    def setup_menu(self):
        menu_bar = wx.MenuBar()

        # File : New Open Save Quit
        file_menu = wx.Menu()
        menu_bar.Append(file_menu, '&File')

        file_item = file_menu.Append(wx.ID_NEW, 'New', 'New sheet')
        self.Bind(wx.EVT_MENU, self.on_new, file_item)

        file_item = file_menu.Append(wx.ID_OPEN, 'Open', 'Open sheet')
        self.Bind(wx.EVT_MENU, self.on_open, file_item)

        file_item = file_menu.Append(wx.ID_SAVE, 'Save', 'Save sheet')
        self.Bind(wx.EVT_MENU, self.on_save, file_item)

        file_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit, file_item)

        # Input: Run(textfield -> values)
        file_menu = wx.Menu()
        menu_bar.Append(file_menu, '&Input')

        file_item = file_menu.Append(wx.ID_EXIT, 'Run')
        self.Bind(wx.EVT_MENU, self.on_run, file_item)
        # Convert: convert to DFA
        file_menu = wx.Menu()
        menu_bar.Append(file_menu, '&Convert')
        file_item = file_menu.Append(wx.ID_EXIT, '&Convert to DFA')
        self.Bind(wx.EVT_MENU, self.on_convert, file_item)

        # Check
        self.check_menu = wx.Menu()
        menu_bar.Append(self.check_menu, 'Check')
        self.Bind(wx.EVT_MENU_OPEN, self.on_check)

        self.SetMenuBar(menu_bar)

    def on_quit(self, event):
        self.Close()

    def on_new(self, event):
        self.Close()

    def on_open(self, event):
        self.Close()

    def on_save(self, event):
        self.Close()

    def on_run(self, event):
        self.Close()

    def on_convert(self, event):
        self.Close()

    def on_check(self, event):
        if event.GetMenu() == self.check_menu:
            self.Close()


if __name__ == '__main__':
    app = wx.App()
    frame = DoodleFrame()
    frame.Show()
    app.MainLoop()
