from threading import Thread, Event

#importing Database
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db
from modules.ResourceSampling import sampleMyAppStatus
import modules
from modules import costants
iter_count = 0

class SimThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown_flag = Event()
    def run(self):
        global iter_count
        while not self.shutdown_flag.is_set():        
            iter_count += 1
            devices = db.getDevices()
            for dev in devices:
                for installedApp in dev["installedApps"]:
                    try:
                        job = db.getJob(installedApp)
                        # Check if the jobs is health
                        for device in job["devices"]:
                            devid = device["deviceId"]
                            sampled = sampleMyAppStatus(devid, device["resourceAsk"]["resources"]["cpu"], 
                                                            device["resourceAsk"]["resources"]["memory"])
                            if sampled["hasCPU"] == False:
                                db.addSimulationValues({
                                    "myAppId": job["myappid"],
                                    "deviceId": devid,
                                    "time": int(time.time()),
                                    "type": costants.FEW_CPU
                                })
                            if sampled["hasMEM"] == False:
                                db.addSimulationValues({
                                    "myAppId": job["myappid"],
                                    "deviceId": devid,
                                    "time": int(time.time()),
                                    "type": costants.FEW_MEM
                                })
                    except TypeError:
                        continue

def getSimulationValues():
    simVal = db.getSimulationValues()
    counters = {}
    for val in simVal:
        myapp = db.getMyApp(val["myAppId"])
        try:
            count = counters[myapp["name"]]
        except KeyError:
            counters[myapp["name"]] = {"name": myapp["name"], "few_cpu_count": 0, "few_mem_count": 0}
            count = counters[myapp["name"]]
        if val["type"] == costants.FEW_CPU: 
            count["few_cpu_count"] = count["few_cpu_count"] + 1
        if val["type"] == costants.FEW_MEM:
            count["few_mem_count"] = count["few_mem_count"] + 1
    values = {}
    values["myapps"] = counters
    values["totalCount"] = iter_count
    return values
                