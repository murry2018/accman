from datetime import datetime, timedelta
from math import ceil
from flask import (Blueprint, make_response, request, flash,
                   url_for, redirect, render_template, session)
import flaskr.model.db as db
from flaskr.model.models import User, Article
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import join
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
    return redirect(url_for('article.show_all',
                            app=request.cookies.get('app', '5')))

@articlebp.route('/', defaults={'page': 1})
@articlebp.route('/<int:page>')
def show_all(page):
    ARTICLE_PER_PAGE = 5
    if 'userid' not in session:
        return redirect(url_for('index'))
    if 'app' in request.cookies:
        try: ARTICLE_PER_PAGE = int(request.cookies['app'])
        except ValueError: pass
    if 'app' in request.args:
        try: ARTICLE_PER_PAGE = int(request.args['app'])
        except ValueError: pass
    (s, e) = ((page-1)*ARTICLE_PER_PAGE, page*ARTICLE_PER_PAGE)
    u = User.query.filter_by(id=session['userid']).first()
    narticle = len(u.articles)
    articles = db.session.query(Article).\
        filter_by(user_id=session['userid']).\
        order_by(Article.id.desc())[s:e]
    pages = ceil(narticle/ARTICLE_PER_PAGE)
    resp = make_response(
        render_template('articlelist.html',
                        username=session['username'],
                        articles=articles,
                        page=page, pages=pages,
                        app=str(ARTICLE_PER_PAGE)))
    resp.set_cookie('app', str(ARTICLE_PER_PAGE))
    return resp

@articlebp.route('/<int:articleid>/view')
def show(articleid):
    if 'userid' not in session:
        return redirect(url_for('index'))
    articles = db.session.query(Article).\
        filter_by(user_id=session['userid'])
    nextitem = articles.filter(Article.id < articleid).\
        order_by(Article.id.desc()).first()
    article = articles.filter_by(id=articleid).first()
    previtem = articles.filter(Article.id > articleid).\
        order_by(Article.id).first()
    if article == None:
        flash('Article does not exist.', 'error')
        return redirect(url_for('article.show_all',
                                app=request.cookies.get('app', '5')))
    if article.publisher.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('article.show_all',
                                app=request.cookies.get('app', '5')))
    return render_template('articleview.html',
                           username=session['username'],
                           article=article,
                           previtem=previtem,
                           nextitem=nextitem,
                           app=request.cookies.get('app', '5'))

@articlebp.route('/<int:articleid>/delete')
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

@articlebp.route('/<int:articleid>/edit', methods=['GET', 'POST'])
def edit(articleid):
    if 'userid' not in session:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=articleid).first()
    if article == None:
        flash('Article does not exist.', 'error')
        return redirect(url_for('article.show_all'))
    if article.publisher.id != session['userid']:
        flash('You don\'t have permission.', 'error')
        return redirect(url_for('article.show_all',))
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
