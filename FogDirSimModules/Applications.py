from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json, os, yaml, io
from werkzeug.utils import secure_filename
import tarfile

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS applications
             (appname text, appID text, version int, proprieties text)''')
conn.commit()
conn.close()

class Applications(Resource):

    @staticmethod
    def valid(token):
        return True

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(["gz", "tar"])

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        if self.valid(args["x-token-id"]):
            if 'file' not in request.files or request.files["file"].filename == '':
                return  """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                            <error>
                                <code>1308</code>
                                <description>Given app package file is invalid: Unsupported Format</description>
                            </error>""", 400, {"ContentType": "application/xml"}
            file = request.files['file']
            print self.allowed_file(file.filename)
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                uploadDir = "./fileApplication"
                if not os.path.exists(uploadDir):
                    os.makedirs(uploadDir)
                file.save(os.path.join(uploadDir, filename))
                
                # Extracting file
                os.chdir(uploadDir)

                appID = str(hash(filename)) # hash became application ID and directory name of application file
                if not os.path.exists(appID):
                    os.makedirs(appID)
                
                if (filename.endswith("tar.gz")):
                    tar = tarfile.open(filename, "r:gz")
                    os.chdir(appID)
                    tar.extractall()
                    tar.close()
                elif (filename.endswith("tar")):
                    tar = tarfile.open(filename, "r:")
                    os.chdir(appID)
                    tar.extractall()
                    tar.close()
                
                # Opening YAML Description of the application
                with open("package.yaml", 'r') as stream:
                    app_data = yaml.load(stream)
                
                os.chdir("../../")

                # Adding app to DB
                conn = sqlite3.connect('FogDirSim.db')
                c = conn.cursor()
                c.execute('''INSERT INTO applications (appname, appID, proprieties, versione) \
                            VALUES ('%s', '%s', '%s', '%s')''' % (app_data["info"]["name"],
                                                                                 appID,
                                                                                 json.dumps(app_data),
                                                                                 app_data["info"]["version"]) )
                conn.commit()
                conn.close()
                
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
    
    def put(self, appid, appversion):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json 
        if self.valid(args["x-token-id"]):
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            c.execute("""
                UPDATE application
                SET proprieties=%s
                WHERE appID='%s' AND version=%s 
            """, json.dumps(data), appid, appversion)
            conn.commit()
            conn.close()
        return {"VERIFICARE"}, 200, {"ContentType": "application/json"}

    def delete(self, appid):
        # In order to delete the app, it must be unistalled from any devices
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument('x-unpublish-on-delete', location='headers') # TODO manage this feature
        args = parser.parse_args()
        if self.valid(args["x-token-id"]):
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            c.execute("""
               DELETE FROM applications 
                WHERE appID='%s'
            """, appid)
            conn.commit()
            conn.close()
        