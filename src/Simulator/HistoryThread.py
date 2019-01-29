from threading import Thread, Lock, Event
import time
from Simulator.SimThread import getDeviceSampling, getMyAppsSampling

lock = Lock()
uptime_history = []
energy_history = []

def reset_history():
    global uptime_history
    global energy_history
    global lock
    with lock:
        uptime_history = []
        energy_history = []
    

class Historian(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown_flag = Event()

    def run(self):
        global lock
        global uptime_history
        global energy_history
        while not self.shutdown_flag.is_set():
            values = getMyAppsSampling()
            total = 1
            if len(values) != 0:
                total = 0
                for val in values:
                    total += val["UP_PERCENTAGE"]
                total = total / len(values)

            values = getDeviceSampling()
            energy = 0
            for val in values:
                energy += val["DEVICE_ENERGY_CONSUMPTION"]
            with lock:
                uptime_history.append(total)
                energy_history.append(energy)
            time.sleep(2)

def get_uptime_history():
    global lock
    with lock:
        return uptime_history
    
def get_energy_history():
    global lock
    with lock:
        return energy_history