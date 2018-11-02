from flask import Flask, request
from flask_restful import Api, Resource, reqparse

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
            data = request.json()
            try:
                devices = data["deploy"]["devices"]
                for device in devices:
                    devid = device["deviceId"]
                    resourceAsk = device["resourceAsk"]
            except KeyError:
                return
            return
        else:
            return self.invalidToken()
    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'Content-Type':'application/json'} 
