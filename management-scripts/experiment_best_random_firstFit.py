from APIWrapper import FogDirector
import time, random, math, os
from infrastructure import ciscorouters_30pz_5b5m20s as infrastructure
import requests
import simplejson, signal

from datetime import datetime

port = os.environ.get('SERVER_PORT', "5000")

infrastructure.create()

def simulation_counter():
    r = requests.get('http://localhost:'+port+'/result/simulationcounter')
    return int(r.text)

def bestFit(cpu, mem):
    _, devices = fd.get_devices()
    devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                            and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
    devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    while len(devices) == 0:
        if simulation_counter() > 15000:
            print("Not able to find a bestfit. Simulation ends")
            exit()
        _, devices = fd.get_devices()
        devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                                    and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
        devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                        dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    best_fit = devices[0]
    return best_fit["ipAddress"], best_fit["deviceId"]

def randomFit():
    _, devices = fd.get_devices()
    r = random.randint(0, len(devices["data"]) - 1)
    return devices["data"][r]["ipAddress"], devices["data"][r]["deviceId"]

def firstFit(cpu, mem): 
    while simulation_counter() < 15000:
        _, devices = fd.get_devices()
        for dev in devices["data"]:
            if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem:
                return dev["ipAddress"], dev["deviceId"]

previous_simulation = []

def reset_simulation(current_identifier):
    url = "http://%s/simulationreset" % ("127.0.0.1:"+port)
    r = requests.get(url)
    output = r.json()
    previous_simulation.append({
        current_identifier: output
    })
    file  = open("simulation_results_best_random_first.txt", "a")
    file.write(str(current_identifier)+"\n")
    out = simplejson.dumps(output, indent=4, sort_keys=True)
    file.write(out)
    file.write("\n\n")
    file.close()
    return output

# Resetting simulator before start
url = "http://%s/simulationreset" % ("127.0.0.1:"+port)
r = requests.get(url)

print("STARTING SIMULATION")

fd = FogDirector("127.0.0.1:"+port)
code = fd.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

DEVICES_NUMBER = 20
DEPLOYMENT_NUMBER = 150



print("STARTING BESTFIT PHASE")
###########################################################################################
#                                   BESTFIT                                               #
###########################################################################################
fallimenti = []
iteration_count = []
for simulation_count in range(0, 15):
    if os.environ.get('SKIP_BEST', None) != None:
        break
    start = time.time()
    reset_simulation("BEST"+str(simulation_count))
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myappId = fd.create_myapp(localapp["localAppId"], dep)

        dt = datetime.now()
        deviceIp, deviceId = bestFit(100, 32)

        dt = datetime.now()
        code, res = fd.fast_install_app(myappId, [deviceId])
 
        while code == 400:
            if simulation_counter() > 15000:
                print("INSTALLED ONLY ", myapp_index, "in 15000")
            fallimento += 1
            deviceIp, deviceId = bestFit(100, 32)
            code, res = fd.fast_install_app(myappId, [deviceId])
        dt = datetime.now()
        fd.fast_start_app(myappId)


    while simulation_counter() < 15000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dep = alert["appName"]
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                _, app_det = fd.get_myapp_details(dep)
                myappId = app_det["myappId"]
                fd.fast_stop_app(myappId)
                fd.fast_uninstall_app(myappId, alert["deviceId"])
                deviceIp, deviceId = bestFit(100, 32)
                code, _ = fd.fast_install_app(myappId, [deviceId])
                while code == 400:
                    fallimento += 1
                    if simulation_counter() > 15000:
                        break
                    deviceIp, deviceId = bestFit(100, 32)
                    code, _ = fd.fast_install_app(myappId, [deviceId]) 
                fd.fast_start_app(myappId)
            if simulation_counter() > 15000:
                break
    fallimenti.append(fallimento)
    iteration_end = simulation_counter()
    iteration_count.append(iteration_end)
    print("{:02d}) iter_count: {:d} (mean: {:f}) - fails: {:d} (mean: {:f})".format(simulation_count, 
                                                                            iteration_end, 
                                                                            sum(iteration_count)/float(len(iteration_count)), 
                                                                            fallimento, 
                                                                            sum(fallimenti)/float(len(fallimenti))
                                                                            ))

print("STARTING RANDOM PHASE")
###########################################################################################
#                                   RANDOMFIT                                             #
###########################################################################################
fallimenti = []
iteration_count = []
for simulation_count in range(0, 15):
    if os.environ.get('SKIP_RANDOM', None) != None:
        break
    start = time.time()
    reset_simulation("RANDOM"+str(simulation_count))
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myappId = fd.create_myapp(localapp["localAppId"], dep)

        deviceIp, deviceId = randomFit()
        code, res = fd.fast_install_app(myappId, [deviceId])
        trial = 0
        while code == 400:
            trial += 1
            if simulation_counter() > 15000:
                print("INSTALLED ONLY ", myapp_index, "in 15000")
            fallimento += 1
            deviceIp, deviceId = randomFit()
            code, res = fd.fast_install_app(myappId, [deviceId])
        fd.fast_start_app(myappId)

    while simulation_counter() < 15000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dep = alert["appName"]  
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                _, app_det = fd.get_myapp_details(dep)
                myappId = app_det["myappId"]
                fd.fast_stop_app(myappId)
                fd.fast_uninstall_app(myappId, alert["deviceId"])
                deviceIp, deviceId = randomFit()
                code, _ = fd.fast_install_app(myappId, [deviceId]) 
                while code == 400:
                    fallimento += 1
                    if simulation_counter() > 15000:
                        break
                    deviceIp, deviceId = randomFit()
                    code, _ = fd.fast_install_app(myappId, [deviceId]) 
                fd.fast_start_app(myappId)
            if simulation_counter() > 15000:
                print("NOT ABLET TO REDEPLOY APPLICATION: ", dep)
                break

    fallimenti.append(fallimento)
    iteration_end = simulation_counter()
    iteration_count.append(iteration_end)
    print("{:02d}) iter_count: {:d} (mean: {:f}) - fails: {:d} (mean: {:f})".format(simulation_count, 
                                                                            iteration_end, 
                                                                            sum(iteration_count)/float(len(iteration_count)), 
                                                                            fallimento, 
                                                                            sum(fallimenti)/float(len(fallimenti))
                                                                            ))
print("STARTING FIRSTFIT PHASE")
###########################################################################################
#                                   FIRSTFIT                                              #
###########################################################################################
fallimenti = []
iteration_count = []
for simulation_count in range(0, 15):
    if os.environ.get('SKIP_FIRST', None) != None:
        break
    start = time.time()
    reset_simulation("FIRST"+str(simulation_count))
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myappId = fd.create_myapp(localapp["localAppId"], dep)

        deviceIp, deviceId = firstFit(100, 32)
        
        code, res = fd.fast_install_app(myappId, [deviceId])
        trial = 0
        while code == 400:
            trial += 1
            if simulation_counter() > 15000:
                print("INSTALLED ONLY ", myapp_index, "in 15000")
            fallimento += 1
            deviceIp, deviceId = firstFit(100, 32)
            code, res = fd.fast_install_app(myappId, [deviceId])
        
        fd.fast_start_app(myappId)

    while simulation_counter() < 15000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dep = alert["appName"]
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                _, app_det = fd.get_myapp_details(dep)
                myappId = app_det["myappId"]
                fd.fast_stop_app(myappId)
                fd.fast_uninstall_app(myappId, alert["deviceId"])
                deviceIp, deviceId = firstFit(100, 32)
                code, _ = fd.fast_install_app(myappId, [deviceId]) 
                while code == 400:
                    if simulation_counter() > 15000:
                        break
                    fallimento += 1
                    deviceIp, deviceId = firstFit(100, 32)
                    code, _ = fd.fast_install_app(myappId, [deviceId])
                if simulation_counter() > 15000:
                    break
                fd.fast_start_app(myappId)
    
    fallimenti.append(fallimento)
    iteration_end = simulation_counter()
    iteration_count.append(iteration_end)
    print("{:02d}) iter_count: {:d} (mean: {:f}) - fails: {:d} (mean: {:f})".format(simulation_count, 
                                                                            iteration_end, 
                                                                            sum(iteration_count)/float(len(iteration_count)), 
                                                                            fallimento, 
                                                                            sum(fallimenti)/float(len(fallimenti))
                                                                            ))