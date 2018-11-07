import pymongo as pm
import time, json
from scipy.stats import truncnorm 
import SECRETS as config
import RealDatabase as rdb

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(   (low - mean) / sd, 
                        (upp - mean) / sd, 
                        loc=mean, scale=sd
                    )

def sampleCPU(devid, time=0):
    device = rdb.getDevice(deviceId = devid)
    mean = device["distribution"]["CPU"]["mean"]
    deviation = device["distribution"]["CPU"]["deviation"]
    maxCPU = device["totalCPU"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxCPU)

def sampleMEM(devid, time=0):
    device = rdb.getDevice(deviceId = devid)
    mean = device["distribution"]["MEM"]["mean"]
    deviation = device["distribution"]["MEM"]["deviation"]
    maxCPU = device["totalMEM"]
    return get_truncated_normal(mean=mean, sd=deviation, low=0, upp=maxCPU)