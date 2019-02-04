from threading import Thread, Event, Lock
import time, random
import Database as db
from Simulator.ResourceSampling import sampleCPU, sampleMEM, get_truncated_normal
from constants import queue
from config import profile_low, profile_normal, profile_high, getEnergyConsumed
import constants
iter_count = 0

device_lock = Lock()
myapp_lock = Lock()
itercount_lock = Lock()

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
MYAPP_LIFETIME = {}
MYAPP_ON_DEVICE_counter = {}
DEVICE_ENERGY_CONSUMPTION_sum = {}
MYAPP_DEVICE_START_counter = {}
MYAPP_ALERT_counter = {}
MYAPP_ALERT_incrementing = {}

def reset_simulation_counters():
    global DEVICE_CRITICAL_CPU_counter_sum
    DEVICE_CRITICAL_CPU_counter_sum = {} 
    global DEVICE_CRITICAL_MEM_counter_sum
    DEVICE_CRITICAL_MEM_counter_sum = {}
    global DEVICE_CPU_USED_sum
    DEVICE_CPU_USED_sum = {}
    global DEVICE_MEM_USED_sum
    DEVICE_MEM_USED_sum = {}
    global resources_sampled_count
    resources_sampled_count = {}
    global NUMBER_OF_MYAPP_ON_DEVICE_counter_sum
    NUMBER_OF_MYAPP_ON_DEVICE_counter_sum = {}
    global DEVICE_DOWN_counter_sum
    DEVICE_DOWN_counter_sum = {}
    global MYAPP_UP_counter
    MYAPP_UP_counter = {}
    global MYAPP_DOWN_counter
    MYAPP_DOWN_counter = {}
    global MYAPP_CPU_CONSUMING_counter
    MYAPP_CPU_CONSUMING_counter = {}
    global MYAPP_MEM_CONSUMING_counter
    MYAPP_MEM_CONSUMING_counter = {}
    global MYAPP_LIFETIME
    MYAPP_LIFETIME = {}
    global MYAPP_ON_DEVICE_counter
    MYAPP_ON_DEVICE_counter = {}
    global DEVICE_ENERGY_CONSUMPTION_sum
    DEVICE_ENERGY_CONSUMPTION_sum = {}
    global MYAPP_DEVICE_START_counter
    MYAPP_DEVICE_START_counter = {}
    global MYAPP_ALERT_counter
    MYAPP_ALERT_counter = {}
    global iter_count
    iter_count = 0
    global MYAPP_ALERT_incrementing
    MYAPP_ALERT_incrementing = {}

myapp_ondevice_already_sampled = {}
def resources_requested(sourceAppName):
    localapp_details = db.getLocalApplicationBySourceName(sourceAppName)
    profile = localapp_details["descriptor"]["app"]["resources"]["profile"]
    if "custom" == profile:
        return (localapp_details["app"]["resources"]["cpu"], localapp_details["app"]["resources"]["memory"])
    elif "c1.tiny" == profile:
        return (100, 32)
    elif "c1.small" == profile:
        return (200, 64)
    elif "c1.medium" == profile:
        return (400, 128)
    elif "c1.large" == profile:
        return (600, 256)
    elif "c1.xlarge" == profile:
        return (1200, 512)
    return (200, 64)

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
            with itercount_lock:
                iter_count += 1
            with device_lock:
                device_sampled_values = {}
                for dev in db.getDevices():
                    deviceId = dev["deviceId"]
                    # Initializing Variable
                    if not deviceId in DEVICE_CRITICAL_CPU_counter_sum:
                        DEVICE_CRITICAL_CPU_counter_sum[deviceId] = 0              
                        DEVICE_CRITICAL_MEM_counter_sum[deviceId] = 0
                        DEVICE_CPU_USED_sum[deviceId] = 0
                        DEVICE_MEM_USED_sum[deviceId] = 0
                        NUMBER_OF_MYAPP_ON_DEVICE_counter_sum[deviceId] = 0
                        DEVICE_DOWN_counter_sum[deviceId] = 0
                        resources_sampled_count[deviceId] = 0
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
                        device_cpu_used = dev["usedCPU"] + dev["totalCPU"] - sampled_free_cpu
                        device_mem_used = dev["usedMEM"] + dev["totalMEM"] - sampled_free_mem
                        DEVICE_CPU_USED_sum[deviceId] += device_cpu_used if device_cpu_used <= dev["totalCPU"] else dev["totalCPU"] 
                        DEVICE_MEM_USED_sum[deviceId] += device_mem_used if device_mem_used <= dev["totalMEM"] else dev["totalMEM"]
                        
                        basal_cpu_usage = dev["totalCPU"] - sampled_free_cpu
                        basal_mem_usage = dev["totalMEM"] - sampled_free_mem
                        consumed_energy = (getEnergyConsumed(deviceId, device_cpu_used, device_mem_used) - 
                                            getEnergyConsumed(deviceId, basal_cpu_usage, basal_mem_usage))
                        DEVICE_ENERGY_CONSUMPTION_sum[deviceId] += consumed_energy
                        resources_sampled_count[deviceId] += 1
                        # adding number of installed apps
                        NUMBER_OF_MYAPP_ON_DEVICE_counter_sum[deviceId] += len(dev["installedApps"])            
                    else: 
                        DEVICE_DOWN_counter_sum[deviceId] += 1
                
            with myapp_lock:
                db.deleteFromSamplingAlerts() # Cleaning all alerts inserted in previous simulation iter
                myapp_jobs_up_counter = {}
                myapp_jobs_down_counter = {}
                for job in db.getJobs():
                    myappId = job["myappId"]
                    
                    if not myappId in MYAPP_ON_DEVICE_counter: # initialize all counters
                        MYAPP_ON_DEVICE_counter[myappId] = {}
                        MYAPP_CPU_CONSUMING_counter[myappId] = {}
                        MYAPP_MEM_CONSUMING_counter[myappId] = {}
                        MYAPP_DEVICE_START_counter[myappId] = {}
                        MYAPP_ALERT_counter[myappId] = {constants.APP_HEALTH: 0, constants.DEVICE_REACHABILITY: 0, 
                                                        constants.MYAPP_CPU_CONSUMING: 0, constants.MYAPP_MEM_CONSUMING: 0}
                        myapp_ondevice_already_sampled[myappId] = {}
                        MYAPP_ALERT_incrementing[myappId] = 0
                    MYAPP_ALERT_incrementing[myappId] += 1 # keeps trace of jobs in order to averaging the alerting counts

                    myapp_details = db.getMyApp(myappId)
                    localapp_resources = resources_requested(myapp_details["sourceAppName"])
                    max_cpu = localapp_resources[0]
                    max_mem = localapp_resources[1]

                    for device in job["payload"]["devices"]:
                        if not device["deviceId"] in MYAPP_ON_DEVICE_counter[myappId]: # Inizializer
                            MYAPP_ON_DEVICE_counter[myappId][device["deviceId"]] = 0
                            MYAPP_DEVICE_START_counter[myappId] [device["deviceId"]] = 0

                        profile_values = get_profile_values(job["profile"])
                        allocated_cpu = device["resourceAsk"]["resources"]["cpu"]
                        allocated_mem = device["resourceAsk"]["resources"]["memory"]
                        application_cpu_sampling = get_truncated_normal(mean=profile_values[0]*max_cpu, sd=profile_values[0]*max_cpu, low=0, upp=allocated_cpu+1).rvs()
                        application_mem_sampling = get_truncated_normal(mean=profile_values[0]*max_mem, sd=profile_values[0]*max_mem, low=0, upp=allocated_mem+1).rvs()
                        
                        device_details = db.getDevice(device["deviceId"])
                        if device_details == None: # the devices is removed without deleting the application
                            continue

                        if ((device["deviceId"] in myapp_ondevice_already_sampled[myappId] and myapp_ondevice_already_sampled[myappId][device["deviceId"]] < iter_count)
                            or (not device["deviceId"] in myapp_ondevice_already_sampled[myappId])):
                            MYAPP_ON_DEVICE_counter[myappId][device["deviceId"]] += 1
                            if job["status"] == "start": 
                                MYAPP_DEVICE_START_counter[myappId][device["deviceId"]] += 1
                            myapp_ondevice_already_sampled[myappId][device["deviceId"]] = iter_count

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
                            MYAPP_ALERT_counter[myappId][constants.DEVICE_REACHABILITY] += 1
                        else:
                            if not myappId in myapp_jobs_up_counter:
                                myapp_jobs_up_counter[myappId] = 1
                            else:
                                myapp_jobs_up_counter[myappId] += 1
                            sampled_free_cpu = device_sampled_values[device["deviceId"]]["free_cpu"]
                            sampled_free_mem = device_sampled_values[device["deviceId"]]["free_mem"]
                            if sampled_free_cpu <= 0:
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
                                MYAPP_ALERT_counter[myappId][constants.APP_HEALTH] += 1
                            if sampled_free_mem <= 0:
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
                                MYAPP_ALERT_counter[myappId][constants.APP_HEALTH] += 1
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
                                MYAPP_ALERT_counter[myappId][constants.MYAPP_CPU_CONSUMING] += 1
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
                                MYAPP_ALERT_counter[myappId][constants.MYAPP_MEM_CONSUMING] += 1

                for myapp in db.getMyApps():
                    myappId = myapp["myappId"]
                    if not myappId in MYAPP_LIFETIME: # Inizializer
                        MYAPP_LIFETIME[myappId] = 0
                        MYAPP_DOWN_counter[myappId] = 0
                        MYAPP_UP_counter[myappId] = 0

                    MYAPP_LIFETIME[myappId] += 1
                    if myapp["minjobs"] == 0: # 0 is assumed to be "all jobs have to be run"
                        if myappId in myapp_jobs_down_counter and myapp_jobs_down_counter[myappId] > 0: # If at least one job in donw
                            MYAPP_DOWN_counter[myappId] += 1
                        elif myappId in myapp_jobs_up_counter and myapp_jobs_up_counter[myappId] > 0:
                            MYAPP_UP_counter[myappId] += 1
                        else: # If there are no instaces running
                            MYAPP_DOWN_counter[myappId] += 1
                    else:
                        if myapp["minjobs"] <= myapp_jobs_up_counter[myappId]:
                            MYAPP_UP_counter[myappId] += 1
                        else:
                            MYAPP_DOWN_counter[myappId] += 1
                
            queue.execute_next_task() # Executes a task if present, otherwise returns immediately                   
                        
def getDeviceSampling():
    with device_lock:
        devices = db.getDevices()
        result = []
        fix_iter = float(iter_count)
        for deviceId in DEVICE_CRITICAL_CPU_counter_sum.keys():
            dev = db.getDevice(deviceId)
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
    with myapp_lock:
        myapps = db.getMyApps()
        result = []
        fix_iter = float(iter_count)
        for myapp in myapps:
            myappId = myapp["myappId"]
            tmp = {}
            tmp["myappId"] = myappId
            tmp["name"] = myapp["name"]
            if myappId in MYAPP_UP_counter:
                tmp["UP_PERCENTAGE"] = MYAPP_UP_counter[myappId] / float(MYAPP_LIFETIME[myappId])
            else:
                tmp["UP_PERCENTAGE"] = 0
            if myappId in MYAPP_DOWN_counter:
                tmp["DOWN_PERCENTAGE"] = MYAPP_DOWN_counter[myappId] / float(MYAPP_LIFETIME[myappId])
            else: 
                tmp["DOWN_PERCENTAGE"] = 0
            if myappId in MYAPP_ON_DEVICE_counter:
                tmp["ON_DEVICE_PERCENTAGE"] = {k: (v / float(MYAPP_LIFETIME[myappId])) 
                                                    for k,v in MYAPP_ON_DEVICE_counter[myappId].items()}
                tmp["ON_DEVICE_START_TIME"] = {k: (v/float(MYAPP_LIFETIME[myappId]))
                                                    for k,v in MYAPP_DEVICE_START_counter[myappId].items()}
            else:
                tmp["ON_DEVICE_PERCENTAGE"] = {}
            if myappId in MYAPP_ALERT_counter:
                tmp["ALERT_PERCENTAGE"] = {k: (v / float(MYAPP_ALERT_incrementing[myappId]))
                                                for k,v in MYAPP_ALERT_counter[myappId].items()}
            else:
                tmp["ALERT_PERCENTAGE"] = {}
            result.append(tmp)
    return result

def getSimulationCount():
    with itercount_lock:
        return iter_count
