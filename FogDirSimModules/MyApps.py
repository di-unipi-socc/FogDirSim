from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS myapps
             (expirytime text, userid int, token text)''')
conn.commit()
conn.close()

class MyApps(Resource):
    @staticmethod
    def valid(token):
        return True
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("searchByName")
        args = parser.parse_args()
        if self.valid(args["x-token-id"]):
            if args["searchByName"] != None:

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
