import requests
import json
import base64

# Suppressing all warning given by the unverified http requestes
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FogDirector():
    def __init__(self, ip, port=80, ssl=False):
        self.ip = ip
        self.port = port
        self.ssl = ssl

    def authenticate(self, username,password):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/tokenservice" % self.ip
        else:
            url = "http://%s/api/v1/appmgr/tokenservice" % self.ip
        r = requests.post(url,auth=(username,password),verify=False)
        if  r.status_code == 202:
            self.token = r.json()['token']
        else:
            return (401, "Invalid Token")
        return (202, self.token)

    def delete_token(self, token):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/tokenservice/%s" % (self.ip, token)
        else:
            url = "http://%s/api/v1/appmgr/tokenservice/%s" % (self.ip, token)
        headers = {'x-token-id': self.token,'content-type': 'application/json'}
        r = requests.delete(url,headers=headers,verify=False)
        if  r.status_code != 200:
            return (r.status_code, r.raise_for_status())
        return (200, r.json() )

    def add_device(self, device_ip, device_user, device_psw, device_port = 8443):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/devices" % self.ip
        else:
            url = "http://%s/api/v1/appmgr/devices" % self.ip
        headers = {'x-token-id':self.token,'content-type': 'application/json'}
        data = {'port':device_port,'ipAddress':device_ip,'username':device_user,'password':device_psw}
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        if  r.status_code != 201:
            return (r.status_code, r.raise_for_status())
        return (201, r.json())

    def delete_device(self, device_id):
        headers = {'x-token-id':self.token, 'content-type': 'application/json'}
        if self.ssl:
            url = "https://%s/api/v1/appmgr/devices/%s" % (self.ip, str(device_id))
        else:
            url = "http://%s/api/v1/appmgr/devices/%s" % (self.ip, str(device_id))
        r=requests.delete(url, headers=headers, verify=False)
        if  r.status_code != 200:
            return (r.status_code, r.raise_for_status())
        return (200, r.json())

    def get_devices(self, limit=10000, offset=0, searchByAnyMatch=None, searchByTags=None):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/devices?offset=%d&limit=%d" % (self.ip, offset, limit)
        else:
            url = "http://%s/api/v1/appmgr/devices?offset=%d&limit=%d" % (self.ip, offset, limit)
        if(searchByTags != None):
            url += "&searchByTags=%s" % searchByTags
        if(searchByAnyMatch != None):
            url += "&searchByAnyMatch=%s" % searchByAnyMatch
        headers = {'x-token-id':self.token}
        r=requests.get(url,headers=headers,verify=False)
        return (200, r.json())

    def get_device_details(self, deviceip):
        code, devices = self.get_devices(searchByAnyMatch=deviceip)
        return (code, devices['data'][0])

    def delete_all_devices(self, limit=10000, offset = 0):
        devices = self.get_devices()
        for device in devices[1]['data']:
            deviceId = device['deviceId']
            r = self.delete_device(deviceId)
            if r[0] != 200:
                return (500, "Error on removing device %s" % deviceId)
        return (200, "All devices deleted")

    def add_app(self, app_file, publish_on_upload = False):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/localapps/upload" % self.ip
        else:
            url = "http://%s/api/v1/appmgr/localapps/upload" % self.ip
        headers = {'x-token-id': self.token}
        if publish_on_upload:
            headers["x-publish-on-upload"] = "true"
        r = requests.post(url, headers=headers, files={'file': open(app_file,'rb')}, verify=False)                      
        if  r.status_code != 201:
            return (r.status_code, r.text)
        return (r.status_code, r.json())

    # Returns all the tags from apps
    def get_all_tags(self):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/tags/" % self.ip
        else:
            url = "http://%s/api/v1/appmgr/tags/" % self.ip
        headers = {'x-token-id': self.token}
        r=requests.get(url,headers=headers,verify=False)
        tags= json.loads((json.dumps(r.json())))
        result = []
        for index in range(len(tags['data'])):
            tag_id=tags['data'][index]['tagId']
            tag_name=tags['data'][index]['name']
            result.append((tag_id, tag_name))
        return (200, result)

    def get_localapp_details(self, localappName=None, localappId=None, search_limit=100):
        if localappId == None and localappName == None:
            return (400, "Specify at least one parameter")
        if self.ssl:
            url = "https://%s/api/v1/appmgr/localapps?limit=%d" % (self.ip, search_limit)
        else:
            url = "http://%s/api/v1/appmgr/localapps?limit=%d" % (self.ip, search_limit)
        headers = {'x-token-id': self.token}
        r = requests.get(url,headers=headers,verify=False)
        apps=r.json()
        if localappName != None:
            for app in apps['data']:
                if localappName == app['name']:
                    return (200, app)
        if localappId != None:
            for app in apps['data']:
                if localappId == app['localAppId']:
                    return (200, app)
        return (404, [])

    def get_myapp_details(self, myapp_name):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (self.ip, myapp_name)
        else:
            url = "http://%s/api/v1/appmgr/myapps?searchByName=%s" % (self.ip, myapp_name)
        headers = {'x-token-id': self.token}
        r=requests.get(url,headers=headers,verify=False)
        return (200, r.json())

    def create_myapp(self, localAppId, myappname, version=1):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps" % self.ip
        else:
            url = "http://%s/api/v1/appmgr/myapps" % self.ip
        headers = {'x-token-id': self.token,'content-type': 'application/json'}
        data = {"appSourceType":"LOCAL_APPSTORE"}
        data["name"] = myappname
        data["sourceAppName"] = localAppId+":"+str(version)
        data["version"] = version
        r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
        if r.status_code != 201:
            return (r.status_code, r.raise_for_status())
        return (201, r.json())

    def is_myapp_present(self, app_name):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (self.ip, app_name)
        else:
            url = "http://%s/api/v1/appmgr/myapps?searchByName=%s" % (self.ip, app_name)
        headers = {'x-token-id': self.token}
        r=requests.get(url,headers=headers,verify=False)
        if r.json() == {}:
            return (200, False)
        else:
            return (200, True)


    def install_app(self, appname, devicesip, resources={"resources":{"profile":"c1.tiny","cpu":100,"memory":32,"network":[{"interface-name":"eth0","network-name":"iox-bridge0"}]}}):
        _, myapp_present = self.is_myapp_present(appname)
        if myapp_present != True :
            return (404, "You have to create the myapp first")
        _, myapp_details = self.get_myapp_details(appname)
        
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        else:
            url = "http://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        headers = {'x-token-id': self.token,'content-type': 'application/json'}
        askedResources = resources
        data = {"deploy":{"config":{},"metricsPollingFrequency":"3600000","startApp":True,"devices":[]}}
        
        for devip in devicesip:
            _, device_details = self.get_device_details(devip)
            data["deploy"]["devices"].append({"deviceId":device_details['deviceId'], "resourceAsk":askedResources})
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        return (r.status_code, r.json())

    def uninstall_app(self, appname, deviceip):
        _, myapp_details = self.get_myapp_details(appname)
        _, device_details = self.get_device_details(deviceip)
        url="http://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        headers = {'x-token-id': self.token,'content-type': 'application/json'}
        data = {"undeploy":{"devices":[-1]}}
        data["undeploy"]["devices"][0] = device_details['deviceId']
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        return (200, r.json())

    def stop_app(self, appname):
        _, myapp_details = self.get_myapp_details(appname)
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        else:
            url = "http://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        headers = {'x-token-id': self.token, "content-type": "application/json"}
        data = {"stop":{}}
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        return (200, r.json())

    def start_app(self, appname):
        _, myapp_details = self.get_myapp_details(appname)
        if self.ssl:
            url = "https://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        else:
            url = "http://%s/api/v1/appmgr/myapps/%s/action" % (self.ip, myapp_details['myappId'])
        headers = {'x-token-id': self.token,'content-type': 'application/json'}
        data = {"start":{}}
        r = requests.post(url,data=json.dumps(data),headers=headers,verify=False)
        return (200, r.json())

    def get_apps(self, limit=100):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/localapps?limit=%d" % (self.ip, limit)
        else:
            url = "http://%s/api/v1/appmgr/localapps?limit=%d" % (self.ip, limit)
        headers = {'x-token-id': self.token}
        r = requests.get(url, headers = headers,verify=False)
        apps=r.json()
        return (200, apps)
  
    def get_alerts(self):
        if self.ssl:
            url = "https://%s/api/v1/appmgr/alerts/" % (self.ip)
        else:
            url = "http://%s/api/v1/appmgr/alerts/" % (self.ip)
        headers = {"x-token-id": self.token}
        r = requests.get(url, headers=headers, verify=False)
        alerts = r.json()
        return (r.status_code, alerts)

    def get_jobs(self):
        # emh... buona fortuna... non esiste...
        pass