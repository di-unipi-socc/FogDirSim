from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import time, json, os, yaml, io
from werkzeug.utils import secure_filename
import tarfile

import sqlite3
conn = sqlite3.connect('FogDirSim.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS applications
             (appname text, appID text, version int, creationTime text, lastupdateTime text, proprieties text, cpuUsage int, memoryUsage int, published int, signed int)''')
            # 0             1               2           3                   4                       5               6               7               8           9
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

    # /api/v1/appmgr/localapps/upload
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
                c.execute('''INSERT INTO applications (appname, appID, proprieties, version, creationTime, lastupdateTime) \
                            VALUES ('%s', '%s', '%s', '%s', '%s', '%s')''' % (app_data["info"]["name"],
                                                                                 appID,
                                                                                 json.dumps(app_data),
                                                                                 app_data["info"]["version"],
                                                                                 int(time.time()),
                                                                                 int(time.time()) ) )
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
    
    # /api/v1/appmgr/localapps/<appid>:<appversion>
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
                SET proprieties=%s, lastupdateTime=%s
                WHERE appID='%s' AND version=%s 
            """ % (json.dumps(data), int(time.time()), appid, appversion) )
            conn.commit()
            conn.close()
        return {"VERIFICARE"}, 200, {"ContentType": "application/json"}

    # /api/v1/appmgr/apps/<appid> <-- WTF? Why apps and not localapps?!!! CISCOOOOO!!!!
    def delete(self, appid):
        # TODO In order to delete the app, it must be unistalled from any devices
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
    
    # /api/v1/appmgr/localapps/ Undocumented but works!
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("limit")
        args = parser.parse_args()
        if self.valid(args["x-token-id"]):
            data = {"data": []}
            conn = sqlite3.connect('FogDirSim.db')
            c = conn.cursor()
            c.execute('''SELECT * FROM applications LIMIT %s''' % (100 if args["limit"] == None else args["limit"]))
            rows = c.fetchall()
            conn.close()
            for app in rows:
                app_props = json.loads(app[5])
                data["data"].append(
                    {
                        "icon": {
                            "caption": "icon",
                            "href": None
                        }, 
                        "images": [],
                        "packages": [
                            {
                                "href": "api/v1/appmgr/localapps/%s:1/packages/e0c9d17e-05a5-4253-a0c9-55e8a6da12c6" % app[1]
                            }
                        ],
                        "creationDate": app[3],
                        "lastUpdatedDate": app[4],
                        "descriptor": {
                            "descriptor-schema-version": app_props["descriptor-schema-version"],
                            "info": app_props["info"],
                            "app": app_props["app"]
                        },
                        "signed": app[9],
                        "localAppId": app[1],
                        "version": app[2],
                        "name": app[0],
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
                        "published": False if app[8] == 0 else True,
                        "services": [],
                        "profileNeeded": app_props["app"]["resource"]["profile"],
                        "cpuUsage": app[6],
                        "memoryUsage": app[7],
                        "classification": "APP",
                        "properties": []
                        }
                )
            return data, 200, {"ContentType": "application/json"}

        