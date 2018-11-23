"""
    RealDatabase describes the infrastructure analyzed and passed to the simulator.
    It is not the database modified by the simulator
"""

import pymongo as pm 
import time, json
import SECRETS as config
from bson.objectid import ObjectId
import Database

client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                   config.db_password, 
                                                   config.db_host, 
                                                   config.db_port))
client.drop_database("realDatabase")
db = client.realDatabase
# Building RealDatabase
db.Rdevices.insert_one({
            "ipAddress": "10.10.20.51",
            "port": 8443,
            "totalCPU": 1000,
            "totalMEM": 128,
            "distributions": { 
                "CPU": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 2.4,
                        "deviation": 3 
                    }
                ],
                "MEM": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 45,
                        "deviation": 2
                    }
                ]
            }
        })
db.Rdevices.insert_one({
            "ipAddress": "10.10.20.52",
            "port": 8443,
            "totalCPU": 1000,
            "totalMEM": 128,
            "distributions": { 
                "CPU": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 2.4,
                        "deviation": 3 
                    }
                ],
                "MEM": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 45,
                        "deviation": 2
                    }
                ]
            }
        })


def getDevice(ip = None, port = None, deviceId = None):
    if ip == None and port == None and deviceId == None:
        return None
    if ip != None and port != None:
        return  db.Rdevices.find_one({"ipAddress": ip, "port": port})
    if deviceId != None:
        return Database.getDevice(deviceId)

    
