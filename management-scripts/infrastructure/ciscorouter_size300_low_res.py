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
    for i in range(0,300):
        r = random.random()
        r1 = random.random()
        deviceId = i+1
        dev = {
                    "ipAddress": "10.10.20."+str(deviceId),
                    "port": 8443,
                    "deviceId": str(deviceId),
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
                                "mean": 950,
                                "deviation": r*500
                            }
                        ],
                        "MEM": [
                            {
                                "timeStart": 0,
                                "timeEnd": 24,
                                "mean": 300,
                                "deviation": r1*200
                            }
                        ]
                    }
                }
        db.Rdevices.insert_one(dev)
        devices.append(dev)
    with open("infrastructure.txt", "wb") as file:
        file.write(cPickle.dump(devices, file))
