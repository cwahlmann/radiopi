import os
import sys, pygame

import time
from ui import touch_device

def set_cross_pos(position, pressed):
    global cross_pos
    if not pressed:
        (x,y) = position
        cross_pos = (x,y) 
          
os.putenv('SDL_FBDEV', '/dev/fb1')

pygame.init()
pygame.mouse.set_visible(False)

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)

ball = pygame.image.load("intro_ball.gif")
ballrect = ball.get_rect()

touch = touch_device.TouchPoller()
touch.start()
calibrator = touch_device.Calibrator(screen, 320, 240, touch)
calibrator.calibrate()

while not calibrator.done:
    print("waiting...")
    time.sleep(1)

print("calibration done.")
touch.stop()
