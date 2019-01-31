from API_executor.Authentication import invalidToken
import time, json
import Database as db
from Simulator.ResourceSampling import sampleCPU, sampleMEM

def computeDeviceId(ip, port):
    return str(abs(hash(ip + str(port))))

def formatDeviceOutput(device):
    res = {}
    res["port"] = device["port"]
    res["contactDetails"] = ""
    res["username"] = device["username"]
    res["ipAddress"] = device["ipAddress"]
    res["ne_id"] = device["ipAddress"] + ":" + str(device["port"])
    res["deviceId"] = device["deviceId"]
    res["serialNumber"] = device["deviceId"]
    res["hostname"] = res["ne_id"]
    res["platformVersion"] = "1.7.0.7"
    res["status"] = "DISCOVERED"
    res["tags"] = device["tags"]
    res["apps"] = device["installedApps"] # TODO: compare with FogDirector output
    capabilities = {}
    capabilities["managementAPIVersion"] = "2.0"
    capabilities["supportedApps"] = [
        "DOCKER",
        "PAAS",
        "LXC"
    ]
    capabilities["nodes"] = [] # TODO: Why this is an array? A device can use several nodes?
    capabilities["nodes"].append({
        "name": "x86_64",
        "cartridges": [],
        "cpu": {
            "available": sampleCPU(device["deviceId"])-device["usedCPU"],
            "total": device["totalCPU"]
        },
        "memory": {
            "available": sampleMEM(device["deviceId"]) - device["usedMEM"],
            "total": device["totalMEM"]
        },
        "disk": {
            "available": "NOT IMPLEMENTED YET",
            "total": "NOT IMPLEMENTED YET"
        },
        "totalVCPU": device["totalVCPU"], 
        "maxVCPUPerApp": device["maxVCPUPerApp"]
    })
    res["capabilities"] = capabilities
    res["supportedProfiles"] = [{
            "default": {
                "cpuShare": 200,
                "memoryShare": 64,
                "vCPU": 1
            },
            "c1.tiny": {
                "cpuShare": 100,
                "memoryShare": 32,
                "vCPU": 1
            },
            "c1.xlarge": {
                "cpuShare": 1200,
                "memoryShare": 256,
                "vCPU": 1
            },
            "c1.medium": {
                "cpuShare": 400,
                "memoryShare": 128,
                "vCPU": 1
            },
            "c1.small": {
                "cpuShare": 200,
                "memoryShare": 64,
                "vCPU": 1
            },
            "c1.large": {
                "cpuShare": 600,
                "memoryShare": 256,
                "vCPU": 1
            }
        }]
    res["networks"] = "NOT IMPLEMENTED YET"
    return res

def post(args, data):
    if db.checkToken(args["x-token-id"]):
        if data == None or\
            data["ipAddress"] == None or\
            data["port"] == None or\
            data["username"] == None or\
            data["password"] == None:
            return {"description": "ipAddress, port, username or password not defined"}, 401, {"ContentType": "application/json"}

        if db.deviceExists(data["ipAddress"], data["port"]):
            return {
                "code": 1101,
                "description": "A device with IP address, %s, already exists in the inventory." % data["ipAddress"]
            }, 409, {"ContentType": "application/json"}

        try:
            devSpecs = db.addDevice(data["ipAddress"], data["port"], data["username"], data["password"])
        except LookupError:
            return {"error": "LookupError: The device you are adding is not present in the RealDatabase"}, 400, {'ContentType':'application/json'}
        del devSpecs["_id"]
        return formatDeviceOutput(devSpecs), 201, {'ContentType':'application/json'}
    else:
        return invalidToken()

def delete(deviceid, args):
    if db.checkToken(args["x-token-id"]):
        dev = db.getDevice(deviceid)
        db.deleteDevice(deviceid)
        del dev["_id"]
        return dev, 200, {"Content-Type": "application/json"}
    else:
        return invalidToken()

def get(args):
    if db.checkToken(args["x-token-id"]):
        data = {"data": []}
        devices = db.getDevices(args["limit"] if args["limit"] != None else 1000, 
                                args["offset"] if args["offset"] != None else 0,
                                args["searchByTags"],
                                args["searchByAnyMatch"])
        
        for device in devices:
            del device["password"] # removing password from the returned HTTP API object
            del device["_id"]
            # formatting tags as API expects
            tags = []
            for tagid in device["tags"]:
                tag = db.getTag(tagid)
                tag["tagId"] = str(tag["_id"])
                del tag["_id"]
                if tag["description"] == "":
                    del tag["description"]
                tags.append(tag)
            device["tags"] = tags
            data["data"].append(formatDeviceOutput(device))
        return data, 200, {'ContentType':'application/json'} 
    else:
        return invalidToken()
        