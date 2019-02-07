from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouters_10pz_5m10s as infrastructure
import requests
import simplejson, signal

infrastructure.create()

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
            print("BESTFIT is not able to find a device (100 trial reached)")
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
    _, devices = fd.get_devices()
    for dev in devices["data"]:
        if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem:
            return dev["ipAddress"]
    firstFit(cpu, mem)

previous_simulation = []
def service_shutdown(*args):
    print('\nOh, ok, I will print the simulation result.Byeee!')
    reset_simulation("shutdown")
    file_name = input("\nFilename to save simulation result: ")
    file  = open(file_name, "w")
    file.write(simplejson.dumps(simplejson.loads(previous_simulation), indent=4, sort_keys=True))
    file.write("\n\n")
    file.close()
    exit()

signal.signal(signal.SIGINT, service_shutdown)

def reset_simulation(current_identifier):
    url = "http://%s/simulationreset" % "127.0.0.1:5000"
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
url = "http://%s/simulationreset" % "127.0.0.1:5000"
r = requests.get(url)
print("STARTING SIMULATION")

fd = FogDirector("127.0.0.1:5000")
code = fd.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

DEVICES_NUMBER = 15
DEPLOYMENT_NUMBER = 110

fallimenti = []
iteration_count = []

print("STARTING BESTFIT PHASE")
###########################################################################################
#                                   BESTFIT                                               #
###########################################################################################
for simulation_count in range(0, 20):
    break
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
        trial = 0
        while code == 400:
            trial += 1
            if trial == 50:
                print(DEPLOYMENT_NUMBER, "are too high value to deploy. (50 fails reached)")
                exit()
            fallimento += 1
            deviceIp = bestFit(100, 32)
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

    r = requests.get('http://localhost:5000/result/simulationcounter')
    iteration_end = int(r.text)
    fallimenti.append(fallimento)
    iteration_count.append(iteration_end)
    print(simulation_count, ") Iter_count:", iteration_end, "(mean:", sum(iteration_count)/len(iteration_count), ") - fails", fallimento, "(mean ", sum(fallimenti)/float(len(fallimenti)), ")")

print("STARTING RANDOM PHASE")
###########################################################################################
#                                   RANDOMFIT                                             #
###########################################################################################
fallimenti = []
iteration_count = []
for simulation_count in range(0, 20):
    break
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
            if trial == 50:
                print(DEPLOYMENT_NUMBER, "applications are too high value to deploy. (50 fails reached)")
                exit()
            fallimento += 1
            deviceIp = randomFit()
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

    r = requests.get('http://localhost:5000/result/simulationcounter')
    iteration_end = int(r.text)
    fallimenti.append(fallimento)
    iteration_count.append(iteration_end)
    print(simulation_count, ") Iter_count:", iteration_end, "(mean:", sum(iteration_count)/len(iteration_count), ") - fails", fallimento, "(mean ", sum(fallimenti)/float(len(fallimenti)), ")")

print("STARTING FIRSTFIT PHASE")
###########################################################################################
#                                   FIRSTFIT                                              #
###########################################################################################
fallimenti = []
iteration_count = []
for simulation_count in range(0, 20):
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
            if trial == 50:
                print(DEPLOYMENT_NUMBER, " applications are too high value to deploy. (50 fails reached)")
                exit()
            fallimento += 1
            deviceIp = firstFit(100, 32)
            code, res = fd.install_app(dep, [deviceIp])
        fd.start_app(dep)

    r = requests.get('http://localhost:5000/result/simulationcounter')
    iteration_end = int(r.text)
    fallimenti.append(fallimento)
    iteration_count.append(iteration_end)
    print(simulation_count, ") Iter_count:", iteration_end, "(mean:", sum(iteration_count)/len(iteration_count), ") - fails", fallimento, "(mean ", sum(fallimenti)/float(len(fallimenti)), ")")
