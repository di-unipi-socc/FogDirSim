from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db
    
def get(args):
    return db.checkToken(args["x-token-id"])

def post(user, psw):
    if user == "admin" and psw == "admin_123":
        epochTime = int(time.time())
        expiryTime = epochTime + 600 # 10 minutes
        token = "%d-1366-4a3a--%d" % (hash(time.time()), int(time.time()))
        userid = 0
        db.addToken(expiryTime, token, userid)
        return {"token":token,"expiryTime":expiryTime,"serverEpochTime":epochTime}, 202, {"Content-Type": "application/json"}
    return {"code":1702,"description":"Incorrect username or password"}, 400, {'Content-Type':'application/json'}

def delete(args, token):
    if db.checkToken(args["x-token-id"]):
        db.deleteToken(token)
        return {"token": token}, 200, {"ContentType": "application/json"}
    else:
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {"ContentType": "application/json"}

def invalidToken():
    return {"code":1703,"description":"Session is invalid or expired"}, 401, {'Content-Type':'application/json'} 
