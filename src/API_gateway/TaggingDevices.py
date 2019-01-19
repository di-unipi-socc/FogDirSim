from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from misc.config import queue

class TaggingDevices(Resource):

    def post(self, tagid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{"devices":[deviceids]}}
        identifier = queue.add_for_processing(("TaggingDevices", "post"), args, data, tagid)
        return queue.get_result(identifier)