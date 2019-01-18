from misc.MagicalQueue import MagicalQueue
from API_executor import Alerts, Applications, Audit, Authentication, Devices, DevicesEvents, Jobs, MyApps, MyAppsAction, TaggingDevices, Tags
from flask import Flask

def methodGetter(moduleName, functionName, *args, **kwargs):
    method = getattr(globals()[moduleName], functionName)
    return method(*args, **kwargs)

queue = MagicalQueue(methodGetter)
flaskApp = Flask(__name__)