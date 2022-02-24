import json
import os
from flask import Flask, make_response, request
import base64

from RouteOptimization import getAllClusterPaths
from image_recognition import verify_AWB
from werkzeug.utils import secure_filename

from image_recognition import verify_location


def create_app():
    UPLOAD_FOLDER = "server/images"
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    @app.route('/hello')
    def index():
        return 'hi travelling ninja'
    
    # @app.route('/getAllClusters')
    # def getAllClusters():
    #     res = make_response(json.dumps(getAllClusterPaths()))
    #     res.headers.add("Access-Control-Allow-Origin", "*")
    #     return res
    
    @app.route('/verifyAWB', methods=['POST'])
    def verifyAWB():
        print("hello")
        print(request.files)
        if request.method == 'POST':
            if 'image' not in request.files:
                return 'No files'
        file = request.files['image']
        if file.filename == '': 
            return 'Empty file name'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('hello2')
        res = verify_AWB(app.config['UPLOAD_FOLDER'] + "/" + filename)
        res = make_response((res))
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Credentials", "true")
        res.headers.add("Access-Control-Allow-Methods", "GET, POST")
        res.headers.add("Access-Control-Allow-Headers", "*" )
        print('hello3')
        # print(res)
        return res
    
    @app.route('/verifyLocation', methods=['POST'])
    def verifyLocation():
        if request.method == 'POST':
            if 'image' not in request.files:
                return 'No files'
        file = request.files['image']
        if file.filename == '':
            return 'Empty file name'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        res = verify_location(app.config['UPLOAD_FOLDER'] + "/" + filename)
        res = make_response(json.dumps(res))
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res
    
    return app