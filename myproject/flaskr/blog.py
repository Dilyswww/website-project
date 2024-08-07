from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    """
    show all of the posts, most recent first
    """
    db = get_db()
    # JOIN is used so that the author information from the user table is available in the result
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods = ('GET', 'POST'))
# user must be logged in to create a blog post
@login_required
def create():
    """
    create a new post for the current user
    """
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
            
        if error is None:
             flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author = True):
    """
    fetch a post by id and check if the author matches the logged in user
    """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        'FROM post p JOIN user u ON p.author_id = u.id'
        'WHERE p.id = ?',
        (id,)
    ).fetchone()
    
    if post is None:
        abort(404, f"Post id {id} does not exist.")
        
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
        
    return post

@bp.route('/<int:id>/update', methods = ('GET', 'POST'))
@login_required
def update(id):
    """
    update a post
    """
    post = get_post(id)
    
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None
        
    if not title:
        error = 'Title is required.'
    
    if error is None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, body = ?'
            'WHERE id = ?',
            (title, body, id)
        )
        db.commit()
        return redirect(url_for('blog.index'))
    
    return render_template('blog/update.html', post = post)

@bp.route('/<int:id>/delete', methods = ('POST',))
@login_required
def delete(id):
    """
    delete a post
    """
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
