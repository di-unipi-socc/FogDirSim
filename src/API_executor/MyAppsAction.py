from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, traceback
from API_executor.Authentication import invalidToken
from misc.Exceptions import NoResourceError
import constants
import Database as db

def post(args, data, myappId):
    if db.checkToken(args["x-token-id"]):
        try:
            myapp = db.getMyApp(myappId)
            if "deploy" in data.keys():
                action = "deploy"
                data = data["deploy"]
                devices = data["devices"]  
                app = db.getLocalApplicationBySourceName(myapp["sourceAppName"])
                if not app["published"]: # This is not checked in FogDirector, but in unpublished app it crash
                    return {"error": "the app have to be published"}, 400, {"content-type": "application/json"}
                deviceSuccessful = []
                profile = constants.MYAPP_PROFILE_NORMAL
                for device in devices:
                    devid = device["deviceId"]
                    resourceAsked = device["resourceAsk"]["resources"]
                    if args["profile"] in [constants.MYAPP_PROFILE_LOW, constants.MYAPP_PROFILE_NORMAL, constants.MYAPP_PROFILE_HIGH]:
                        profile = args["profile"]
                    else:
                        profile = constants.MYAPP_PROFILE_NORMAL
                    try:
                        try:
                            db.checkAndAllocateResource(devid, resourceAsked["cpu"], resourceAsked["memory"])
                        except TypeError:
                            return {"Error": "Device does not exist"}, 400, {"content-type: application/json"}
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
                # TODO: if la myapp è già sul device: ritorna errore  
                jobid = db.addJobs(myappId, deviceSuccessful, profile=profile, payload=data)
                
            elif "start" in data.keys() or "stop" in data.keys(): 
                action = "start" if "start" in data.keys() else "stop"
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
                
            elif "undeploy" in data.keys(): 
                action = "undeploy"
                data = data[action]
                devices_payload = data["devices"]
                myapp = db.getMyApp(myappId) # Taken for Name only
                myapp_jobs = db.getJobs(myappId)
                if myapp_jobs == 0:
                    return {"Error": "no jobs are running"}, 400, {"content-type": "application/json"}
                for job in myapp_jobs:
                    try:
                        jobDescr = job["payload"]
                        resourcesDevs = jobDescr["devices"]
                        for device in resourcesDevs:
                            if device["deviceId"] in devices_payload:
                                cpu = 0
                                mem = 0
                                resourceAsked = device["resourceAsk"]["resources"]
                                if device["deviceId"] in devices_payload:
                                    cpu = device["resourceAsk"]["resources"]["cpu"]
                                    mem = device["resourceAsk"]["resources"]["memory"]
                                    db.deallocateResource(device["deviceId"],cpu, mem)
                                    db.removeMyAppsFromDevice(myappId, device["deviceId"])
                                    db.uninstallJob(myappId, device["deviceId"])

                                    db.addMyAppLog({
                                        "time": int(time.time()),
                                        "action": action,
                                        "deviceSerialNo": device["deviceId"],
                                        "appName": myapp["name"],
                                        "appVersion": "1",
                                        "severity": "info",
                                        "user": "admin",
                                        "message": action+" operation succeeded"
                                    })
                    except TypeError:
                        return {"Error": "Internal Error TypeError"}, 500, {"content-type": "application/json"}
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
