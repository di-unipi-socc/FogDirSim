from threading import Thread, Event
import time, random
import Database as db
from Simulator.ResourceSampling import sampleCPU, sampleMEM, get_truncated_normal
from constants import queue
from config import profile_low, profile_normal, profile_high, getEnergyConsumed
import constants
iter_count = 0

# Volatile Simulaton Memory
DEVICE_CRITICAL_CPU_counter_sum = {} 
DEVICE_CRITICAL_MEM_counter_sum = {}
DEVICE_CPU_USED_sum = {}
DEVICE_MEM_USED_sum = {}
resources_sampled_count = {}
NUMBER_OF_MYAPP_ON_DEVICE_counter_sum = {}
DEVICE_DOWN_counter_sum = {}
MYAPP_UP_counter = {}
MYAPP_DOWN_counter = {}
MYAPP_CPU_CONSUMING_counter = {}
MYAPP_MEM_CONSUMING_counter = {}
MYAPP_ON_DEVICE_counter = {}
DEVICE_ENERGY_CONSUMPTION_sum = {}

def resources_requested(sourceAppName):
    localapp_details = db.getLocalApplicationBySourceName(sourceAppName)
    # TODO: Complete function
    return (100, 32)

def get_profile_values(profile):
    if profile == constants.MYAPP_PROFILE_HIGH:
        return profile_high
    elif profile == constants.MYAPP_PROFILE_LOW:
        return profile_low
    else:
        return profile_normal


class SimThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.shutdown_flag = Event()
    def run(self):
        global iter_count
        while not self.shutdown_flag.is_set():
            queue.execute_next_task() # Executes a task if present, otherwise returns immediately
            iter_count += 1
            device_sampled_values = {}
            for dev in db.getDevices():
                deviceId = dev["deviceId"]
                # Initializing Variable
                if not deviceId in DEVICE_CRITICAL_CPU_counter_sum:
                    DEVICE_CRITICAL_CPU_counter_sum[deviceId] = 0
                if not deviceId in DEVICE_CRITICAL_MEM_counter_sum:
                    DEVICE_CRITICAL_MEM_counter_sum[deviceId] = 0
                if not deviceId in DEVICE_CPU_USED_sum:
                    DEVICE_CPU_USED_sum[deviceId] = 0
                if not deviceId in DEVICE_MEM_USED_sum:
                    DEVICE_MEM_USED_sum[deviceId] = 0
                if not deviceId in NUMBER_OF_MYAPP_ON_DEVICE_counter_sum:
                    NUMBER_OF_MYAPP_ON_DEVICE_counter_sum[deviceId] = 0
                if not deviceId in DEVICE_DOWN_counter_sum:
                    DEVICE_DOWN_counter_sum[deviceId] = 0
                if not deviceId in resources_sampled_count:
                    resources_sampled_count[deviceId] = 0
                if not deviceId in DEVICE_ENERGY_CONSUMPTION_sum:
                    DEVICE_ENERGY_CONSUMPTION_sum[deviceId] = 0    
                r = random.random()
                if dev["alive"] and r <= dev["chaos_down_prob"]:
                    db.setDeviceDown(deviceId)
                if not dev["alive"] and r <= dev["chaos_revive_prob"]:
                    db.setDeviceAlive(deviceId)  

                if db.deviceIsAlive(deviceId):
                    sampled_free_cpu = sampleCPU(deviceId) - dev["usedCPU"] 
                    sampled_free_mem = sampleMEM(deviceId) - dev["usedMEM"]
                    device_sampled_values[deviceId] = {"free_cpu": sampled_free_cpu, "free_mem": sampled_free_mem}
                    # adding critical CPU, MEM
                    if sampled_free_cpu <= 0:
                        DEVICE_CRITICAL_CPU_counter_sum[deviceId] += 1
                    if sampled_free_mem <= 0:
                        DEVICE_CRITICAL_MEM_counter_sum[deviceId] += 1
                    # adding sampled resources
                    DEVICE_CPU_USED_sum[deviceId] += dev["usedCPU"]
                    DEVICE_MEM_USED_sum[deviceId] += dev["usedMEM"]
                    
                    cpu_usage = dev["totalCPU"]-sampled_free_cpu
                    mem_usage = dev["totalMEM"]-sampled_free_mem
                    basal_cpu_usage = cpu_usage - dev["usedCPU"]
                    basal_mem_usage = mem_usage - dev["usedMEM"]
                    consumed_energy = (getEnergyConsumed(deviceId, cpu_usage, mem_usage) - 
                                        getEnergyConsumed(deviceId, basal_cpu_usage, basal_mem_usage))
                    DEVICE_ENERGY_CONSUMPTION_sum[deviceId] += consumed_energy
                    resources_sampled_count[deviceId] += 1
                    # adding number of installed apps
                    NUMBER_OF_MYAPP_ON_DEVICE_counter_sum[deviceId] += len(dev["installedApps"])            
                else: 
                    DEVICE_DOWN_counter_sum[deviceId] += 1
            
            db.deleteFromSamplingAlerts() # Cleaning all alerts inserted in previous simulation iter
            myapp_jobs_up_counter = {}
            myapp_jobs_down_counter = {}
            for job in db.getJobs():
                myappId = job["myappId"]
                if not myappId in MYAPP_ON_DEVICE_counter:
                    MYAPP_ON_DEVICE_counter[myappId] = {}
                if not myappId in MYAPP_CPU_CONSUMING_counter:
                    MYAPP_CPU_CONSUMING_counter[myappId] = {}
                    MYAPP_MEM_CONSUMING_counter[myappId] = {}
                myapp_details = db.getMyApp(myappId)
                localapp_resources = resources_requested(myapp_details["sourceAppName"])
                max_cpu = localapp_resources[0]
                max_mem = localapp_resources[1]
                for device in job["payload"]["devices"]:
                    profile_values = get_profile_values(job["profile"])
                    allocated_cpu = device["resourceAsk"]["resources"]["cpu"]
                    allocated_mem = device["resourceAsk"]["resources"]["memory"]
                    application_cpu_sampling = get_truncated_normal(mean=profile_values[0]*max_cpu, sd=profile_values[0], low=0, upp=allocated_cpu+1).rvs()
                    application_mem_sampling = get_truncated_normal(mean=profile_values[0]*max_mem, sd=profile_values[0], low=0, upp=allocated_mem+1).rvs()
                    if device["deviceId"] in MYAPP_ON_DEVICE_counter[myappId]:
                        MYAPP_ON_DEVICE_counter[myappId][device["deviceId"]] += 1
                    else:
                        MYAPP_ON_DEVICE_counter[myappId][device["deviceId"]] = 1

                    device_details = db.getDevice(device["deviceId"])
                    if not db.deviceIsAlive(device["deviceId"]):
                        if not myappId in myapp_jobs_down_counter:
                            myapp_jobs_down_counter[myappId] = 1
                        else:
                            myapp_jobs_down_counter[myappId] += 1
                        db.addAlert({
                            "deviceId": device["deviceId"],
                            "ipAddress": device_details["ipAddress"],
                            "hostname": device_details["ipAddress"],
                            "appName": myapp_details["name"],
                            "severity": "critical",
                            "type": "status",
                            "message": "The device is not reachable",
                            #"message": "The desired state of the app on this device was \"running\" but the actual state is \"stopped\"",
                            "time": int(iter_count), # Relative
                            "source": "Device periodic report",
                            "action": "",
                            "status": "ACTIVE",
                            "simulation_type": constants.DEVICE_REACHABILITY
                        }, from_sampling=True)
                    else:
                        if not myappId in myapp_jobs_up_counter:
                            myapp_jobs_up_counter[myappId] = 1
                        else:
                            myapp_jobs_up_counter[myappId] += 1
                        sampled_free_cpu = device_sampled_values[device["deviceId"]]["free_cpu"]
                        sampled_free_mem = device_sampled_values[device["deviceId"]]["free_mem"]
                        if sampled_free_cpu < 0:
                            db.addAlert({
                                "deviceId": device["deviceId"],
                                "ipAddress": device_details["ipAddress"],
                                "hostname": device_details["ipAddress"],
                                "appName": myapp_details["name"],
                                "severity": "critical",
                                "type": "status",
                                "message": "The node on which this app is installed has critical problem with CPU resource",
                                #"message": "The desired state of the app on this device was \"running\" but the actual state is \"stopped\"",
                                "time": int(iter_count), # Relative
                                "source": "Device periodic report",
                                "action": "",
                                "status": "ACTIVE",
                                "simulation_type": constants.APP_HEALTH
                            }, from_sampling=True)
                        if sampled_free_mem < 0:
                            myapp_details = db.getMyApp(job["myappId"])
                            db.addAlert({
                                "deviceId": device["deviceId"],
                                "ipAddress": device_details["ipAddress"],
                                "hostname": device_details["ipAddress"],
                                "appName": myapp_details["name"],
                                "severity": "critical",
                                "message": "The node on which this app is installed has critical problem with Memory resource",
                                #"message": "The desired state of the app on this device was \"running\" but the actual state is \"stopped\"",
                                "time": int(iter_count), # Relative
                                "source": "Device periodic report",
                                "action": "",
                                "status": "ACTIVE",
                                "simulation_type": constants.APP_HEALTH
                            }, from_sampling=True)
                        if application_cpu_sampling > max_cpu*0.95:
                            db.addAlert({
                                "deviceId": device["deviceId"],
                                "ipAddress": device_details["ipAddress"],
                                "hostname": device_details["ipAddress"],
                                "appName": myapp_details["name"],
                                "severity": "critical",
                                "message": "Application is consuming more that 95%% of allocated CPU on current devices",
                                "time": int(iter_count), # Relative
                                "source": "Device periodic report",
                                "action": "",
                                "status": "ACTIVE",
                                "simulation_type": constants.MYAPP_CPU_CONSUMING
                            }, from_sampling=True)
                        if application_mem_sampling > max_mem*0.95:
                             db.addAlert({
                                "deviceId": device["deviceId"],
                                "ipAddress": device_details["ipAddress"],
                                "hostname": device_details["ipAddress"],
                                "appName": myapp_details["name"],
                                "severity": "critical",
                                "message": "Application is consuming more that 95%% of allocated MEM on current devices",
                                "time": int(iter_count), # Relative
                                "source": "Device periodic report",
                                "action": "",
                                "status": "ACTIVE",
                                "simulation_type": constants.MYAPP_MEM_CONSUMING
                            }, from_sampling=True)

            for myapp in db.getMyApps():
                myappId = myapp["myappId"]
                if myapp["minjobs"] == 0:
                    if myappId in myapp_jobs_down_counter and myapp_jobs_down_counter[myappId] > 0: # 0 is assumed to be "all jobs have to be run"
                        if myappId in MYAPP_DOWN_counter:
                            MYAPP_DOWN_counter[myappId] += 1
                        else:
                            MYAPP_DOWN_counter[myappId] = 1
                    else:
                        if myappId in MYAPP_UP_counter:
                            MYAPP_UP_counter[myappId] += 1
                        else:
                            MYAPP_UP_counter[myappId] = 1
                else:
                    if myapp["minjobs"] < myapp_jobs_up_counter[myappId]:
                        if myappId in MYAPP_UP_counter:
                            MYAPP_UP_counter[myappId] += 1
                        else:
                            MYAPP_UP_counter[myappId] = 1
                    else:
                        if myappId in MYAPP_DOWN_counter:
                            MYAPP_DOWN_counter[myappId] += 1
                        else:
                            MYAPP_DOWN_counter[myappId] = 1
                
                        
                        
def getDeviceSampling():
    devices = db.getDevices()
    result = []
    fix_iter = float(iter_count)
    for dev in devices:
        deviceId = dev["deviceId"]
        tmp = {}
        tmp["deviceId"] = deviceId
        tmp["ipAddress"] = dev["ipAddress"]
        tmp["port"] = dev["port"]
        tmp["totalCPU"] = dev["totalCPU"]
        tmp["totalMEM"] = dev["totalMEM"]
        tmp["CRITICAL_CPU_PERCENTAGE"] = DEVICE_CRITICAL_CPU_counter_sum[deviceId] / float(resources_sampled_count[deviceId])
        tmp["CRITICAL_MEM_PERCENTAGE"] = DEVICE_CRITICAL_MEM_counter_sum[deviceId] / float(resources_sampled_count[deviceId])
        tmp["AVERAGE_CPU_USED"] = DEVICE_CPU_USED_sum[deviceId] / float(resources_sampled_count[deviceId])
        tmp["AVERAGE_MEM_USED"] = DEVICE_MEM_USED_sum[deviceId] / float(resources_sampled_count[deviceId])
        tmp["AVERAGE_MYAPP_COUNT"] = NUMBER_OF_MYAPP_ON_DEVICE_counter_sum[deviceId] / float(resources_sampled_count[deviceId])
        tmp["DEVICE_DOWN_PROB_chaos"] = DEVICE_DOWN_counter_sum[deviceId] / fix_iter 
        tmp["DEVICE_ENERGY_CONSUMPTION"] = DEVICE_ENERGY_CONSUMPTION_sum[deviceId] / float(resources_sampled_count[deviceId]) 
        result.append(tmp)
    return result

def getMyAppsSampling():
    myapps = db.getMyApps()
    result = []
    fix_iter = float(iter_count)
    for myapp in myapps:
        myappId = myapp["myappId"]
        tmp = {}
        tmp["myappId"] = myappId
        tmp["name"] = myapp["name"]
        if myappId in MYAPP_UP_counter:
            tmp["UP_PERCENTAGE"] = MYAPP_UP_counter[myappId] / fix_iter
        else:
            tmp["UP_PERCENTAGE"] = 0
        if myappId in MYAPP_DOWN_counter:
            tmp["DOWN_PERCENTAGE"] = MYAPP_DOWN_counter[myappId] / fix_iter
        else: 
            tmp["DOWN_PERCENTAGE"] = 0
        if myappId in MYAPP_ON_DEVICE_counter:
            tmp["ON_DEVICE_PERCENTAGE"] = {k: (v / fix_iter) 
                                                for k,v in MYAPP_ON_DEVICE_counter[myappId].items()}
        else:
            tmp["ON_DEVICE_PERCENTAGE"] = {}
        result.append(tmp)
    return result
