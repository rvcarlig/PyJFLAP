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
    
    def find_next_states(self, from_state, to_state):
        for arc_to_state in self.nfa_states.iterkeys():
            print arc_to_state.state_name
            if arc_to_state in to_state.arcs.keys():
                # copy the state to be added to dfa
                if not to_state.arcs[arc_to_state].is_lambda_trans():
                    new_state = copy.deepcopy(arc_to_state)
                    new_state.arcs.clear()
                    self.states[new_state] = self.nfa_states[arc_to_state]
                    self.clicked_state.add_arc(new_state, to_state.arcs[arc_to_state].get_value())
                else:
                    if len(to_state.arcs[arc_to_state].get_value()) > 1:
                        trans = to_state.arcs[arc_to_state].get_value().split(':', 1) 
                        trans_values = to_state.arcs[arc_to_state].get_value()[
                                       to_state.arcs[arc_to_state].get_value().index(':') + 1:].split(',')
                        new_state = copy.deepcopy(arc_to_state)
                        new_state.arcs.clear()
                        self.states[new_state] = self.nfa_states[arc_to_state]
                        for val in trans_values:
                            if val == unichr(955):
                                self.find_next_states(from_state, arc_to_state)
                            else:                                        
                                if new_state in self.clicked_state.arcs.iterkeys():
                                    self.clicked_state.add_new_arc_value(new_state, val)
                                else:
                                    self.clicked_state.add_arc(new_state, trans[0] + ':' + val)
                                    
    def expand(self, state):
        # find the state in nfa_states
        for state_in_nfa in self.nfa_states.iterkeys():
            if state_in_nfa.state_name == self.clicked_state.state_name:
                # find the states to which the current state has arcs
                self.find_next_states(state, state_in_nfa)
                                            
                        
    
                
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
