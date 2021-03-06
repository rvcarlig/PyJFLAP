from enum import Enum
from math import sqrt
import wx
from Transition import Transition


class StateType(Enum):
    Normal = 0
    Start = 1
    End = 2

    def __str__(self):
        return str(self.value)


class State:

    def __init__(self, position, state_name, radius=50, selected=False, state_type=StateType.Normal.value):
        self.position = position
        self.type = state_type
        self.radius = radius
        self.arcs = {}
        self.selected = selected
        self.state_name = state_name
        self.current = False
        self.bad_input = False
        self.ok_input = False

    def __str__(self):
        return self.state_name

    def set_type(self, state_type):
        self.type ^= state_type.value

    def get_type(self):
        return self.type

    def is_end_state(self):
        return self.type >> 1 & 1 == 1

    def is_start_state(self):
        return self.type & 1 == 1

    def add_transition(self, state, transition):
        self.arcs[state] = transition

    def add_arc(self, arc, value):
        up = True
        if arc.contains_arc(self):
            up = False
        if arc == self:
            new_trans = Transition(self.position, self.position, value, True, up)
        else:
            new_trans = Transition(self.position, arc.position, value, False, up)
        self.arcs[arc] = new_trans
        
    def remove_arc(self, arc):
        if arc in self.arcs.iterkeys():
            del self.arcs[arc]

    def draw(self, dc):
        brush = wx.Brush('White', wx.SOLID)
        if self.selected:
            brush = wx.Brush('Yellow', wx.SOLID)
        if self.current:
            brush = wx.Brush('Grey', wx.SOLID)
        if self.bad_input:
            brush = wx.Brush('Red', wx.SOLID)
        if self.ok_input:
            brush = wx.Brush('Green', wx.SOLID)
        dc.SetBrush(brush)
        dc.DrawCircle(self.position[0], self.position[1], self.radius)
        if self.is_end_state():
            dc.DrawCircle(self.position[0], self.position[1], self.radius - 5)
        if self.is_start_state():
            dc.DrawLine(self.position[0]-self.radius, self.position[1],
                        self.position[0]-2*self.radius, self.position[1]-self.radius)
            dc.DrawLine(self.position[0]-2*self.radius, self.position[1]-self.radius,
                        self.position[0]-2*self.radius, self.position[1]+self.radius)
            dc.DrawLine(self.position[0]-2*self.radius, self.position[1]+self.radius,
                        self.position[0]-self.radius, self.position[1])

        for arc in self.arcs.itervalues():
            dc.DrawText(arc.get_value(), arc.get_value_pos()[0], arc.get_value_pos()[1])
            if arc.is_self_trans():
                dc.DrawLine(arc.get_start_pos()[0], arc.get_start_pos()[1],
                            arc.get_end_pos()[0], arc.get_end_pos()[1]-85)
            else:
                dc.DrawLine(arc.get_start_pos()[0], arc.get_start_pos()[1],
                            arc.get_end_pos()[0], arc.get_end_pos()[1])
        dc.DrawText(self.state_name, self.position[0], self.position[1])

    def set_selected(self, selected):
        self.selected = selected

    def set_position(self, position):
        self.position = position
        for arc in self.arcs.iterkeys():
            self.arcs[arc].change_start_pos(position)

    def get_position(self):
        return self.position

    def is_within(self, pos):
        distance = sqrt(((pos[0] - self.position[0]) ** 2) +
                        ((pos[1] - self.position[1]) ** 2))
        return distance < self.radius

    def contains_arc(self, arc):
        return arc in self.arcs.iterkeys()

    def set_name(self, name):
        self.state_name = name

    def set_arc_value(self, arc, value):
        self.arcs[arc].change_arc_value(value)

    def add_new_arc_value(self, arc, value):
        self.arcs[arc].add_new_arc_value(value)

    def get_degree(self):
        return len(self.arcs)
