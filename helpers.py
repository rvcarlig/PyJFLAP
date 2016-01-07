import wx

class InputWind(wx.Frame):
    def __init__(self, controller, parent=None):
        super(InputWind, self).__init__(parent, size=(200, 200))
        self.controller = controller
        self.controller.Disable()
        self.panel = wx.Panel(self)
        self.update_button = wx.Button(self.panel, label="Update")
        self.finish_button = wx.Button(self.panel, label="Finish")
        self.lblname = wx.StaticText(self.panel, label="Your name:")
        self.editname = wx.TextCtrl(self.panel, size=(140, -1))
        self.editname.SetValue(self.controller.clicked_state.state_name)
        self.text_boxes = []

        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.lblname, (0, 0))
        self.sizer.Add(self.editname, (0, 1))
        i = 1
        for arc in self.controller.clicked_state.arcs:
            label_name = self.controller.clicked_state.state_name+'->'+arc.state_name
            self.sizer.Add(wx.StaticText(self.panel, label=label_name+":"), (i, 0))
            new_text_box = wx.TextCtrl(self.panel, size=(140, -1))
            new_text_box.SetValue(self.controller.clicked_state.arcs[arc])
            self.text_boxes.append(new_text_box)
            self.sizer.Add(new_text_box, (i, 1))
            i += 1
        self.sizer.Add(self.update_button, (i, 0))
        self.sizer.Add(self.finish_button, (i, 1))

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.update_button.Bind(wx.EVT_BUTTON, self.on_update)
        self.finish_button.Bind(wx.EVT_BUTTON, self.on_finish)

    def on_update(self, event):
        self.controller.clicked_state.set_name(self.editname.GetValue())
        i = 0
        for arc in self.controller.clicked_state.arcs:
            print "self.controller.clicked_state.update(arc," + self.text_boxes[i].GetValue() +")"
            self.controller.clicked_state.set_arcValue(arc, self.text_boxes[i].GetValue())
            i += 1
        self.controller.redraw()
        # self.clicked_state.set_name(self.editname.GetValue())
        # self.panel.Close()
        # self.redraw()

    def on_finish(self, event):
        self.controller.Enable()
        self.Close()

class TransWind(wx.Frame):
    def __init__(self, controller, parent=None):
        super(TransWind, self).__init__(parent, size=(200, 200))
        self.controller = controller
        self.controller.Disable()
        self.panel = wx.Panel(self)
        self.finish_button = wx.Button(self.panel, label="Ok")
        self.lblname = wx.StaticText(self.panel, label="Transition values:")
        self.values = wx.TextCtrl(self.panel, size=(140, -1))
        
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.lblname, (0, 0))
        self.sizer.Add(self.values, (0, 1))
        self.sizer.Add(self.finish_button, (1, 0))
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.finish_button.Bind(wx.EVT_BUTTON, self.on_finish)

    def on_finish(self, event):
        temp_state = filter(lambda x: x.get_position() == self.controller.startPos.get_position(), self.controller.states.iterkeys())
        temp_state[0].add_arc(self.controller.endPos, self.values.GetValue())
        self.controller.endPos = None
        self.controller.startPos = None
        self.controller.redraw()
        self.controller.Enable()
        self.Close()

class RunWind(wx.Frame):
    def __init__(self, controller, parent=None):
        super(RunWind, self).__init__(parent, size=(200, 200))
        self.controller = controller
        self.controller.Disable()
        self.panel = wx.Panel(self)
        self.run_button = wx.Button(self.panel, label="Run")
        self.runlblname = wx.StaticText(self.panel, label="Input:")
        self.resultlbl = wx.StaticText(self.panel)
        self.close_button = wx.Button(self.panel, label="Close")
        self.input = wx.TextCtrl(self.panel, size=(140, -1))
        
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.runlblname, (0, 0))
        self.sizer.Add(self.input, (0, 1))
        self.sizer.Add(self.resultlbl, (1, 0))
        self.sizer.Add(self.run_button, (2, 0))        
        self.sizer.Add(self.close_button, (2, 1))
        
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.close_button.Bind(wx.EVT_BUTTON, self.on_finish)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)

    def on_finish(self, event):
        self.controller.Enable()
        self.Close()

    def on_run(self, event):
        self.resultlbl.SetLabel("Running...")
        self.resultlbl.SetLabel(self.controller.verifyInput(self.input.GetValue()))
