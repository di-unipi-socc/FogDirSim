from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from Authentication import invalidToken
import time, json
from modules.ResourceSampling import sampleMyAppStatus
from Simulator import costants

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Alerts(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            alerts = db.getAlerts()
            data = []
            devices = db.getDevices()
            for dev in devices:
                for installedApp in dev["installedApps"]:
                    job = db.getJob(installedApp)
                    appname = db.getMyApp(job["myappid"])["name"]
                    # Check if the jobs is health
                    for device in job["devices"]:
                        devid = device["deviceId"]
                        sampled = sampleMyAppStatus(devid, device["resourceAsk"]["resources"]["cpu"], 
                                                            device["resourceAsk"]["resources"]["memory"])
                        if sampled["hasCPU"] == False:
                            data.append({
                                "myAppId": job["myappid"],
                                "deviceId": devid,
                                "time": int(time.time()),
                                "type": costants.FEW_CPU,
                                "message": "Application "+appname+" has too few CPU to run well."
                            })
                        if sampled["hasMEM"] == False:
                            data.append({
                                "myAppId": job["myappid"],
                                "deviceId": devid,
                                "time": int(time.time()),
                                "type": "Application "+appname+" has too few MEM to run well."
                            })
                for alert in alerts:
                    data.append(alert)
                data.sort(lambda x,y: -1 if x["time"] < y["time"] else (0 if x["time"] == y["time"] else 1))
            return {"data": data}, 200, {"content-type": "application/json"}
        else:
            return invalidToken()