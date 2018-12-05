from threading import Thread, Event

#importing Database
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

from modules.ResourceSampling import sampleCPU, sampleMEM
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
            device_sampled_values = {}
            for dev in db.getDevices():   
                sampled_free_cpu = sampleCPU(dev["deviceId"]) - dev["usedCPU"] 
                sampled_free_mem = sampleMEM(dev["deviceId"]) - dev["usedMEM"]
                device_sampled_values[dev["deviceId"]] = {"free_cpu": sampled_free_cpu, "free_mem": sampled_free_mem}
                if sampled_free_cpu <= 0:
                    db.addSimulationValues({
                        "time": time.time(),
                        "type": costants.DEVICE_LOW_CPU,
                        "deviceId": dev["deviceId"],
                        "value": sampled_free_mem
                    })
                if sampled_free_mem <= 0:
                    db.addSimulationValues({
                        "time": time.time(),
                        "type": costants.DEVICE_LOW_MEM,
                        "deviceId": dev["deviceId"],
                        "value": sampled_free_mem
                    })
            for myapp in db.getMyApps():
                # If exists a job with mypp => it is installed
                jobs = db.getJobs(myapp["myappId"])
                if jobs.count() == 0:
                    db.addSimulationValues({
                        "myappId": myapp["myappId"],
                        "value": costants.MYAPP_UNINSTALLED,
                        "type": costants.MYAPP_STATUS
                    })
                else:
                    db.addSimulationValues({
                        "myappId": myapp["myappId"],
                        "value": costants.MYAPP_INSTALLED,
                        "type": costants.MYAPP_STATUS
                    })
            for job in db.getJobs():
                # Cleaning all alerts inserted in previous simulation iter
                db.deleteFromSamplingAlerts()
                for device in job["payload"]["deploy"]["devices"]:
                    db.addSimulationValues({
                        "type": costants.APP_ON_DEVICE,
                        "deviceId": device["deviceId"],
                        "myappId": job["myappId"],
                        "status": costants.JOB_STARTED if job["status"] == "start" else costants.JOB_STOPPED
                    })
                    # To manage respect with app distribution, generates alerts
                    sampled_free_cpu = device_sampled_values[device["deviceId"]]["free_cpu"]
                    sampled_free_mem = device_sampled_values[device["deviceId"]]["free_mem"]
                    #cpu_request = device["resourceAsk"]["resources"]["cpu"]
                    #mem_request = device["resourceAsk"]["resources"]["memory"]
                    if sampled_free_cpu < 0: # TODO: Extend with memory
                        device_details = db.getDevice(device["deviceId"])
                        myapp_details = db.getMyApp(job["myappId"])
                        db.addAlert({
                            "deviceId": device["deviceId"],
                            "ipAddress": device_details["ipAddress"],
                            "hostname": device_details["ipAddress"],
                            "appName": myapp_details["name"],
                            "severity": "critical",
                            "type": "status",
                            "message": "The node on which this app is installed has critical problem with resources",
                            #"message": "The desired state of the app on this device was \"running\" but the actual state is \"stopped\"",
                            "time": int(time.time()), # Relative
                            "source": "Device periodic report",
                            "action": "",
                            "status": "ACTIVE",
                            "pagiaros_type": costants.APP_HEALTH
                        }, from_sampling=True)
                        db.addSimulationValues({
                            "type": costants.APP_ON_DEVICE_WITH_NO_RESOURCES,
                            "myappId": job["myappId"],
                            "deviceId": device["deviceId"]
                        })


def getDeviceSampling():
    devices = db.getDevices()
    result = []
    fix_iter = float(iter_count)
    for dev in devices:
        tmp = {}
        tmp["deviceId"] = dev["deviceId"]
        tmp["ipAddress"] = dev["ipAddress"]
        tmp["port"] = dev["port"]
        tmp["FEW_CPU_PERCENTAGE"] = ( db.getSimulationValues({"type": costants.DEVICE_LOW_CPU, "deviceId": dev["deviceId"]}).count() ) / fix_iter
        tmp["FEW_MEM_PERCENTAGE"] = ( db.getSimulationValues({"type": costants.DEVICE_LOW_MEM, "deviceId": dev["deviceId"]}).count() ) / fix_iter
        result.append(tmp)
    return result

def getMyAppsSampling():
    myapps = db.getMyApps()
    result = []
    fix_iter = float(iter_count)
    for myapp in myapps:
        inst = float(db.db.simulation.count({"myappId": myapp["myappId"], "type": costants.MYAPP_STATUS, "value": costants.MYAPP_INSTALLED}))
        uninst = float(db.db.simulation.count({"myappId": myapp["myappId"], "type": costants.MYAPP_STATUS, "value": costants.MYAPP_UNINSTALLED}))
        tmp = {}
        tmp["myappId"] = myapp["myappId"]
        tmp["name"] = myapp["name"]
        tmp["UNINSTALLED_TIME_PERCENTAGE"] = uninst / (inst+uninst)
        tmp["INSTALLED_TIME_PERCENTAGE"] =  inst / (inst + uninst)
        result.append(tmp)
    return result

def getAppOnDeviceSampling():
    myapps = db.getMyApps()
    result = []
    fix_iter = float(iter_count)     
    query_result = db.db.simulation.aggregate([   
            {
                "$match": { "type": costants.APP_ON_DEVICE}
            },
            {
                "$project": {
                    "myappId": "$myappId",
                    "deviceId": "$deviceId",
                    "started": { "$cond": [ { "$eq": ["$status", costants.JOB_STARTED] }, 1, 0 ] },
                    "stopped": { "$cond": [ { "$eq": ["$status", costants.JOB_STOPPED] }, 1, 0 ] } 
                }
            },
            {
                "$group": {
                    "_id": { "deviceId": "$deviceId", "myappId": "$myappId" },
                    "start_count": { "$sum": "$started" },
                    "stop_count": { "$sum": "$stopped" },
                    "total_count": { "$sum": 1 }
                }
            }
    ])
    for doc in query_result:
        result.append({
            "myappId": doc["_id"]["myappId"],
            "deviceId": doc["_id"]["deviceId"],
            "START_TIME_PERCENTAGE": doc["start_count"] / float(doc["total_count"]),
            "STOP_TIME_PERCENTAGE": doc["stop_count"] / float(doc["total_count"]),
            "INSTALL_ON_DEVICE_PERCENTAGE": float(doc["total_count"]) / db.db.simulation.count({"myappId": doc["_id"]["myappId"], "type": costants.MYAPP_STATUS, "value": costants.MYAPP_INSTALLED}) 
        })
    return result