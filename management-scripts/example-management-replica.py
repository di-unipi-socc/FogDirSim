from APIWrapper import FogDirector
import time, random, math
from infrastructure import ciscorouter_size300 as infrastructure

infrastructure.create()

fg = FogDirector("127.0.0.1:5000")
code = fg.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

DEVICES_NUMBER = 5
DEPLOYMENT_NUMBER = 30
    # Adding devices
for i in range(0, DEVICES_NUMBER):
    deviceId = i+1      
    _, device1 = fg.add_device("10.10.20."+str(deviceId), "cisco", "cisco")

# Uploading Application
code, localapp = fg.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)


for myapp_index in range(0, DEPLOYMENT_NUMBER):
    # Creating myapp1 endpoint
    dep = "dep"+str(myapp_index)
    _, myapp1 = fg.create_myapp(localapp["localAppId"], dep)

    # first installation
    r = random.random()
    deviceIp = "10.10.20."+str(math.floor(r*DEVICES_NUMBER) + 1)

    code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
    while code == 400:
        print("*** Cannot deploy to the building router. Try another ***")
        r = random.random()
        deviceIp = "10.10.20."+str(math.floor(r*DEVICES_NUMBER)+1)
        code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
    print("DEPLOYED", dep, "ON", deviceIp)
    # second installation
    r = random.random()
    deviceIp = "10.10.20."+str(math.floor(r*DEVICES_NUMBER) + 1)
    fg.start_app(dep)

for myapp_index in range(0, int(DEPLOYMENT_NUMBER/2)):
    # Creating myapp1 endpoint
    dep = "dep"+str(myapp_index)
    _, myapp1 = fg.create_myapp(localapp["localAppId"], dep)
    
    code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
    while code == 400:
        print("*** Cannot deploy to the building router. Try another ***")
        r = random.random()
        deviceIp = "10.10.20."+str(math.floor(r*DEVICES_NUMBER)+1)
        code, res = fg.install_app(dep, [deviceIp], resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}})
    print("DEPLOYED", dep, "ON", deviceIp)
    fg.start_app(dep)