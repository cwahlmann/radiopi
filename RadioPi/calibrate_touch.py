import pygame
import os
import time
from ui.touch_device import TouchDevice
from calibration.calibrator import CalibratorView
from ui.view import ImageFont, UI
from view.radio_view import Images

os.putenv('SDL_FBDEV', '/dev/fb1')

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((320, 240))
pygame.display.set_caption("Radio PI")

font = ImageFont('gfx/font.png', (20, 20))
font_pushed = ImageFont('gfx/font_pushed.png', (20, 20))
font_inactive = ImageFont('gfx/font_inactive.png', (20, 20))
ui = UI(screen, 320, 240, (0, 0, 0))
images = Images(font, font, font_pushed, font_inactive)

fontspath = "fonts/dejavu-fonts-ttf-2.37/ttf/"
fonts = [
    fontspath + 'DejaVuSans.ttf',
    fontspath + 'DejaVuSans-Bold.ttf',
    fontspath + 'DejaVuSans-Oblique.ttf',
    fontspath + 'DejaVuSans-BoldOblique.ttf'
]
sizes = [12, 16, 20, 24]
colors = [(255,255,255), (0,255,0)]

calibrator_view = CalibratorView(images, fonts, sizes, colors)
calibrator_view.set_size(320, 240);
calibrator_view.visible = True

ui.get_root().add(calibrator_view)

ui.get_root().show()
ui.refresh()

#input_device = MouseDevice()
#pygame.mouse.set_visible(True)
pygame.mouse.set_visible(False)
input_device = TouchDevice()
input_device.calibration_load('calibration.ini')

while not calibrator_view.done:
    input_device.poll(ui)
    ui.refresh()
    time.sleep(0.05)

input_device.calculate_calibration(calibrator_view.pos_list, calibrator_view.tpos_list)
input_device.calibration_print()
os.system("cp calibration.ini ~calibration.ini");
input_device.calibration_save('calibration.ini')
