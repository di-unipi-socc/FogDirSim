import pymongo as pm 
import time, json, random
import infrastructure.SECRETS as config
import _pickle as cPickle

def create():
    devices = []
    client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                    config.db_password, 
                                                    config.db_host, 
                                                    config.db_port))
    client.drop_database("realDatabase")
    db = client.realDatabase
    if False:
        for i in range(0,5):
            deviceId = i+1
            dev = {
                        "ipAddress": "10.10.20."+str(deviceId),
                        "port": 8443,
                        "deviceId": deviceId,
                        "totalCPU": 2500,
                        "totalVCPU": 2,
                        "maxVCPUPerApp": 2,
                        "totalMEM": 1024,
                        "chaos_down_prob": 0,
                        "chaos_revive_prob": 1,
                        "distributions": { 
                            "CPU": [
                                {
                                    "timeStart": 0,
                                    "timeEnd": 24,
                                    "mean": 1700,
                                    "deviation": 500
                                }
                            ],
                            "MEM": [
                                {
                                    "timeStart": 0,
                                    "timeEnd": 24,
                                    "mean": 850,
                                    "deviation": 450
                                }
                            ]
                        }
                    }
            db.Rdevices.insert_one(dev)
            devices.append(dev)
    
    for i in range(0,5):
        deviceId = i+1
        dev = {
                    "ipAddress": "10.10.20."+str(deviceId),
                    "port": 8443,
                    "deviceId": deviceId,
                    "totalCPU": 1500,
                    "totalVCPU": 2,
                    "maxVCPUPerApp": 2,
                    "totalMEM": 1024,
                    "chaos_down_prob": 0,
                    "chaos_revive_prob": 1,
                    "distributions": { 
                        "CPU": [
                            {
                                "timeStart": 0,
                                "timeEnd": 24,
                                "mean": 1000,
                                "deviation": 400
                            }
                        ],
                        "MEM": [
                            {
                                "timeStart": 0,
                                "timeEnd": 24,
                                "mean": 750,
                                "deviation": 450
                            }
                        ]
                    }
                }
        db.Rdevices.insert_one(dev)
        devices.append(dev)
    for i in range(0,5):
        deviceId = i+6
        dev = {
                    "ipAddress": "10.10.20."+str(deviceId),
                    "port": 8443,
                    "deviceId": deviceId,
                    "totalCPU": 1200,
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
                                "mean": 800,
                                "deviation": 400
                            }
                        ],
                        "MEM": [
                            {
                                "timeStart": 0,
                                "timeEnd": 24,
                                "mean": 300,
                                "deviation": 200
                            }
                        ]
                    }
                }
        db.Rdevices.insert_one(dev)
        devices.append(dev)

    with open("infrastructure.txt", "wb") as file:
        file.write((cPickle.dumps(devices)))

