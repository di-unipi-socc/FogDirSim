from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from Authentication import invalidToken
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Devices(Resource):

    @staticmethod
    def computeDeviceId(ip, port):
        return str(abs(hash(ip + str(port))))

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{'port':'8888','ipAddress':device_ip,'username':'t','password':'t'}
        
        if db.checkToken(args["x-token-id"]):
            if data == None or\
                data["ipAddress"] == None or\
                data["port"] == None or\
                data["username"] == None or\
                data["password"] == None:
                return {"description": "ipAddress, port, username or password not defined"}, 401, {"ContentType": "application/json"}

            if db.deviceExists(data["ipAddress"], data["port"]):
                return {
                    "code": 1101,
                    "description": "A device with IP address, %s, already exists in the inventory." % data["ipAddress"]
                }, 409, {"ContentType": "application/json"}

            try:
                devSpecs = db.addDevice(data["ipAddress"], data["port"], data["username"], data["password"])
            except LookupError:
                return {"error": "LookupError: The device you are adding is not present in the RealDatabase"}, 400, {'ContentType':'application/json'}
            del devSpecs["_id"]
            return devSpecs, 201, {'ContentType':'application/json'}
        else:
            return invalidToken()

    def delete(self, deviceid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            dev = db.getDevice(deviceid)
            db.deleteDevice(deviceid)
            del dev["_id"]
            return dev, 200, {"Content-Type": "application/json"}
        else:
            return invalidToken()

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int)
        parser.add_argument("offset", type=int)
        parser.add_argument("searchByTags")
        parser.add_argument("searchByAnyMatch")
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        
        if db.checkToken(args["x-token-id"]):
            data = {"data": []}
            devices = db.getDevices(args["limit"] if args["limit"] != None else 1000, 
                                    args["offset"] if args["offset"] != None else 0,
                                    args["searchByTags"],
                                    args["searchByAnyMatch"])
            
            for device in devices:
                del device["password"] # removing password from the returned HTTP API object
                del device["_id"]
                data["data"].append(device)

            return data, 200, {'ContentType':'application/json'} 
        else:
            return invalidToken()
        