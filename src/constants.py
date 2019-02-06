SAMPLE_INTERVAL = 1
current_infrastructure = {}

DEVICE_CRITICAL_CPU = 1
DEVICE_CRITICAL_MEM = 2
DEVICE_DOWN = 3
DEVICE_CPU_USED = 4
DEVICE_MEM_USED = 5
DEVICE_MYAPP_COUNT = 6

MYAPP_INSTALLED = 4
MYAPP_UNINSTALLED = 5
MYAPP_STATUS = 6
JOB_STARTED = 7
JOB_STOPPED = 8
JOB_STATUS = 9
APP_ON_DEVICE = 10
APP_ON_DEVICE_WITH_NO_RESOURCES_CPU = 11
APP_ON_DEVICE_WITH_NO_RESOURCES_MEM = 12

MYAPP_PROFILE_LOW = "relax"
MYAPP_PROFILE_NORMAL = "normal"
MYAPP_PROFILE_HIGH = "angry"

# Alerts Type
APP_HEALTH = "APP_HEALTH" # App is corrupted on a the device or ***has some other issue with its health***. 
DEVICE_REACHABILITY = "DEVICE_REACHABILITY"
MYAPP_CPU_CONSUMING = "MYAPP_CPU_CONSUMING"
MYAPP_MEM_CONSUMING = "MYAPP_MEM_CONSUMING"

from misc.MagicalQueue import MagicalQueue
from flask import Flask
def methodGetter(moduleName, functionName, *args, **kwargs):
    method = getattr(globals()[moduleName], functionName)
    return method(*args, **kwargs)

queue = MagicalQueue(methodGetter)
flaskApp = Flask(__name__, static_folder="sim-gui/build/static")


from API_executor import Alerts, Applications, Audit, Authentication, Devices, DevicesEvents, Jobs, MyApps, MyAppsAction, TaggingDevices, Tags


