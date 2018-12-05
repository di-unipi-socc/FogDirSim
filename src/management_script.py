from modules.APIWrapper import FogDirector
from modules import costants
import time

fg = FogDirector("10.10.20.50", ssl=True)
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
print code
print res
while code == 400:
    code, res = fg.install_app(myappname, ["10.10.20.51"])

code, res = fg.install_app(myappname, ["10.10.20.52"])
print res
while code == 400:
    code, res = fg.install_app(myappname, ["10.10.20.52"])

fg.start_app(myappname)

import sys
sys.exit()

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
