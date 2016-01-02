from enum import Enum
from math import sqrt
import wx


class EditorState(Enum):
    Select = 0
    DrawCircle = 1
    DrawTransition = 2
    Delete = 3


class StateType(Enum):
    Normal = 0
    Start = 1
    End = 2


class State:
    def __init__(self, position):
        self.position = position
        self.type = StateType.Normal
        self.radius = 50
        self.arcs = []

    def set_type(self, state_type):
        self.type = state_type

    def add_arc(self, arc):
        self.arcs.append(arc)

    def draw(self, dc):
        if self.type == StateType.Normal:
            dc.DrawCircle(self.position[0], self.position[1], self.radius)
        elif self.type == StateType.End:
            dc.DrawCircle(self.position[0], self.position[1], self.radius)
            dc.DrawCircle(self.position[0], self.position[1], self.radius - 5)
        else:
            dc.DrawCircle(self.position[0], self.position[1], self.radius)
            dc.DrawLine(self.position[0]-self.radius, self.position[1],
                        self.position[0]-2*self.radius, self.position[1]-self.radius)
            dc.DrawLine(self.position[0]-2*self.radius, self.position[1]-self.radius,
                        self.position[0]-2*self.radius, self.position[1]+self.radius)
            dc.DrawLine(self.position[0]-2*self.radius, self.position[1]+self.radius,
                        self.position[0]-self.radius, self.position[1])

        for arc in self.arcs:
            dc.DrawLine(self.position[0], self.position[1], arc.position[0], arc.position[1])

    def get_position(self):
        return self.position

    def is_within(self, pos):
        distance = sqrt(((pos[0] - self.position[0]) ** 2) +
                        ((pos[1] - self.position[1]) ** 2))
        return distance < self.radius


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

    def make_start_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.Start)
            self.redraw()
            print 'make_start_state'

    def make_end_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.End)
            self.redraw()
            print 'make_end_state'

    def on_left_down(self, event):
        if self.drawingState == EditorState.DrawCircle:
            self.previousPosition = event.GetPositionTuple()
            print self.previousPosition
            new_state = State(event.GetPositionTuple())
            state_nb = self.currentState
            if self.reusableStateNames:
                state_nb = self.reusableStateNames[0]
                del self.reusableStateNames[0]
            else:
                self.currentState += 1
            new_state_name = wx.StaticText(self, label = 'q'+str(state_nb), pos=new_state.get_position())
            self.states[new_state] = state_nb             
            self.stateNames[state_nb] = new_state_name

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
                        break
                temp_state = filter(lambda x: x.get_position() == self.startPos.get_position(), self.states.iterkeys())
                temp_state[0].add_arc(self.endPos)
                self.endPos = None
                self.startPos = None
        elif self.drawingState == EditorState.Delete:
            click_position = event.GetPositionTuple()
            for state, stateNb in self.states.iteritems():
                    if state.is_within(click_position):
                        del self.states[state]
                        self.stateNames[stateNb].Destroy()
                        del self.stateNames[stateNb]  
                        self.reusableStateNames.append(stateNb)
                        self.reusableStateNames.sort()
                        break
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
        if event.Dragging() and event.LeftIsDown() and self.drawingState == EditorState.Select:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)

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
            self.Refresh(False)

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
