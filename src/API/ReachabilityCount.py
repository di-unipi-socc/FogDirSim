from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS devicesReachability
             (deviceid int, port int, user text, psw text, devid text)''')
conn.commit()
conn.close()

# TODO
"""
GET /api/v1/appmgr/devices/reachabilityCount
{devices: {href: "/api/v1/appmgr/devices?searchByReachabilityLessThan=day"}, count: 1}
{devices: {href: "/api/v1/appmgr/devices?searchByReachabilityLessThan=month"}, count: 0}
{devices: {href: "/api/v1/appmgr/devices?searchByDeviceStatus=offline"}, count: 0}
"""