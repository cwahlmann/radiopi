import threading
import time

i = 0
running = True

def loop():
    global i, running
    while running:
        i = i + 1
        print(i)
        time.sleep(0.5)
        
print("START")
threading.Thread(target=loop).start()
time.sleep(2)
print("STOP")
running = False
