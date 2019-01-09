import os
import sys, pygame

import time
from input_control.touch_device import TouchPoller

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
        screen.fill(white)
        pygame.draw.line(screen, (255, 0, 0), (x - 10, y), (x + 10, y))
        pygame.draw.line(screen, (255, 0, 0), (x, y - 10), (x, y + 10))
        pygame.display.flip()
        self.touch.on_pressed(self.store_input)
        
    def store_input(self, position, pressed):
        if not pressed:
            print("pressed!!!! %d, %d", self.touch.touch_i, self.touch.touch_j)
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
        
        dtx = tx1-tx0
        dty = ty1-ty0
        
        dx = x1 - x0
        dy = y1 - y0
        
        self.touch.ofs_touch_i = tx0
        self.touch.ofs_touch_j = ty0
        self.touch.fx = dy / dty
        self.touch.ofsx = y0
        self.touch.fy = dx / dtx
        self.touch.ofsy = x0

        print ("dt: (%d, %d)  d: (%d, %d)  f: (%f, %f)" %(dtx, dty, dx, dy, self.touch.fx, self.touch.fy))        
        self.done = True

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

touch = TouchPoller()
touch.start()
calibrator = Calibrator(screen, 320, 240, touch)
calibrator.calibrate()
while not calibrator.done:
    print("waiting...")
    time.sleep(1)

print("calibration done.")
touch.on_pressed(set_cross_pos)

cross_pos = (0,0)

while 1:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]
    
    screen.fill(white)
    screen.blit(ball, ballrect)
    (x,y) = cross_pos
    pygame.draw.line(screen, (255, 0, 0), (x - 10, y), (x + 10, y))
    pygame.draw.line(screen, (255, 0, 0), (x, y - 10), (x, y + 10))

    pygame.display.flip()
#    time.sleep(0.05)


