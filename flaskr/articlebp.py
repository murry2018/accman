from datetime import datetime, timedelta
from math import ceil
from flask import (Blueprint, current_app, request, flash,
                   url_for, redirect, render_template, session)
import flaskr.model.db as db
from flaskr.model.models import User, Article
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from sqlalchemy.exc import IntegrityError
from markupsafe import escape

articlebp = Blueprint('article', __name__,
                      template_folder='template')

def nowkor():
    return datetime.utcnow() + timedelta(hours=9)

@articlebp.route('/new', methods=['GET', 'POST'])
def new():
    if 'userid' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('articleform.html',
                               username=session['username'])
    # POST
    title = request.form['title']
    if request.form['title'] == '':
        title = '(Untitled)'
    content = request.form['content']
    if request.form['content'] == '':
        content = '(Empty article)'
    u = User.query.filter_by(id=session['userid']).first()
    a = Article(title=title, content=content)
    a.publisher = u
    db.session.add(a)
    db.session.commit()
    flash('memo({}) saved.'.format(title),'good')
    return redirect(url_for('article.show_all'))

@articlebp.route('/', defaults={'page': 1})
@articlebp.route('/<int:page>')
def show_all(page):
    ARTICLE_PER_PAGE = 5
    if 'userid' not in session:
        return redirect(url_for('index'))
    (s, e) = ((page-1)*ARTICLE_PER_PAGE, page*ARTICLE_PER_PAGE)
    narticle = Article.query.join(Article.publisher).count()
    articles = Article.query.join(Article.publisher).\
        order_by(Article.id.desc())[s:e]
    pages = ceil(narticle/ARTICLE_PER_PAGE)
    return render_template('articlelist.html',
                           username=session['username'],
                           articles=articles,
                           page=page, pages=pages)

@articlebp.route('/view/<int:articleid>')
def show(articleid):
    if 'userid' not in session:
        return redirect(url_for('index'))
    nextitem = Article.query.filter(Article.id < articleid).\
        order_by(Article.id.desc()).first()
    article = Article.query.filter_by(id=articleid).first()
    previtem = Article.query.filter(Article.id > articleid).\
        order_by(Article.id).first()
    if article == None:
        flash('Article does not exist.', 'error')
        return redirect(url_for('article.show_all'))
    if article.publisher.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('article.show_all'))
    return render_template('articleview.html',
                           username=session['username'],
                           article=article,
                           previtem=previtem,
                           nextitem=nextitem)

@articlebp.route('/delete/<int:articleid>')
def delete(articleid):
    if 'userid' not in session:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=articleid).first()
    if article == None:
        flash('Article does not exist.', 'error')
        return redirect(url_for('article.show_all'))
    if article.publisher.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('article.show_all'))
    db.session.delete(article)
    db.session.commit()
    flash('Deleted successfully.', 'good')
    return redirect(url_for('article.show_all'))

@articlebp.route('/edit/<int:articleid>', methods=['GET', 'POST'])
def edit(articleid):
    if 'userid' not in session:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=articleid).first()
    if article == None:
        flash('Article does not exist.', 'error')
        return redirect(url_for('article.show_all'))
    if article.publisher.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('article.show_all'))
    if request.method == 'GET':
        return render_template('articleedit.html',
                               username=session['username'],
                               article=article)
    # POST
    title = request.form['title']
    if request.form['title'] == '':
        title = '(Untitled)'
    content = request.form['content']
    if request.form['content'] == '':
        content = '(Empty article)'
    article.title = title
    article.content = content
    db.session.commit()
    flash('memo({}) saved.'.format(title),'good')
    return redirect(url_for('article.show_all'))
