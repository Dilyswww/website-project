import sqlite3
import click
# g is a special object that is unique for each request
# current_app is another special object that points to the Flask application handling the request
from flask import current_app, g

def get_db():
    """
    returns g.db, if not created, set it
    """
    if 'db' not in g:
        # establishes a connection to the file pointed at by the DATABASE configuration key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        # tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e = None):
    """
    checks if a connection was created by checking if g.db was set. If exists, it is closed.
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
def init_db():
    """
    Clear existing data and create new tables.
    """
    db = get_db()
    
    # opens a file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        
# defines a command line command called init-db that calls the init_db function and shows a success message to the user.   
@click.command('init-db')
def init_db_command():
    """
    Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    """
    takes an application and does the registration
    """
    # tells Flask to call that function when cleaning up after returning the response
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with the flask command
    app.cli.add_command(init_db_command)