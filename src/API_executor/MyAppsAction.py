from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, traceback
from API_executor.Authentication import invalidToken
from misc.Exceptions import NoResourceError
from misc import constants
import Database as db

class MyAppsAction(Resource):
    
    def post(self, args, data, myappId):
        if db.checkToken(args["x-token-id"]):
            data = request.json
            try:
                action = data.keys()[0]
                myapp = db.getMyApp(myappId)
                if action == "deploy":
                    data = data[action]
                    devices = data["devices"]  
                    app = db.getLocalApplicationBySourceName(myapp["sourceAppName"])
                    if not app["published"]: # This is not checked in FogDirector, but in unpublished app it crash
                        return {"error": "the app have to be published"}, 400, {"content-type": "application/json"}
                    deviceSuccessful = []
                    if False: #TODO: if myapp name already exists
                        return {
                            "code": 1304,
                            "description": "An app with name com.cisco.eng.ccm.model.app.App@95815c9e already exists." # Cisco does not return the name but the identifier
                        }, 409, {"content-type": "application/json"} 
                    for device in devices:
                        devid = device["deviceId"]
                        resourceAsked = device["resourceAsk"]["resources"]
                        if args["profile"] in [constants.MYAPP_PROFILE_LOW, constants.MYAPP_PROFILE_NORMAL, constants.MYAPP_PROFILE_HIGH]:
                            profile = args["profile"]
                        else:
                            profile = constants.MYAPP_PROFILE_NORMAL
                        try:
                            db.checkAndAllocateResource(devid, resourceAsked["cpu"], resourceAsked["memory"])
                            db.addMyAppToDevice(myappId, devid, profile)
                            db.addMyAppLog({
                                "time": int(time.time()),
                                "action": action,
                                "deviceSerialNo": devid,
                                "appName": myapp["name"],
                                "appVersion": "1",
                                "severity": "info",
                                "profile": profile,
                                "user": "admin",
                                "message": action+" operation succeeded"
                            })
                            deviceSuccessful.append(device)
                        except NoResourceError as e:
                            db.addMyAppLog({
                                "time": int(time.time()),
                                "action": action,
                                "deviceSerialNo": devid,
                                "appName": myapp["name"],
                                "appVersion": "1",
                                "severity": "info",
                                "user": "admin",
                                "message": action+" operation failed, no sufficient resources"
                            })
                            return {
                                "code": 1000,
                                "description": str(e)
                            }, 400, {"content-type": "application/json"}
                            
                    jobid = db.addJobs(myappId, deviceSuccessful, profile=profile, payload=request.json)
                    
                elif action == "start" or action == "stop": # TODO: add response for this request
                    db.addMyAppLog({
                        "time": int(time.time()),
                        "action": action,
                        "appName": myapp["name"],
                        "appVersion": "1",
                        "severity": "info",
                        "user": "admin",
                        "message": action+" operation succeeded"
                    })
                    jobid = db.updateJobsStatus(myappId, action)
                    
                elif action == "undeploy": # TODO: add correct response for this request
                    data = data[action]
                    devices_payload = data["devices"]
                    myapp = db.getMyApp(myappId) # Taken for Name only
                    jobs = db.getJobs(myappId)
                    for job in jobs:
                        jobDescr = job["payload"]
                        resourcesDevs = jobDescr["deploy"]["devices"]
                        for device in resourcesDevs:
                            if device["deviceId"] in devices_payload:
                                cpu = 0
                                mem = 0
                                for dev in resourcesDevs: # Searching for my device
                                    resourceAsked = dev["resourceAsk"]["resources"]
                                    if dev["deviceId"] in devices_payload:
                                        cpu = dev["resourceAsk"]["resources"]["cpu"]
                                        mem = dev["resourceAsk"]["resources"]["memory"]
                                        db.deallocateResource(dev["deviceId"],cpu, mem)
                                        db.removeMyAppsFromDevice(myappId, dev["deviceId"])
                                        db.addMyAppLog({
                                            "time": int(time.time()),
                                            "action": action,
                                            "deviceSerialNo": dev["deviceId"],
                                            "appName": myapp["name"],
                                            "appVersion": "1",
                                            "severity": "info",
                                            "user": "admin",
                                            "message": action+" operation succeeded"
                                        })
                 # TODO: Conform to FOGDIRECTOR
                try:
                    return {
                        "jobId": str(jobid)
                    }, 200, {"content-type": "application/json"}   
                except UnboundLocalError:
                    return {}, 200, {"content-type": "application/json"}
            except KeyError as e:
                traceback.print_exc()
                return {
                        "code": 1001,
                        "description": "Given request is not valid: "+str(e)
                    }, 400, {"content-type": "application/json"}
            return {
                    "code": 500,
                    "description": "An unexpected error happened. {0}"
                }, 500, {"content-type": "application/json"} 
        else:
            return invalidToken()
