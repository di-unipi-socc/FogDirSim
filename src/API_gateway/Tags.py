from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from constants import queue

class Tags(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json #{"name": "name_tag"}
        identifier = queue.add_for_processing(("Tags", "post"), args, data)
        return queue.get_result(identifier)

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("Tags", "get"), args)
        return queue.get_result(identifier)
        