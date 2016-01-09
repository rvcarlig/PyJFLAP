import wx
#from State import State, StateType
import collections


class Transition:

    def __init__(self, start_position, end_position, value, same_state, is_up):
    
        self.start_position = start_position
        self.end_position = end_position        
        self.value = value
        self.same_state = same_state
        self.up = is_up
        self.valuePos = [0, 0]
        self.update_value_pos()
        
    def add_new_arc_value(self, value):
        self.value = self.value + ", " + value
        
    def change_arc_value(self, value):
        self.value = value
        
    def change_start_pos(self, pos):
        self.start_position = pos
        self.update_value_pos()
        
    def change_end_pos(self, pos):
        self.end_position = pos
        self.update_value_pos()
        
    def update_value_pos(self):
        if self.same_state:
            self.valuePos[0] = self.start_position[0] - 20
            self.valuePos[1] = self.start_position[1] - 100
        elif self.up:
            self.valuePos[0] = (self.start_position[0]+self.end_position[0])/2
            self.valuePos[1] = (self.start_position[1]+self.end_position[1])/2 - 10
        else:
            self.valuePos[0] = (self.start_position[0]+self.end_position[0])/2
            self.valuePos[1] = (self.start_position[1]+self.end_position[1])/2 + 10
            
    def get_value(self):
        return self.value
        
    def get_value_pos(self):
        return (self.valuePos[0], self.valuePos[1])
        
    def get_start_pos(self):
        return self.start_position
        
    def get_end_pos(self):
        return self.end_position
        
    def is_self_trans(self):
        return (self.start_position == self.end_position)
        
    def is_clicked(self, pos):
        if (self.valuePos[0] < pos[0] < self.valuePos[0]+50):
            if (self.valuePos[1]-10 < pos[1] < self.valuePos[1]+10):
                return True
        return False
