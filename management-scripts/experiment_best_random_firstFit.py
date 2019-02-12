from APIWrapper import FogDirector
import time, random, math, os
from infrastructure import ciscorouters_20pz_5b5m10s as infrastructure
import requests
import simplejson, signal

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
        if simulation_counter() > 10000:
            print("Not able to find a bestfit. Simulation ends")
            exit()
        _, devices = fd.get_devices()
        devices = [ dev for dev in devices["data"] if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu 
                                    and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem]
        devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"], 
                                                        dev["capabilities"]["nodes"][0]["memory"]["available"]) ))
    best_fit = devices[0]
    return best_fit["ipAddress"]

def randomFit():
    _, devices = fd.get_devices()
    r = random.randint(0, len(devices["data"]) - 1)
    return devices["data"][r]["ipAddress"]

def firstFit(cpu, mem): 
    while simulation_counter() < 10000:
        _, devices = fd.get_devices()
        for dev in devices["data"]:
            if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem:
                return dev["ipAddress"]

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

print("STARTING BESTFIT PHASE")
###########################################################################################
#                                   BESTFIT                                               #
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

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myapp1 = fd.create_myapp(localapp["localAppId"], dep)

        deviceIp = bestFit(100, 32)
        code, res = fd.install_app(dep, [deviceIp])
        while code == 400:
            if simulation_counter() > 10000:
                print("NOT ABLET TO REDEPLOY APPLICATION: ", dep)
                exit()
            fallimento += 1
            deviceIp = bestFit(100, 32)
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

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
                fd.stop_app(dep)
                fd.uninstall_app(dep, alert["ipAddress"])
                new_device = bestFit(100, 32)
                code, _ = fd.install_app(dep, [new_device]) 
                while code == 400:
                    fallimento += 1
                    if simulation_counter() > 10000:
                        print("NOT ABLET TO REDEPLOY APPLICATION: ", dep)
                        exit()
                    new_device = bestFit(100, 32)
                    code, _ = fd.install_app(dep, [new_device]) 
                print("migrating", dep, "from", alert["ipAddress"], "to", new_device)
                fd.start_app(dep)
    
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
    reset_simulation(simulation_count)
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myapp1 = fd.create_myapp(localapp["localAppId"], dep)

        deviceIp = randomFit()
        code, res = fd.install_app(dep, [deviceIp])
        trial = 0
        while code == 400:
            trial += 1
            if simulation_counter() < 5000:
                print("NOT ABLET TO DEPLOY ALL APPLICATIONs. Deployed number: ", myapp_index)
                exit()
            fallimento += 1
            deviceIp = randomFit()
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

    while simulation_counter() < 10000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dep = alert["appName"]
                
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                fd.stop_app(dep)
                fd.uninstall_app(dep, alert["ipAddress"])
                new_device = randomFit()
                code, _ = fd.install_app(dep, [new_device]) 
                while code == 400:
                    fallimento += 1
                    if simulation_counter() > 10000:
                        print("NOT ABLET TO REDEPLOY APPLICATION: ", dep)
                        exit()
                    new_device = randomFit()
                    code, _ = fd.install_app(dep, [new_device]) 
                print("migrating", dep, "from", alert["ipAddress"], "to", new_device)
                fd.start_app(dep)
    
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
    reset_simulation(simulation_count)
    fallimento = 0
    for i in range(0, DEVICES_NUMBER):
        deviceId = i+1      
        _, device1 = fd.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

    # Uploading Application
    code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

    for myapp_index in range(0, DEPLOYMENT_NUMBER):
        dep = "dep"+str(myapp_index)
        _, myapp1 = fd.create_myapp(localapp["localAppId"], dep)

        deviceIp = firstFit(100, 32)
        code, res = fd.install_app(dep, [deviceIp])
        trial = 0
        while code == 400:
            trial += 1
            if simulation_counter() > 10000:
                print("NOT ABLET TO DEPLOY ALL APPLICATIONs. Deployed number: ", myapp_index)
                exit()
            fallimento += 1
            deviceIp = firstFit(100, 32)
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

    while simulation_counter() < 10000:
        _, alerts = fd.get_alerts()
        migrated = []
        for alert in alerts["data"]:
            if "APP_HEALTH" == alert["type"]: 
                dep = alert["appName"]
                if dep in migrated:
                    continue
                else:
                    migrated.append(dep)
                fd.stop_app(dep)
                fd.uninstall_app(dep, alert["ipAddress"])
                new_device = firstFit(100, 32)
                code, _ = fd.install_app(dep, [new_device]) 
                while code == 400:
                    if simulation_counter() > 10000:
                        print("NOT ABLET TO REDEPLOY APPLICATION: ", dep)
                        exit()
                    fallimento += 1
                    new_device = firstFit(100, 32)
                    code, _ = fd.install_app(dep, [new_device]) 
                print("migrating", dep, "from", alert["ipAddress"], "to", new_device)
                fd.start_app(dep)
    
    fallimenti.append(fallimento)
    iteration_end = simulation_counter()
    iteration_count.append(iteration_end)
    print("{:02d}) iter_count: {:d} (mean: {:f}) - fails: {:d} (mean: {:f})".format(simulation_count, 
                                                                            iteration_end, 
                                                                            sum(iteration_count)/float(len(iteration_count)), 
                                                                            fallimento, 
                                                                            sum(fallimenti)/float(len(fallimenti))
                                                                            ))