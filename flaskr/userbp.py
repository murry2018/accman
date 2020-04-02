from datetime import datetime, timedelta
from flask import (Blueprint, current_app, request, flash,
                   url_for, redirect, render_template, session)
import flaskr.model.db as db
from flaskr.model.models import User
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from sqlalchemy.exc import IntegrityError

userbp = Blueprint('user', __name__, template_folder='template')

def nowkor():
    return datetime.utcnow() + timedelta(hours=9)

@userbp.route('/new/form')
def new_form():
    if 'userid' in session:
        return redirect(url_for('index'))
    return render_template('userform.html')
    
@userbp.route('/new/request', methods=['POST'])
def new_request():
    if 'userid' in session:
        return redirect(url_for('index'))
    if (request.form['identifier'] == '' or
        request.form['username']   == '' or
        request.form['password']   == ''):
        flash('Please complete form', 'error')
        return redirect(url_for('user.new_form'))
    
    if db.session.query(User).\
       filter(User.identifier == request.form['identifier']).\
       count() > 0:
        flash('User ID "{}" is already exist.'.\
              format(request.form['identifier'])
              , 'error')
        return redirect(url_for('user.new_form'))
    
    hashed_password = generate_password_hash(
        request.form['password'], "sha256")
    u = User(identifier=request.form['identifier'],
             username=request.form['username'],
             password=hashed_password)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        flash('User ID "{}" is already exist.'.\
              format(request.form['identifier'])
              , 'error')
        db.session.rollback()
        return redirect(url_for('user.new_form'))
    flash('Hello, {}! Please sign in to keep going :)'.\
          format(request.form['username']),
          'good')
    return redirect(url_for('index'))

# user information
@userbp.route('/')
def show():
    if 'userid' not in session:
        return redirect(url_for('index'))
    return render_template('userinfo.html', session=session)

@userbp.route('/modify/password', methods=['GET', 'POST'])
def modify_password():
    if 'userid' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('modify_password.html')
    else: # POST
        pass
    if (request.form['currentpass'] == '' or
        request.form['password'] == ''):
        flash('Please complete form.', 'error')
        return redirect(url_for('user.modify_password'))
    users = db.session.query(User).\
        filter(User.id == session['userid']).all()
    if len(users) == 0:
        flash('Your account has been deleted', 'warning')
        return redirect(url_for('user.auth_destroy'))
    if len(users) > 1:
        flash(('It seems duplicated User ID "{}" exist. '
               'Please announce it to admin.').\
              format(session['userid']),
              'warning')
    user = users[-1]
    if not check_password_hash(user.password, request.form['currentpass']):
        flash('Wrong password', 'error')
        return redirect(url_for('user.modify_password'))
    user.password = generate_password_hash(
        request.form['password'], "sha256")
    db.session.commit()
    return redirect(url_for('user.show'))

@userbp.route('/modify/identifier', methods=['GET', 'POST'])
def modify_identifier():
    if 'userid' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('modify_identifier.html',
                               current=session['identifier'])
    else: # POST
        if request.form['identifier'] == '':
            flash('Please complete form.', 'error')
            return redirect(url_for('user.modify_identifier'))
        users = db.session.query(User).\
            filter(User.id == session['userid']).all()
        if len(users) == 0:
            flash('Your account has been deleted', 'warning')
            return redirect(url_for('user.auth_destroy'))
        if len(users) > 1:
            flash(('It seems duplicated User ID "{}" exist. '
                   'Please announce it to admin.').\
                  format(session['userid']),
                  'warning')
        target = db.session.query(User).\
            filter(User.identifier == request.form['identifier']).first()
        if target is not None:
            flash('User ID "{}" is already exist.'.\
                  format(request.form['identifier'])
                  , 'error')
            return redirect(url_for('user.modify_identifier'))
        user = users[-1]
        user.identifier = request.form['identifier']
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('User ID "{}" is already exist.'.\
                  format(request.form['identifier'])
                  , 'error')
            return redirect(url_for('user.modify_identifier'))
        
        flash('Identifier successfully changed!', 'good')
        session['identifier'] = request.form['identifier']
        return redirect(url_for('user.show'))

# logout
@userbp.route('/auth/destroy')
def auth_destroy():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# login form
@userbp.route('/auth/form')
def auth_form():
    if 'userid' in session:
        return redirect(url_for('index'))
    return render_template('signin.html')

# login
@userbp.route('/auth/request', methods=['POST'])
def auth_request():
    if 'userid' in session:
        return redirect(url_for('index'))
    if (request.form['identifier'] == '' or
        request.form['password']   == ''):
        flash('Please complete form', 'error')
        return redirect(url_for('user.auth_form'))

    users = db.session.query(User).\
        filter(User.identifier == request.form['identifier']).\
        all()
    if len(users) == 0:
        flash('User ID "{}" does not exist.'.\
              format(request.form['identifier']),
              'error')
        return redirect(url_for('user.auth_form'))
    if len(users) > 1:
        flash(('It seems duplicated User ID "{}" exist. '
               'Please announce it to admin.').\
              format(request.form['identifier']),
              'warning')
    user = users[-1]
    if not check_password_hash(user.password, request.form['password']):
        flash('Password is wrong.', 'error')
        return redirect(url_for('user.auth_form'))
    user.lastlogin = user.currlogin
    user.currlogin = nowkor()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('FATAL: Failed to update user login', 'error')
    session['userid'] = user.id
    session['identifier'] = user.identifier
    session['username'] = user.username
    session['lastlogin'] = user.lastlogin
    return redirect(url_for('index'))

# account deletion confirm
@userbp.route('/shutdown')
def shutdown():
    if 'userid' not in session:
        return redirect(url_for('index'))
    return render_template('shutdown.html')

# account deletion
@userbp.route('/goodbye/<really>')
def goodbye(really):
    if 'userid' not in session:
        return redirect(url_for('index'))
    if really != 'really':
        flash('Thank you for staying with me! :D', 'good')
        return redirect(url_for('index'))
    User.query.filter_by(id=session['userid']).delete()
    db.session.commit()
    return redirect(url_for('user.auth_destroy'))
