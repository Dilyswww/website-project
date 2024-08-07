# A Blueprint is a way to organize a group of related views and other code. 
# The authentication blueprint will have views to register new users and to log in and log out.

import functools
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for   
)


# creates a Blueprint named 'auth'
bp = Blueprint('auth', __name__, url_prefix = '/auth')

# associates the URL /register with the register view function
# If the user submitted the form, request.method will be 'POST'
# request.form is a special type of dict mapping submitted form keys and 
# values. The user will input their username and password.
@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
    
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
            
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('auth.login'))
            
        # flash() stores messages that can be retrieved when rendering the template.
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # fetchone() returns one row from the query.
        # If the query returned no results, it returns None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username, try again'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password, try again'
            
        if error is None:
            # session is a dict that stores data across requests. 
            # When validation succeeds, the user’s id is stored in a new session.
            session.clear()
            session.user_id = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')

# registers a function that runs before the view function, 
# no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    """
    checks if a user id is stored in the session and gets that user’s data from the database
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        
        
# remove the user id from the session to log out
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
        
def login_required(view):
    """
    decorator, returns a new view function that wraps the original view it’s applied to
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view