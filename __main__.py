from flask import Flask
from flask_restful import Api, Resource, reqparse

from API.Devices import Devices
from API.TaggingDevices import TaggingDevices
from API.Tags import Tags
from API.Applications import Applications
from API.Authentication import Authentication
import Database as db
app = Flask(__name__)
api = Api(app)

api.add_resource(Devices, "/api/v1/appmgr/devices", "/api/v1/appmgr/devices/<deviceid>")
api.add_resource(Authentication, "/api/v1/appmgr/tokenservice","/api/v1/appmgr/tokenservice/<token>")
api.add_resource(Tags, "/api/v1/appmgr/tags")
api.add_resource(TaggingDevices, "/api/v1/appmgr/tags/<tagid>/devices")
api.add_resource(Applications, "/api/v1/appmgr/localapps/upload", # POST
                               "/api/v1/appmgr/localapps/<appURL>", # PUT
                               "/api/v1/appmgr/apps/<appURL>", # DELETE
                               "/api/v1/appmgr/localapps") # GET

app.run(debug=True)

