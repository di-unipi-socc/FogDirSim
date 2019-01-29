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

    db.Rdevices.insert_one({
            "ipAddress": "10.10.20.51",
            "port": 8443,
            "deviceId": 1,
            "totalCPU": 2000,
            "totalMEM": 128,
            "totalVCPU": 2,
            "maxVCPUPerApp": 2,
            "chaos_down_prob": 0.01,
            "chaos_revive_prob": 0.2,
            "distributions": { 
                "CPU": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 2000,
                        "deviation": 39
                    }
                ],
                "MEM": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 120,
                        "deviation": 16
                    }
                ]
            }
        })
    db.Rdevices.insert_one({
                "ipAddress": "10.10.20.52",
                "port": 8443,
                "deviceId": 2,
                "totalCPU": 1000,
                "totalVCPU": 2,
                "maxVCPUPerApp": 2,
                "totalMEM": 128,
                "chaos_down_prob": 0.4,
                "chaos_revive_prob": 0.2,
                "distributions": { 
                    "CPU": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 189,
                            "deviation": 30
                        }
                    ],
                    "MEM": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 105,
                            "deviation": 32
                        }
                    ]
                }
            })     
    db.Rdevices.insert_one({
                "ipAddress": "10.10.20.53",
                "port": 8443,
                "deviceId": 3,
                "totalCPU": 1000,
                "totalVCPU": 2,
                "maxVCPUPerApp": 2,
                "totalMEM": 128,
                "chaos_down_prob": 0.01,
                "chaos_revive_prob": 0.2,
                "distributions": { 
                    "CPU": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 330,
                            "deviation": 78
                        }
                    ],
                    "MEM": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 118,
                            "deviation": 20
                        }
                    ]
                }
            })
