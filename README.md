# FogDirSimulator

These lines try to simulate Fog Director in order to prevent you to put in production an application that will destroy your infrastructure.
<center>
![Home Screenshot](https://github.com/alessandro308/FogDirSimulator/blob/master/docs/img/home_screen_video.gif?raw=true)
</center>
## How it works?
It simulates Fog Director giving the same [API of Fog Director](https://developer.cisco.com/docs/iox/#!fog-director-api-documentation/cisco-fog-director-rest-api) but executing all the operation only on a Database instead of on your infrastructure.

This simulator loads the infrastructure from a given Database (a.k.a. RealDatabase). 

## Run an example
### Install the tool
In order to install this tool you have to copy this repository and install the requirements:
```
git clone https://github.com/alessandro308/FogDirSimulator
pip3 install requirements.txt
```
The tool use a MongoDB instance to keep trace of the simulation status. You can run it in a container:
```
docker run -d --name some-mongo -e MONGO_INITDB_ROOT_USERNAME=YourName -e MONGO_INITDB_ROOT_PASSWORD=YourPassword -v $PWD/mongodb:/data/db -p 27017:27017 mongo
```
### Configure the tool
In order to be run, you have to specify the database connection configuration. Create a file called `SECRETS.py` in `/src` folder and insert the configuration values following the `SECRETS_demo.py` file format.

### Define the infrastructure
In order to define your infrastructure (i.e. devices avaialable, resources distribution, chaos parameters) you have to edit `RealDatabase.py` script. This script is executed at the start and populate the database used to read devices specs at runtime. You can use the devices example or defining your own devices. In order to add a device you have to insert some code lines like:
```python
db.Rdevices.insert_one({ 
                "ipAddress": "10.10.20."+str(deviceId),
                "port": 8443,
                "deviceId": deviceId,
                "totalCPU": 1700,
                "totalVCPU": 2,
                "maxVCPUPerApp": 2,
                "totalMEM": 512,
                "chaos_down_prob": 0,
                "chaos_revive_prob": 1,
                "distributions": { 
                    "CPU": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24, 
                            "mean": 1500,
                            "deviation": 78
                        }
                    ],
                    "MEM": [
                        {
                            "timeStart": 0,
                            "timeEnd": 24,
                            "mean": 300,
                            "deviation": 10
                        }
                    ]
                }
            })
```
### Execute the simulator
You are now ready to start the tool, move in the tool folder and start python scripts:
```
cd FogDirSimulator
python3 src
```

Start your management script / execute your API calls by hand, as you prefer. Open your browser at `http://localhost:5000/` and see your results! Enjoy!

## Available API (in progress)
All the API not reported here, are not available yet.

###### Authentication
 - `POST /api/v1/appmgr/tokenservice` To create a new token
    - Use this function to create a new token. A username and password have to be passed as basic HTTP Authentication. For the moment, these credential are hardcoded (admin, admin_123) and the token is not checked by other functions. 
 - `DELETE /API/v1/appmgr/tokenservice/<token>` To delete a valid token
    - Delete the token passed in the URL from the valid tokens. This function needs `x-token-id` field in the header to be executed

###### Devices
 - `POST /api/v1/appmgr/devices` To add a new device
    - Add a device to infrastructure. It requires a json data in the body with the following schema: `{ "port":8880, "ipAddress":"1.1.1.1", "username":"admin", "password":"test_psw"}`
 - `GET /api/v1/appmgr/devices?limit=100&offset=0&searchByTags=ciccio&searchByAnyMatch=123.12.1.2` To get devices from the database (all parameters are optionals)
    - Returns all the devices inserted. The output JSON is `{"data": [{device1}, {device2} ...]}`

###### Tags
 - `POST /api/v1/appmgr/tags` - To add a new tag to tag library
    - Create a new tag. It is not assigned to any device. It requires to pass data as JSON: `{"name": "tagname"}`
 - `GET /api/v1/appmgr/tags` - To get all tags from tag library
    - Returns all tags created in the system, with their ids
 - `POST /api/v1/appmgr/tags/<tagid>/devices` - To add a tag to selected devices (devices are provided as json data)
    - Tag a device with a specific tag. The tag is passed in URL, the device instead in the body as JSON array: `{"devices":[deviceids]}}`

###### Local Applications
 - `POST /api/v1/appmgr/localapps/upload` - To add an application from a file 
    - Use this function to upload an application. It must have a `package.yaml` file formatted as required for the IOX Application. This API accepts the following headers: `x-publish-on-upload`
 - `PUT /api/v1/appmgr/localapps/<appid>:<appversion>` - To update the application metadata, e.g. published status
    - Update an application (i.e. publish it, change description...). The original API requires to have all the field returned by the GET API, this API accepts also only the changed field. The `<appversion>` can be omitted, in that case its value becomes 1.
 - `DELETE /api/v1/appmgr/apps/<appid>` - To delete the application (it have to be uninstalled from every device)
    - Delete an application passing its `<appid>` in the URL. This API accepts the following headers: `x-unpublish-on-delete`. If `x-unpublish-on-delete` is not specified, its values is `false`.
 - `GET /api/v1/appmgr/localapps/` - Get all the app (published and unpublished)

###### MyApps (deployments)
 - `POST /api/v1/appmgr/myapps` - Before you can install an unpublished app on a device by using the API, you must create a myapp endpoint for the app. This API requires the following data: `{"name":appname,"sourceAppName":"c36d727c-e9c5-46ed-bc7e-cbdd5cf49786:1.0","version":"1.0","appSourceType":"LOCAL_APPSTORE"}` (in this simulator only `LOCAL_APPSTORE` type is supported)
 - `DELETE /api/v1/appmgr/myapps/<myappid>` - Delete the myapp endpoint. If the myapp is installed on some device, an error is returned.
 - `GET /api/v1/appmgr/myapps?searchByName=name` - Returns a JSON object that contains the `myappId` given the `myappName` (Not yet implemented) 

###### MyApps actions
 - `POST /api/v1/appmgr/myapps/<myappid>/action` - Use this API to modify the state of the `<myappid>` myapp. 
 For example, in order to deploy the app, you have to use the following JSON in the request data field:
 ```json
{
  "deploy": {
    "config": {
      
    },
    "metricsPollingFrequency": "3600000",
    "startApp": true,
    "devices": [
      {
        "deviceId": "DEVICE_TO_INSTALL",
        "resourceAsk": {
          "resources": {
            "profile": "c1.tiny",
            "cpu": 100,
            "memory": 32,
            "network": [
              {
                "interface-name": "eth0",
                "network-name": "iox-bridge0"
              }
            ]
          }
        }
      }
    ]
  }
}
 ```
 or, in order to *start* (respectivily, *stop*) myapp, you have to use the following Json object in the data field:
 ```json
 {"start":{}}
 ```
###### Device Events
 - `GET /api/v1/appmgr/devices/<devid>/events/` - Since FogDirector doesn't have a properly documented API, we assume some events type taken from the FogDirector Manual.

###### Application Events (Audit)
 - `GET /api/v1/appmgr/audit` - provides information about app state change events, who performed them, when they were performed and what the operation was. These audit information can be filtered by device serial id, by app and version or even by the user who performed it (but the official documentation doesn't report the exact name to use this filters then the filters are not implemented).
 This API supports* the following URL parameter:
    - `limit`
    - `offset`
    - `searchByAction`

###### Alerts
 - `GET /api/v1/appmgr/alerts` - provides the alerts about the infrastructure and applications status

###### NOT YET IMPLEMENTED
 - `/api/v1/appmgr/devices/<devid>/apps/<myappdid>/logs` 
 - The Audit API is not fully supported

## Tested functions
In order to run the tests, execute `PYTHONPATH=$PYTHONPATH:tests py.test`

All the tests are run over the Simulator AND Fog Director. They succeed in both systems.
 - Simple login and logout
 - Add a device
 - Try to add an already inserted device
 - Delete a device
 - Get a device by its IP address
 - Upload, then delete an application
 - Upload, then publish an application
 - Get the applications present in the system
 - Delete a local application (with and without `x-unpublish-on-delete`)
 - Add a tag
 - Try to add an already inserted tag
 - Tag a device
 - Published LocalApp
 - Created new Deployment (myapp)
 - Installed/Uninstalled an application on a device

## Infrastructure
In order to be executed, this simulator requires the infrastructure on which the operation has to be simulated.
The Infrastructure is composed by:
 - Devices
    The collection `devices` describes the devices of the infrastructure, identified by `IP` and `PORT`. Additional information required are: 
    - `totalCPU`: the maximum CPU available on the device
    - `totalMEM`: the maximum Memory available on the device
    - `totalVCPU`: the amount of Virtual CPU on the device
    - `maxVCPUPerApp`: the maximum number of VCPU for application
    - `distribution.CPU`: an array that contains the distribution of *free* CPU used with time references (`timeStart`-`timeEnd` identify the time when this distribution have to be considered valid. The interval `0-24` have to be covered adding all the time slices) 
    - `distribution.MEM`: an array that contains the distribution of MEM used with time references 

    JSON rappresentation of a generic device:
    ```json
        {
            "ipAddress": "10.10.20.51",
            "port": 8443,
            "totalCPU": 1000,
            "totalMEM": 128,
            "distributions": { 
                "CPU": [ 
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 2.4,
                        "deviation": 3 
                    }
                ],
                "MEM": [
                    {
                        "timeStart": 0,
                        "timeEnd": 24,
                        "mean": 45,
                        "deviation": 2
                    }
                ]
            }
        }
    ```

## Limitations / Main differences from Fog Director
 - The simulator doesn't manage multi versions applications. Each application is identified by an ID that is unique among all others application and versions (then in `/api/v1/appmgr/localapps/<appid>:<appversion>` the version is ignored).
 - In the PUT `/api/v1/appmgr/localapps/<appid>:<appversion>` API, also not completed description of application is accepted. In Fog Director this "partial body" returns an error.
 - When a new device is added, all the information on the device are returned (the discovery phase is not simulated)
 - The device events names type are assumed from the manual and they should not be as FogDirector types
 - Some IDs that are interger in FogDirector, in the simulator are strings.
 - Only one user is admitted (`admin` user, `admin123` password)
 - This simulator does not manage Network Interfaces Resources
 - Some API are created over documentation, the logic is understood looking at the Sandbox responses (/jobs, /myapps)
 - Simulator doens't check SHA1 in package.yaml of localapp
 - On simulator you can start or stop the myapp. On GUI you can start or stop the myapp on a specific device (even if there exists API that supports the other behaviour)

## Assumptions and simplifications
 - The management is done by a single user (no multi-user management)
 - All the operations are atomically and are computed once for every simulation run
 - We assume that for every myapps only one deploy can be done. It simplifies the simulation and monitoring system but not reduce the possible states of the tool. This good practice is also implicitely suggested using the GUI.
 - We don't model the things (serial/remote) binding 
 - We don't model the network since FD doesn't
 - There is no correlations among samplings and no correlation between resources usages

## I know that I know nothing. (Socrates)
 - We don't know how to manage a case where, deploying an application on multiple devices, one of them has no resources
 - We don't know if a single Myapp can be deployed twice on a device
 - We don't know WHY GET /myapps returns an array but, with searchByName parameter returns a single element
 - I don't understand how this badly designed tool can be used in a production environment
 - Why exists the `job` definition
