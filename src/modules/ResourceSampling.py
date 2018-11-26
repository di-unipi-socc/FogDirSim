import pymongo as pm
import time, json
from scipy.stats import truncnorm 
import SECRETS as config
import Database as db

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(   (low - mean) / sd, 
                        (upp - mean) / sd, 
                        loc=mean, scale=sd
                    )

def sampleCPU(devid, time=0):
    """
        Sampling considering only the distribution variables
    """
    device = db.getDevice(devid)
    mean = device["distributions"]["CPU"][time]["mean"]
    deviation = device["distributions"]["CPU"][time]["deviation"]
    maxCPU = device["totalCPU"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxCPU).rvs()

def sampleMEM(devid, time=0):
    """
        Sampling considering only the distribution variables
    """
    device = db.getDevice(devid)
    mean = device["distributions"]["MEM"][time]["mean"]
    deviation = device["distributions"]["MEM"][time]["deviation"]
    maxMEM = device["totalMEM"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxMEM).rvs()

def sampleBusyCPU(devid, time=0):
    """
        Sampling considering the distribution and the used cpu by myapps
    """
    sampled = sampleCPU(devid, time)
    dev = db.getDevice(devid)
    return sampled - dev["usedCPU"] 

def sampleBusyMEM(devid, time=0):
    """
        Sampling considering the distribution and the used mem by myapps
    """
    sampled = sampleMEM(devid, time)
    dev = db.getDevice(devid)
    return sampled - dev["usedMEM"] 

def sampleMyAppStatus(devid, requestedCPU, requestedMEM, time=0):
    dev = db.getDevice(devid)
    sampledBusyCPU = sampleBusyCPU(devid, time)
    sampledBusyMEM = sampleBusyMEM(devid, time)
    # Computing the freeCPU as total-(sampled - myapp_itself) since myapp cpu is included in the "usedCPU from sampleFreeCPU"
    freeCPU = dev["totalCPU"] - (sampledBusyCPU - requestedCPU)
    freeMEM = dev["totalMEM"] - (sampledBusyMEM - requestedMEM)
    return {"hasCPU": freeCPU > requestedCPU, 
            "hasMEM": freeMEM > requestedMEM}