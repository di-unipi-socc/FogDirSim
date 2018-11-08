from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json
from Authentication import invalidToken

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Audit(Resource):
    def get(self):
        logs = db.getMyAppsLog()
        data = []
        for log in logs:
            del log["_id"]
            data.append(log)
        return {"data": data}, 200, {"content-type": "application/json"}
        
    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'Content-Type':'application/json'} 
