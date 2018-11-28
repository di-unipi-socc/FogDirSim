from modules.APIWrapper import FogDirector
from modules import costants

fg = FogDirector("127.0.0.1:5000")
fg.authenticate("admin", "admin_123")

# Adding devices
_, device = fg.add_device("10.10.20.51", "cisco", "cisco")
fg.add_device("10.10.20.52", "cisco", "cisco")

# Uploading Application
fg.add_app("../tests/NettestApp2V1_lxc.tar.gz", publish_on_upload=True)

# Creating myapp endpoint
_, localapps = fg.get_apps()
app = localapps["data"][0]
localAppId = app["localAppId"]
myappname = "FirstMyApp"
_, myapp = fg.create_myapp(localAppId, myappname)

# Deploying on Device with default resources
code, res = fg.install_app(myappname, device["ipAddress"])
while code == 400:
    code, res = fg.install_app(myappname, device["ipAddress"])

fg.start_app(myappname)
_, alerts = fg.get_alerts()
for alert in alerts:
    if alert["type"]== costants.FEW_CPU or alert["type"] == costants.FEW_MEM:
        # There is a QOS violation for the application alert["myAppId"]
        _, myapp = fg.get_myapp_details(myappId=alert["myappId"])
        fg.stop_app(myappname)
        _, devices = fg.get_devices()
        job = fg.ge
        for device in devices:
            if device["deviceId"] == alert["deviceId"]:
                fg.uninstall_app(myappname, device["ipAddress"])
        _, devices = fg.get

