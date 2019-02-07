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

    # Building RealDatabase
    db.Rdevices.insert_one({
    "ipAddress": "10.10.20.51",
    "port": 8443,
    "deviceId": 1,
    "totalCPU": 200,
    "totalMEM": 64,
    "totalVCPU": 2,
    "maxVCPUPerApp": 2,
    "chaos_down_prob": 0.0,
    "chaos_revive_prob": 0.0,
    "distributions": { 
        "CPU": [
        {
            "mean": 180,
            "deviation": 40
        }
        ],
        "MEM": [
        {
            "mean": 56,
            "deviation": 17
        }
        ]
    }
    })
    db.Rdevices.insert_one({
    "ipAddress": "10.10.20.52",
    "port": 8443,
    "deviceId": 2,
    "totalCPU": 200,
    "totalMEM": 128,
    "totalVCPU": 2,
    "maxVCPUPerApp": 2,
    "chaos_down_prob": 0.0,
    "chaos_revive_prob": 0.0,
    "distributions": { 
        "CPU": [
        {
            "mean": 190,
            "deviation": 30
        }
        ],
        "MEM": [
        {
            "mean": 106,
            "deviation": 32
        }
        ]
    }
    })     
    db.Rdevices.insert_one({
    "ipAddress": "10.10.20.53",
    "port": 8443,
    "deviceId": 3,
    "totalCPU": 400,
    "totalMEM": 128,
    "totalVCPU": 2,
    "maxVCPUPerApp": 2,
    "chaos_down_prob": 0.0,
    "chaos_revive_prob": 0.0,
    "distributions": { 
        "CPU": [
        {
            "mean": 330,
            "deviation": 80
        }
        ],
        "MEM": [
        {
            "mean": 118,
            "deviation": 21
        }
        ]
    }
    })