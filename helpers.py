import wx
import copy

class DFAWindow(wx.Window):
    pen_color = 'Black'
    pen_thickness = 1
    
    def __init__(self, nfa_states, parent):
        super(DFAWindow, self).__init__(parent, size=(800, 600),
                                           style=wx.NO_FULL_REPAINT_ON_RESIZE)
                                           
        self.states = {}
        self.nfa_states = nfa_states
        self.clicked_state = None 
        self.set_initial_state()
        
        self.init_drawing()
        self.setup_buttons()
        self.bind_events()
        self.init_buffer()
        
    def set_initial_state(self):
        for state in self.nfa_states.iterkeys():
            if state.get_type() == 1:
                new_state = copy.deepcopy(state)
                new_state.arcs.clear()
                self.states[new_state] = self.nfa_states[state]
                break
                
    def setup_buttons(self):
        wx.Button(self, 1, 'Select', (0, 0), (100, 40))
        self.Bind(wx.EVT_BUTTON, self.select_state, id=1)
        wx.Button(self, 2, 'Expand', (100, 0), (100, 40))
        self.Bind(wx.EVT_BUTTON, self.expand_state, id=2)
    
    def init_drawing(self):
        self.drawingState = 0
        self.SetBackgroundColour('WHITE')
        self.currentThickness = self.pen_thickness
        self.currentColour = self.pen_color
        self.lines = []
        self.previousPosition = (0, 0)

    def bind_events(self):
        for event, handler in [
                (wx.EVT_LEFT_DOWN, self.on_left_down),  # Start drawing
                (wx.EVT_LEFT_UP, self.on_left_up),  # Stop drawing
                (wx.EVT_MOTION, self.on_motion),  # Draw
                (wx.EVT_SIZE, self.on_size),  # Prepare for redraw
                (wx.EVT_IDLE, self.on_idle),  # Redraw
                (wx.EVT_PAINT, self.on_paint)  # Refresh
                ]:
            self.Bind(event, handler)

    def init_buffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.reInitBuffer = False

    def expand_state(self, event):
        self.drawingState = 1
        
    def select_state(self, event):
        self.drawingState = 0
        
    def on_left_down(self, event):
        if self.drawingState == 0:
            click_position = event.GetPositionTuple()
            self.selected_state = None
            for state in self.states.iterkeys():
                    state.set_selected(False)
                    if state.is_within(click_position):
                        self.selected_state = state
                        break
            if self.selected_state is not None:
                self.selected_state.set_selected(True)
            self.CaptureMouse()
        elif self.drawingState == 1:
            click_position = event.GetPositionTuple()
            self.clicked_state = None
            for state in self.states.iterkeys():
                if state.is_within(click_position):
                    self.clicked_state = state
                    break
            if self.clicked_state is not None:
                self.expand(self.clicked_state)
                
        self.redraw()
    
    def expand(self, state):
        # find the state in nfa_states
        for state_in_nfa in self.nfa_states.iterkeys():
            if state_in_nfa.state_name == self.clicked_state.state_name:
                # find the states to which the current state has arcs
                for arc_to_state in self.nfa_states.iterkeys():
                    print arc_to_state.state_name
                    if arc_to_state in state_in_nfa.arcs.keys():
                        # copy the state to be added to dfa
                        if not state_in_nfa.arcs[arc_to_state].is_lambda_trans():
                            new_state = copy.deepcopy(arc_to_state)
                            new_state.arcs.clear()
                            self.states[new_state] = self.nfa_states[arc_to_state]
                            self.clicked_state.add_arc(new_state, state_in_nfa.arcs[arc_to_state].get_value())
                        else:
                            if len(state_in_nfa.arcs[arc_to_state].get_value()) > 1:
                                trans = state_in_nfa.arcs[arc_to_state].get_value().split(':', 1) 
                                trans_values = state_in_nfa.arcs[arc_to_state].get_value()[
                                               state_in_nfa.arcs[arc_to_state].get_value().index(':') + 1:].split(',')
                                new_state = copy.deepcopy(arc_to_state)
                                new_state.arcs.clear()
                                self.states[new_state] = self.nfa_states[arc_to_state]
                                for val in trans_values:
                                    if val == unichr(955):
                                        continue;
                                    else:                                        
                                        if new_state in self.clicked_state.arcs.iterkeys():
                                            self.clicked_state.add_new_arc_value(new_state, val)
                                        else:
                                            self.clicked_state.add_arc(new_state, trans[0] + ':' + val)
                                            
                        

    def redraw(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()
        self.Refresh(False)
        dc.BeginDrawing()
        pen = wx.Pen(wx.NamedColour(self.pen_color), self.pen_thickness, wx.SOLID)
        brush = wx.Brush(self.pen_color, wx.TRANSPARENT)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        for state in self.states.iterkeys():
            state.draw(dc)

        dc.EndDrawing()

    def on_left_up(self, event):
        if self.HasCapture():
            if self.selected_state is not None:
                self.selected_state.set_selected(False)
                self.selected_state = None
            self.ReleaseMouse()
    
    def on_motion(self, event):
        if event.Dragging() and event.LeftIsDown() and self.drawingState == 0\
                and self.selected_state is not None:
            self.selected_state.set_position(event.GetPositionTuple())
            for state in self.states.iterkeys():
                for arc in state.arcs.keys():
                    if arc == self.selected_state:
                        state.arcs[self.selected_state].change_end_pos(event.GetPositionTuple())
            self.redraw()

    def on_size(self, event):
        self.reInitBuffer = True

    def on_idle(self, event):
        if self.reInitBuffer:
            self.init_buffer()
            self.redraw()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

        
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
        for arc in self.controller.clicked_state.arcs.iterkeys():
            label_name = self.controller.clicked_state.state_name+'->'+arc.state_name
            self.sizer.Add(wx.StaticText(self.panel, label=label_name+":"), (i, 0))
            new_text_box = wx.TextCtrl(self.panel, size=(140, -1))
            new_text_box.SetValue(self.controller.clicked_state.arcs[arc].get_value()
                                  [self.controller.clicked_state.arcs[arc].get_value().index(':') + 1:])
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
        new_name = self.editname.GetValue()
        state_nb = int(new_name[new_name.index('q') + 1:])
        if state_nb in self.controller.states.values():
            return
        self.controller.reusableStateNames.append(int(self.controller.clicked_state.state_name
                                                      [self.controller.clicked_state.state_name.index('q') + 1:]))
        self.controller.states[self.controller.clicked_state] = state_nb
        
        self.controller.clicked_state.set_name(new_name)
        i = 0
        for arc in self.controller.clicked_state.arcs.iterkeys():
            self.controller.clicked_state.set_arc_value(arc, new_name+'->'+arc.state_name + ':' +
                                                       self.text_boxes[i].GetValue())
            i += 1
        self.controller.redraw()

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
        self.lambda_button = wx.Button(self.panel, label=unichr(955))
        self.lblname = wx.StaticText(self.panel, label="Transition values:")
        self.values = wx.TextCtrl(self.panel, size=(140, -1))
        self.values.SetValue(unichr(955))
        
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.lblname, (0, 0))
        self.sizer.Add(self.values, (0, 1))
        self.sizer.Add(self.finish_button, (1, 0))
        self.sizer.Add(self.lambda_button, (1, 1))
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.finish_button.Bind(wx.EVT_BUTTON, self.on_finish)
        self.lambda_button.Bind(wx.EVT_BUTTON, self.on_lambda)

    def on_finish(self, event):
        start_state = filter(lambda x: x.get_position() == self.controller.startPos.get_position(),
                             self.controller.states.iterkeys())
        end_state = filter(lambda x: x.get_position() == self.controller.endPos.get_position(),
                           self.controller.states.iterkeys())
        if self.controller.endPos in start_state[0].arcs.iterkeys():
            start_state[0].add_new_arc_value(self.controller.endPos, self.values.GetValue())
        else:
            start_state[0].add_arc(self.controller.endPos, self.controller.startPos.state_name+'->' +
                                   end_state[0].state_name+":"+self.values.GetValue())
        self.controller.endPos = None
        self.controller.startPos = None
        self.controller.redraw()
        self.controller.Enable()
        self.Close()
        
    def on_lambda(self, event):
        self.values.SetValue(self.values.GetValue() + unichr(955))


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
        self.sim_button = wx.Button(self.panel, label="Step by step simulation")
        self.input = wx.TextCtrl(self.panel, size=(140, -1))
        
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.runlblname, (0, 0))
        self.sizer.Add(self.input, (0, 1))
        self.sizer.Add(self.resultlbl, (1, 0))
        self.sizer.Add(self.run_button, (2, 0))
        self.sizer.Add(self.sim_button, (2, 1))
        self.sizer.Add(self.close_button, (2, 2))
        
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.close_button.Bind(wx.EVT_BUTTON, self.on_finish)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)
        self.sim_button.Bind(wx.EVT_BUTTON, self.on_simulation)

    def on_finish(self, event):
        self.controller.Enable()
        self.Close()

    def on_run(self, event):
        self.resultlbl.SetLabel("Running...")
        self.resultlbl.SetLabel(self.controller.verify_input(self.input.GetValue()))

    def on_simulation(self, event):
        self.controller.setup_sim()
        sim_window = SimWind(self.controller)
        sim_window.Show()        

class SimWind(wx.Frame):
    def __init__(self, controller, parent=None):
        super(SimWind, self).__init__(parent, size=(200, 200))
        self.controller = controller
        self.controller.Disable()
        self.panel = wx.Panel(self)
        self.defaultColor = self.panel.GetBackgroundColour()
        self.next_button = wx.Button(self.panel, label="Step")
        self.close_button = wx.Button(self.panel, label="Close")
        self.input = self.controller.run_win.input.GetValue()
        self.input_values = []
        self.input_sizer = wx.GridBagSizer()
        self.button_sizer = wx.GridBagSizer()
        self.string_index = 0
        self.result = wx.StaticText(self.panel)        
        if self.controller.doodle.start_state is None:
            self.result.SetLabel("No Start State")
        elif self.input == "":
            self.result.SetLabel("No Input")
        self.font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)
        
        self.sizer = wx.GridBagSizer(5, 5)

        i = 0
        for c in self.input:            
            new_text_box = wx.StaticText(self.panel)
            new_text_box.SetLabel(c)
            new_text_box.SetFont(self.font)
            new_text_box.SetForegroundColour('Black')
            self.input_values.append(new_text_box)
            self.input_sizer.Add(new_text_box, (0, i))            
            i += 1
        
        self.sizer.Add(self.input_sizer, (0, 0))
        self.button_sizer.Add(self.next_button, (0, 0))
        self.button_sizer.Add(self.close_button, (0, 1))
        self.sizer.Add(self.result, (1, 0))
        self.sizer.Add(self.button_sizer, (2, 0))

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        self.next_button.Bind(wx.EVT_BUTTON, self.on_next)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_finish)

    def on_finish(self, event):
        for state in self.controller.doodle.states:
            state.current = False
            state.bad_input = False
            state.ok_input = False
        self.controller.doodle.redraw()
        self.controller.Enable()
        self.Close()

    def on_next(self, event):
        if self.controller.doodle.start_state is not None and self.controller.finish is False:
            if self.string_index > 0:
                self.input_values[self.string_index - 1].SetLabel(self.input_values[self.string_index - 1].GetLabel())
                self.input_values[self.string_index - 1].SetBackgroundColour(self.defaultColor)
                self.input_values[self.string_index - 1].SetForegroundColour('Black')
            if self.string_index < len(self.input_values):
                self.input_values[self.string_index].SetLabel(self.input_values[self.string_index].GetLabel())
                self.input_values[self.string_index].SetBackgroundColour('White')
                self.input_values[self.string_index].SetForegroundColour('Red')
                self.result.SetLabel(self.controller.sim_step(self.input[self.string_index],
                                         True if self.string_index == len(self.input) - 1 else False))
                self.controller.doodle.redraw()
                self.string_index += 1


class WarningWind(wx.Frame):
    def __init__(self, controller, text, parent=None):
        super(WarningWind, self).__init__(parent, size=(200, 200))
        self.controller = controller
        self.controller.Disable()
        self.panel = wx.Panel(self)
        self.finish_button = wx.Button(self.panel, label="Ok")
        self.lblname = wx.StaticText(self.panel, label=text)
    
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.lblname, (0, 0))
        self.sizer.Add(self.finish_button, (1, 0))
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizerAndFit(self.border)
        self.SetSizerAndFit(self.windowSizer)

        # Set event handlers
        self.finish_button.Bind(wx.EVT_BUTTON, self.on_finish)

    def on_finish(self, event):
        self.controller.Enable()
        self.Close()


class ConvertWind(wx.Frame):
    def __init__(self, controller, parent):
        super(ConvertWind, self).__init__(parent, size=(800, 640))
        
        self.doodle = DFAWindow(controller.doodle.states, self)
