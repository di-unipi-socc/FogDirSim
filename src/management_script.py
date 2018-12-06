from modules.APIWrapper import FogDirector
from modules import costants
import time

fg = FogDirector("127.0.0.1:5000")
code = fg.authenticate("admin", "admin_123")
if code == 401:
    print "Failed Authentication"

# Adding devices
_, device = fg.add_device("10.10.20.51", "cisco", "cisco")
fg.add_device("10.10.20.52", "cisco", "cisco")

# Uploading Application
code, text = fg.add_app("../tests/NettestApp2V1_lxc.tar.gz", publish_on_upload=True)
if code != 201:
    print text

# Creating myapp endpoint
_, localapps = fg.get_apps()
app = localapps["data"][0]
localAppId = app["localAppId"]
myappname = "FirstMyApp"
_, myapp = fg.create_myapp(localAppId, myappname)

# Deploying on Device with default resources
code, res = fg.install_app(myappname, ["10.10.20.51"])
while code == 400:
    code, res = fg.install_app(myappname, ["10.10.20.51"])

code, res = fg.install_app(myappname, ["10.10.20.52"])
while code == 400:
    code, res = fg.install_app(myappname, ["10.10.20.52"])

fg.start_app(myappname)

#import sys
#sys.exit()

fg.add_app("../tests/TestApp2.tar.gz", publish_on_upload=True)
# Creating myapp endpoint
_, localapps = fg.get_apps()
app = localapps["data"][1]
localAppId = app["localAppId"]
myappname = "TestApp"
_, myapp = fg.create_myapp(localAppId, myappname)

time.sleep(5)

code, res = fg.install_app(myappname, ["10.10.20.52"])
while code == 400:
    code, res = fg.install_app(myappname, ["10.10.20.52"])

def otherDevice(actual):
    if actual == "10.10.20.52":
        return "10.10.20.51"
    else:
        return "10.10.20.52"

while True:
    time.sleep(5)
    _, alerts = fg.get_alerts()
    for alert in alerts["data"]:
        if 0 == alert["pagiaros_type"]:
            if alert["appName"] == "FirstMyApp":
                "stop App"
                fg.stop_app("FirstMyApp")
                "unistall App"
                fg.uninstall_app("FirstMyApp", alert["ipAddress"])
                "install App"
                fg.install_app("FirstMyApp", [otherDevice(alert["ipAddress"])])
                "start app"
                fg.start_app("FirstMyApp")
