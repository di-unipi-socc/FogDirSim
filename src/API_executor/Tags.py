from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from API.Authentication import invalidToken
import Database as db

def post(args, data):
    if db.checkToken(args["x-token-id"]):
        try:
            tagname = data["name"]
        except KeyError:
            return {
                "code": 1000,
                "description": "An unexpected error happened. Validation failed for classes [com.cisco.eng.ccm.model.device.Tag] during persist time for groups [javax.validation.groups.Default, ]\nList of constraint violations:[\n\tConstraintViolationImpl{interpolatedMessage='may not be null', propertyPath=name, rootBeanClass=class com.cisco.eng.ccm.model.device.Tag, messageTemplate='{javax.validation.constraints.NotNull.message}'}\n]"
            }, 500, {"ContentType": "application/json"}
        try:
            tagdescription = data["description"]
        except KeyError:
            tagdescription = ""

        if db.tagExists(tagname):
            return {
                "code": 1402,
                "description": "Tag with name new_tag, already exist."
            }, 409, {"ContentType": "application/json"}

        tagid = str(db.addTag(tagname, tagdescription))
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
            "name": "newtag"
        }, 201, {'ContentType':'application/json'} 
    else:
        return invalidToken()
        
def get(args):
    if db.checkToken(args["x-token-id"]):
        tags = db.getTags()
        data = []
        for tag in tags:
            data.append({
                "_links": {
                    "device": {
                        "href": "/api/v1/appmgr/tags/%s/devices" % str(tag["_id"])
                    },
                    "self": {
                        "href": "/api/v1/appmgr/%s/2714" % str(tag["_id"])
                    }
                },
                "tagId": str(tag["_id"]),
                "name": tag["name"],
                "description": tag["description"] 
            })
        return {"data": data}, 200, {'ContentType':'application/json'} 
    else:
        return invalidToken()


