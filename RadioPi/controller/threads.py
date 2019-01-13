from threading import Thread
from time import sleep

class InterruptableThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.runnable = lambda: False
        self.interrupted = False
    
    def interrupt(self):
        self.interrupted = True
        
    def is_interrupted(self):
        return self.interrupted
    
    def with_runnable(self, runnable):
        self.runnable = runnable
        return self

    def get_runnable(self):
        return self.runnable

    def run(self):
        self.runnable()


class TimerThread(InterruptableThread):

    def __init__(self, delay):
        InterruptableThread.__init__(self)
        self.delay = delay
        self.running_thread = None

    def run(self):
        while not self.is_interrupted():
            if self.running_thread:
                self.running_thread.interrupt()                
            self.running_thread = InterruptableThread().with_runnable(self.get_runnable())
            self.running_thread.start()
            sleep(self.delay)
        if self.running_thread:
            self.running_thread.interrupt()
