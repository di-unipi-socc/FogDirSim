from flask import Flask
from flask_restful import Api, Resource, reqparse
from FogDirSimModules.Authentication import Authentication
from FogDirSimModules.Devices import Devices
from FogDirSimModules.TaggingDevices import TaggingDevices
from FogDirSimModules.Tags import Tags
from FogDirSimModules.Applications import Applications

app = Flask(__name__)
api = Api(app)

api.add_resource(Devices, "/api/v1/appmgr/devices")
api.add_resource(Authentication, "/api/v1/appmgr/tokenservice")
api.add_resource(Tags, "/api/v1/appmgr/tags")
api.add_resource(TaggingDevices, "/api/v1/appmgr/tags/<tagid>/devices")
api.add_resource(Applications, "/api/v1/appmgr/localapps/upload")
api.add_resource(Applications, "/api/v1/appmgr/localapps/<appid>:<appversion>")
api.add_resource(Applications, "/api/v1/appmgr/apps/<appid>")
app.run(debug=True)