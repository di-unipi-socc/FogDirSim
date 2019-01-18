from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from API.Authentication import invalidToken
import time, json
from misc.config import queue

class Devices(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{'port':'8888','ipAddress':device_ip,'username':'t','password':'t'}
        identifier = queue.add_for_processing(("Devices", "post"), args, data)
        return queue.get_result(identifier)

    def delete(self, deviceid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()

        identifier = queue.add_for_processing(("Devices", "delete"), deviceid, args)        
        return queue.get_result(identifier)

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int)
        parser.add_argument("offset", type=int)
        parser.add_argument("searchByTags")
        parser.add_argument("searchByAnyMatch")
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        
        identifier = queue.add_for_processing(("Devices", "get"), args)
        return queue.get_result(identifier)
    
        