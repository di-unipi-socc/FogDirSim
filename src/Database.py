import pymongo as pm 
import time, json
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
        devSpecs["deviceId"] = hash(devSpecs["ipAddress"]+":"+str(devSpecs["port"]))
    devSpecs["username"] = user
    devSpecs["password"] = pasw
    devSpecs["usedCPU"] = 0 # these two variables are computed only with apps installed by the simulator
    devSpecs["usedMEM"] = 0 
    devSpecs["installedApps"] = []
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
        return db.devices.find({"tags": searchByTag}).skip(offset).limit(limit)
    if searchByAnyMatch != None:
        return db.devices.find({ "$text": { "$search": searchByAnyMatch } })
    return db.devices.find().skip(offset).limit(limit)

lock = threading.Lock()
def checkAndAllocateResource(devid, cpu, mem):
    sampledCPU = sampling.sampleCPU(devid)
    sampledMEM = sampling.sampleMEM(devid)
    with lock: # Syncronized version of python
        device = getDevice(devid)
        availableCPU = device["totalCPU"] - device["usedCPU"] - sampledCPU
        availableMEM = device["totalMEM"] - device["usedMEM"] - sampledMEM
        if cpu > availableCPU or mem > availableMEM:
            raise NoResourceError("CPU (available/requested): %d/%d, MEM: %d/%d" % (availableCPU, cpu, availableMEM, mem))
        db.devices.find_one_and_update(
            {"deviceId": devid},
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
    db.devices.find_one_and_update({
        "deviceId": devid
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
        {"_id": deviceid},
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
        "_id": appid,
        "version": sourceAppName.split(":")[1]
    })

# My apps
def createMyApp(appname, sourceAppName, version, apptype):
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
    if db.devices.count_documents({"installedApps": appid}) > 0:
        raise MyAppInstalledOnDeviceError("Myapps is installed on some device")
    return db.myapps.find_one_and_delete({"_id": ObjectId(appid)})

def myAppExists(sourceAppName):
    return db.myapps.count_documents({"sourceAppName": sourceAppName}) > 0

def getMyApp(myappid):
    return db.myapps.find_one({"myappId": myappid})
    
# Jobs App
def addJobs(myappid, devices, status="DEPLOY", payload={}):
    return db.jobs.insert_one({
        "myappid": myappid,
        "status": status,
        "devices": devices,
        "payload": payload
    }).inserted_id

def updateJobsStatus(myappid, status):
    return db.jobs.find_and_modify({
        "myappid": myappid
    }, {"$set": {"status": status} } ) 

def getJob(myappid):
    return db.jobs.find_one({"myappdid": myappid})

# Logs
def addMyAppLog(log):
    db.myappsLogs.insert_one(log)
def getMyAppsLog():
    return db.myappsLogs.find()