from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from constants import queue

class Authentication(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("Authentication", "get"), args)
        return queue.get_result(identifier)
        
    """
        If true: {"token":"822b6377-1366-4a3a-aca3-3a14c3c82608","expiryTime":1540462820079,"serverEpochTime":1540461020081}
        if False: {"code":1702,"description":"Incorrect username or password"}
    """

    def post(self):
        return queue.get_result(
            queue.add_for_processing(("Authentication", "post"), request.authorization["username"], request.authorization["password"]))
        
    def delete(self, token):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        return queue.get_result(
                queue.add_for_processing(("Authentication", "delete"), args, token))