import json
from flask import Flask, make_response, request

from RouteOptimization import getAllClusterPaths

def create_app():
    app = Flask(__name__)
    
    @app.route('/hello')
    def index():
        return 'hi travelling ninja'
    
    @app.route('/getAllClusters')
    def getAllClusters():
        res = make_response(json.dumps(getAllClusterPaths()))
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res
    
    return app