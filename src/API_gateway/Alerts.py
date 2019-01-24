from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from constants import queue

class Alerts(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        return queue.get_result(
            queue.add_for_processing(("Alerts", "get"), args)
        )