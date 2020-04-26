import configparser

import pygame

from evdev import InputDevice
from events.events import UiEvent
from ui.input_device import AbstractInputDevice
from _operator import pos


class TouchDevice (AbstractInputDevice):
            
    def __init__(self):
        self.dev = InputDevice('/dev/input/event0')     

        self.touch_i = -1
        self.touch_j = -1
        self.pressed = False

        self.old_pressed = False
        self.old_pos = (-1,-1)
        
        self.ofs_touch_i = 0
        self.ofs_touch_j = 0
        self.fx = 1
        self.ofsx = 0
        self.fy = 1
        self.ofsy = 0
        
    def get_position(self):
        return ((self.touch_i - self.ofs_touch_i) * self.fy + self.ofsy,
            (self.touch_j - self.ofs_touch_j) * self.fx + self.ofsx)

    def get_raw_position(self):
        return (self.touch_i, self.touch_j)

    def poll(self, ui):
        event = self.dev.read_one()                    
        while (event != None):
            self.handle_event(ui, event) 
            event = self.dev.read_one()                    
            
    def handle_event(self, ui, event):               
            if (event.code == 0 and event.type == 3):  # Y-Axis
                self.touch_i = event.value
            elif (event.code == 1 and event.type == 3):  # X-Axis
                self.touch_j = event.value
            elif (event.code == 330 and event.type == 1):  # Touch Pressed / Released
                self.pressed = event.value
                if self.pressed:
                    self.touch_i = -1
                    self.touch_j = -1
                        
            # check if all data ist present
            if self.touch_i < 0 or self.touch_j < 0:
                return

            pos = self.get_position()
            
            # mouse move event?
            (opx, opy) = self.old_pos
            (x,y) = pos
            if opx != x or opy != y:
                self.old_pos = pos
                ui.on_event(UiEvent(UiEvent.MOUSE_MOVE_EVENT, pos))
                
            # mouse up / down / click event
            if self.old_pressed == self.pressed:
                return
            
            self.old_pressed = self.pressed

            if self.pressed:
                ui.on_event(UiEvent(UiEvent.MOUSE_DOWN_EVENT, pos))
                ui.on_event(UiEvent(UiEvent.MOUSE_CLICK_EVENT, pos))
                ui.on_event(UiEvent(UiEvent.RAW_MOUSE_DOWN_EVENT, (self.touch_i, self.touch_j)))
            else:
                ui.on_event(UiEvent(UiEvent.MOUSE_UP_EVENT, pos))
                ui.on_event(UiEvent(UiEvent.RAW_MOUSE_UP_EVENT, (self.touch_i, self.touch_j)))
                self.touch_i = -1
                self.touch_j = -1

    def calculate_calibration(self, p, tp):
        (x0, y0) = p[0]
        (x1, y1) = p[1]

        print(tp)

        (tx0, ty0) = tp[0]
        (tx1, ty1) = tp[1]

        dtx = tx1 - tx0
        dty = ty1 - ty0

        dx = x1 - x0
        dy = y1 - y0

        self.ofs_touch_i = tx0
        self.ofs_touch_j = ty0
        self.fx = dy / dty
        self.ofsx = y0
        self.fy = dx / dtx
        self.ofsy = x0

    def calibration_print(self):
        print("ofs_touch = (%d, %d)" % (self.ofs_touch_i,self.ofs_touch_j))
        print("ofs_f = (%f, %f)" % (self.fx,self.fy))
        print("ofs_ofs = (%d, %d)" % (self.ofsx, self.ofsy))

    def calibration_save(self, filename):
        config = configparser.ConfigParser()
        config['CALIBRATION'] = {
            'ofs_touch_i': self.ofs_touch_i,
            'ofs_touch_j': self.ofs_touch_j,
            'fx': self.fx,
            'fy': self.fy,
            'ofsx': self.ofsx,
            'ofsy': self.ofsy,
        }        
        with open(filename, 'w') as configfile:
            config.write(configfile)

    def calibration_load(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        self.ofs_touch_i = float(config['CALIBRATION']['ofs_touch_i']) 
        self.ofs_touch_j = float(config['CALIBRATION']['ofs_touch_j'])
        self.fx = float(config['CALIBRATION']['fx']) 
        self.fy = float(config['CALIBRATION']['fy'])
        self.ofsx = float(config['CALIBRATION']['ofsx'])
        self.ofsy = float(config['CALIBRATION']['ofsy'])
