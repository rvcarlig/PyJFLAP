from enum import Enum
from State import State, StateType
from helpers import InputWind, TransWind
import wx


class EditorState(Enum):
    Select = 0
    DrawCircle = 1
    DrawTransition = 2
    Delete = 3


# noinspection PyAttributeOutsideInit,PyUnusedLocal,PyIncorrectDocstring
class DoodleWindow(wx.Window):
    pen_color = 'Black'
    pen_thickness = 1

    def __init__(self, parent):
        super(DoodleWindow, self).__init__(parent, size=(800, 600),
                                           style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.states = {}
        self.currentState = 0
        self.reusableStateNames = []
        self.stateNames = {}
        self.arcs = []

        self.init_drawing()
        self.make_menu()
        self.setup_buttons()
        self.bind_events()
        self.init_buffer()

    def setup_buttons(self):
        wx.Button(self, 1, 'Select', (0, 0), (100, 40))
        wx.Button(self, 2, 'Draw State', (100, 0), (100, 40))
        wx.Button(self, 3, 'Draw Transition', (200, 0), (100, 40))
        wx.Button(self, 4, 'Delete', (300, 0), (100, 40))
        self.Bind(wx.EVT_BUTTON, self.change_state, id=1)
        self.Bind(wx.EVT_BUTTON, self.change_state, id=2)
        self.Bind(wx.EVT_BUTTON, self.change_state, id=3)
        self.Bind(wx.EVT_BUTTON, self.change_state, id=4)

    def init_drawing(self):
        self.drawingState = EditorState.DrawCircle
        self.SetBackgroundColour('WHITE')
        self.currentThickness = self.pen_thickness
        self.currentColour = self.pen_color
        self.lines = []
        self.previousPosition = (0, 0)
        self.startPos = None
        self.endPos = None

    def bind_events(self):
        for event, handler in [
                (wx.EVT_LEFT_DOWN, self.on_left_down),  # Start drawing
                (wx.EVT_LEFT_UP, self.on_left_up),  # Stop drawing
                (wx.EVT_MOTION, self.on_motion),  # Draw
                (wx.EVT_RIGHT_UP, self.on_right_up),  # Popup menu
                (wx.EVT_SIZE, self.on_size),  # Prepare for redraw
                (wx.EVT_IDLE, self.on_idle),  # Redraw
                (wx.EVT_PAINT, self.on_paint),  # Refresh
                (wx.EVT_WINDOW_DESTROY, self.clean_up)]:
            self.Bind(event, handler)

    def init_buffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.reInitBuffer = False

    def change_state(self, event):
        print event.GetId()
        self.drawingState = EditorState(event.GetId() - 1)

    def make_menu(self):
        self.menu = wx.Menu()
        file_item = self.menu.Append(wx.NewId(), 'Start State', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.make_start_state, file_item)

        file_item = self.menu.Append(wx.NewId(), 'End State', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.make_end_state, file_item)

        file_item = self.menu.Append(wx.NewId(), 'Edit State', kind = wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.change_state_name, file_item)

    def change_state_name(self, event):
        if self.clicked_state is not None:
            input = InputWind(self)
            input.Show()
            print "changing"

    def make_start_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.Start)
            self.redraw()

    def make_end_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.End)
            self.redraw()

    def on_left_down(self, event):
        if self.drawingState == EditorState.DrawCircle:
            self.previousPosition = event.GetPositionTuple()
            print self.previousPosition
            state_nb = self.currentState
            if self.reusableStateNames:
                state_nb = self.reusableStateNames[0]
                del self.reusableStateNames[0]
            else:
                self.currentState += 1
            new_state = State(event.GetPositionTuple(), 'q' + str(state_nb))
            self.states[new_state] = state_nb
        elif self.drawingState == EditorState.DrawTransition:
            click_position = event.GetPositionTuple()
            if self.startPos is None:
                for state in self.states.iterkeys():
                    if state.is_within(click_position):
                        self.startPos = state
                        break
            else:
                for state in self.states.iterkeys():
                    if state.is_within(click_position):
                        self.endPos = state
                        input = TransWind(self)
                        input.Show()
                        break
                               
                #temp_state = filter(lambda x: x.get_position() == self.startPos.get_position(), self.states.iterkeys())
                #temp_state[0].add_arc(self.endPos, self.values)
                #self.endPos = None
                #self.startPos = None
        elif self.drawingState == EditorState.Delete:
            click_position = event.GetPositionTuple()
            for state, stateNb in self.states.iteritems():
                    if state.is_within(click_position):
                        for state2 in self.states.keys():
                            if state2.contains_arc(state):                                
                                self.reusableStateNames.append(self.states[state2])
                                state2.remove_arc(state)
                        del self.states[state]
                        self.reusableStateNames.append(stateNb)
                        self.reusableStateNames.sort()
                        break
        else:
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
        self.redraw()

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

    def on_right_up(self, event):
        click_position = event.GetPositionTuple()
        self.clicked_state = None
        for state in self.states.iterkeys():
            if state.is_within(click_position):
                self.clicked_state = state
                break
        if self.clicked_state is not None:
            self.PopupMenu(self.menu)

    def on_motion(self, event):
        """ Called when the mouse is in motion. If the left button is
            dragging then draw a line from the last event position to the
            current one. Save the coordinates for redraws. """
        if event.Dragging() and event.LeftIsDown() and self.drawingState == EditorState.Select\
                and self.selected_state is not None:
            self.selected_state.set_position(event.GetPositionTuple())
            self.redraw()

    def on_size(self, event):
        """ Called when the window is resize. We set a flag so the idle
            handler will resize the buffer. """
        self.reInitBuffer = True

    def on_idle(self, event):
        """ If the size was changed then resize the bitmap used for double
            buffering to match the window size.  We do it in Idle time so
            there is only one refresh after resizing is done, not lots while
            it is happening. """
        if self.reInitBuffer:
            self.init_buffer()
            self.redraw()

    def on_paint(self, event):
        """ Called when the window is exposed.
         Create a buffered paint DC.  It will create the real
         wx.PaintDC and then blit the bitmap to it when dc is
         deleted.  Since we don't need to draw anything else
         here that's all there is to it. """
        dc = wx.BufferedPaintDC(self, self.buffer)

    def clean_up(self, event):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu


        
