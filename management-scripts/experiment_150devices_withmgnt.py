from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouters_310pz_5b5m300s_withFails as infrastructure
import requests
import simplejson, signal, os
from collections import defaultdict
import array

infrastructure.create()

port = os.environ.get('SERVER_PORT', "5000")
fd = FogDirector("127.0.0.1:"+port)
code = fd.authenticate("admin", "admin_123")


def simulation_counter():
    r = requests.get('http://localhost:'+port+'/result/simulationcounter')
    return int(r.text)

def bestFit(cpu, mem):
    _, devices = fd.get_devices()
    devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                            and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
    devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    trial = 0
    while len(devices) == 0:
        trial += 1
        if trial == 100:
            return None, None
        _, devices = fd.get_devices()
        devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                                    and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
        devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                        dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    best_fit = devices[0]
    return best_fit["ipAddress"], best_fit["deviceId"]

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


def reset_simulation():
    url = "http://%s/simulationreset" % ("127.0.0.1:"+port)
    r = requests.get(url)
    output = r.json()
    try:
        file  = open("simulation_results_failure.txt", "a")
        file.write("# corrected dev and myapps number - Devices: "+str(DEVICE_NUMBER)+" - # Deployments: "+str(DEPLOYMENT_NUMBER)+"\n")
        file.write("\""+str(DEVICE_NUMBER)+"\"{")
        out = simplejson.dumps(output, indent=4, sort_keys=True)
        file.write(out)
        file.write("},\n\n")
        file.close()
    except NameError:
        pass

def add_devices():
    for i in range(1, DEVICE_NUMBER+1):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

def install_apps():
    for i in range(0, DEPLOYMENT_NUMBER):
        try:
            dep = "dep"+str(i)
            _, myappId = fd.create_myapp(localapp["localAppId"], dep)

            deviceIp, deviceId = bestFit(100, 32)
            if deviceIp == None:
                return i
            r = random.random()
            code, res = fd.fast_install_app(myappId, [deviceId], profile="normal")
            trial = 0
            while code == 400:
                trial += 1
                if trial == 100:
                    return i
                deviceIp, deviceId = bestFit(100, 32)
                code, res = fd.fast_install_app(myappId, [deviceId])
            fd.fast_start_app(myappId)
        except KeyboardInterrupt:
            print(i)
            return i
    return DEPLOYMENT_NUMBER

def install_apps_FT():
    dev_list = fog_torch()
    dev_list = dev_list_sort(dev_list)
    for myapp_index in range(0, DEPLOYMENT_NUMBER):
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
            code, res = fd.fast_install_app(myappId, [deviceId])
            if code != 400:
                dev_list[0][1] -= 100
                dev_list[0][2] -= 32
        fd.fast_start_app(myappId)

def install_apps_ft():
    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dev_list = dev_list_sort(dev_list)
            
        dep = "dep"+str(myapp_index)
        _, myappId = fd.create_myapp(localapp["localAppId"], dep)
        
        deviceId = dev_list[0][0]
        r = random.random()
        if r < 0.5:
            code, res = fd.fast_install_app(myappId, [deviceId], profile="angry")
        else:
            code, res = fd.fast_install_app(myappId, [deviceId], profile="normal")
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

reset_simulation()
for DEVICE_NUMBER in [35, 50, 70]:
    DEPLOYMENT_NUMBER = 150
    print("STARTING ", DEVICE_NUMBER, DEPLOYMENT_NUMBER)
    add_devices()
    code, localapp = fd.add_app("./TestApp_tiny.tar.gz", publish_on_upload=True)
    installed_apps = install_apps_FT()
    while simulation_counter() < 3000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"] or "DEVICE_REACHABILITY" == alert["type"]: 
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
                    if simulation_counter() > 3000:
                        break
                    deviceIp, deviceId = bestFit(100, 32)
                    code, _ = fd.fast_install_app(myappId, [deviceId]) 
                fd.fast_start_app(myappId)
    reset_simulation()

reset_simulation()