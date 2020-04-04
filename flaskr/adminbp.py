from flask import (Blueprint, render_template, flash, url_for,
                   current_app, session, abort, request, redirect)
from flaskr.model.models import User, Account, Article
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
import flaskr.model.db as db

adminbp = Blueprint('admin', __name__, template_folder='template')

@adminbp.route('/')
def index():
    if 'userid' not in session:
        abort(404)
    if session['identifier'] != current_app.config['ADMINID']:
        abort(404)
    us = User.query.all()
    return render_template('adminpage.html', users=us)

@adminbp.route('/user/<int:id>')
def getuser(id):
    if 'userid' not in session:
        abort(404)
    if session['identifier'] != current_app.config['ADMINID']:
        abort(404)
    u = User.query.filter_by(id=id).first()
    if u == None:
        flash('#User<{}> not found.'.format(id), 'error')
        return redirect(url_for('admin.index'))
    return render_template('admin_getuser.html',
                           user=u, narticle=len(u.articles), naccount=len(u.accounts))
        

@adminbp.route('/user/<int:id>/rm')
def rmuser(id):
    if 'userid' not in session:
        abort(404)
    if session['identifier'] != current_app.config['ADMINID']:
        abort(404)
    u = User.query.filter_by(id=id).first()
    if u == None:
        flash('User doesn\'t exist.', 'error')
        return redirect(url_for('admin.index'))
    db.session.delete(u)
    db.session.commit()
    flash('User successfully removed.', 'good')
    return redirect(url_for('admin.index'))

@adminbp.route('/user/<int:id>/chpass', methods=['GET', 'POST'])
def chpass(id):
    if 'userid' not in session:
        abort(404)
    if session['identifier'] != current_app.config['ADMINID']:
        abort(404)
    u = User.query.filter_by(id=id).first()
    if u == None:
        flash('User doesn\'t exist.', 'error')
        return redirect(url_for('admin.index'))
    if request.method == 'GET':
        return render_template('admin_chpass.html', id=id, identifier=u.identifier)
    # POST    
    u.password = generate_password_hash(request.form['password'], "sha256")
    db.session.commit()
    flash('User\'s password successfully changed.', 'good')
    return redirect(url_for('admin.getuser', id=id))
