from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from API_executor.Authentication import invalidToken
import time, json
import Database as db

def get(args):
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