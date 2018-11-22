from threading import Thread, Event

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class SimThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown_flag = Event()
    def run(self):
        while not self.shutdown_flag.is_set():
            devices = db.getDevices()
            for dev in devices:
                for installedApp in dev["installedApps"]:
                    job = db.getJob(installedApp)
                    print job