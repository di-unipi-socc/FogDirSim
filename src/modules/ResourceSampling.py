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
    device = db.getDevice(devid)
    mean = device["distributions"]["CPU"][time]["mean"]
    deviation = device["distributions"]["CPU"][time]["deviation"]
    maxCPU = device["totalCPU"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxCPU).rvs()

def sampleMEM(devid, time=0):
    device = db.getDevice(devid)
    print device
    mean = device["distributions"]["MEM"][time]["mean"]
    deviation = device["distributions"]["MEM"][time]["deviation"]
    maxCPU = device["totalMEM"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxCPU).rvs()