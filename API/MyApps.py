from flask import Flask, request
from flask_restful import Api, Resource, reqparse

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class MyApps(Resource):
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            data = request.json
            try:
                appname = data["name"]
                sourceAppName = data["sourceAppName"]
                version = data["version"]
                appSourceType = data["appSourceType"]
            except KeyError:
                return {
                        "code": 1001,
                        "description": "Given request is not valid: {0}"
                    }, 400, {"Content-Type": "application/json"}
            if db.myAppExists(sourceAppName):
                return """{
                        "code": 1304,
                        "description": "An app with name %s already exists."
                    }""" % (sourceAppName), 409, {"content-type": "application/json"}
            myapp = {"myappId": -1,
                    "name": appname,
                    "_links": {
                        "sourceApp": {
                            "href": "/api/v1/appmgr/apps/%s" % sourceAppName
                        },
                        "icon": {
                            "href": "/api/v1/appmgr/localapps/%s/icon" % sourceAppName
                        },
                        "configurations": {
                            "href": "/api/v1/appmgr/myapps/%s/configurations" % myappappid
                        },
                        "summaryState": {
                            "href": "/api/v1/appmgr/myapps/%s/summaryState" % myappappid
                        },
                        "aggregatedStats": {
                            "href": "/api/v1/appmgr/myapps/%s/aggregatedStats" % myappappid
                        },
                        "tags": {
                            "href": "/api/v1/appmgr/myapps/%s/tags" % myappappid
                        },
                        "action": {
                            "href": "/api/v1/appmgr/myapps/%s/action" % myappappid
                        },
                        "notifications": {
                            "href": "/api/v1/appmgr/myapps/%s/notifications" % myappappid
                        },
                        "self": {
                            "href": "/api/v1/appmgr/myapps/%s" % myappappid
                        }
                    }
                }
            myapp = db.createMyApp(myapp)
            return myapp, 201, {"content-type": "application/json"}
        else:
            return self.invalidToken()
        
    def delete(self, myappid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            app = db.deleteMyApp(myappid)
            del app["_id"]
            return 
        else:
            return self.invalidToken()

    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'Content-Type':'application/json'} 


"""
GET ?searchByName SE TROVA
{
    "myappId": "2715",
    "name": "httpd",
    "_links": {
        "sourceApp": {
            "href": "/api/v1/appmgr/apps/7bdb377d-45fd-4a8e-a17c-5baa244b1f45:latest"
        },
        "icon": {
            "href": "/api/v1/appmgr/localapps/7bdb377d-45fd-4a8e-a17c-5baa244b1f45:latest/icon"
        },
        "configurations": {
            "href": "/api/v1/appmgr/myapps/2715/configurations"
        },
        "summaryState": {
            "href": "/api/v1/appmgr/myapps/2715/summaryState"
        },
        "aggregatedStats": {
            "href": "/api/v1/appmgr/myapps/2715/aggregatedStats"
        },
        "tags": {
            "href": "/api/v1/appmgr/myapps/2715/tags"
        },
        "action": {
            "href": "/api/v1/appmgr/myapps/2715/action"
        },
        "notifications": {
            "href": "/api/v1/appmgr/myapps/2715/notifications"
        },
        "self": {
            "href": "/api/v1/appmgr/myapps/2715"
        }
    } ALTRIMENTI SE NON TROVA {}
}
"""
