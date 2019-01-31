from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouter_size300 as infrastructure
import requests
import json, signal

infrastructure.create()

def bestFit(cpu, mem):
    _, devices = fg.get_devices()
    devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"]]
    devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    best_fit = devices[0]
    return best_fit["ipAddress"]

def randomFit(start_range, end_range):
    deviceId = int(random.random()*end_range)+start_range
    fg.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

def firstFit(cpu, mem):
    _, devices = fg.get_devices()
    devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"]]
    best_fit = devices[0]
    return best_fit["ipAddress"]

def FTpi_like(cpu, mem):
    # Not reasonable
    for _ in range(0, 1000):
        bestFit(cpu, mem) # requires 1 iteration for each counting => 1000 iteration for every device choice
    return None

def service_shutdown(signum, frame):
    print('\nOh, ok, I will print the simulation result.Byeee!')
    r = reset_simulation("new")
    print(r)
    exit()

signal.signal(signal.SIGINT, service_shutdown)

previous_simulation = []
def reset_simulation(current_identifier):
    url = "http://%s/simulationreset" % "127.0.0.1:5000"
    r = requests.get(url)
    previous_simulation.append({
        current_identifier: r
    })
    return r.json()
reset_simulation(0)

fg = FogDirector("127.0.0.1:5000")
code = fg.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

DEVICES_NUMBER = 20
DEPLOYMENT_NUMBER = 150
    # Adding devices

for DEPLOYMENT_NUMBER in range(20, 200, 10):

    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fg.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fg.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        # Creating myapp1 endpoint
        dep = "dep"+str(myapp_index)
        _, myapp1 = fg.create_myapp(localapp["localAppId"], dep)

        deviceIp = bestFit(100, 32)

        code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
        while code == 400:
            print("*** Cannot deploy", dep,"to the building router", deviceIp, ".Try another ***")
            deviceIp = bestFit(100, 32)
            code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
        
        fg.start_app(dep)

    count = 0
    last_count_alerted = 0
    while count < 10000 or (count > 4000 and count-last_count_alerted > 150) :
        count += 1
        _, alerts = fg.get_alerts()
        for alert in alerts["data"]:
            last_count_alerted = count
            if "APP_HEALTH" == alert["simulation_type"]: # No other alerts can be triggered
                dep = alert["appName"]
                print("**Moving ", dep, "****")
                code, _ = fg.stop_app(dep)
                print("stop_app ", dep, code)
                #"unistall App"
                code, _ = fg.uninstall_app(dep, alert["ipAddress"])
                print("uninstall", dep, code)
                #"install App"
                devip =  bestFit(100, 32)
                code, _ = fg.install_app("dep", [devip]) 
                while code == 400:
                    devip =  bestFit(100, 32)
                    code, _ = fg.install_app("dep", [devip])  
                print(dep, " installed on ", devip)
                #"start app"
                code, _ = fg.start_app(dep)
                print("start app", dep, code)

    r = reset_simulation("sim_count:"+str(count)+":depl_num:"+str(DEPLOYMENT_NUMBER))
    print(r)

print(previous_simulation)