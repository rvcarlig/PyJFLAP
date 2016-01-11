from enum import Enum
from State import State, StateType
from helpers import InputWind, TransWind
from Transition import Transition
from math import sqrt
from copy import deepcopy
import wx
import json
import random


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

        self.init_drawing()
        self.make_menu()
        self.setup_buttons()
        self.bind_events()
        self.init_buffer()

        self.start_state = None

    def clear(self):
        self.states.clear()
        self.stateNames.clear()
        self.reusableStateNames = []
        self.currentState = 0
        assert len(self.states) == 0
        assert len(self.stateNames) == 0
        assert len(self.reusableStateNames) == 0
        self.redraw()

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
        self.drawingState = EditorState(event.GetId() - 1)

    def make_menu(self):
        self.menu = wx.Menu()
        file_item = self.menu.Append(wx.NewId(), 'Start State', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.make_start_state, file_item)

        file_item = self.menu.Append(wx.NewId(), 'End State', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.make_end_state, file_item)

        file_item = self.menu.Append(wx.NewId(), 'Edit State', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.change_state_name, file_item)

    def change_state_name(self, event):
        if self.clicked_state is not None:
            input_window = InputWind(self)
            input_window.Show()

    def make_start_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.Start)
            self.start_state = self.clicked_state
            self.redraw()

    def make_end_state(self, event):
        if self.clicked_state is not None:
            self.clicked_state.set_type(StateType.End)
            self.redraw()

    def on_left_down(self, event):
        if self.drawingState == EditorState.DrawCircle:
            self.previousPosition = event.GetPositionTuple()
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
                        trans_window = TransWind(self)
                        trans_window.Show()
                        break
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
                    for key in state.arcs.keys():
                        if state.arcs[key].is_clicked(click_position):
                            state.remove_arc(key)
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
            for state in self.states.iterkeys():
                for arc in state.arcs.keys():
                    if arc == self.selected_state:
                        state.arcs[self.selected_state].change_end_pos(event.GetPositionTuple())
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

    def save(self, path):
        if len(path) > 0:
            with open(path, 'w') as outfile:
                    json.dump(
                            {
                                'states':
                                    [
                                        {
                                            'state_name': state.state_name,
                                            'type': str(state.type),
                                            'radius': state.radius,
                                            'selected': state.selected,
                                            'position': state.position,
                                            'key': key_state
                                        }
                                        for state, key_state in self.states.items()
                                    ],
                                'arcs':
                                    [
                                        {
                                            'start': str(state),
                                            'end': str(key),
                                            'value': transition.value,
                                            'value_position': transition.valuePos,
                                            'up': transition.up
                                        }
                                        for state in self.states
                                        for key, transition in state.arcs.items()
                                    ]
                            }, fp=outfile, indent=4, sort_keys=False)

    def load(self, path):
        if len(path) > 0:
            self.clear()
            with open(path, 'r') as infile:
                data = json.load(infile)
            for state in data["states"]:
                new_state = State(position=state["position"], state_name=state["state_name"],
                                  radius=state["radius"], selected=state["selected"])
                self.states[new_state] = state["key"]
            for arc in data['arcs']:
                start_state = self.get_state_by_name(self.states, arc['start'])
                end_state = self.get_state_by_name(self.states, arc['end'])
                start_state.add_transition(end_state,
                                           Transition(start_position=start_state.position,
                                                      end_position=end_state.position,
                                                      value=arc['value'],
                                                      same_state=start_state.position == end_state.position,
                                                      is_up=arc['up'],
                                                      values_pos=arc['value_position'])
                                           )
            self.redraw()

    # noinspection PyPep8Naming
    def to_gem_layout(self):
        OPTIMAL_EDGE_LENGTH = 10.0
        GRAVITATIONAL_CONSTANT = 1.0 / 16.0

        r_max = 120 * len(self.states)
        t_global = TMIN + 1

        # barycenter of the graph
        records = {}
        c = [0, 0]
        for state in self.states:
            r = Record()
            r.position = state.position
            c[0] += r.position[0]
            c[1] += r.position[1]
            records[state] = r

        new_states = deepcopy(self.states)
        for i in range(r_max):
            # Choose a vertex V to update.
            if len(new_states) == 0:
                new_states = deepcopy(self.states)
            index = random.randint(0, len(new_states)-1)
            nstate = self.get_state_by_name(self.states, new_states.keys()[index].state_name)
            record = records[nstate]
            new_states.pop(new_states.keys()[index])
            pos = nstate.position
            # Compute the impulse of V.
            theta = nstate.get_degree()
            theta *= 1.0 + theta / 2.0
            p = [
                (c[0] / len(self.states) - nstate.position[0]) * GRAVITATIONAL_CONSTANT * theta,
                (c[1] / len(self.states) - nstate.position[1]) * GRAVITATIONAL_CONSTANT * theta,
            ]
            # Random disturbance
            p[0] += random.uniform(0.0, 1.0) * 10.0 - 5.0
            p[1] += random.uniform(0.0, 1.0) * 10.0 - 5.0
            # Forces exerted by other nodes
            for other_state in self.states:
                if other_state == nstate:
                    continue
                delta = [
                    pos[0] - other_state.position[0],
                    pos[1] - other_state.position[1]
                ]
                d2 = delta[0]*delta[0] + delta[1]*delta[1]
                o2 = OPTIMAL_EDGE_LENGTH * OPTIMAL_EDGE_LENGTH
                if delta[0] != 0.0 or delta[1] != 0.0:
                    p[0] += delta[0] * o2 / d2
                    p[1] += delta[1] * o2 / d2
                if nstate.contains_arc(other_state):
                    p[0] -= delta[0] * d2 / (o2 * theta)
                    p[1] -= delta[1] * d2 / (o2 * theta)

            # Adjust the position and temperature
            if p[0] != 0.0 or p[1] != 0.0:
                absp = sqrt(abs(p[0]*p[0] + p[1]*p[1]))
                p[0] *= record.temperature / absp
                p[1] *= record.temperature / absp

                # update position
                nstate.set_position([pos[0] + p[0], pos[1]+p[1]])
                # update barycenter
                c[0] += p[0]
                c[1] += p[1]

        self.redraw()

    @staticmethod
    def get_state_by_name(seq, value):
        for el in seq:
            if el.state_name == value:
                return el
                
    def check_nfa(self):
        # check each state for nondeterminism
        for state in self.states.iterkeys():
            # check for lambda
            for trans in state.arcs.itervalues():
                if trans.is_lambda_trans():
                    return True
            # Check all transitions against all other transitions to see if any are equal.
            for arc in state.arcs.iterkeys():
                for arc2 in state.arcs.iterkeys():
                    if arc == arc2:
                        continue
                    else: 
                        if state.arcs[arc].check_same_value(state.arcs[arc2]):
                            return True
        return False

TMAX = 256
TMIN = 3


class Record:
    def __init__(self):
        self.position = []
        self.lastImpulse = []
        self.temperature = TMIN
        self.skew = 0.0
