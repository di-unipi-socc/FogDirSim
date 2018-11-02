from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Authentication(Resource):
    
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        return db.checkToken(args["x-token-id"])
    """
        If true: {"token":"822b6377-1366-4a3a-aca3-3a14c3c82608","expiryTime":1540462820079,"serverEpochTime":1540461020081}
        if False: {"code":1702,"description":"Incorrect username or password"}
    """
    def post(self):
        #parser = reqparse.RequestParser()
        #parser.add_argument("")
        #parser.add_argument('User-Agent', location='headers')
        if request.authorization["username"] == "admin" and request.authorization["password"] == "admin_123":
            epochTime = int(time.time())
            expiryTime = epochTime + 600 # 10 minutes
            token = "%d-1366-4a3a--%d" % (hash(time.time()), int(time.time()))
            userid = 0
            db.addToken(expiryTime, token, userid)
            return {"token":token,"expiryTime":expiryTime,"serverEpochTime":epochTime}, 202, {"Content-Type": "application/json"}
        return {"code":1702,"description":"Incorrect username or password"}, 400, {'Content-Type':'application/json'}

    def delete(self, token):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            db.deleteToken(token)
            return {"token": token}, 200, {"ContentType": "application/json"}
        else:
            return {"code":1703,"description":"Session is invalid or expired"}, 401, {"ContentType": "application/json"}
            