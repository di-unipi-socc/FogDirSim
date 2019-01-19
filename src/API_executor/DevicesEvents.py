from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from API_executor.Authentication import invalidToken
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class DeviceEvents(Resource):
    def get(self, devid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            return "Not Implemented Yet" # TODO Implement this
        else:
            return invalidToken()