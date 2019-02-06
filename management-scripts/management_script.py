from APIWrapper import FogDirector
import time, requests

FOG_DIRECTOR_HOST = "127.0.0.1:5000"

def reset_simulation():
    url = "http://%s/simulationreset" % "127.0.0.1:5000"
    r = requests.get(url)
    return r.json()
reset_simulation()

fd = FogDirector(FOG_DIRECTOR_HOST)
code = fd.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

# Adding devices
_, device1 = fd.add_device("10.10.20.51", "cisco", "cisco")
_, device2 = fd.add_device("10.10.20.52", "cisco", "cisco")
_, device3 = fd.add_device("10.10.20.53", "cisco", "cisco")

code, localapp = fd.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

_, myapp1 = fd.create_myapp(localapp["localAppId"], "dep1")
_, myapp2 = fd.create_myapp(localapp["localAppId"], "dep2")

# Deploying on devices with default resources, 
# that are c1.small profile, defined by custom library
code, res = fd.install_app("dep1", ["10.10.20.51"])
while code == 400:
    code, res = fd.install_app("dep1", ["10.10.20.51"])

code, res = fd.install_app("dep2", ["10.10.20.52"])
while code == 400:
    code, res = fd.install_app("dep2", ["10.10.20.52"])

fd.start_app("dep1")
fd.start_app("dep2")

def otherDevice(current):
    return "10.10.20.51" if current == "10.10.20.52" else "10.10.20.52"


moved1 = False
while True:
    _, alerts = fd.get_alerts()
    for alert in alerts["data"]:
        if "APP_HEALTH" == alert["type"]: # Device issues
            if alert["appName"] == "dep1" and not moved1:
                print("migrating dep1")
                fd.stop_app("dep1")
                fd.uninstall_app("dep1", alert["ipAddress"])
                code, _ = fd.install_app("dep1", ["10.10.20.53"]) 
                while code == 400:
                    code, _ = fd.install_app("dep1", ["10.10.20.53"]) 
                fd.start_app("dep1")
                moved1 = True
            elif alert["appName"] == "dep2":
                print("migrating dep2 from", alert["ipAddress"],"to",otherDevice(alert["ipAddress"]))
                fd.stop_app("dep2")
                code, _ = fd.uninstall_app("dep2", alert["ipAddress"])
                if code != 200:
                    print("uninstalling returns", code)
                code, _ = fd.install_app("dep2", [otherDevice(alert["ipAddress"])])
                print("Install returns", code)
                while code == 400:
                    fd.install_app("dep2", [otherDevice(alert["ipAddress"])])
                    print("Install returns", code)
                code, _ = fd.start_app("dep2")