# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import os
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import send_from_directory
from werkzeug import secure_filename
from utils import uuid36

# configuration
DATABASE = 'data/flaskr.db'
UPLOAD_FOLDER = 'data/files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])
DEBUG = True
SECRET_KEY = 'asdf2hbh;sd56fkshn:qw2n1u38'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024 # limit uploads to 64MB


# !!!

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        abort(401)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        g.db.execute('insert into attachments (resid, title, filename) values (?, ?, ?)',
             [request.form['resid'], request.form['title'], filename])
        g.db.commit()
        return redirect(url_for('entry_view',
                                resid=request.form['resid']))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# !!!

def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select resid, title, text from entries order by id desc')
    entries = [dict(resid=row[0], title=row[1], text=row[2]) for row in cur.fetchall()] 
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    xid = uuid36().lower()
    g.db.execute('insert into entries (resid, title, text) values (?, ?, ?)',
                 [xid, request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/view/<resid>', methods=['GET'])
def entry_view(resid):
    cur = g.db.execute("select resid, title, text from entries where resid='%s' order by id desc" % resid)
    row = cur.fetchone()
    entry = dict(resid=row[0], title=row[1], text=row[2]) 
    cur = g.db.execute("select resid, title, filename from attachments where resid='%s' order by id desc" % resid)
    files = [dict(resid=row[0], title=row[1], filename=row[2]) for row in cur.fetchall()]
    return render_template('show_files.html', entry=entry, files=files)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

