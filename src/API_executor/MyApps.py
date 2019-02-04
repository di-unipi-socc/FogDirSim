from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from misc.Exceptions import MyAppInstalledOnDeviceError
from API_executor.Authentication import invalidToken
import constants
import Database as db

def post(args, data):
    if db.checkToken(args["x-token-id"]):
        try:
            appname = data["name"]
            sourceAppName = data["sourceAppName"]
            version = data["version"]
            appType = data["appSourceType"]
        except KeyError:
            return {
                    "code": 1001,
                    "description": "Given request is not valid: {0}"
                }, 400, {"Content-Type": "application/json"}
        if db.myAppExists(appname):
            return {
                    "code": 1304,
                    "description": "An app with name %s already exists." % appname # Cisco does not return the name but the identifier
                }, 409, {"content-type": "application/json"}
        if appType != "LOCAL_APPSTORE":
            {
                "code": -1,
                "description": "This simulator is not able to manage not LOCAL_APPSTORE applications"
            }, 400, {"Content-Type": "application/json"}
        if args["minjobs"] != None:
            myapp = db.createMyApp(appname, sourceAppName, version, appType, minjobs=args["minjobs"])
        else:
            myapp = db.createMyApp(appname, sourceAppName, version, appType)
        del myapp["_id"]
        return {"myappId": myapp["myappId"], "name": myapp["name"]}, 201, {"content-type": "application/json"}
    else:
        return invalidToken()
    
def delete(args, myappId):
    if db.checkToken(args["x-token-id"]):
        try:
            app = db.deleteMyApp(myappId)

            del app["_id"]
            return app
        except MyAppInstalledOnDeviceError as e:
            return {"Error": str(e)}, 400, {"Content-type": "application/json"} # TODO: this response is not compared with FogDirector
        return {"Simulation Internal Server Error in MyApps_executor delete", 500}
    else:
        return invalidToken()

def get(args):
    if db.checkToken(args["x-token-id"]):
        data = {"data": []}
        myapps = db.getMyApps(args["searchByName"])
        for myapp in myapps:
            del myapp["_id"]
            data["data"].append(myapp)
            if args["searchByName"] != None:
                return myapp, 200, {'ContentType':'application/json'} 
        return data, 200, {'ContentType':'application/json'} 
    else:
        return invalidToken()
