from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from API_executor.Authentication import invalidToken
import time, json
from functools import cmp_to_key
from misc.ResourceSampling import sampleMyAppStatus
from misc import constants

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

def get(args):
    if db.checkToken(args["x-token-id"]):
        alerts = db.getAlerts()
        data = []
        for alert in alerts:
            data.append(alert)
        data.sort(key=cmp_to_key(lambda x,y: -1 if x["time"] < y["time"] else (0 if x["time"] == y["time"] else 1)))
        return {"data": data}, 200, {"content-type": "application/json"}
    else:
        return invalidToken()