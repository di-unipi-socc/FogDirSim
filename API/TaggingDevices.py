from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS devicetag
             (tagid int, deviceid int)''')
conn.commit()
conn.close()

class TaggingDevices(Resource):
    @staticmethod
    def valid(token):
        return True

    def post(self, tagid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{"devices":[deviceids]}}
        print data
        if self.valid(args["x-token-id"]):
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            for dev in data["devices"]:
                # Checking if there exist already this tag for this device
                print tagid, dev
                c.execute("SELECT * FROM devicetag WHERE tagid=%s AND deviceid=%s" % (tagid, dev))
                data=c.fetchall()
                if len(data)==0:
                    c.execute('''INSERT INTO devicetag VALUES (%s, "%s")''' % (tagid, dev))
            # Getting tag name given the id
            c.execute("SELECT rowid, name FROM tags WHERE rowid = %s" % tagid)
            rows = c.fetchall()
            tagname = rows[0][1]
            conn.commit()
            conn.close()
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
            "name": tagname
        }, 200, {"ContentType": "application/json"}