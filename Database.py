import pymongo as pm 
import time, json
import SECRETS as config
import RealDatabase as rdb
from bson.objectid import ObjectId
from bson.int64 import Int64

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

def getAvailableResources(devid):
    dev = db.devices.find_one({"deviceId": Int64(devid)})



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
    return db.applications.find_one({"_id": ObjectId(appid)})
    
def updateLocalApplication(appid, newValues):
    _id = appid if type(appid) == int else ObjectId(appid)
    db.applications.update_one(
        {"_id": _id},
        {"$set": newValues}
    )

def deleteLocalApplication(appid):
    db.applications.find_one_and_delete({"_id": ObjectId(appid)})

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
    return db.myapps.find_one_and_delete({"_id": ObjectId(appid)})

def myAppExists(sourceAppName):
    return db.myapps.count_documents({"sourceAppName": sourceAppName}) > 0

# Installed App
def getDeviceWithApplication(appid):
    return []