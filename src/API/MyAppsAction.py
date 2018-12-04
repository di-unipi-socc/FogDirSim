from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, traceback
from Authentication import invalidToken
from modules.Exceptions import NoResourceError
#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class MyAppsAction(Resource):
    def post(self, myappid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            data = request.json
            try:
                action = data.keys()[0]
                myapp = db.getMyApp(myappid)
                if action == "deploy":
                    data = data[action]
                    devices = data["devices"]  
                    app = db.getLocalApplicationBySourceName(myapp["sourceAppName"])
                    if not app["published"]: # This is not checked in FogDirector
                        return {"error": "the app have to be published"}, 400, {"content-type": "application/json"}
                    deviceSuccessful = []
                    for device in devices:
                        devid = device["deviceId"]
                        resourceAsked = device["resourceAsk"]["resources"]
                        try:
                            db.checkAndAllocateResource(devid, resourceAsked["cpu"], resourceAsked["memory"])
                            db.addMyAppToDevice(myappid, devid)
                            db.addMyAppLog({
                                "time": int(time.time()),
                                "action": action,
                                "deviceSerialNo": devid,
                                "appName": myapp["name"],
                                "appVersion": "1",
                                "severity": "info",
                                "user": "admin",
                                "message": action+" operation succeeded"
                            })
                            deviceSuccessful.append(device)
                        except NoResourceError, e:
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
                            
                    jobid = db.addJobs(myappid, deviceSuccessful, payload=request.json)
                    
                elif action == "start" or action == "stop":
                    db.addMyAppLog({
                        "time": int(time.time()),
                        "action": action,
                        "appName": myapp["name"],
                        "appVersion": "1",
                        "severity": "info",
                        "user": "admin",
                        "message": action+" operation succeeded"
                    })
                    jobid = db.updateJobsStatus(myappid, action)
                elif action == "undeploy":
                    data = data[action]
                    devices = data["devices"]
                    myapp = db.getMyApp(myappid)
                    jobDescr = db.getJob(myappid)["payload"]
                    resourcesDevs = jobDescr["deploy"]["devices"]
                    for device in devices:
                        devid = device["deviceId"]
                        resourceAsked = device["resourceAsk"]["resources"]
                        cpu = 0
                        mem = 0
                        for dev in resourcesDevs: # TODO TEST it!
                            if dev["deviceId"] == dev["deviceId"]:
                                cpu = dev["resourceAsk"]["resources"]["cpu"]
                                mem = dev["resourceAsk"]["resources"]["mem"]
                        db.deallocateResource(devid,cpu, mem)
                        db.removeMyAppsFromDevice(myappid, devid)
                        db.addMyAppLog({
                            "time": int(time.time()),
                            "action": action,
                            "deviceSerialNo": devid,
                            "appName": myapp["name"],
                            "appVersion": "1",
                            "severity": "info",
                            "user": "admin",
                            "message": action+" operation succeeded"
                        })
                return {
                    "jobId": str(jobid)
                }, 200, {"content-type": "application/json"}   
            except KeyError, e:
                traceback.print_exc()
                return {
                        "code": 1001,
                        "description": "Given request is not valid: "+str(e)
                    }, 400, {"content-type": "application/json"}
            return
        else:
            return invalidToken()
