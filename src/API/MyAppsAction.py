from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from modules.Exceptions import NoResourceError
#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class MyAppsAction(Resource):
    def post(self, appid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            data = request.json
            try:
                action = data.keys()[0]
                if action == "deploy":
                    data = data[action]
                    devices = data["devices"]
                    # TODO check if the application is published
                    for device in devices:
                        devid = device["deviceId"]
                        resourceAsked = device["resourceAsk"]["resources"]
                        try:
                            db.checkAndAllocateResource(devid, resourceAsked["cpu"], resourceAsked["memory"])
                            db.addMyAppToDevice(appid, devid)
                        except NoResourceError, e:
                            return {
                                "code": 1000,
                                "description": str(e)
                            }, 400, {"content-type": "application/json"}
                    jobid = db.addJobs(appid, data["devices"])
                    return {
                        "jobId": jobid,
                        "_links": {
                            "href": "/api/v1/appmgr/jobs/2710"
                        }
                    }, 200, {"content-type": "application/json"}
                elif action == "start" or action == "stop":
                    jobid = db.updateJobsStatus(appid, action)
                    return {
                        "jobId": jobid,
                        "_links": {
                            "href": "/api/v1/appmgr/jobs/2710"
                        }
                    }, 200, {"content-type": "application/json"}
            except KeyError:
                return {
                        "code": 1001,
                        "description": "Given request is not valid: {0}"
                    }, 400, {"content-type": "application/json"}
            return
        else:
            return self.invalidToken()
    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'Content-Type':'application/json'} 
