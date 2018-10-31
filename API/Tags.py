from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tags
             (name text, description text)''')
conn.commit()
conn.close()

class Tags(Resource):
    @staticmethod
    def valid(token):
        return True

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{"name": "name_tag"}
        if self.valid(args["x-token-id"]):
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
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            c.execute('''INSERT INTO tags VALUES ("%s", "%s")''' % (tagname, tagdescription))
            conn.commit()
            conn.close()
            return {
                "_links": {
                    "device": {
                        "href": "/api/v1/appmgr/tags/%d/devices" % c.lastrowid
                    },
                    "self": {
                        "href": "/api/v1/appmgr/tags/%d" % c.lastrowid
                    }
                },
                "tagId": c.lastrowid,
                "name": "newtag"
            }, 200, {'ContentType':'application/json'} 
    
    def get(self):
        conn = sqlite3.connect('FogDirSim.db')
        c = conn.cursor()
        c.execute('''SELECT rowid, * FROM tags''')
        tags = []
        for tag in c:
            tags.append({
                "_links": {
                    "device": {
                        "href": "/api/v1/appmgr/tags/%d/devices" % tag[0]
                    },
                    "self": {
                        "href": "/api/v1/appmgr/%d/2714" % tag[0]
                    }
                },
                "tagId": tag[0],
                "name": tag[1],
                "description": None
            })
        return {"data": tags}, 200, {'ContentType':'application/json'} 
    
    
