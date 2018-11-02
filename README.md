# FogDirSimulator

These lines try to simulate Fog Director in order to prevent you to put in production an application that will destroy your infrastructure.

## How it works?
It simulates Fog Director giving the same [API of Fog Director](https://developer.cisco.com/docs/iox/#!fog-director-api-documentation/cisco-fog-director-rest-api) but executing all the operation only on a Database instead of on your infrastructure.

#### Available API (in progress)
A better (incomplete in this moment) documentation can be found [here](https://documenter.getpostman.com/view/2935895/RzZ4p2B7)

###### Authentication
 - `POST /api/v1/appmgr/tokenservice` To get a new token
    - Use this function to get a new token. A username and password have to be passed as basic HTTP Authentication. For the moment, these credential are hardcoded (admin, admin_123). 
 - `DELETE /api/v1/appmgr/tokenservice/<token>` To delete a valid token
    - Delete the token passed in the URL from the valid tokens. This function needs `x-token-id` field in the header to be executed

###### Devices
 - `POST /api/v1/appmgr/devices` To add a new device
 - `GET /api/v1/appmgr/devices?limit=100&offset=0&searchByTags=ciccio&searchByAnyMatch=123.12.1.2` To get devices from the database (all parameters are optionals)

###### Tags
 - `POST /api/v1/appmgr/tags` - To add a new tag to tag library
 - `GET /api/v1/appmgr/tags` - To get all tags from tag library
 - `POST /api/v1/appmgr/tags/<tagid>/devices` - To add a tag to selected devices (devices are provided as json data)

###### Local Applications
 - `POST /api/v1/appmgr/localapps/upload` - To add an application from a file 
 - `PUT /api/v1/appmgr/localapps/<appid>:<appversion>` - To update the application metadata, e.g. published status
 - `DELETE /api/v1/appmgr/apps/<appid>` - To delete the application (it have to be uninstalled from every device)
 - `GET /api/v1/appmgr/localapps/` - Get all the app (published and unpublished)

## In progress
This is the first project where I use MongoDB. Please, report any mistake on the NoSQL paradigm!

## Limitations
 - The simulator not manages multiversion application. Each application is identified by an ID that is unique among all others application:versions.