from flask import Flask

def create_app():
    app = Flask(__name__)
    
    @app.route('/api/hello')
    def index():
        return 'hi travelling ninja'
    
    return app