class UiEvent:
    MOUSE_CLICK_EVENT = 0
    MOUSE_DOWN_EVENT = 1
    MOUSE_UP_EVENT = 2
    MOUSE_MOVE_EVENT = 3
    MOUSE_ENTER_EVENT = 4
    MOUSE_LEAVE_EVENT = 5
    RAW_MOUSE_DOWN_EVENT = 11
    RAW_MOUSE_UP_EVENT = 12

    def __init__(self, event_type, pos):
        self.event_type = event_type
        self.pos = pos
        
    def is_type(self, event_type):
        return self.event_type == event_type

    def get_pos(self):
        return self.pos
