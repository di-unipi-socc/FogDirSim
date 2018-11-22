import json
def test_publish_function(response):
    data = response.json()["data"][0]
    data["published"] = True
    return {"app_data": json.dumps(data), "localAppId": data["localAppId"], "localAppVersion": data["version"]}

def test_notpublish(response):
    data = response.json()
    return data["published"] == False

def checkIp10102051(response):
    data = response.json()
    devices = data["data"]
    for dev in devices:
        if dev["ipAddress"] == "10.10.20.51":
            return True
    return False

def checkIp10102051nodata(response):
    dev = response.json()
    if dev["ipAddress"] == "10.10.20.51":
        return True
    return False

def getdeviceid(response):
    data = response.json()
    devices = data["data"]
    for dev in devices:
        if dev["ipAddress"] == "10.10.20.51":
            return {"deviceId": str(dev["deviceId"])}

def getAppdetails(response):
    app = response.json()
    return {"appname": app["name"], "localAppId": app["localAppId"], "sourceAppName": app["localAppId"]+":"+app["version"], "version": app["version"], "appSourceType": "LOCAL_APPSTORE"}

def getdevicedetails(response):
    data = response.json()
    dev = data["data"][0]

def getMyAppId(response):
    data = response.json()
    return {"myAppId": str(data["myappId"])}

def getDeviceId(response):
    data = response.json()
    return {"deviceId": str(data["deviceId"])}

def print_(response):
    print response
    return {}