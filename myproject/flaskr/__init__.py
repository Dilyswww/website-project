import os
from flask import Flask

def create_app(test_confit = None):
    # create and configure the app
    # name: The name of the current Python module. This is needed so that Flask knows where to look for templates, static files, and so on.
    # instance_relative_config=True: tells the app that configuration files are relative to the instance folder.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',   
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return "Hello, World!"
    
    return app