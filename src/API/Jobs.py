from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from Authentication import invalidToken
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Jobs(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            jobs = db.getJobs()
            data = []
            for job in jobs:
                job["id"] = str(job["_id"])
                del job["_id"]
                data.append(job)
            return {"data": data}, 200, {"content-type": "application/json"}
        else:
            return invalidToken()