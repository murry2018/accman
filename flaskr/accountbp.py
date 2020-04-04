from flask import (Blueprint, current_app, request, flash,
                   url_for, redirect, render_template, session)
import flaskr.model.db as db
from flaskr.model.models import User, Account
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from sqlalchemy.exc import IntegrityError

accountbp = Blueprint('account', __name__,
                      template_folder='template')

@accountbp.route('/new', methods=['GET','POST'])
def new():
    if 'userid' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('accountform.html',
                               username=session['username'])
    # POST
    sitename=request.form['sitename']
    sitelink=request.form['sitelink']
    userid=request.form['userid']
    email=request.form['email']
    phone=request.form['phone']
    password=request.form['password']
    pass2nd=request.form['pass2nd']
    description=request.form['description']
    if (sitename == '' or
        (userid == '' and password == '' and
         email == '' and phone == '')):
        flash('Please complete form', 'error')
        return redirect(url_for('account.show_all'))
    if password != '':
        password = generate_password_hash(password, "sha256")
    if pass2nd != '':
        pass2nd = generate_password_hash(pass2nd, "sha256")
    u = User.query.filter_by(id=session['userid']).first()
    a = Account(sitename=sitename,
                sitelink=sitelink,
                userid=userid,
                email=email,
                phone=phone,
                password=password,
                pass2nd=pass2nd,
                description=description)
    a.owner = u
    db.session.add(a)
    db.session.commit()
    flash('Account ({}@{}) saved.'.\
          format('?' if userid == '' else userid, sitename),
          'good')
    return redirect(url_for('account.show_all'))

@accountbp.route('/', defaults={'page': 1})
@accountbp.route('/<page>')
def show_all(page):
    ACCOUNT_PER_PAGE = 10
    if 'userid' not in session:
        return redirect(url_for('index'))
    if 'app' in request.args:
        ACCOUNT_PER_PAGE = int(request.args['app'])
    (s, e) = ((page-1)*ACCOUNT_PER_PAGE, page*ACCOUNT_PER_PAGE)
    return None
