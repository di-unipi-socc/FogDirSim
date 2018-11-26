from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse

from API.Devices import Devices
from API.TaggingDevices import TaggingDevices
from API.Tags import Tags
from API.Applications import Applications
from API.Authentication import Authentication
from API.MyApps import MyApps
from API.MyAppsAction import MyAppsAction
from API.Audit import Audit
from API.DevicesEvents import DeviceEvents
from API.Jobs import Jobs
from API.Alerts import Alerts
import Database as db
from Simulator.SimThread import SimThread, getSimulationValues
import signal, threading, time


app = Flask(__name__)
api = Api(app)

api.add_resource(Devices, "/api/v1/appmgr/devices", "/api/v1/appmgr/devices/<deviceid>")
api.add_resource(Authentication, "/api/v1/appmgr/tokenservice","/api/v1/appmgr/tokenservice/<token>")
api.add_resource(Tags, "/api/v1/appmgr/tags")
api.add_resource(TaggingDevices, "/api/v1/appmgr/tags/<tagid>/devices")
api.add_resource(Applications, "/api/v1/appmgr/localapps/upload", # POST
                               "/api/v1/appmgr/localapps/<appURL>", # PUT
                               "/api/v1/appmgr/apps/<appURL>", # DELETE
                               "/api/v1/appmgr/localapps") # GET
api.add_resource(MyApps, "/api/v1/appmgr/myapps", "/api/v1/appmgr/myapps/",
                         "/api/v1/appmgr/myapps/<myappid>") # DELETE
api.add_resource(MyAppsAction, "/api/v1/appmgr/myapps/<myappid>/action")
api.add_resource(DeviceEvents, "/api/v1/appmgr/devices/<devid>/events/")
api.add_resource(Audit, "/api/v1/appmgr/audit/")
api.add_resource(Jobs, "/pi/v1/appmgr/jobs", "/api/v1/appmgr/jobs/")
api.add_resource(Alerts, "/pi/v1/appmgr/alerts", "/api/v1/appmgr/alerts/")

def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    simulatorThread.shutdown_flag.set()
    exit()

print "Creating Simulation Thread"
simulatorThread = SimThread()
signal.signal(signal.SIGINT, service_shutdown)
simulatorThread.start()

@app.route("/result")
def simulator_result():
    values = getSimulationValues()
    return render_template("result.html", values=values)
app.run(debug=True, use_reloader=False)

