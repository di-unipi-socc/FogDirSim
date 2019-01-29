from APIWrapper import FogDirector
import time
from infrastructure import ciscorouter_size300 as infrastructure

#infrastructure.create()

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

# Creating myapps endpoint
dep1 = "dep1"
_, myapp1 = fg.create_myapp(localapp["localAppId"], dep1)

dep2 = "dep2"
_, myapp2 = fg.create_myapp(localapp["localAppId"], dep2)

dep3 = "dep3"
_, myapp3 = fg.create_myapp(localapp["localAppId"], dep3)

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

print("Starting Installing dep3")
code, res = fg.install_app(dep3, ["10.10.20.51"], minjobs=1)
while code == 400:
    code, res = fg.install_app(dep3, ["10.10.20.51"], minjobs=1)
code, res = fg.install_app(dep3, ["10.10.20.52"], minjobs=1)
while code == 400:
    code, res = fg.install_app(dep3, ["10.10.20.52"], minjobs=1)
print("Finished to Install dep3")

fg.start_app(dep1)
fg.start_app(dep2)
fg.start_app(dep3)

def otherDevice(actual):
    if actual == "10.10.20.52":
        return "10.10.20.53"
    else:
        return "10.10.20.52"

moved1 = False
count = 0
while True:
    count += 1
    _, alerts = fg.get_alerts()
    for alert in alerts["data"]:
        if "APP_HEALTH" == alert["simulation_type"]: #APP_HEALTH
            if alert["appName"] == "dep1" and not moved1:
                print("**Moving dep1 from 1 to 3")
                #"stop App"
                code, _ =fg.stop_app("dep1")
                print("stop_app dep1", code)
                #"unistall App"
                code, _ = fg.uninstall_app("dep1", alert["ipAddress"])
                print("uninstall dep1", code)
                #"install App"
                code, _ = fg.install_app("dep1", ["10.10.20.53"]) 
                while code == 400:
                    code, _ = fg.install_app("dep1", ["10.10.20.53"]) 
                print("app Installed on dev3")
                #"start app"
                code, _ = fg.start_app("dep1")
                print("start app dep1", code)
                moved1 = True
            elif count == 50 or alert["appName"] == "dep2":
                print("**Toggling dep2")
                code, _ = fg.stop_app("dep2")
                print("stop app dep2", code)
                code, _ = fg.uninstall_app("dep2", alert["ipAddress"])
                print("uninstall dep2 from ", alert["ipAddress"], code)
                code, _ = fg.install_app("dep2", [otherDevice(alert["ipAddress"])])
                while code == 400:
                    fg.install_app("dep2", [otherDevice(alert["ipAddress"])])

                print("installed app dep2 on", otherDevice(alert["ipAddress"]))
                code, _ = fg.start_app("dep2")
                print("started dep2 ", code)

