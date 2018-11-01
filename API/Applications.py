from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json, os, yaml, io
from werkzeug.utils import secure_filename
import tarfile

#importing Database
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Database as db

class Applications(Resource):

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(["gz", "tar"])

    # /api/v1/appmgr/localapps/upload
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            if 'file' not in request.files or request.files["file"].filename == '':
                # Thank you CISCO for returning an XML here...
                return  """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                            <error>
                                <code>1308</code>
                                <description>Given app package file is invalid: Unsupported Format</description>
                            </error>""", 400, {"ContentType": "application/xml"}
            file = request.files['file']
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                uploadDir = "./fileApplication"
                if not os.path.exists(uploadDir):
                    os.makedirs(uploadDir)
                file.save(os.path.join(uploadDir, filename))
                
                # Extracting file
                os.chdir(uploadDir)

                tmpDir = str(hash(filename)) 
                if not os.path.exists(tmpDir):
                    os.makedirs(tmpDir)
                
                if (filename.endswith("tar.gz")):
                    tar = tarfile.open(filename, "r:gz")
                    os.chdir(tmpDir)
                    tar.extractall()
                    tar.close()
                elif (filename.endswith("tar")):
                    tar = tarfile.open(filename, "r:")
                    os.chdir(tmpDir)
                    tar.extractall()
                    tar.close()
                
                # Opening YAML Description of the application
                with open("package.yaml", 'r') as stream:
                    app_data = yaml.load(stream)
                os.chdir("../")
                
                appID = str(db.addLocalApplication(int(time.time()), int(time.time()), app_data))
                os.rename(tmpDir, appID)

                os.chdir("../")

                return {
                    "icon": {
                        "caption": "icon",
                        "href": "api/v1/appmgr/localapps/"+str(appID)+":1/icon"
                    },
                    "images": [],
                    "packages": [
                        {
                            # TODO: What is the second ID?
                            "href": "api/v1/appmgr/localapps/"+str(appID)+":1/packages/5ee94405-ae7b-4dcf-abc8-5e35813a993b"
                        }
                    ],
                    "creationDate": int(time.time()),
                    "descriptor": {
                        "descriptor-schema-version": app_data["descriptor-schema-version"],
                        "info": app_data["info"],
                        "app": app_data["app"]
                    },
                    "signed": False,
                    "_links": {
                        "icon": {
                            "href": "api/v1/appmgr/localapps/"+appID+":1/icon"
                        },
                        "images": {
                            "href": "api/v1/appmgr/localapps/"+appID+":1/images"
                        },
                        "packages": {
                            "href": "api/v1/appmgr/localapps/"+appID+":1/packages"
                        },
                        "configuration": {
                            "href": "api/v1/appmgr/localapps/"+appID+":1/config"
                        },
                        "self": {
                            "href": "api/v1/appmgr/localapps/"+appID+":1"
                        }
                    },
                    "localAppId": appID,
                    "version": app_data["info"]["version"],
                    "name": app_data["info"]["name"],
                    "description": {
                        "contentType": "text",
                        "content": app_data["info"]["description"]
                    },
                    "releaseNotes": {
                        "contentType": "text"
                    },
                    "appType": app_data["app"]["type"],
                    "categories": [],
                    "published": False,
                    "services": [],
                    "profileNeeded": app_data["app"]["resources"]["profile"],
                    "cpuUsage": 0,
                    "memoryUsage": 0,
                    "classification": "APP",
                    "properties": []
                }, 200, {"ContentType": "application/json"}

            #if application already exists
            return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                    <error>
                        <code>1316</code>
                        <description>An app with the same deployId already exists. Please make sure that the first forty characters of the app do not match with any of the existing apps.</description>
                    </error>
                """, 409, {"ContentType": "application/xml"}
        else:
            return self.invalidToken()

    # /api/v1/appmgr/localapps/<appid>:<appversion>
    def put(self, appid, appversion):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json 
        if db.checkToken(args["x-token-id"]):
            print "DA IMPLEMENTARE"
        return {"VERIFICARE"}, 200, {"ContentType": "application/json"}

    # /api/v1/appmgr/apps/<appid> <-- WTF? Why apps and not localapps?!!! CISCOOOOO!!!!
    def delete(self, appid):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument('x-unpublish-on-delete', location='headers') # TODO manage this feature
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            if args["x-unpublish-on-delete"] == None:
                app = db.getLocalApplication(appid)
                if app == None:
                    return "", 200 # Yes, it returns 200 even if the application doesn't exists
                if app["published"]:
                    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                                <error>
                                    <code>1303</code>
                                    <description>App NettestApp2 is in use: Unable to delete apps with name NettestApp2
                                As app with name NettestApp2 and version1 is in published state</description>
                            </error>""", 400, {"ContentType": "application/xml"}
            db.deleteLocalApplication(appid)
            return "", 200
        else:
            return self.invalidToken()

    
    # /api/v1/appmgr/localapps/ Undocumented but works!
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("limit")
        args = parser.parse_args()
        if db.checkToken(args["x-token-id"]):
            data = {"data": []}
            apps = db.getLocalApplications()
            for app in apps:
                app_props = app["data"]
                data["data"].append(
                    {
                        "icon": {
                            "caption": "icon",
                            "href": None
                        }, 
                        "images": [],
                        "packages": [
                            {
                                "href": "api/v1/appmgr/localapps/%s:1/packages/e0c9d17e-05a5-4253-a0c9-55e8a6da12c6" % str(app["_id"])
                            }
                        ],
                        "creationDate": app["creationDate"],
                        "lastUpdatedDate": app["lastupdateTime"],
                        "descriptor": {
                            "descriptor-schema-version": app_props["descriptor-schema-version"],
                            "info": app_props["info"],
                            "app": app_props["app"]
                        },
                        "signed": app["signed"],
                        "localAppId": str(app["_id"]),
                        "version": app_props["info"]["version"],
                        "name": app_props["info"]["name"],
                        "description": {
                            "contentType": "text",
                            "content":  app_props["info"]["description"]
                        },
                        "releaseNotes": {
                            "contentType": "text"
                        },
                        "appType": app_props["app"]["type"],
                        "categories": [],
                        "vendor": "",
                        "published": app["published"],
                        "services": [],
                        "profileNeeded": app_props["app"]["resources"]["profile"],
                        "cpuUsage": app["cpuUsage"],
                        "memoryUsage": app["memoryUsage"],
                        "classification": "APP",
                        "properties": []
                        }
                )
            return data, 200, {"ContentType": "application/json"}

    @staticmethod
    def invalidToken():
        return {"code":1703,"description":"Session is invalid or expired"}, 401, {'ContentType':'application/json'} 
