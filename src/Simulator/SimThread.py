from threading import Thread, Event

#importing Database
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db
from modules.ResourceSampling import sampleMyAppStatus

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
                    # Check if the jobs is health
                    for device in job["devices"]:
                        devid = device["deviceId"]

                        sampled = sampleMyAppStatus(devid, device["resourcesAsk"]["resources"]["cpu"], 
                                                           device["resourcesAsk"]["resources"]["memory"])
                        if sampled["hasCPU"] == False:
                            db.addAlert({
                                "myAppId": job["myappid"],
                                "severity": "HIGH",
                                "message": "unsufficient resource CPU on device "+devid,
                                "deviceId": devid,
                                "time": int(time.time())
                            })
                        if sampled["hasMEM"] == False:
                            db.addAlert({
                                "myAppId": job["myappid"],
                                "severity": "HIGH",
                                "message": "unsufficient resource MEM on device "+devid,
                                "deviceId": devid,
                                "time": int(time.time())
                            })