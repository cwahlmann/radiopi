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
            
    def poll(self, ui):
        event = self.dev.read_one()
                    
        if (event != None):                
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
            else:
                ui.on_event(UiEvent(UiEvent.MOUSE_UP_EVENT, pos))
                self.touch_i = -1
                self.touch_j = -1
            
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

 
# TODO!!
class Calibrator():

    def __init__(self, screen, width, height, touch):
        self.width = width
        self.height = height
        self.screen = screen;
        self.touch = touch
        self.pos = [(10, 10), (width - 10, height - 10)]
        self.tpos = []
        self.index = 0
        self.done = False
        
    def calibrate(self):
        self.index = 0
        self.done = False
        self.next()
        
    def next(self):
        (x, y) = self.pos[self.index]
        self.screen.fill((255, 255, 255))
        pygame.draw.line(self.screen, (255, 0, 0), (x - 10, y), (x + 10, y))
        pygame.draw.line(self.screen, (255, 0, 0), (x, y - 10), (x, y + 10))
        pygame.display.flip()
        # todo
        self.touch.on_click(self.store_input)
        
    def store_input(self, position):
        self.tpos.append((self.touch.touch_i, self.touch.touch_j))
        self.index = self.index + 1
        if self.index < len(self.pos):
            self.next()
        else:
            self.finish()

    def finish(self):
        (x0, y0) = self.pos[0]
        (x1, y1) = self.pos[1]

        (tx0, ty0) = self.tpos[0]
        (tx1, ty1) = self.tpos[1]
        
        dtx = tx1 - tx0
        dty = ty1 - ty0
        
        dx = x1 - x0
        dy = y1 - y0
        
        self.touch.ofs_touch_i = tx0
        self.touch.ofs_touch_j = ty0
        self.touch.fx = dy / dty
        self.touch.ofsx = y0
        self.touch.fy = dx / dtx
        self.touch.ofsy = x0
        # TODO!!
        self.touch.on_click(self.touch.default_on_click)
        self.touch.calibration_save('calibration.ini')
        self.done = True
