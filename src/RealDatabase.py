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

"""

# Devices based on Cisco® 890 Series Integrated Services Routers (ISRs) 
for i in range(0,300):
    deviceId = i+1
    db.Rdevices.insert_one({
                "ipAddress": "10.10.20."+str(deviceId),
                "port": 8443,
                "deviceId": deviceId,
                "totalCPU": 1700,
                "totalVCPU": 2,
                "maxVCPUPerApp": 2,
                "totalMEM": 512,
                "chaos_down_prob": 0,
                "chaos_revive_prob": 1,
                "distributions": { 
                    "CPU": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 1500,
                            "deviation": 78
                        }
                    ],
                    "MEM": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 300,
                            "deviation": 10
                        }
                    ]
                }
            })
"""
def getDevice(ip = None, port = None, deviceId = None):
    if ip == None and port == None and deviceId == None:
        return None
    if ip != None and port != None:
        return  db.Rdevices.find_one({"ipAddress": ip, "port": port})
    if deviceId != None:
        return Database.getDevice(deviceId)

    
