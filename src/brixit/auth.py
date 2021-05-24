import functools
import random
import string
import commonUtils as cu
import Constants as k
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import fileUtils

bp = Blueprint('auth', __name__, url_prefix='/auth')


def GenerateSerial():
    """ Creates a serial key for a new user and inserts it into the database """
    key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(k.kSerialLength))
    sql = sqlite3.connect(cu.settings.DB_User)
    if sql.execute('SELECT serialKey FROM keys WHERE serialKey = ?', [key]).fetchone() is not None:
        print("Error: Serial key in use!")
        return

    sql.execute('INSERT INTO keys (serialKey) VALUES (?)', [key])
    sql.commit()
    print("Here is your new serial key:")
    print(key)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #key = request.form['serialKey']

        key = "1WFJD0CIHZNK3NZD"

        serverDb = fileUtils.GetDb()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not key:
            error = 'Serial key is required.'
        elif serverDb.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if serverDb.execute(
            'SELECT serialKey FROM keys WHERE serialKey = ?', [key]
        ).fetchone() is None:
            error = 'Serial key is invalid.'.format(username)

        if error is None:
            serverDb.execute('INSERT INTO user (username, password, serialKey) VALUES (?, ?, ?)', [username, generate_password_hash(password), key])
            serverDb.commit()

            serverDb.execute("DELETE FROM keys WHERE serialKey = ?", [key])
            serverDb.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        serverDb = fileUtils.GetDb()
        error = None
        user = serverDb.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = fileUtils.GetDb().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

if __name__ == "__main__":
    GenerateSerial()
