from ui.view import ImageComponent, UiEvent, \
    UiComponent, ButtonComponent, TextlabelComponent, ListViewComponent


class KeyComponent(ButtonComponent):

    def __init__(self, image, keycode):
        ButtonComponent.__init__(self, image)
        self.keycode = keycode


class Images:
    BUTTON_SELECT_STATION = 0
    BUTTON_VOLUME_UP = 1
    BUTTON_VOLUME_DOWN = 2
    BUTTON_START = 3
    BUTTON_STOP = 4
    BUTTON_SELECT_UP = 5
    BUTTON_SELECT_DOWN = 6
    BUTTON_SETUP = 7
    BUTTON_SMALL_UP = 8
    BUTTON_SMALL_DOWN = 9
    BUTTON_SCAN = 10
    BUTTON_OFS_KEY = 100
    
    FRAME_TOP_LEFT = 20
    FRAME_TOP_RIGHT = 21
    FRAME_BOTTOM_LEFT = 22
    FRAME_BOTTOM_RIGHT = 23
    FRAME_LEFT = 24
    FRAME_RIGHT = 25
    FRAME_TOP = 26
    FRAME_BOTTOM = 27
    
    LABEL_RADIO_PI = 40    
    LABEL_WAVE = 41
    LABEL_WLAN = 42
    LABEL_WLAN_0 = 43
    LABEL_WLAN_1 = 44
    LABEL_WLAN_2 = 45
    LABEL_WLAN_3 = 46

    def __init__(self, font, font_button_active, font_button_pushed, font_button_inactive):
        self.font = font
        self.font_button_active = font_button_active
        self.font_button_pushed = font_button_pushed
        self.font_button_inactive = font_button_inactive
        
        self.label_images = {
            Images.LABEL_RADIO_PI: font.get_image(16, 10, 6, 2),
            Images.LABEL_WAVE: font.get_image(8, 10, 8, 2),
            Images.LABEL_WLAN: font.get_image(22, 8, 2, 2),
            Images.LABEL_WLAN_0: font.get_image(22, 4, 1, 1),
            Images.LABEL_WLAN_1: font.get_image(23, 4, 1, 1),
            Images.LABEL_WLAN_2: font.get_image(21, 5, 1, 1),
            Images.LABEL_WLAN_3: font.get_image(22, 5, 1, 1),

            Images.FRAME_TOP_LEFT: font.get_image(6, 8, 1, 1),
            Images.FRAME_TOP_RIGHT: font.get_image(7, 8, 1, 1),
            Images.FRAME_BOTTOM_LEFT: font.get_image(6, 10, 1, 1),
            Images.FRAME_BOTTOM_RIGHT: font.get_image(7, 10, 1, 1),
            Images.FRAME_LEFT: font.get_image(6, 9, 1, 1),
            Images.FRAME_RIGHT: font.get_image(7, 9, 1, 1),
            Images.FRAME_TOP: font.get_image(6, 11, 1, 1),
            Images.FRAME_BOTTOM: font.get_image(7, 11, 1, 1),
            }
        self.button_images = {
            Images.BUTTON_SELECT_STATION: self.get_button_image(0, 8, 4, 4),
            Images.BUTTON_START: self.get_button_image(0, 0, 4, 4),
            Images.BUTTON_STOP: self.get_button_image(4, 0, 4, 4),
            Images.BUTTON_VOLUME_UP: self.get_button_image(4, 4, 4, 4),
            Images.BUTTON_VOLUME_DOWN: self.get_button_image(0, 4, 4, 4),
            Images.BUTTON_SELECT_UP: self.get_button_image(4, 8, 2, 2),
            Images.BUTTON_SELECT_DOWN: self.get_button_image(4, 10, 2, 2),
            Images.BUTTON_SETUP: self.get_button_image(22, 10, 2, 2),
            Images.BUTTON_SMALL_UP: self.get_button_image(22, 3, 1, 1),
            Images.BUTTON_SMALL_DOWN: self.get_button_image(23, 3, 1, 1),
            Images.BUTTON_SCAN: self.get_button_image(21, 4, 1, 1),
            }
        for j in range(10):
            for i in range(16):
                c = i + j * 16
                if c == 0x28:
                    # space                    
                    self.button_images[Images.BUTTON_OFS_KEY + 0x28] = self.get_button_image(i + 8, j, 2, 1)
                elif c != 0x58 and c != 0x88 and c != 0x29 and c != 0x59 and c != 0x89:                    
                    self.button_images[Images.BUTTON_OFS_KEY + c] = self.get_button_image(i + 8, j, 1, 1)
                
    def get_button_image(self, x, y, w, h):
        return (self.font_button_active.get_image(x, y, w, h),
                self.font_button_pushed.get_image(x, y, w, h),
                self.font_button_inactive.get_image(x, y, w, h))

    def label(self, name):
        return self.label_images[name]        

    def button(self, name):
        return self.button_images[name]        


class KeyboardComponent(UiComponent):
    CHARSET = "qwertzuiopü+    "\
            +"^asdfghjklöä#   "\
            +"<yxcvbnm  ,.-   "\
            +"QWERTZUIOPÜ*    "\
            +"°ASDFGHJKLÖÄ'   "\
            +">YXCVBNM  ;:_   "\
            +"1234567890ß~    "\
            +"!\"§$%&/()=?€    "\
            +"|{[]}\@µ  ,.-   "
    
    def __init__(self, images):
        UiComponent.__init__(self)
        self.images = images
        self.caps = 0  # lower / upper / lock
        self.num = 0  # alpha / num
        self.caps_buttons = []
        self.num_buttons = []
        self.favourite_buttons = []
        self.favourite = False
        self.keyboards = []
        for i in range(3):
            keyboard = UiComponent().set_pos(0, 0).set_size(300, 60)
            self.add_keys(keyboard, i * 3)
            self.keyboards.append(keyboard)
            self.add(keyboard)
        self.show_keyboard()

    def set_keyboard_handler(self, keyboard_handler):
        self.keyboard_handler = keyboard_handler

    def disable_favourite_button(self): 
        for favorite_button in self.favourite_buttons:
            favorite_button.hide()
            
    def add_keys(self, keyboard, offset):
        for y in range(3):
            for x in range(13):
                if y == 0 and x == 12:
                    # backspace
                    keyboard.add(KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 29), 12)\
                        .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_key(source.keycode))
                        .set_pos(x * 20 + 20, y * 20))                    
                elif (x == 8 and (y == 2 or y == 5 and y == 8)):
                    c = 0x28
                    keyboard.add(KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + c), c)\
                        .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_key(source.keycode))
                        .set_pos(x * 20, y * 20))                    
                elif not (x == 9 and (y == 2 or y == 5 and y == 8)):
                    c = x + (y + offset) * 16
                    keyboard.add(KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + c), c)\
                        .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_key(source.keycode))
                        .set_pos(x * 20, y * 20))
        # delete
        keyboard.add(KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x0d), 13)\
                .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_key(13))
                .set_pos(14 * 20, 0))

        # caps
        caps_button = KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x1e), 14)\
                .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_caps())
        self.caps_buttons.append(caps_button)
        keyboard.add(caps_button.set_pos(13 * 20, 20))

        # alphanum
        num_button = KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x0e), 15)\
                .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_alphanum())
        self.num_buttons.append(num_button)
        keyboard.add(num_button.set_pos(13 * 20, 40))

        # favourite button
        favourite_button = KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x2f), 0x2f)\
                .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_favourite_key())
        self.favourite_buttons.append(favourite_button)
        keyboard.add(favourite_button.set_pos(14 * 20, 20))        

        # return button
        return_button = KeyComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x2d), 0x2d)\
                .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_key(0x2d))
        keyboard.add(return_button.set_pos(14 * 20, 40))

    def handle_favourite_key(self):
        self.favourite = not self.favourite
        if self.favourite:
            key = 0x2e
        else:
            key = 0x2f
        for button in self.favourite_buttons:
            button.set_images(self.images.button(Images.BUTTON_OFS_KEY + key))
        self.handle_select_key(key)
        self.set_changed()
        return True

    def show_keyboard(self):
        if self.num:
            self.keyboards[0].hide()
            self.keyboards[1].hide()
            self.keyboards[2].show()
            self.set_changed()
            return True
        if self.caps:
            self.keyboards[0].hide()
            self.keyboards[1].show()
            self.keyboards[2].hide()
            self.set_changed()
            return True
        self.keyboards[0].show()
        self.keyboards[1].hide()
        self.keyboards[2].hide()        
        self.set_changed()
        return True
    
    def handle_select_key(self, keycode):
        if self.caps == 1:
            self.caps = 0
            self.show_keyboard()
        self.keyboard_handler(keycode)
        return True
    
    def handle_caps(self):
        if self.num:
            self.num = 0
            self.caps = 0
            for num_button in self.num_buttons:
                num_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + 0x0e))
        else:
            self.caps = self.caps + 1
            if self.caps == 3:
                self.caps = 0
        if self.caps < 2:
            b = 0x1e
        else:
            b = 0x1f
        for caps_button in self.caps_buttons:
            caps_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + b))
        self.show_keyboard()
        return True
        
    def handle_alphanum(self):
        self.num = 1 - self.num
        if self.num == 0:
            self.caps = 0
        for caps_button in self.caps_buttons:
            caps_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + 0x1e))
        if self.num == 0:
            b = 0x0e
        else:
            b = 0x0f
        for num_button in self.num_buttons:
            num_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + b))
        self.show_keyboard()
        return True


class RadioPlayView(UiComponent):
                    
    def __init__(self, screen, images, framebuilder, fonts, sizes, colors):
        UiComponent.__init__(self)
        self.screen = screen
        self.images = images
        self.framebuilder = framebuilder
        
        self.show_start_button = False
        self.station = None
        self.favourite = False
              
        self.add(ImageComponent(self.images.label(Images.LABEL_RADIO_PI)).set_pos(20, 0))
        self.add(ImageComponent(self.images.label(Images.LABEL_WAVE)).set_pos(140, 0))
        
        self.framebuilder.frame(self, 0, 2, 16, 6)
        self.framebuilder.frame(self, 0, 8, 4, 4)
        self.framebuilder.frame(self, 4, 8, 4, 4)
        self.framebuilder.frame(self, 8, 8, 4, 4)
        self.framebuilder.frame(self, 12, 8, 4, 4)

        self.handle_volume_down = self.default_key_handler
        self.handle_volume_up = self.default_key_handler
        self.handle_start = self.default_key_handler
        self.handle_stop = self.default_key_handler
        self.handle_select_station = self.default_key_handler
        self.handle_favourite = self.default_favourite_handler
        
        self.volume_up_button = ButtonComponent(self.images.button(Images.BUTTON_VOLUME_DOWN))\
            .set_pos(0, 160)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_volume_down()) 
        self.add(self.volume_up_button)

        self.volume_down_button = ButtonComponent(self.images.button(Images.BUTTON_VOLUME_UP))\
            .set_pos(80, 160)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_volume_up())  
        self.add(self.volume_down_button)

        self.start_stop_button = ButtonComponent(self.images.button(Images.BUTTON_STOP))\
            .set_pos(160, 160)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_start_stop()) 
        self.add(self.start_stop_button)
        
        self.add(ButtonComponent(self.images.button(Images.BUTTON_SELECT_STATION))\
            .set_pos(240, 160)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_station())
            )

        self.stationlabel = TextlabelComponent("---", fonts, sizes, colors)
        self.stationlabel.set_pos(10, 50).set_size(300, 100) 
        self.add(self.stationlabel)

        # favourite
        self.favourite_button = ButtonComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x2f))
        self.favourite_button.set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.switch_favourite()).set_pos(290, 50)
        self.add(self.favourite_button)

        self.set_station(None)

    def switch_favourite(self):
        self.favourite = not self.favourite
        self.set_favourite_button(self.favourite)
        self.handle_favourite(self.favourite)

    def set_favourite_button(self, favourite):
        if self.favourite:
            self.favourite_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + 0x2e))
        else:
            self.favourite_button.set_images(self.images.button(Images.BUTTON_OFS_KEY + 0x2f))                                

    def set_station(self, station):
        self.station = station
        if self.station == None:
            self.stationlabel.set_text(" \n \n^°   --- no audio stream ---°_")
            self.favourite_button.deactivate()
            self.start_stop_button.deactivate()
            self.volume_up_button.deactivate()
            self.volume_down_button.deactivate()
        else:
            self.stationlabel.set_text(
                "^*%s*_\n*%s*\n%s\n_~%s~\n~%s~^" % (
                    self.station.get_name(),
                    # self.station.get_votes(), 
                    # self.station.get_negative_votes(), 
                    " ".join(self.station.get_tags()),
                    self.station.get_location(),
                    self.station.get_codec(),
                    self.station.get_homepage()
                ))
            self.favourite = self.station.get_favourite()
            self.set_favourite_button(self.favourite)
            self.favourite_button.activate()
            self.start_stop_button.activate()
            self.volume_up_button.activate()
            self.volume_down_button.activate()
        self.set_changed()

    def default_key_handler(self):
        print("default button handler")
        
    def default_favourite_handler(self, favourite):
        print("default favourite handler: %s" % favourite)

    def handle_start_stop(self):
        if self.show_start_button:
            self.show_start_button = False
            self.start_stop_button.set_images(self.images.button(Images.BUTTON_STOP))
            self.handle_start()
        else:
            self.show_start_button = True
            self.start_stop_button.set_images(self.images.button(Images.BUTTON_START))
            self.handle_stop()

                        
class RadioSelectView(UiComponent):
                    
    def __init__(self, screen, images, framebuilder, fonts, sizes, colors):
        UiComponent.__init__(self)
        self.screen = screen
        self.images = images
        self.framebuilder = framebuilder
        self.fonts = fonts
        self.sizes = sizes
        self.colors = colors
        self.keyboard_mode = 0  # 0 = num, 1 = numeric
        self.filter = ""
        self.show_start_button = True

        self.favourite = False
        self.favourite_icon = ButtonComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x2e))
              
        self.add(ImageComponent(self.images.label(Images.LABEL_RADIO_PI)).set_pos(20, 0))
        self.add(ImageComponent(self.images.label(Images.LABEL_WAVE)).set_pos(140, 0))
        
        self.framebuilder.frame(self, 0, 2, 14, 6)
        #self.framebuilder.frame(self, 14, 2, 2, 2)
        self.framebuilder.frame(self, 14, 2, 2, 4)
#        self.framebuilder.frame(self, 14, 6, 2, 2)
        self.framebuilder.frame(self, 0, 8, 16, 4)
                
        self.handle_select_up = self.default_key_handler
        self.handle_select_down = self.default_key_handler
        self.handle_select_key = self.default_key_handler
        self.handle_play_station = self.default_play_station_handler
        self.handle_setup = self.default_key_handler
        self.handle_select_station = self.default_key_handler

        self.add(ButtonComponent(self.images.button(Images.BUTTON_SETUP))\
            .set_pos(280, 120)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_setup())
            )

        self.add(ButtonComponent(self.images.button(Images.BUTTON_SELECT_UP))\
            .set_pos(280, 45)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_up())
            )

        self.add(ButtonComponent(self.images.button(Images.BUTTON_SELECT_DOWN))\
            .set_pos(280, 75)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_down())
            )

        self.station_list_view = ListViewComponent(self.fonts, self.sizes, self.colors)
        self.station_list_view.set_size(260, 100, 35).set_pos(10, 50)
        self.station_list_view.set_to_string(lambda station: self.get_station_string(station))
        self.station_list_view.set_to_icon(lambda station: self.get_station_icon(station)) 
        self.station_list_view.set_handle_select(lambda station: self.handle_play_station(station))
        self.station_list_view.set_empty_message("-- no stations found --")
        self.add(self.station_list_view)

        self.keyboard = KeyboardComponent(self.images)
        self.keyboard.set_pos(10, 170).set_size(300, 60)
        self.keyboard.set_keyboard_handler(lambda keycode: self.handle_select_key(keycode))
        self.add(self.keyboard) 

    def set_stations(self, stations, name_filter):
        self.filter = name_filter
        if len(stations) == 0:
            self.station_list_view.set_empty_message("_-- no stations found for *°%s°* --^" % name_filter.upper()) 
        self.station_list_view.set_items(stations)
        self.set_changed()

    def get_station_string(self, station):
        s = "_*%s* %s\n%s - %s" % (
            station.get_name(),
            station.get_location(),
            " ".join(station.get_tags()),
            station.get_codec(),
            )
        if self.filter:
            for F in self.filter.upper().split():
                S = s.upper()
                i0 = 0
                i = S.find(F)
                result = ""
                while i >= 0:
                    if (i > 0): 
                        result = result + s[i0:i]
                    result = result + "°" + s[i:i + len(F)] + "°"
                    i0 = i + len(F)
                    i = S.find(F, i0)
                if (i0 < len(S)): 
                    result = result + s[i0:]
                s = result
        return s
        
    def get_station_icon(self, station):
        if not station.get_favourite():
            return None
        return self.favourite_icon

    def default_key_handler(self):
        print("default button handler")

    def default_play_station_handler(self, station):
        print("default station handler")

        
class RadioSetupView(UiComponent):
                    
    def __init__(self, screen, images, framebuilder, fonts, sizes, colors):
        UiComponent.__init__(self)
        self.screen = screen
        self.images = images
        self.framebuilder = framebuilder
        self.fonts = fonts
        self.sizes = sizes
        self.colors = colors
        
        self.handle_select_up = self.default_handler      
        self.handle_select_down = self.default_handler
        self.handle_select_wlan= self.default_select_handler
        self.handle_change_password = self.default_handler
        self.handle_return_key = self.default_handler
        self.handle_scan_wlan = self.default_handler

        self.add(ImageComponent(self.images.label(Images.LABEL_RADIO_PI)).set_pos(20, 0))
        self.add(ImageComponent(self.images.label(Images.LABEL_WAVE)).set_pos(140, 0))
        
        self.framebuilder.frame(self, 0, 2, 9, 3)
        self.framebuilder.frame(self, 0, 5, 9, 3)
        self.framebuilder.frame(self, 9, 2, 7, 6)

        self.ssid = ""
        self.pw = ""
        
        self.edit_pw = True
        
        self.lan_ip = "unknown"
        self.wlan_ip = "unknown"
        
        self.wlan_list = []

        self.framebuilder.frame(self, 0, 8, 16, 4)
                        
        self.add(ButtonComponent(self.images.button(Images.BUTTON_SMALL_UP))\
            .set_pos(188, 50)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_up())
            )

        self.add(ButtonComponent(self.images.button(Images.BUTTON_SCAN))\
            .set_pos(188, 90)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_scan_wlan())
            )

        self.add(ButtonComponent(self.images.button(Images.BUTTON_SMALL_DOWN))\
            .set_pos(188, 130)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_select_down())
            )

        self.network_status_label = TextlabelComponent("",
                                                       self.fonts, self.sizes, self.colors)
        self.network_status_label.set_pos(10, 55).set_size(170, 50)
        self.add(self.network_status_label)
        
        self.network_ssid_label = TextlabelComponent("", self.fonts, self.sizes, self.colors)
        self.network_ssid_label.set_pos(10, 115).set_size(170, 18)
        self.network_ssid_label.set_event_listener(UiEvent.MOUSE_CLICK_EVENT, self.on_edit_ssid_field)
        self.add(self.network_ssid_label)

        self.network_pw_field = TextlabelComponent("", self.fonts, self.sizes, self.colors)
        self.network_pw_field.set_pos(10, 130).set_size(140, 18)
        self.network_pw_field.set_event_listener(UiEvent.MOUSE_CLICK_EVENT, self.on_edit_pw_field)
        self.add(self.network_pw_field)

        self.add(ButtonComponent(self.images.button(Images.BUTTON_OFS_KEY + 0x3d))\
            .set_pos(150, 130)\
            .set_event_listener(UiEvent.MOUSE_CLICK_EVENT, lambda event, source: self.handle_change_password())
            )
        
        self.wlan_level_icons = [
                ImageComponent(self.images.label(Images.LABEL_WLAN_0)),
                ImageComponent(self.images.label(Images.LABEL_WLAN_1)),
                ImageComponent(self.images.label(Images.LABEL_WLAN_2)),
                ImageComponent(self.images.label(Images.LABEL_WLAN_3)),
            ]
        
        self.wlan_list_view = ListViewComponent(self.fonts, self.sizes, self.colors)
        self.wlan_list_view.set_size(100, 100, 17).set_pos(210, 50)
        self.wlan_list_view.set_to_string(lambda item: self.wlan_item_to_string(item))
        self.wlan_list_view.set_to_icon(lambda item: self.wlan_item_to_icon(item))
        self.wlan_list_view.set_handle_select(lambda item: self.handle_select_wlan(item))
        self.wlan_list_view.set_empty_message("_- no signal -")
        self.wlan_list_view.set_items(self.wlan_list)
        self.add(self.wlan_list_view)

        self.keyboard = KeyboardComponent(self.images)
        self.keyboard.set_pos(10, 170).set_size(300, 60)
        self.keyboard.set_keyboard_handler(lambda keycode: self.handle_select_key(keycode))
        self.keyboard.disable_favourite_button()
        self.add(self.keyboard) 
        
        self.set_ips("", "")
        self.set_pw("")
        self.set_ssid("")

    def on_edit_ssid_field(self, event, source):
        self.edit_pw = False
        self.update_pw_field()
        self.update_ssid_field()
        return True
        
    def on_edit_pw_field(self, event, source):
        self.edit_pw = True
        self.update_pw_field()
        self.update_ssid_field()
        return True

    def masked(self, s):
        return "." * len(s)
    
    def set_ips(self, lan_ip, wlan_ip):
        if lan_ip:
            self.lan_ip = lan_ip
        else:
            self.lan_ip = "unknown"
        if wlan_ip:
            self.wlan_ip = wlan_ip
        else:
            self.wlan_ip = "unknown"
        self.network_status_label.set_text("_*LAN:* %s\n*WLAN:* %s" % (self.lan_ip, self.wlan_ip))
        self.set_changed()

    def set_ssid(self, ssid):
        self.ssid = ssid
        self.update_ssid_field()

    def update_ssid_field(self):
        cursor = ""
        if not self.edit_pw:
            cursor = "\\_"
        if self.ssid:
            self.network_ssid_label.set_text("_*SSID:* °%s%s°" % (self.ssid, cursor))
        else:
            self.network_ssid_label.set_text("_*SSID:* °%s°" % cursor)
        self.set_changed()

    def get_ssid(self):
        return self.ssid

    def set_pw(self, pw):
        self.pw = pw
        self.update_pw_field()

    def update_pw_field(self):        
        cursor = ""
        if self.edit_pw:
            cursor = "\\_"
        if self.pw:
            self.network_pw_field.set_text("_*PW:* °%s%s°" % (self.masked(self.pw), cursor))
        else:
            self.network_pw_field.set_text("_*PW:* °%s°" % cursor)            
        self.set_changed()
        
    def get_pw(self):
        return self.pw
        
    def set_wlan_list(self, wlan_list):
        self.wlan_list = wlan_list
        self.wlan_list_view.set_items(self.wlan_list)
        self.wlan_list_view.set_selected(0)
        self.set_changed()

    def wlan_item_to_icon(self, item):
        n = int(3.9 * item.level / item.level_max)
        return self.wlan_level_icons[n]
        
    def wlan_item_to_string(self, item):
        ssid = item.ssid
        if ssid == self.ssid:
            return "_*" + ssid + "*"
        return "_" + ssid
    
    def handle_select_key(self, keycode):
        # delete
        if keycode == 0x0d:
            if self.edit_pw:
                self.set_pw("")
            else:
                self.set_ssid("")
        # backspace
        elif keycode == 0x0c:
            if self.edit_pw:
                self.set_pw(self.pw[0:-1])
            else:
                self.set_ssid(self.ssid[0:-1])
        # return
        elif keycode == 0x2d:
            self.handle_return_key()
        else:
            if self.edit_pw:
                self.set_pw(self.pw + KeyboardComponent.CHARSET[keycode])
            else:
                self.set_ssid(self.ssid + KeyboardComponent.CHARSET[keycode])
        return True
    
    def default_handler(self):
        print ("default handler")
        return True

    def default_select_handler(self, item):
        print ("default selection handler: %s" % item)
        return True
