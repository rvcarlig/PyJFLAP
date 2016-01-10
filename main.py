import wx
from Window import DoodleWindow
from helpers import RunWind, WarningWind, ConvertWind
from State import StateType


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class DoodleFrame(wx.Frame):
    def __init__(self, parent=None):
        super(DoodleFrame, self).__init__(parent, title="Doodle Frame",
                                          size=(800, 640),
                                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.setup_menu()
        self.doodle = DoodleWindow(self)
        self.current_state = None

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

        file_item = file_menu.Append(101, 'Run')
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
        self.doodle.clear()

    def on_open(self, event):
        open_file_dialog = wx.FileDialog(self, "Open", "", "",
                                         "Python files (*.py)|*.py",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        open_file_dialog.ShowModal()
        self.doodle.load(open_file_dialog.GetPath())
        open_file_dialog.Destroy()

    def on_save(self, event):
        save_file_dialog = wx.FileDialog(self, "Save As", "", "",
                                         "Python files (*.py)|*.py",
                                         wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        save_file_dialog.ShowModal()
        self.doodle.save(save_file_dialog.GetPath())
        save_file_dialog.Destroy()

    def on_run(self, event):
        self.run_win = RunWind(self)
        self.run_win.Show()

    def on_convert(self, event):
        for state in self.doodle.states.iterkeys():
            if state.type == StateType.Start:
                break
        else:
            wind = WarningWind(self, "Initial state needed!")
            wind.Show()
        if not self.doodle.check_nfa():
            wind = WarningWind(self, "Not a NFA!")
            wind.Show()
        else:
            dfa_win = ConvertWind(self, self)
            dfa_win.Show()

    def on_check(self, event):
        if event.GetMenu() == self.check_menu:
            self.Close()
    
    def verify_input(self, input_str):
        if input_str == "":
            return "No input"
        current_state = None
        if self.doodle.start_state is None:
            return "No Start State"
        else:
            current_state = self.doodle.start_state
            
        complete = True
        
        for c in input_str:
            for arc in current_state.arcs:
                if c in current_state.arcs[arc]:
                    current_state = arc
                    break
            else:
                complete = False

        if current_state.type == StateType.End and complete == True:
            return "Input accepted!"
        else:
            return "Input rejected!"

    def sim_step(self, character, is_last):
        for arc in self.current_state.arcs:
            if character in self.current_state.arcs[arc]:
                self.current_state.current = False
                self.current_state = arc
                self.current_state.current = True
                break
        else:
            self.complete = False

        if self.complete:
            if is_last:
                if self.current_state.type == StateType.End:
                    self.current_state.ok_input = True
                    self.finish = True
                    return "Input accepted!"                
                else:
                    self.current_state.bad_input = True
                    self.finish = True
                    return "Input rejected!"
            else:
                return ""
        else:
            self.current_state.bad_input = True
            self.finish = True
            return "Input rejected!"

    def setup_sim(self):
        if self.doodle.start_state is not None:
            self.doodle.start_state.current = True
        self.current_state = self.doodle.start_state
        self.complete = True
        self.finish = False
        self.doodle.redraw()
        
if __name__ == '__main__':
    app = wx.App()
    frame = DoodleFrame()
    frame.Show()
    app.MainLoop()
