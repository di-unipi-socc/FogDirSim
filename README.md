# FogDirSimulator

These lines try to simulate Fog Director in order to prevent you to put in production an application that will destroy your infrastructure.

## How it works?
It simulates Fog Director giving the same [API of Fog Director](https://developer.cisco.com/docs/iox/#!fog-director-api-documentation/cisco-fog-director-rest-api) but executing all the operation only on a Database instead of on your infrastructure.

#### Available API (in progress)

###### Authentication
 - `POST /api/v1/appmgr/tokenservice` To get a new token
 - `DELETE /api/v1/appmgr/tokenservice/<token>` To delete a valid token
 - `POST /api/v1/appmgr/devices` To add a new device
 - `GET /api/v1/appmgr/devices?limit=100&offset=0&searchByTags=ciccio&searchByAnyMatch=123.12.1.2` To get devices from the database (all parameters are optionals)
 - `POST /api/v1/appmgr/tags` - To add a new tag to tag library
 - `GET /api/v1/appmgr/tags` - To get all tags from tag library
 - `POST /api/v1/appmgr/tags/<tagid>/devices` - To add a tag to selected devices (devices are provided as json data)
 - `POST /api/v1/appmgr/localapps/upload` - To add an application from a file 
 - `PUT /api/v1/appmgr/localapps/<appid>:<appversion>` - To update the application metadata, e.g. published status
 - `DELETE /api/v1/appmgr/apps/<appid>` - To delete the application (it have to be uninstalled from every device)
 - `GET /api/v1/appmgr/localapps/` - Get all the app (published and unpublished)
