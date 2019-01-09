import pygame
from events.events import UiEvent
from ui.input_device import AbstractInputDevice

class MouseDevice (AbstractInputDevice):
    def __init__(self):
        self.mouse_down = False
        
    def poll(self, ui):
        ev = pygame.event.get()
        for event in ev:
            if not self.mouse_down and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                ui.on_event(UiEvent(UiEvent.MOUSE_DOWN_EVENT, pos))
                ui.on_event(UiEvent(UiEvent.MOUSE_CLICK_EVENT, pos))
                self.mouse_down = True
            elif self.mouse_down and event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                ui.on_event(UiEvent(UiEvent.MOUSE_UP_EVENT, pos))
                self.mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                ui.on_event(UiEvent(UiEvent.MOUSE_MOVE_EVENT, pos))
                self.mouse_down = False
