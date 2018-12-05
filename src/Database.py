import pymongo as pm 
import time, json, sys
import SECRETS as config
import RealDatabase as rdb
from bson.objectid import ObjectId
from bson.int64 import Int64
import modules.ResourceSampling as sampling
import threading
from  modules.Exceptions import NoResourceError, MyAppInstalledOnDeviceError

client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                   config.db_password, 
                                                   config.db_host, 
                                                   config.db_port))
client.drop_database("fogdirector")
db = client.fogdirector
db.devices.create_index([('$**', pm.TEXT)], name='TextIndex', default_language='english')

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
    devSpecs["tags"] = []
    db.devices.insert_one(devSpecs)
    return devSpecs
def deviceExists(ipAddress, port):
    return db.devices.count_documents({"ipAddress": ipAddress, "port": port}) > 0
def getDevice(devid):
    return db.devices.find_one({"deviceId": Int64(devid)})
def deleteDevice(devid):
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
        devs = db.devices.find({"$where": func }).skip(offset).limit(limit)
        return devs
    return db.devices.find().skip(offset).limit(limit)

lock = threading.Lock()
def checkAndAllocateResource(devid, cpu, mem):
    sampledCPU = sampling.sampleCPU(devid)
    sampledMEM = sampling.sampleMEM(devid)
    with lock: # Syncronized version of python
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
        device = getDevice(devid)
        db.devices.find_one_and_update(
            {"deviceId": devid},
            { "$inc": {"usedCPU": -cpu, "usedMEM": -mem} }
        )     
def addMyAppToDevice(myappid, devid):
    r = db.devices.find_one_and_update({
        "deviceId": Int64(devid)
    }, {
        "$addToSet": {"installedApps": myappid}
    })
def removeMyAppsFromDevice(myappid, devid):
    db.devices.find_one_and_update({
        "deviceId": devid
    }, {
        "$pull": {"installedApps": myappid}
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
    return db.applications.insert_one(appdata).inserted_id
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
def createMyApp(appname, sourceAppName, version, apptype):
    with myapp_lock:
        myappappid = db.myapps.insert_one({
            "name": appname,
            "sourceAppName": sourceAppName,
            "version": version,
            "type": apptype
        }).inserted_id
        return db.myapps.find_one_and_update({"_id": myappappid}, 
                                                {"$set": {
                                                    "myappId": str(myappappid)
                                                }
                                            }, return_document=pm.ReturnDocument.AFTER)
def deleteMyApp(appid):
    with myapp_lock:
        if db.devices.count_documents({"installedApps": appid}) > 0:
            raise MyAppInstalledOnDeviceError("Myapps is installed on some device")
        return db.myapps.find_one_and_delete({"_id": ObjectId(appid)})
def myAppExists(sourceAppName):
    with myapp_lock:
        return db.myapps.count_documents({"sourceAppName": sourceAppName}) > 0
def getMyApp(myappid):
    with myapp_lock:
        return db.myapps.find_one({"myappId": myappid})
def getMyApps(searchByName=None):
    with myapp_lock:
        if searchByName != None:
            return db.myapps.find({"name": searchByName})
        return db.myapps.find()
    
# Jobs App
def addJobs(myappid, devices, status="DEPLOY", payload={}):
    return db.jobs.insert_one({
        "myappId": myappid,
        "status": status,
        "devices": devices,
        "payload": payload
    }).inserted_id
def updateJobsStatus(myappid, status):
    return db.jobs.update_many({
        "myappId": myappid
    }, {"$set": {"status": status} } ) 

def getJobs(myappid = None):
    if myappid == None:
        return db.jobs.find()
    return db.jobs.find({"myappId": str(myappid)})
    

# Logs
def addMyAppLog(log):
    db.myappsLogs.insert_one(log)
def getMyAppsLog():
    return db.myappsLogs.find()

# Alerts
def addAlert(alert, from_sampling=False):
    db.alerts.insert_one({"alert": alert, "from_sampling": from_sampling})
def deleteFromSamplingAlerts():
    db.alerts.delete_many({"from_sampling": True})
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