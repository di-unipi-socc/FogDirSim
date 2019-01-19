from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from API_executor.Authentication import invalidToken
import Database as db

def post(args, data, tagid):
    tag = db.getTag(tagid)
    if db.checkToken(args["x-token-id"]):
        try:
            deviceIds = data["devices"]
        except KeyError:
            deviceIds = []
        for deviceid in deviceIds:
            db.tagDevice(int(deviceid), tagid)
    else:
        return invalidToken()
    
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