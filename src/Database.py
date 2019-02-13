import pymongo as pm 
import time, json, sys
import SECRETS as config
import RealDatabase as rdb
from bson.objectid import ObjectId
from bson.int64 import Int64
import Simulator.ResourceSampling as sampling
import threading
import constants
from  misc.Exceptions import NoResourceError, MyAppInstalledOnDeviceError

client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                   config.db_password, 
                                                   config.db_host, 
                                                   config.db_port))
db = None
def resetSimulation():
    global db
    client.drop_database("fogdirector")
    db = client.fogdirector 
   # db.devices.create_index([('deviceId', pm.ASCENDING)], name='device_index', default_language='english')
   # db.myapps.create_index([('myappId', pm.TEXT)], name='myapps_index', default_language='english')
   # db.applications.create_index([('localappId', pm.TEXT)], name='localapp_index', default_language='english')
 
resetSimulation()

# Authentication
def addToken(expiryTime, token, user):
    db.tokens.insert_one({
        "expiryTime": expiryTime,
        "token": token,
        "user": user,
        "creationTime": int(time.time())
    })
    db.tokens.delete_many({
        "expiryTime": {"$lt": int(time.time())}
    })
def checkToken(token):
    return True
    count = db.tokens.count_documents({
        "token": token,
        "expiryTime": {"$gt": int(time.time())}
    })
    return count > 0
def deleteToken(token):
    db.tokens.delete_many({
        "token": token
    })

# Devices
def addDevice(ipAddress, port, user, pasw):
    devSpecs = rdb.getDevice(ipAddress, port)
    if devSpecs == None:
        raise LookupError("The device you are adding is not present in the RealDatabase")
    if "deviceId" not in devSpecs.keys():
        devSpecs["deviceId"] = abs(hash(devSpecs["ipAddress"]+":"+str(devSpecs["port"])))
    devSpecs["username"] = user
    devSpecs["password"] = pasw
    devSpecs["usedCPU"] = 0 # these two variables are computed only with apps installed by the simulator
    devSpecs["usedMEM"] = 0 
    devSpecs["installedApps"] = []
    devSpecs["alive"] = True
    devSpecs["tags"] = []
    db.devices.insert_one(devSpecs)
    return devSpecs
def setDeviceDown(deviceId):
    db.devices.update_one({"deviceId": int(deviceId)}, {"$set": {"alive": False}})
def setDeviceAlive(deviceId):
    db.devices.update_one({"deviceId": int(deviceId)}, {"$set": {"alive": True}})
def deviceIsAlive(deviceId):
    return db.devices.count_documents({"deviceId": int(deviceId), "alive": True}) > 0
def deviceExists(ipAddress, port):
    return db.devices.count_documents({"ipAddress": ipAddress, "port": port}) > 0
def getDevice(devid):
    return db.devices.find_one({"deviceId": Int64(devid)})
def deleteDevice(devid):
    installedApps = db.devices.find_one({"deviceId": Int64(devid)})["installedApps"]
    for app in installedApps:
        uninstallJob(app["appid"], devid)
    db.devices.find_one_and_delete({"deviceId": Int64(devid)})

def getDevices(limit=100, offset=0, searchByTag=None, searchByAnyMatch=None):
    if searchByTag != None:
        tag = db.tags.find_one({"name": searchByTag})
        try:
            return db.devices.find({"tags": str(tag["_id"])}).skip(offset).limit(limit)
        except KeyError:
            return []
    if searchByAnyMatch != None:
        func = """function() {
                    var deepIterate = function  (obj, value) {
                        for (var field in obj) {
                            if (obj[field] == value){
                                return true;
                            }
                            var found = false;
                            if ( typeof obj[field] === 'object') {
                                found = deepIterate(obj[field], value)
                                if (found) { return true; }
                            }
                        }
                        return false;
                    };
                    return deepIterate(this, "%s")}""" % str(searchByAnyMatch)
        devs = db.devices.find({"$where": func }, no_cursor_timeout=True).skip(offset).limit(limit)
        return devs
    return db.devices.find(no_cursor_timeout=True).skip(offset).limit(limit)

lock = threading.Lock()
def checkAndAllocateResource(devid, cpu, mem):
    sampledCPU = constants.current_infrastructure[devid][0]
    sampledMEM = constants.current_infrastructure[devid][1]
    with lock: 
        device = getDevice(devid)
        availableCPU = sampledCPU - device["usedCPU"]
        availableMEM = sampledMEM - device["usedMEM"]
        if cpu > availableCPU or mem > availableMEM:
            raise NoResourceError("CPU (available/requested): %d/%d, MEM: %d/%d" % (int(availableCPU), cpu, int(availableMEM), mem))
        db.devices.find_one_and_update(
            {"deviceId": Int64(devid)},
            { "$inc": {"usedCPU": cpu, "usedMEM": mem} }
        )
def deallocateResource(devid, cpu, mem):
    with lock:
        db.devices.find_one_and_update(
            {"deviceId": Int64(devid)},
            { "$inc": {"usedCPU": -cpu, "usedMEM": -mem} }
        )     
def addMyAppToDevice(myappid, devid, profile):
    db.devices.find_one_and_update({
        "deviceId": Int64(devid)
    }, {
        "$addToSet": {"installedApps": {"appid": myappid, "profile": profile}}
    })
def removeMyAppsFromDevice(myappid, devid):
    db.devices.find_one_and_update({
        "deviceId": devid
    }, {
        "$pull": {"installedApps": {"appid": myappid}}
    })

# Tags
def addTag(tagname, tagdescription):
    tagid = db.tags.insert_one({
        "name": tagname,
        "description": tagdescription
    }).inserted_id
    return tagid
def tagExists(tagname):
    return db.tags.count_documents({"name": tagname}) > 0
def getTags():
    return db.tags.find()
def getTag(tagid):
    return db.tags.find_one({"_id":  ObjectId(tagid)})
def tagDevice(deviceid, tag):
    db.devices.update_one(
        {"deviceId": deviceid},
        {"$addToSet": {"tags": tag}}
    )

# Local Application
def addLocalApplication(appdata):
    appId = db.applications.insert_one(appdata).inserted_id
    db.applications.find_one_and_update({"_id": appId}, 
                                        {"$set": {
                                            "sourceAppName": str(appId)+":1",
                                            "localAppId": str(appId)
                                        }
                                    }, return_document=pm.ReturnDocument.AFTER)
    return appId

def localApplicationExists(appid, version=1):
    return db.applications.count_documents({"localAppId": appid, "version": version}) > 0
def getLocalApplications():
    return db.applications.find()
def getLocalApplication(appid):
    appid = appid if type(appid) == int else ObjectId(appid)
    return db.applications.find_one({"_id": appid})
def updateLocalApplication(appid, newValues):
    _id = appid if type(appid) == int else ObjectId(appid)
    db.applications.update_one(
        {"_id": _id},
        {"$set": newValues}
    )
def deleteLocalApplication(appid):
    db.applications.find_one_and_delete({"_id": ObjectId(appid)})
def getLocalApplicationBySourceName(sourceAppName):
    appid = sourceAppName.split(":")[0]
    appid = appid if type(appid) == int else ObjectId(appid)
    return db.applications.find_one({
        "_id": appid#,
        #"version": sourceAppName.split(":")[1]
    })

# My apps
myapp_lock = threading.Lock()
def createMyApp(appname, sourceAppName, version, apptype, minjobs=0):
    with myapp_lock:
        myappappid = db.myapps.insert_one({
            "name": appname,
            "sourceAppName": sourceAppName,
            "version": version,
            "type": apptype,
            "minjobs": minjobs
        }).inserted_id
        return db.myapps.find_one_and_update({"_id": myappappid}, 
                                                {"$set": {
                                                    "myappId": str(myappappid)
                                                }
                                            }, return_document=pm.ReturnDocument.AFTER)
def deleteMyApp(appid):
    with myapp_lock:
        if db.devices.count_documents({"installedApps.appid": appid}) > 0:
            raise MyAppInstalledOnDeviceError("Myapps is installed on some device")
        return db.myapps.find_one_and_delete({"_id": ObjectId(appid)})
def myAppExists(name):
    with myapp_lock:
        return db.myapps.count_documents({"name": name}) > 0
def getMyApp(myappid):
    with myapp_lock:
        return db.myapps.find_one({"myappId": myappid})
def getMyApps(searchByName=None):
    with myapp_lock:
        if searchByName != None:
            return db.myapps.find({"name": searchByName}, no_cursor_timeout=True)
        return db.myapps.find(no_cursor_timeout=True)
    
# Jobs App
def addJobs(myappid, devices, profile=constants.MYAPP_PROFILE_NORMAL, status="DEPLOY",payload={}):
    return db.jobs.insert_one({
        "myappId": myappid,
        "status": status,
        "devices": devices,
        "payload": payload,
        "profile": profile
    }).inserted_id
def updateJobsStatus(myappid, status):
    db.jobs.update_many({
        "myappId": myappid
    }, {"$set": {"status": status} } )
    return myappid

def uninstallJob(myappId, deviceId):
    db.jobs.update({
        "myappId": myappId,
    }, { "$pull": { 'devices': { "deviceId": deviceId } } })
    db.jobs.remove({ "devices": { "$exists": True, "$size": 0 } })

def getJobs(myappid = None):
    if myappid == None:
        return db.jobs.find(no_cursor_timeout=True)
    return db.jobs.find({"myappId": str(myappid)}, no_cursor_timeout=True)
    

# Logs
def addMyAppLog(log):
    db.myappsLogs.insert_one(log)
def getMyAppsLog():
    return db.myappsLogs.find()

# Alerts
def addAlert(alert):
    db.alerts.insert_one({"alert": alert})
def deleteAlerts():
    db.alerts.drop()
def getAlerts():
    return db.alerts.aggregate([
        {
            "$replaceRoot": { "newRoot": "$alert" }
        }
    ])

#Simulation
def addSimulationValues(values):
    db.simulation.insert_one(values)
def getSimulationValues(_filter):
    return db.simulation.find(_filter)

