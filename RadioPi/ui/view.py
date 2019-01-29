import pygame   

from events.events import UiEvent
from controller.threads import InterruptableThread
import time

class UiComponent:

    def __init__(self):
        self.parent = None
        self.root = self
        self.components = []
        self.visible = True
        self.active = True
        self.changed = False
        self.pos = (0, 0)
        (self.width, self.height)= (1, 1)
        self.event_listeners = {}
        self.mouse_over = False
        
    def get_parent(self):
        return self.parent
    
    def set_parent(self, new_parent):
        self.parent = new_parent;
        self.root = new_parent.get_root()
        return self
    
    def get_root(self):
        return self.root
    
    def show(self):
        self.visible = True
        self.changed = True
        return self
        
    def hide(self):
        self.visible = False
        self.changed = True
        return self

    def activate(self):
        self.active = True
        self.changed = True
        return self
        
    def deactivate(self):
        self.active = False
        self.changed = True
        return self

    def clear(self):
        self.components = []
        self.changed = True
        return self

    def get_pos(self):
        return self.pos
    
    def set_pos(self, x, y):
        self.pos = (x, y)
        self.changed = True
        return self
    
    def get_size(self):
        return (self.width, self.height)
    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def set_size(self, w, h):
        (self.width, self.height) = (w, h)
        self.changed = True
        return self

    def has_changed(self):
        return self.changed
    
    def set_changed(self):
        if not self.visible:
            return
        self.changed = True
        if self.get_parent():
            self.get_parent().set_changed()
        return self
    
    def clear_changed(self):
        self.changed = False
        for component in self.components:
            component.clear_changed()
        return self
        
    def add(self, component):
        component.set_parent(self)
        self.components.append(component)
        self.set_changed()
        return self
        
    def get_components(self):
        return self.components

    def set_event_listener(self, event_type, listener):
        self.event_listeners[event_type] = listener
        return self

    def on_event(self, event, offset):
        if not self.visible or not self.active:
            return False
        if event.is_type(UiEvent.MOUSE_MOVE_EVENT):
            self.on_mouse_move_event(event, offset)
        (x, y) = event.get_pos()
        (ox, oy) = offset
        if not self.is_in(x - ox, y - oy):
            return False        
        (px, py) = self.pos
        for component in self.components:
            if component.on_event(event, (px + ox, py + oy)):
                return True
        if not event.event_type in self.event_listeners.keys():
            return False
        return self.event_listeners[event.event_type](event, self)

    def on_mouse_move_event(self, event, offset):
        (x, y) = event.get_pos()
        (ox, oy) = offset
        (px, py) = self.pos
        
        if not self.is_in(x - ox, y - oy):
            if self.mouse_over:
                self.mouse_over = False
                if UiEvent.MOUSE_LEAVE_EVENT in self.event_listeners.keys():
                    self.event_listeners[UiEvent.MOUSE_LEAVE_EVENT](
                        UiEvent(UiEvent.MOUSE_LEAVE_EVENT, (px + ox, py + oy)), self)
            return
        if not self.mouse_over:
            self.mouse_over = True
            if UiEvent.MOUSE_ENTER_EVENT in self.event_listeners.keys():
                self.event_listeners[UiEvent.MOUSE_ENTER_EVENT](
                    UiEvent(UiEvent.MOUSE_ENTER_EVENT, (px + ox, py + oy)), self)

    def is_in(self, x, y):
        (w, h) = self.get_size()
        (px, py) = self.pos
        return x >= px and x < px + w and y >= py and y < py + h
    
    def draw(self, screen, offset):
        if not self.visible:
            return
        (ox, oy) = offset
        (x, y) = self.pos
        for component in self.components:
            component.draw(screen, (ox + x, oy + y))

    
class UI:

    def __init__(self, screen, w, h, background):
        self.root_user = UiComponent()
        self.root_user.set_size(w, h)
        self.root_user.set_pos(0, 0)
        self.root = self.root_user
        self.screensaver = None 
        self.screensaver_active = False
        self.last_action = time.time()
        self.timeout = 60
        self.screen = screen
        self.background = background
    
    def set_screensaver(self, screensaver):
        self.screensaver = screensaver
        self.screensaver.set_mouse_click_handler(self.stop_screensaver)

    def start_screensaver(self):
        self.screensaver_active = True
        self.root = self.screensaver
        self.root.set_changed()
        self.screensaver.start()

    def stop_screensaver(self):
        self.screensaver.stop()
        self.root = self.root_user
        self.screensaver_active = False
        self.root.set_changed()
                
    def refresh(self):
        if self.screensaver and not self.screensaver_active and time.time() > self.last_action + self.timeout:
            self.start_screensaver()
        if not self.root.has_changed():
            return
        self.root.clear_changed()
        self.screen.fill(self.background)
        self.root.draw(self.screen, (0, 0))
        pygame.display.flip()

    def on_event(self, event):
        self.last_action = time.time()
        self.root.on_event(event, (0, 0))
        
    def get_root(self):
        return self.root_user

class ImageComponent(UiComponent):

    def __init__(self, image):
        UiComponent.__init__(self)
        self.set_image(image)
        
    def set_image(self, image):
        self.image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.set_size(self.rect.width, self.rect.height)
        self.set_changed()
        return self
        
    def draw(self, screen, offset):
        if not self.visible:
            return
        (ox, oy) = offset
        (x, y) = self.get_pos()
        r = self.rect.move(x + ox, y + oy)
        screen.blit(self.image, r)
        UiComponent.draw(self, screen, offset)


class ButtonComponent(ImageComponent):

    def __init__(self, images):
        (self.image_active, self.image_pushed, self.image_inactive) = images
        self.pushed = False
        ImageComponent.__init__(self, self.image_active)
        self.set_event_listener(UiEvent.MOUSE_DOWN_EVENT, lambda event, source: self.handle_mouse_down())
        self.set_event_listener(UiEvent.MOUSE_UP_EVENT, lambda event, source: self.handle_mouse_up())
        self.set_event_listener(UiEvent.MOUSE_LEAVE_EVENT, lambda event, source: self.handle_mouse_leave())
    
    def handle_mouse_down(self):
        if not self.active or not self.visible:
            return False
        if not self.pushed:
            self.set_image(self.image_pushed)
            self.pushed = True
        return True
    
    def handle_mouse_up(self):
        if not self.active or not self.visible:
            return False
        if self.pushed:
            self.set_image(self.image_active)
            self.pushed = False
        return True

    def handle_mouse_leave(self):
        self.handle_mouse_up()
        
    def activate(self):
        if self.visible and not self.active:
            self.set_image(self.image_active)
            self.pushed = False            
        return ImageComponent.activate(self)
    
    def deactivate(self):
        if self.visible and self.active:
            self.set_image(self.image_inactive)
        return ImageComponent.deactivate(self)

    def set_images(self, images):
        (self.image_active, self.image_pushed, self.image_inactive) = images
        self.chose_image()

    def chose_image(self):
        if self.active:
            if self.pushed:
                self.set_image(self.image_pushed)
            else:
                self.set_image(self.image_active)
            return
        self.set_image(self.image_inactive)
    
class ImageFont:

    def __init__(self, imagefile, tilesize):
        self.image = pygame.image.load(imagefile)
        #self.image.set_colorkey((255, 0, 255))
        self.imagerect = self.image.get_rect()
        self.tilesize = tilesize
        (w, h) = (self.imagerect.right, self.imagerect.bottom)
        (sw, sh) = self.tilesize
        (self.nx, self.ny) = (int(w / sw), int(h / sh))
        
    def get_image(self, col, row, w, h):
        if col < 0 or col >= self.nx or row < 0 or row >= self.ny:
            return None
        (sw, sh) = self.tilesize
        result = pygame.Surface((int(sw * w), int(sh * h)))
        result.set_colorkey((0, 0, 0))
        result.blit(self.image, result.get_rect(), (sw * col, sh * row, w * sw, h * sh))
        return result.convert_alpha()

class FrameBuilder(UiComponent):
    
    def __init__(self, tl, tr, bl, br, l, r, t, b, tw, th):
        UiComponent.__init__(self)
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br
        self.l = l
        self.r = r
        self.t = t
        self.b = b
        self.tw = tw
        self.th = th

    def frame(self, root, x, y, w, h):
        root.add(ImageComponent(self.tl).set_pos(x * self.th, y * self.tw))
        root.add(ImageComponent(self.tr).set_pos((x + w - 1) * self.tw, y * self.th))
        root.add(ImageComponent(self.bl).set_pos(x * self.tw, (y + h - 1) * self.th))
        root.add(ImageComponent(self.br).set_pos((x + w - 1) * self.tw, (y + h - 1) * self.th))
        
        for i in range(w - 2):
            root.add(ImageComponent(self.t).set_pos((x + 1 + i) * self.tw, y * self.th))
            root.add(ImageComponent(self.b).set_pos((x + 1 + i) * self.tw, (y + h - 1) * self.th))
            
        for i in range(h - 2):
            root.add(ImageComponent(self.l).set_pos(x * self.tw, (y + 1 + i) * self.th))
            root.add(ImageComponent(self.r).set_pos((x + w - 1) * self.tw, (y + 1 + i) * self.th))        

class TextlabelComponent(UiComponent):
    
    REGULAR = 0
    BOLD = 1
    ITALIC = 2
    BOLD_ITALIC = 3
    
    SIZE_SMALL = 0
    SIZE_REGULAR = 1
    SIZE_BIG = 2
    SIZE_HUGE = 3
    
    COLOR_0 = 0
    COLOR_1 = 1
    
    def __init__(self, text, fonts, sizes, colors):
        UiComponent.__init__(self)
        self.fonts = fonts
        self.sizes = sizes
        self.colors = colors
        self.set_text(text)
    
    def set_text(self, new_text):
        self.text = new_text
        self.set_changed()
        return self
    
    def text(self):
        return self.text

    def draw(self, screen, offset):
        (px, py) = self.get_pos()
        (ox, oy) = offset
        italic = 0
        bold = 0
        size = TextlabelComponent.SIZE_REGULAR
        color = TextlabelComponent.COLOR_0
        masked = 0
        y = py
        (width, height) = self.get_size()
        for line in self.text.split('\n'):
            x = 0
            line_height = 0
            textsurfaces = []
            word = ""
            for c in line:
                if c == '\\':
                    masked = 1 - masked   
                elif "*~°^_".find(c) < 0 or masked:
                    masked = 0
                    word = word + c
                else:
                    if (word):
                        s = size
                        if s < 0:
                            s = 0
                        if s >= len(self.sizes):
                            s = len(self.sizes)-1                        
                        font = pygame.font.Font(self.fonts[bold + italic], self.sizes[s])
                        textsurface = font.render(word, True, self.colors[color])
                        (sx, sy) = textsurface.get_size()
                        if x < width-1:
                            textsurfaces.append((x, sy, textsurface))
                        if sy > line_height:
                            line_height = sy
                        x = x + sx 
                        word = ""
                    if c == '*':
                        bold = 1 - bold
                    elif c == '~':
                        italic = 2 - italic
                    elif c == '°':
                        color = 1 - color
                    elif c == '^':
                        size = size + 1
                    elif c == '_':
                        size = size - 1
            if (word):
                s = size
                if s < 0:
                    s = 0
                if s >= len(self.sizes):
                    s = len(self.sizes)-1
                font = pygame.font.Font(self.fonts[bold + italic], self.sizes[s])
                textsurface = font.render(word, True, self.colors[color])
                (sx, sy) = textsurface.get_size()
                if x < width-1:
                    textsurfaces.append((x, sy, textsurface))
                if sy > line_height:
                    line_height = sy
                x = x + sx #+ int(sy / 3)
                word = ""
            for (x, sy, textsurface) in textsurfaces:
                (sw, sh) = textsurface.get_size()
                if x + sw > width:
                    sw = width - x
                if y + line_height + sh - sy > height:
                    sh = height - (y + line_height + sy)
                screen.blit(textsurface, (ox + x + px, oy + y + line_height - sy), (0,0,sw,sh))
            if y-sy > height:
                break
            y = y + line_height
                
class ListViewComponent(TextlabelComponent):
    def __init__(self, fonts, sizes, colors):
        TextlabelComponent.__init__(self, "", fonts, sizes, colors)
        self.items = []
        self.labels = []
        self.rows = 0
        self.selected = 0
        self.line_height = 0
        self.to_string = lambda item: "%s" % item
        self.to_icon = lambda item: None
        self.handle_select = lambda item: print("select item: %s" % self.to_string(item))
        self.set_event_listener(UiEvent.MOUSE_CLICK_EVENT, self.handle_click_event)
        self.empty_message = ""

    def set_size(self, w, h, line_height):
        TextlabelComponent.set_size(self, w, h)
        self.line_height = line_height
        self.rows = int((h +line_height-1)/ line_height)
        self.init_rows()
        return self

    def init_rows(self):
        self.labels = []
        w = self.get_width()
        for i in range(self.rows):
            label = TextlabelComponent("", self.fonts, self.sizes, self.colors)
            label.set_size(w, self.line_height)
            self.labels.append(label)

    def set_empty_message(self, empty_message):
        self.empty_message = empty_message

    def set_handle_select(self, handle_select):
        self.handle_select = handle_select
        
    def set_selected(self, selected):
        self.selected = selected
        self.set_changed()

    def get_selected_item(self):
        if len(self.items) == 0:
            return None
        return self.items[self.selected]
    
    def get_selected(self):
        return self.selected

    def select_next(self):
        if len(self.items) == 0:
            return None
        if self.selected < len(self.items)-1:
            self.selected = self.selected + 1
        self.set_changed()
        return self.items[self.selected]

    def select_prev(self):
        if len(self.items) == 0:
            return None
        if self.selected > 0:
            self.selected = self.selected - 1
        self.set_changed()
        return self.items[self.selected]

    def set_items(self, items):
        self.items = items
        self.selected = 0
        self.set_changed()
                   
    def handle_click_event(self, event, source):
        (ex, ey) = event.pos
        (px, py) = self.get_pos()
        i = int((ey-py) / self.line_height) + self.selected
        if i < len(self.items):
            self.handle_select(self.items[i])
        return True
        
    def set_to_string(self, to_string):
        self.to_string = to_string
        
    def set_to_icon(self, to_icon):
        self.to_icon = to_icon

    def draw(self, screen, offset):
        (px, py) = self.get_pos()
        height = self.get_height()
        width = self.get_width()
        (ox, oy) = offset

        if len(self.items) == 0:
            label = self.labels[0]
            label.set_text(self.empty_message)
            label.draw(screen, (px + ox, py + oy))
            return            

        y = 0
        i = self.selected
        row = 0
        while y < height and i < len(self.items):
            item = self.items[i]
            label = self.labels[row]
            label.set_text(self.to_string(item))
            label.draw(screen, (px + ox, py + oy + y))
            
            icon = self.to_icon(item)
            if icon != None:
                (w,h) = icon.get_size()
                icon.draw(screen, (px + ox + width - w, py + oy + y))

            i = i + 1
            row = row + 1
            y = y + self.line_height

class ScreensaverComponent (UiComponent):
    def __init__(self, do_animation):
        UiComponent.__init__(self)
        self.do_animation = do_animation
        self.mouse_click_handler = self.default_mouse_click_handler
        self.set_event_listener(UiEvent.MOUSE_CLICK_EVENT, self.handle_mouse_click)
        self.animation_thread = None
        
    def set_mouse_click_handler(self, mouse_click_handler):
        self.mouse_click_handler = mouse_click_handler
        
    def start(self):
        if self.animation_thread:
            self.animation_thread.interrupt()
        self.animation_thread = InterruptableThread().with_runnable(self.animation)
        self.animation_thread.start()

    def stop(self):
        if self.animation_thread:
            self.animation_thread.interrupt()
        
    def handle_mouse_click(self, event, offset):
        self.animation_thread.interrupt()
        self.mouse_click_handler()
        return True

    def default_mouse_click_handler(self):
        print("default Screensaver CLICK")

    def animation(self):
        while not self.animation_thread.is_interrupted():
            self.do_animation()
            time.sleep(0.1)
