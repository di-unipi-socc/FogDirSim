from APIWrapper import FogDirector 
from infrastructure import ciscorouters_310pz_5b5m300s_withFails as infrastructure
from collections import defaultdict
import array, requests, simplejson, random, os
infrastructure.create()

MAX_SIMULATION_ITER = 15000

port = "5000"
fd = FogDirector("127.0.0.1:"+port)
code = fd.authenticate("admin", "admin_123")

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

def simulation_counter():
    r = requests.get('http://localhost:'+port+'/result/simulationcounter')
    return int(r.text)
def check_termination():
    if simulation_counter() > MAX_SIMULATION_ITER:
        return True
    return False

def reset_simulation(write_file = True):
    url = "http://%s/simulationreset" % ("127.0.0.1:"+port)
    r = requests.get(url)
    output = r.json()
    if not write_file:
        return output
    file  = open("simulation_results_paper.txt", "a")
    file.write("# DEVICE_NUMBER: "+str(DEVICE_NUMBER)+" - APP_EXTRA: "+str(APP_EXTRA)+"\n")
    out = simplejson.dumps(output, indent=4, sort_keys=True)
    file.write(out)
    file.write("\n\n")
    file.close()
    return output

def add_devices():
    for i in range(1, DEVICE_NUMBER+1):
        deviceId = i+1      
        fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

def dev_list_sort(dev_list):
    dev_list.sort(reverse=True, key=(lambda val: (val[1], val[2], val[0])))
    return dev_list
def fog_torch():
    values = defaultdict(lambda: array.array("f", [0, 0]))
    MAX_ITER = 500
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

def increment_resources(deviceList, deviceId, new_cpu, new_mem):
    for x in deviceList:
        if x[0] == deviceId:
            x[1] += new_cpu
            x[2] += new_mem
            return deviceList
    return deviceList

DEPLOYMENT_NUMBER = 150
try:
    os.remove("simulation_results_paper.txt")
except FileNotFoundError:
    pass
reset_simulation(write_file=False)
for COUNTER_SIM in range(0, 5):
    file  = open("simulation_results_paper.txt", "a")
    file.write("# STARTING NEW SIMULATION EPOCH: "+str(COUNTER_SIM)+"\n")
    for DEVICE_NUMBER in range(100, 151, 10):
        for APP_EXTRA in range(150, 151, 10): # APP_EXTRA = 150
            print("DevNumber", DEVICE_NUMBER, "APP_EXTRA", APP_EXTRA)
            add_devices()
            dev_list = fog_torch()
            # Uploading Application
            code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

            for myapp_index in range(0, DEPLOYMENT_NUMBER):
                
                dev_list = dev_list_sort(dev_list)
                    
                dep = "dep"+str(myapp_index)
                _, myappId = fd.create_myapp(localapp["localAppId"], dep, minjobs=1)
                
                deviceId = dev_list[0][0]
                profile = "normal"
                r = random.random()
                if r < 0.2:
                    profile = "angry"
                code, res = fd.fast_install_app(myappId, [deviceId], profile=profile)

                device_notReachable = 0
                current_device = 0
                if code != 400:
                    dev_list[0][1] -= 100
                    dev_list[0][2] -= 32
                while code == 400:
                    if "Error" in res and res["Error"] == "Device does not reachable":
                        device_notReachable += 1
                        if device_notReachable == 10:
                            current_device += 1
                            device_notReachable = 0
                            deviceId = dev_list[current_device][0]
                    r = random.random()
                    if r < 0.2:
                        code, res = fd.fast_install_app(myappId, [deviceId], profile="angry")
                    else:
                        code, res = fd.fast_install_app(myappId, [deviceId])
                    if code != 400:
                        dev_list[current_device][1] -= 100
                        dev_list[current_device][2] -= 32

                if myapp_index < APP_EXTRA:
                    deviceId = dev_list[0][0]
                    profile = "normal"
                    r = random.random()
                    if r < 0.2:
                        profile = "angry"
                    code, res = fd.fast_install_app(myappId, [deviceId], profile=profile)

                    device_notReachable = 0
                    current_device = 0
                    if code != 400:
                        dev_list[0][1] -= 100
                        dev_list[0][2] -= 32
                    while code == 400:
                        if "Error" in res and res["Error"] == "Device does not reachable":
                            device_notReachable += 1
                            if device_notReachable == 10:
                                current_device += 1
                                device_notReachable = 0
                                deviceId = dev_list[current_device][0]
                        r = random.random()
                        if r < 0.2:
                            profile = "angry"
                        code, res = fd.fast_install_app(myappId, [deviceId], profile=profile)
                        if code != 400:
                            dev_list[current_device][1] -= 100
                            dev_list[current_device][2] -= 32

                fd.fast_start_app(myappId)
            
            offline_devices = []
            myapp_problems = defaultdict(lambda: defaultdict(lambda: 0))
            dev_unreachable_appId = defaultdict(lambda: [])
            while not check_termination():
                _, alerts = fd.get_alerts()
                migrated = []
                for alert in alerts["data"]:
                    if "APP_HEALTH" == alert["type"]: 
                        # Migrating
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
                        r = random.random()
                        profile = "normal"
                        if r < 0.2:
                            profile = "angry"
                        code, _ = fd.fast_install_app(myappId, [deviceId], profile=profile)
                        while code == 400:
                            if check_termination():
                                break
                            deviceIp, deviceId = bestFit(100, 32)
                            r = random.random()
                            profile = "normal"
                            if r < 0.2:
                                profile = "angry"
                            code, _ = fd.fast_install_app(myappId, [deviceId], profile=profile)
                        fd.fast_start_app(myappId)
                    elif "DEVICE_REACHABILITY" == alert["type"]:
                        dep = alert["appName"]
                        if dep in migrated:
                            continue
                        else:
                            migrated.append(dep)
                        _, app_det = fd.get_myapp_details(dep)
                        myappId = app_det["myappId"]
                        dev_unreachable_appId[alert["deviceId"]].append(myappId)
                        deviceIp, deviceId = bestFit(100, 32)
                        code, _ = fd.fast_install_app(myappId, [deviceId])
                        while code == 400:
                            if check_termination():
                                break
                            deviceIp, deviceId = bestFit(100, 32)
                            code, _ = fd.fast_install_app(myappId, [deviceId]) 
                        fd.fast_start_app(myappId)
                    elif "MYAPP_CPU_CONSUMING" == alert["type"]:
                        continue # QUESTA SOTTO È impossible da gestire con le API note
                        myappId = app_det["myappId"]
                        devId = alert["deviceId"]
                        myapp_problems[myappId][devId] += 1
                        if myapp_problems[myappId][devId] == 5:
                            dep = alert["appName"]
                            if dep in migrated:
                                continue
                            else:
                                migrated.append(dep)
                            _, app_det = fd.get_myapp_details(dep)
                            myappId = app_det["myappId"]
                            fd.fast_stop_app(myappId)
                            fd.fast_uninstall_app(myappId, alert["deviceId"])
                            deviceIp, deviceId = bestFit(100, 32) # BUONA FORTUNA...
                            code, _ = fd.fast_install_app(myappId, [deviceId])
                            while code == 400:
                                if check_termination():
                                    break
                                deviceIp, deviceId = bestFit(100, 32)
                                code, _ = fd.fast_install_app(myappId, [deviceId]) 
                            fd.fast_start_app(myappId)
                    elif "MYAPP_MEM_CONSUMING" == alert["type"]:
                        pass # guarda sopra e buona fortuna

                _, devices = fd.get_devices()
                for dev in devices["data"]:
                    devId = dev["deviceId"]
                    if devId in offline_devices:
                        for myappId in dev_unreachable_appId[devId]:
                            fd.fast_uninstall_app(myappId, devId)
                        dev_unreachable_appId[devId] = []
            reset_simulation()
