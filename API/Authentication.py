from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tokens
             (expirytime text, userid int, token text)''')
conn.commit()
conn.close()

class Authentication(Resource):
    @staticmethod
    def valid(token):
        conn = sqlite3.connect('FogDirSim.db')
        c = conn.cursor()
        c.execute('''SELECT expirytime FROM tokens WHERE token="%s"''' % token)
        row = c.fetchall()
        conn.close()
        if len(row) > 0 and row[0] > int(time.time()):
            return True
        return False

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
            expiryTime = epochTime + 20000
            token = "%d-1366-4a3a--%d" % (hash(time.time()), int(time.time()))
            userid = 0
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            query = "INSERT INTO tokens VALUES('%s', %d, '%s')" % (expiryTime, userid, token)
            c.execute(query)
            conn.commit()
            conn.close()
            return {"token":token,"expiryTime":expiryTime,"serverEpochTime":epochTime}
        return {"code":1702,"description":"Incorrect username or password"}, 400, {'ContentType':'application/json'}

    def delete(self, token):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if self.valid(args["x-token-id"]):
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            c.execute('''DELETE FROM tokens
                        WHERE token="%s"''' % token)
            conn.commit()
            conn.close()
            return {"token": token}, 200, {"ContentType": "application/json"}
        else:
            return {"code":1703,"description":"Session is invalid or expired"}, 401, {"ContentType": "application/json"}
            