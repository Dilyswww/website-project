import os
from flask import Flask


def create_app(test_config = None):
    """
    Create and configure an instance of the Flask application.
    """
    # name: The name of the current Python module. This is needed so that Flask knows where to look for templates, static files, and so on.
    # instance_relative_config=True: tells the app that configuration files are relative to the instance folder.
    app = Flask(__name__, instance_relative_config = True)
    
   
    app.config.from_mapping( # set default configuration
        SECRET_KEY='dev',    # used by Flask and extensions to keep data safe
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        # overrides the default configuration with values taken from the config.py file in the instance folder if it exists.
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
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    print("App created and route registered")
    return app