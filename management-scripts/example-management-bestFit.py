from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouter_size300_low_res as infrastructure
import requests
import json, signal

infrastructure.create()
tmp = 0
def bestFit(cpu, mem, print_result=False):
    _, devices = fg.get_devices()
    devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
    devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    if print_result:
        print("***********")
        for dev in devices:
            print(dev["ipAddress"], (dev["capabilities"]["nodes"][0]["cpu"]["available"], dev["capabilities"]["nodes"][0]["memory"]["available"]))
    if len(devices) == 0:
        print("THE SYSTEM HAS NO ENOUGH RESOURCES TO SUPPORT YOUR IDEA. SORRY.")
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

def service_shutdown(*args):
    print('\nOh, ok, I will print the simulation result.Byeee!')
    r = reset_simulation("new")
    print(r)
    exit()

#signal.signal(signal.SIGINT, service_shutdown)

previous_simulation = []
def reset_simulation(current_identifier):
    url = "http://%s/simulationreset" % "127.0.0.1:5000"
    r = requests.get(url)
    previous_simulation.append({
        current_identifier: r
    })
    return r.json()
reset_simulation(0)
print("STARTING SIMULATION")

fg = FogDirector("127.0.0.1:5000")
code = fg.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

DEVICES_NUMBER = 20
DEPLOYMENT_NUMBER = 150

for DEPLOYMENT_NUMBER in range(130, 200, 10):
    print("Trying to deploy", str(DEPLOYMENT_NUMBER), "number of devices")
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fg.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fg.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        # Creating myapp1 endpoint
        _, myapp1 = fg.create_myapp(localapp["localAppId"], dep)

        deviceIp = bestFit(100, 32)
        code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
        trial = 0
        while code == 400:
            trial += 1
            if trial == 100:
                print(DEPLOYMENT_NUMBER, "are too high value to deploy")
            print("*** Cannot deploy", dep,"to the building router", deviceIp, ".Try another ***")
            deviceIp = bestFit(100, 32, print_result=True)
            code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
        
        fg.start_app(dep)

    count = 0
    last_count_alerted = 0
    try:
        while count < 20000:
            if count % 200 == 0:
                print ("Count: "+str(count))
                print ("last_count_alerted: ", str(last_count_alerted), " - diff", count-last_count_alerted)
            if (count > 2000 and count-last_count_alerted > 150):
                break
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
                    code, _ = fg.install_app(dep, [devip]) 
                    while code == 400:
                        devip =  bestFit(100, 32)
                        code, _ = fg.install_app(dep, [devip])  
                    print(dep, " installed on ", devip)
                    #"start app"
                    code, _ = fg.start_app(dep)
                    print("start app", dep, code)
    except KeyboardInterrupt:
        r = input("Exit (y/n)?")
        if r == "y":
            service_shutdown()
            exit()

    r = reset_simulation("sim_count:"+str(count)+":depl_num:"+str(DEPLOYMENT_NUMBER))
    file  = open("simulation_result.txt", "a")
    file.write("sim_count: "+str(count)+" - depl_num: "+str(DEPLOYMENT_NUMBER)+"\n")
    file.write(json.dumps(r))
    file.write("\n\n")
    file.close()

file  = open("final_simulation_result.txt", "w")
file.write(json.dumps(previous_simulation))
file.close()
