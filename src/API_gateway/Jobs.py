from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
import Database as db
from misc.config import queue

class Jobs(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("Jobs", "get"), args)
        return queue.get_result(identifier)