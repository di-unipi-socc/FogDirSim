from flask import Flask, render_template, jsonify, send_from_directory
from flask_restful import Api, Resource, reqparse
import os, time
from API_gateway.Devices import Devices
from API_gateway.TaggingDevices import TaggingDevices
from API_gateway.Tags import Tags
from API_gateway.Applications import Applications
from API_gateway.Authentication import Authentication
from API_gateway.MyApps import MyApps
from API_gateway.MyAppsAction import MyAppsAction
from API_gateway.Audit import Audit
from API_gateway.DevicesEvents import DeviceEvents
from API_gateway.Jobs import Jobs
from API_gateway.Alerts import Alerts
import Database as db
from Simulator.SimThread import SimThread
from Simulator.HistoryThread import Historian
from Simulator import HistoryThread
import signal, threading, time, Simulator
import constants
from threading import Thread, Lock

app = constants.flaskApp

def main():
    global app
    api = Api(app)
    api.add_resource(Devices, "/api/v1/appmgr/devices", "/api/v1/appmgr/devices/<deviceid>")
    api.add_resource(Authentication, "/api/v1/appmgr/tokenservice","/api/v1/appmgr/tokenservice/<token>")
    api.add_resource(Tags, "/api/v1/appmgr/tags")
    api.add_resource(TaggingDevices, "/api/v1/appmgr/tags/<tagid>/devices")
    api.add_resource(Applications, "/api/v1/appmgr/localapps/upload", # POST
                                "/api/v1/appmgr/localapps/<appURL>", # PUT
                                "/api/v1/appmgr/apps/<appURL>", # DELETE
                                "/api/v1/appmgr/localapps", "/api/v1/appmgr/localapps/") # GET
    api.add_resource(MyApps, "/api/v1/appmgr/myapps", "/api/v1/appmgr/myapps/",
                            "/api/v1/appmgr/myapps/<myappId>") # DELETE
    api.add_resource(MyAppsAction, "/api/v1/appmgr/myapps/<myappId>/action")
    api.add_resource(DeviceEvents, "/api/v1/appmgr/devices/<devid>/events/")
    api.add_resource(Audit, "/api/v1/appmgr/audit/")
    api.add_resource(Jobs, "/api/v1/appmgr/jobs", "/api/v1/appmgr/jobs/")
    api.add_resource(Alerts, "/api/v1/appmgr/alerts", "/api/v1/appmgr/alerts/")

    
    def service_shutdown(signum, frame):
        print('\nOh, ok, I\'ll shutdown all the thread in a second... Byeee!')
        simulatorThread.shutdown_flag.set()
        historianThread.shutdown_flag.set()
        exit()
    signal.signal(signal.SIGINT, service_shutdown)
    print("Creating Simulation Thread")
    simulatorThread = SimThread()
    historianThread = Historian()
    
    simulatorThread.start()
    historianThread.start()

    @app.route("/result/devices")
    def result_device():
        values = Simulator.SimThread.getDeviceSampling()
        return jsonify(values)
    
    @app.route("/result/myapps")
    def result_myapps():
        values = Simulator.SimThread.getMyAppsSampling()
        return jsonify(values)

    @app.route("/result/simulationcounter")
    def sim_count():
        return str(Simulator.SimThread.getSimulationCount())

    @app.route("/result/totalenergy")
    def result_system_energy():
        values = Simulator.SimThread.getDeviceSampling()
        total = 0
        for val in values:
            total += val["DEVICE_ENERGY_CONSUMPTION"]
        return total
        
    @app.route("/result/systemuptime")
    def result_system_uptime():
        values = Simulator.SimThread.getMyAppsSampling()
        if len(values) == 0:
            return 1
        total = 0
        for val in values:
            total += val["UP_PERCENTAGE"] 
        return total / len(values)

    @app.route("/result/uptime_history")
    def get_uptime_history():
        val = HistoryThread.get_uptime_history()
        return jsonify(val)

    @app.route("/result/energy_history")
    def get_energy_history():
            return jsonify(HistoryThread.get_energy_history())
    
    @app.route("/simulationreset")
    def reset_simulation():
        average_alerts = {}
        myapps = Simulator.SimThread.getMyAppsSampling()
        for myapp in myapps:
            for k in myapp["ALERT_PERCENTAGE"]:
                if k in average_alerts:
                    average_alerts[k] += myapp["ALERT_PERCENTAGE"][k]
                else:
                    average_alerts[k] = myapp["ALERT_PERCENTAGE"][k]
        for k in average_alerts:
            average_alerts[k] /= len(myapps)
        result = {
            "energy": result_system_energy(),
            "uptime": result_system_uptime(),
            "uptime_history": HistoryThread.get_uptime_history(),
            "alerts": average_alerts,
            "iteration_count": sim_count()
        }
        with Simulator.SimThread.device_lock:
            with Simulator.SimThread.myapp_lock:
                Simulator.SimThread.reset_simulation_counters()
                db.resetSimulation()
                Simulator.HistoryThread.reset_history()
        return jsonify(result)

    # Serve React App
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists("sim-gui/build/" + path):
            return send_from_directory('sim-gui/build', path)
        else:
            return send_from_directory('sim-gui/build', 'index.html')
    return app 

if __name__ == "__main__":
    app = main()
    app.run(debug=True, use_reloader=False, threaded=True)