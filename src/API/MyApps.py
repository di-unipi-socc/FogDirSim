from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from misc.Exceptions import MyAppInstalledOnDeviceError
from API.Authentication import invalidToken
from misc import constants
from misc.config import queue
import Database as db

class MyApps(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json
        identifier = queue.add_for_processing(("MyApps", "post"), args, data)
        return queue.get_result(identifier)
        
    def delete(self, myappId):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("MyApps", "delete"), args, myappId)
        return queue.get_result(identifier)

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument('searchByName')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("MyApps", "get"), args)
        return queue.get_result(identifier)
