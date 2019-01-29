import pymongo as pm 
import time, json
import infrastructure.SECRETS as config

def create():
    client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                    config.db_password, 
                                                    config.db_host, 
                                                    config.db_port))
    client.drop_database("realDatabase")
    db = client.realDatabase

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
                                "mean": 400,
                                "deviation": 78
                            }
                        ],
                        "MEM": [
                            {
                                "timeStart": 0,
                                "timeEnd": 24,
                                "mean": 150,
                                "deviation": 100
                            }
                        ]
                    }
                })