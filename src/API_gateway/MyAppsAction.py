from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, traceback
from misc.config import queue
import Database as db

class MyAppsAction(Resource):
    def post(self, myappId):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("profile")
        args = parser.parse_args()
        data = request.json
        identifier = queue.add_for_processing(("MyAppsAction", "post"), args, data, myappId)
        return queue.get_result(identifier)
