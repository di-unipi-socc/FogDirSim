from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from Authentication import invalidToken
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Alerts(Resource):
    def get(self):
        alerts = db.getAlerts()
        data = []
        for alert in alerts:
            data.append(alert)
        return {"data": data}, 200, {"content-type": "application/json"}