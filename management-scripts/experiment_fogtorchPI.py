from APIWrapper import FogDirector
import time, random, math, os
from infrastructure import ciscorouters_30pz_5b5m20s as infrastructure
import requests
import simplejson, signal, array
from collections import defaultdict

port = os.environ.get('SERVER_PORT', "5000")

infrastructure.create()

def simulation_counter():
    r = requests.get('http://localhost:'+port+'/result/simulationcounter')
    return int(r.text)

def dev_list_sort(dev_list):
    dev_list.sort(reverse=True, key=(lambda val: (val[1], val[2], val[0])))
    return dev_list
def device(deviceList, deviceId):
    for x in deviceList:
        if x[0] == deviceId:
            return x
    return None
def incrementresources(deviceList, deviceId, new_cpu, new_mem):
    for x in deviceList:
        if x[0] == deviceId:
            x[1] += new_cpu
            x[2] += new_mem
            return deviceList
    return deviceList

def fog_torch():
    values = defaultdict(lambda: array.array("f", [0, 0]))
    MAX_ITER = 200
    for _ in range(0, MAX_ITER):
        _, devices = fd.get_devices()
        for dev in devices["data"]:
            values[dev["deviceId"]][0] = dev["capabilities"]["nodes"][0]["cpu"]["available"]
            values[dev["deviceId"]][1] = dev["capabilities"]["nodes"][0]["memory"]["available"]
    dev_list = []
    for k in values:
        dev_list.append([k, values[k][0]/MAX_ITER, values[k][1]/MAX_ITER])
    dev_list = dev_list_sort(dev_list)
    return dev_list

previous_simulation = []

def reset_simulation(current_identifier):
    url = "http://%s/simulationreset" % ("127.0.0.1:"+port)
    r = requests.get(url)
    output = r.json()
    previous_simulation.append({
        current_identifier: output
    })
    file  = open("simulation_results_firstFit.txt", "a")
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

fallimenti = []
iteration_count = []

print("STARTING FOGTORCH PHASE")
###########################################################################################
#                                   FOGTORCH                                              #
###########################################################################################
for simulation_count in range(0, 15):
    if os.environ.get('SKIP_BEST', None) != None:
        break
    start = time.time()
    reset_simulation(simulation_count)
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    dev_list = fog_torch()
    dev_list = dev_list_sort(dev_list)
    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        if 
        if DEPLOYMENT_NUMBER % 200 == 0:
            dev_list = fog_torch()
            dev_list = dev_list_sort(dev_list)
        else:
            dev_list = dev_list_sort(dev_list)
            
        dep = "dep"+str(myapp_index)
        _, myappId = fd.create_myapp(localapp["localAppId"], dep)
        
        deviceId = dev_list[0][0]
        code, res = fd.fast_install_app(myappId, [deviceId])
        if code != 400:
            dev_list[0][1] -= 100
            dev_list[0][2] -= 32
        while code == 400:
            fallimento += 1
            deviceId = dev_list[0][0]
            code, res = fd.fast_install_app(myappId, [deviceId])
            if code != 400:
                dev_list[0][1] -= 100
                dev_list[0][2] -= 32
        fd.fast_start_app(myappId)

    while simulation_counter() < 15000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dev_list = dev_list_sort(dev_list)
                dep = alert["appName"]
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                _, app_det = fd.get_myapp_details(dep)
                myappId = app_det["myappId"]
                fd.fast_stop_app(myappId)
                fd.fast_uninstall_app(myappId, alert["deviceId"])
                dev_list = incrementresources(dev_list, alert["deviceId"], 100, 32)
                dev_list = dev_list_sort(dev_list)
                deviceId = dev_list[0][0]
                code, res = fd.fast_install_app(myappId, [deviceId])
                if code != 400:
                    dev_list[0][1] -= 100
                    dev_list[0][2] -= 32
                code, _ = fd.fast_install_app(myappId, [deviceId])
                while code == 400:
                    fallimento += 1
                    code, res = fd.fast_install_app(myappId, [deviceId])
                    if code != 400:
                        dev_list[0][1] -= 100
                        dev_list[0][2] -= 32
                    code, _ = fd.fast_install_app(myappId, [deviceId]) 
                print("migrating", dep, "from", alert["ipAddress"], "to", deviceId)
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
