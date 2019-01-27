import time

from controller.threads import TimerThread


class Time:

    def __init__(self):
        self.hh = 0
        self.mm = 0
        self.ss = 0
        
    def get_time(self):
        return (self.hh, self.mm, self.ss)

    def with_time(self, time):
        (self.hh, self.mm, self.ss) = time
        return self
        
    def get_hh(self):
        return self.hh

    def get_mm(self):
        return self.mm

    def get_ss(self):
        return self.ss
    
    def with_hh(self, hh):
        self.hh = hh
        return self
    
    def with_mm(self, mm):
        self.mm = mm
        return self

    def with_ss(self, ss):
        self.ss = ss
        return self
    
    def is_before(self, other):
        if self.hh < other.hh:
            return True
        if self.hh == other.hh:
            return False
        if self.mm < other.mm:
            return True
        if self.mm == other.mm:
            return False
        return self.ss < other.ss
        
    def is_after(self, other):
        if self.hh > other.hh:
            return True
        if self.hh == other.hh:
            return False
        if self.mm > other.mm:
            return True
        if self.mm == other.mm:
            return False
        return self.ss > other.ss

    def matches(self, other, match_ss=False):
        matching = self.hh == other.hh and self.mm == other.mm and (not match_ss or self.ss == other.ss)
        return matching

    def add(self, other):
        t = (self.hh + other.get_hh()) * 3600 + (self.mm + other.get_mm()) * 60 + self.ss + other.get_ss()
        (r, ss) = divmod(t, 60)
        (r1, mm) = divmod(r, 60)
        (x, hh) = divmod(r1, 24)
        return Time().with_time((hh, mm, ss))
         
    def sub(self, other):
        t = (self.hh - other.get_hh()) * 3600 + (self.mm - other.get_mm()) * 60 + self.ss - other.get_ss()
        if t < 0:
            t = t + 24 * 3600
        (r, ss) = divmod(t, 60)
        (r1, mm) = divmod(r, 60)
        (x, hh) = divmod(r1, 24)
        return Time().with_time((hh, mm, ss))
    
    def get_string(self):
        return "%02d:%02d.%02d" % (self.get_hh(), self.get_mm(), self.get_ss())

                
class AlarmClock:

    def __init__(self):
        self.wake = Time()
        self.wake_enabled = False
        self.wake_matched = False
        self.sleep = Time()
        self.sleep_enabled = False
        self.sleep_matched = False
        self.offset = Time()
        self.tick_handler = lambda t: print("T I C K %s" % t.get_string())
        self.wake_handler = lambda t: print("WAKE %s" % t.get_string())
        self.sleep_handler = lambda t: print("SLEEP %s" % t.get_string())
        self.timer_thread = TimerThread(1).with_runnable(self.handle_tick)
        self.timer_thread.start()

    def on_tick(self, tick_handler):
        self.tick_handler = tick_handler
        
    def on_wake(self, wake_handler):
        self.wake_handler = wake_handler

    def on_sleep(self, sleep_handler):
        self.sleep_handler = sleep_handler

    def current_time(self):
        (tm_year,
        tm_mon,
        tm_mday,
        tm_hour,
        tm_min,
        tm_sec,
        tm_wday,
        tm_yday,
        tm_isdst) = time.localtime(time.time())
        return Time().with_time((tm_hour, tm_min, tm_sec)).add(self.offset)

    def with_wake(self, time_wake):
        self.wake = time_wake
        self.wake_enabled = True
        return self
    
    def with_no_wake(self):
        self.wake_enabled = False
        return self

    def with_sleep(self, time_sleep):
        self.sleep = time_sleep
        self.sleep_enabled = True
        return self

    def with_no_sleep(self):
        self.sleep_enabled = False
        return self
        
    def with_offset(self, offset):
        self.offset = offset
        return self

    def get_wake(self):
        return self.wake
    
    def get_sleep(self):
        return self.sleep
    
    def get_offset(self):
        return self.offset
    
    def handle_tick(self):
        t = self.current_time()
        
        if self.wake_enabled:
            if self.wake.matches(t):
                if not self.wake_matched:
                    self.wake_matched = True
                    self.wake_handler(t)
            else:
                self.wake_matched = False

        if self.sleep_enabled:
            if self.sleep.matches(t):
                if not self.sleep_matched:
                    self.sleep_matched = True
                    self.sleep_handler(t)
            else:
                self.sleep_matched = False
        
        self.tick_handler(t)
        
