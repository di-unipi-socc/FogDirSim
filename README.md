# FogDirSimulator

These lines try to simulate Fog Director in order to prevent you to put in production an application that will destroy your infrastructure.

## How it works?
It simulates Fog Director giving the same [API of Fog Director](https://developer.cisco.com/docs/iox/#!fog-director-api-documentation/cisco-fog-director-rest-api) but executing all the operation only on a Database instead of on your infrastructure.

This simulator loads the infrastructure from a given Database (a.k.a. RealDatabase). 

#### Available API (in progress)
All the API not reported here, are not available yet.

###### Authentication
 - `POST /api/v1/appmgr/tokenservice` To create a new token
    - Use this function to create a new token. A username and password have to be passed as basic HTTP Authentication. For the moment, these credential are hardcoded (admin, admin_123) and the token is not checked by other functions. 
 - `DELETE /api/v1/appmgr/tokenservice/<token>` To delete a valid token
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
    - Update an application (i.e. publish it, change description...). The original API requires to have all the field returned by the GET API, this API accepts also only the changed field. The `<appversion>` can be omitted, in that case its value becames 1.
 - `DELETE /api/v1/appmgr/apps/<appid>` - To delete the application (it have to be uninstalled from every device)
    - Delete an application passing its `<appid>` in the URL. This API accepts the following headers: `x-unpublish-on-delete`. If `x-unpublish-on-delete` is not specified, its values is `false`.
 - `GET /api/v1/appmgr/localapps/` - Get all the app (published and unpublished)

## Tested functions
In order to run the tests, execute `PYTHONPATH=$PYTHONPATH:test py.test`
All the tests are run over the Simulator AND Fog Director. They success on both systems.
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

## Infrastructure
In order to be executed, this simulator requires the infrastructure on which the operation have to be simulated.
The Infrastructure is composed by:
 - Devices
    The collection `devices` describes the devices of the infrastructure, identified by `IP` and `PORT`. Addictional information required are: 
    - `totalCPU`: the maximum CPU available on the device
    - `totalMEM`: the maximum Memory available on the device
    - `distribution.CPU`: an array that contains the distribution of CPU used with time references (`timeStart`-`timeEnd` identify the time when this distribution have to be consider valid. The interval `0-24` have to be covered adding all the time slices) 
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
 - The simulator doesn't manage multiversions applications. Each application is identified by an ID that is unique among all others application and versions (then in `/api/v1/appmgr/localapps/<appid>:<appversion>` the version is ignored).
 - In the PUT `/api/v1/appmgr/localapps/<appid>:<appversion>` API, also not completed description of application is accepted. In Fog Director this "partial body" returns an error.
 - When new device is added, all the information on the device are returned (the discovery phase is not simulated)
## In progress
This is the first project where I use MongoDB. Please, report any mistake on the NoSQL paradigm!

