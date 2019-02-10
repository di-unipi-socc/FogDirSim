from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouters_50pz_50m as infrastructure
import requests
import simplejson, signal

infrastructure.create()

fd = FogDirector("127.0.0.1:5000")
code = fd.authenticate("admin", "admin_123")

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
            return None
        _, devices = fd.get_devices()
        devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                                    and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
        devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                        dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    best_fit = devices[0]
    return best_fit["ipAddress"]

def reset_simulation():
    url = "http://%s/simulationreset" % "127.0.0.1:5000"
    r = requests.get(url)
    output = r.json()
    try:
        file  = open("simulation_results_uptimeVSmyappsnumber_3.txt", "a")
        file.write("# Devices: "+str(DEVICE_NUMBER)+" - # Deployments: "+str(DEPLOYMENT_NUMBER)+" - # Successfully Installed: "+str(installed_apps)+"\n")
        del output["uptime_history"]
        out = simplejson.dumps(output, indent=4, sort_keys=True)
        file.write(out)
        file.write("\n\n")
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
            _, myapp = fd.create_myapp(localapp["localAppId"], dep)

            deviceIp = bestFit(100, 32)
            if deviceIp == None:
                return i
            code, res = fd.install_app(dep, [deviceIp])
            trial = 0
            while code == 400:
                trial += 1
                if trial == 100:
                    return i
                deviceIp = bestFit(100, 32)
                code, res = fd.install_app(dep, [deviceIp])
            fd.start_app(dep)
        except KeyboardInterrupt:
            print(i)
            return i
    return DEPLOYMENT_NUMBER

reset_simulation()
for DEVICE_NUMBER in range(35, 45, 5):
    for DEPLOYMENT_NUMBER in range(10, 300, 10):
        print(DEVICE_NUMBER, DEPLOYMENT_NUMBER)
        add_devices()
        code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)
        installed_apps = install_apps()
        reset_simulation()
        if installed_apps < DEPLOYMENT_NUMBER:
            break
        wait = 2000
        while wait > 0:
            fd.get_alerts()
            wait -= 1