from math import ceil
from flask import (Blueprint, make_response, request, flash,
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
    if sitelink != '' and '://' not in sitelink:
        sitelink = 'http://' + sitelink
    userid=request.form['userid']
    email=request.form['email']
    phone=request.form['phone']
    password=request.form['password']
    pass2nd=''
    if 'pass2nd' in request.form:
        pass2nd=request.form['pass2nd']
    description=request.form['description']
    if (sitename == '' or
        (userid == '' and password == '' and
         email == '' and phone == '')):
        flash('Please complete form', 'error')
        return redirect(url_for('account.show_all',
                                app=request.cookies.get('app', '10')))
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
    flash('account ({}@{}) saved.'.\
          format('(id:none)' if userid == '' else userid, sitename),
          'good')
    return redirect(url_for('account.show_all',
                            app=request.cookies.get('app', '10')))

@accountbp.route('/', defaults={'page': 1})
@accountbp.route('/<page>')
def show_all(page):
    ACCOUNT_PER_PAGE = 10
    if 'userid' not in session:
        return redirect(url_for('index'))
    if 'app' in request.cookies:
        try: ACCOUNT_PER_PAGE = int(request.cookies['app'])
        except ValueError: pass
    if 'app' in request.args:
        try: ACCOUNT_PER_PAGE = int(request.args['app'])
        except ValueError: pass
    (s, e) = ((page-1)*ACCOUNT_PER_PAGE, page*ACCOUNT_PER_PAGE)
    u = User.query.filter_by(id=session['userid']).first()
    naccount = len(u.accounts)
    accounts = db.session.query(Account).\
        filter_by(user_id=session['userid']).\
        order_by(Account.id.desc())[s:e]
    pages = ceil(naccount/ACCOUNT_PER_PAGE)
    resp = make_response(
        render_template('accountlist.html',
                        username=session['username'],
                        accounts=accounts,
                        page=page, pages=pages,
                        app=str(ACCOUNT_PER_PAGE)))
    resp.set_cookie('app', str(ACCOUNT_PER_PAGE))
    return resp

@accountbp.route('/<int:id>/view')
def show(id):
    if 'userid' not in session:
        return redirect(url_for('index'))
    accounts = db.session.query(Account).\
        filter_by(user_id=session['userid'])
    nextitem = accounts.filter(Account.id < id).\
        order_by(Account.id.desc()).first()
    account = accounts.filter_by(id=id).first()
    previtem = accounts.filter(Account.id > id).\
        order_by(Account.id).first()
    if account == None:
        flash('Account does not exist.', 'error')
        return redirect(url_for('account.show_all'))
    if account.owner.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('account.show_all'))
    return render_template('accountview.html',
                           username=session['username'],
                           account=account,
                           previtem=previtem,
                           nextitem=nextitem,
                           app=request.cookies.get('app', '10'))

@accountbp.route('/<int:id>/edit/', defaults={'what': 'info'}, methods=['GET','POST'])
@accountbp.route('/<int:id>/edit/<what>', methods=['GET','POST'])
def edit(id, what):
    if 'userid' not in session:
        return redirect(url_for('index'))
    a = Account.query.filter_by(id=id).first()
    if a == None:
        flash('Account does not exist.', 'error')
        return redirect(url_for('account.show_all'))
    if a.user_id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('account.show_all'))
    if request.method == 'GET':
        if what == 'info':
            return render_template('accountedit.html',
                                   username=session['username'],
                                   account=a)
        elif what == 'pass':
            return render_template('accounteditpass.html',
                                   username=session['username'],
                                   account=a)
        else:
            abort(404)
    # POST
    if what == 'info':
        a.sitename = request.form['sitename']
        a.sitelink = request.form['sitelink']
        if a.sitelink != '' and '://' not in a.sitelink:
            a.sitelink = 'http://' + a.sitelink
        a.userid   = request.form['userid']
        a.email    = request.form['email']
        a.phone    = request.form['phone']
        a.description = request.form['description']
        if (a.sitename == '' or
            (a.userid == '' and a.email == '' and
             a.phone == '' and a.password == '')):
            db.session.rollback()
            flash('Please complete form.', 'error')
            return redirect(url_for('account.edit', id=id, what=what))
    elif what == 'pass':
        a.password = request.form.get('password', '')
        if a.password != '':
            a.password = generate_password_hash(a.password, "sha256")
        a.pass2nd  = request.form.get('pass2nd', '')
        if a.pass2nd != '':
            a.password = generate_password_hash(a.pass2nd, "sha256")
        if (a.userid == '' and a.email == '' and
            a.phone == '' and a.password == ''):
            db.session.rollback()
            flash('Please complete form.', 'error')
            return redirect(url_for('account.edit', id=id, what=what))
    else:
        abort(404)
    db.session.commit()
    flash('account ({}@{}) saved.'.\
          format('(id:none)' if a.userid == '' else a.userid, a.sitename),
          'good')
    return redirect(url_for('account.show_all'))
            

@accountbp.route('/<int:id>/delete')
def delete(id):
    if 'userid' not in session:
        return redirect(url_for('index'))
    a = Account.query.filter_by(id=id).first()
    if a == None:
        flash('Account does not exist.', 'error')
        return redirect(url_for('account.show_all'))
    if a.user_id != session['userid']:
        flash('You don\'t have permission', 'error')
        return redirect(url_for('account.show_all'))
    db.session.delete(a)
    db.session.commit()
    flash('Deleted successfully.', 'good')
    return redirect(url_for('account.show_all'))
    

@accountbp.route('/<int:id>/checkpass/<int:field>', methods=['POST'])
def checkpass(id, field):
    if 'userid' not in session:
        return redirect(url_for('index'))
    a = Account.query.filter_by(id=id).first()
    if a == None:
        flash('Account does not exist.', 'error')
        return redirect(url_for('account.show_all'))
    if a.user_id != session['userid']:
        flash('You don\'t have permission', 'error')
        return redirect(url_for('account.show_all'))
    password = a.password if field == 1 else a.pass2nd
    checkword = request.form['password']
    if check_password_hash(password, checkword):
        flash('Yes! That is the valid password.', 'good')
        return redirect(url_for('account.show', id=id))
    else:
        flash('You entered wrong password.', 'warning')
        return redirect(url_for('account.show', id=id))
        
