from flask import Flask, request, make_response, Response
from flask_restful import Api, Resource, reqparse
import time, json, os, yaml, io
import tarfile
from werkzeug.utils import secure_filename
from constants import queue

file_error_string = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                            <error>
                                <code>1308</code>
                                <description>Given app package file is invalid: Unsupported Format</description>
                            </error>'''
def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(["gz", "tar"])

class Applications(Resource):
    # /api/v1/appmgr/localapps/upload
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("x-publish-on-upload", location="headers")
        args = parser.parse_args()
        file = request.files['file']
        if 'file' not in request.files or request.files["file"].filename == '' or not (file and allowed_file(file.filename)):
            # Thank you CISCO for returning an XML here...
            return  file_error_string, 400, {"Content-Type": "application/xml"} # TODO: resolve output, not XML but string now
        filename = secure_filename(file.filename)
        uploadDir = "./fileApplication"
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        path = os.path.join(uploadDir, filename)
        file.save(path)

        identifier = queue.add_for_processing(("Applications", "post"), args, request, uploadDir, filename)
        return queue.get_result(identifier)

    # /api/v1/appmgr/localapps/<appid>:<appversion>
    def put(self, appURL):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        args = parser.parse_args()
        data = request.json 
        identifier = queue.add_for_processing(("Applications", "put"), args, data, appURL)
        return queue.get_result(identifier)

    # /api/v1/appmgr/apps/<appid> <-- WTF? Why apps and not localapps?!!! CISCOOOOO!!!!
    def delete(self, appURL):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument('x-unpublish-on-delete', location='headers')
        args = parser.parse_args()
        identifier = queue.add_for_processing(("Applications", "delete"), args, appURL)
        return queue.get_result(identifier)

    
    # /api/v1/appmgr/localapps/ Undocumented but works!
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('x-token-id', location='headers')
        parser.add_argument("limit")
        args = parser.parse_args()
        identifier = queue.add_for_processing(("Applications", "get"), args)
        return queue.get_result(identifier)
