from APIWrapper import FogDirector
import time

fg = FogDirector("127.0.0.1:5000")
code = fg.authenticate("admin", "admin_123")
if code == 401:
    print("Failed Authentication")

# Adding devices
_, device1 = fg.add_device("10.10.20.51", "cisco", "cisco")
_, device2 = fg.add_device("10.10.20.52", "cisco", "cisco")
_, device3 = fg.add_device("10.10.20.53", "cisco", "cisco")

# Uploading Application
code, localapp = fg.add_app("./NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

# Creating myapp1 endpoint
dep1 = "dep1"
_, myapp1 = fg.create_myapp(localapp["localAppId"], dep1)
# Creating myapp1 endpoint
dep2 = "dep2"
_, myapp1 = fg.create_myapp(localapp["localAppId"], dep2)

# adding a second localapp
#fg.add_app("./TestApp2.tar.gz", publish_on_upload=True)
#_, localapps = fg.get_apps()
#app = localapps["data"][1]
#localAppId = app["localAppId"]
#myappname2 = "TestApp"
#_, myapp2 = fg.create_myapp(localAppId, myappname2)

# Deploying on Devices with default resources
code, res = fg.install_app(dep1, ["10.10.20.51"])
while code == 400:
    print("*** Cannot deploy to the building router. ***")
    code, res = fg.install_app(dep1, ["10.10.20.51"])

code, res = fg.install_app(dep2, ["10.10.20.52"])
while code == 400:
    code, res = fg.install_app(dep2, ["10.10.20.52"])

fg.start_app(dep1)
fg.start_app(dep2)

def otherDevice(actual):
    if actual == "10.10.20.52":
        return "10.10.20.51"
    else:
        return "10.10.20.52"

moved1 = False
while True:
    _, alerts = fg.get_alerts()
    for alert in alerts["data"]:
        if 0 == alert["simulation_type"]: #APP_HEALTH
            if alert["appName"] == "dep1" and not moved1:
                #"stop App"
                fg.stop_app("dep1")
                #"unistall App"
                fg.uninstall_app("dep1", alert["ipAddress"])
                #"install App"
                print("Moving dep1 from 1 to 3")
                while fg.install_app("dep1", ["10.10.20.53"]) == 400:
                    continue
                #"start app"
                fg.start_app("dep1")
                moved1 = True
            elif alert["appName"] == "dep2":
                fg.stop_app("dep2")
                fg.uninstall_app("dep2", alert["ipAddress"])
                print("Toggling dep2")
                while fg.install_app("dep2", [otherDevice(alert["ipAddress"])]):
                    continue
                fg.start_app("dep2")

