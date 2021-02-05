
import logging
log = logging.getLogger(__name__)


import threading
from time import time, sleep
from automation.MachineMotion import DIRECTION

class Conveyor():   
    
    def __init__(self, name, mm, axis_config = None, axis=None, uStep=None, default_speed=100, default_accel=100, direction=DIRECTION.POSITIVE, gain= 157):
        
        defined_by_axis_config = axis_config is not None
        defined_by_keyword = all([kw is not None for kw in [axis, direction, uStep]])
        if defined_by_axis_config:
            self.axis = axis_config['axis']
            self.uStep = axis_config['uStep']
            self.direction = axis_config['direction']
        elif defined_by_keyword:
            self.axis = axis
            self.uStep = uStep
            self.direction = direction
        else:
            raise Exception("Error with initialization")

        self.gain = gain
        self.name = name
        self.mm = mm
        self.speed = default_speed
        self.accel = default_accel

        
        self.mm.configAxis(self.axis, self.uStep, self.gain)
        self.mm.configAxisDirection(self.axis, self.direction)
        
        if self.direction == DIRECTION.NEGATIVE:
            self.speed = self.speed*-1
    
    def set_box_length(self, length):
        self.box_length = length
        
    def jog_box_length(self):
        self.mm.emitRelativeMove(axis, DIRECTION.positive, self.box_length)
        self.mm.waitForMotionCompletion()
        return Tu

 
    def stop_rolling(self):
        print("Stopping {} a={}".format(self.axis, self.accel))     
        self.mm.stopContinuousMove(self.axis, self.accel)
        return True
        
    def start_rolling(self):
        print("Rolling {} v={} a={}".format(self.axis, self.speed, self.accel))
        self.mm.setContinuousMove(self.axis, self.speed, self.accel)
        return True
 