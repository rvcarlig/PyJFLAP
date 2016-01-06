from enum import Enum
from math import sqrt
import wx


class StateType(Enum):
    Normal = 0
    Start = 1
    End = 2


class State:

    def __init__(self, position, state_name):
        self.position = position
        self.type = StateType.Normal
        self.radius = 50
        self.arcs = []
        self.selected = False
        self.state_name = state_name
        self.up = True

    def set_type(self, state_type):
        self.type = state_type

    def add_arc(self, arc):
        self.arcs.append(arc)
        
    def remove_arc(self, arc):
        if arc in self.arcs:
            self.arcs.remove(arc)

    def draw(self, dc):
        brush = wx.Brush('White', wx.SOLID)
        if self.selected:
            brush = wx.Brush('Yellow', wx.SOLID)
        dc.SetBrush(brush)
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
            if arc.contains_arc(self):
                if arc.up:
                    self.up = False
                if self.up:
                    dc.DrawText(self.state_name+'->'+arc.state_name, (self.position[0]+arc.position[0])/2,
                                (self.position[1]+arc.position[1])/2 + 10)
                else:
                    dc.DrawText(self.state_name+'->'+arc.state_name, (self.position[0]+arc.position[0])/2,
                                (self.position[1]+arc.position[1])/2 - 10)
            else:
                dc.DrawText(self.state_name+'->'+arc.state_name, (self.position[0]+arc.position[0])/2,
                            (self.position[1]+arc.position[1])/2 + 10)
            dc.DrawLine(self.position[0], self.position[1], arc.position[0], arc.position[1])

        dc.DrawText(self.state_name, self.position[0], self.position[1])

    def set_selected(self, selected):
        self.selected = selected

    def set_position(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def is_within(self, pos):
        distance = sqrt(((pos[0] - self.position[0]) ** 2) +
                        ((pos[1] - self.position[1]) ** 2))
        return distance < self.radius

    def contains_arc(self, arc):
        return arc in self.arcs

    def set_name(self, name):
        self.state_name = name
