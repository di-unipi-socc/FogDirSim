from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class TaggingDevices(Resource):

    def post(self, tagid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{"devices":[deviceids]}}
        tag = db.getTag(tagid)

        if db.checkToken(args["x-token-id"]):
            try:
                deviceIds = data["devices"]
            except KeyError:
                deviceIds = []
            for deviceid in deviceIds:
                db.tagDevice(int(deviceid), tagid)
        else:
            return self.invalidToken()
        
        # You can destroy the server but the only information returned is the tag itself. Cisco, REALLY??
        return {
            "_links": {
                "device": {
                    "href": "/api/v1/appmgr/tags/%s/devices" % tagid
                },
                "self": {
                    "href": "/api/v1/appmgr/tags/%s" % tagid
                }
            },
            "tagId": tagid,
            "name": tag["name"],
            "description": tag["description"]
        }, 200, {"ContentType": "application/json"}

    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'ContentType':'application/json'} 