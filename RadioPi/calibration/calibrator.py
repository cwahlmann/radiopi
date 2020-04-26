from events.events import UiEvent
from ui.view import UiComponent, TextlabelComponent
import pygame


class CalibratorView(UiComponent):
    def __init__(self, images, fonts, sizes, colors):
        UiComponent.__init__(self)
        self.width = 320
        self.height = 240
        self.pos_list = [(10, 10), (self.width - 10, self.height - 10)]
        self.tpos_list = []
        self.index = 0
        self.done = False
        self.textlabel = TextlabelComponent("CLICK on crosses to calibrate", fonts, sizes, colors)
        self.textlabel.set_pos(20, 110)
        self.textlabel.set_size(280, 20)
        self.textlabel.visible = True
        self.add(self.textlabel)

    def on_event(self, event, offset):
        if event.is_type(UiEvent.RAW_MOUSE_DOWN_EVENT):
            self.next(event.get_pos())
            return True
        return False

    def next(self, position):
        self.tpos_list.append(position)
        if self.index < len(self.pos_list) - 1:
            self.index = self.index + 1
            self.set_changed()
        else:
            self.done = True
        return self

    def draw(self, screen, offset):
        if self.visible:
            (x, y) = self.pos_list[self.index]
            pygame.draw.line(screen, (255, 0, 0), (x - 10, y), (x + 10, y), 2)
            pygame.draw.line(screen, (255, 0, 0), (x, y - 10), (x, y + 10), 2)
            self.set_changed()
        UiComponent.draw(self, screen, offset)
