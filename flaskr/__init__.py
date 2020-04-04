from flask import Flask, g, render_template, session
import os

def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    
    """ config loading """
    app.config.from_mapping(
        SECRET_KEY='dev',
        ADMINID='admin'
    )

    app.config.from_envvar('FLASK_SETTINGS', silent=True)

    secret_ = os.environ.get('SECRET_KEY')
    if secret_ != None:
        app.config['SECRET_KEY'] = secret_
    adminid_ = os.environ.get('ADMINID')
    if adminid_ != None:
        app.config['ADMINID'] = adminid_
    dburl_ = os.environ.get('DATABASE_URL')
    if adminid_ != None:
        app.config['DATABASE_URL'] = dburl_
    
    """ database config """
    import flaskr.model.db as db

    db.init_db(app.config['DATABASE_URL'])
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    """ Blueprints """
    from flaskr.userbp import userbp
    app.register_blueprint(userbp, url_prefix='/user')
    from flaskr.articlebp import articlebp
    app.register_blueprint(articlebp, url_prefix='/article')
    from flaskr.accountbp import accountbp
    app.register_blueprint(accountbp, url_prefix='/account')
    from flaskr.adminbp import adminbp
    app.register_blueprint(adminbp, url_prefix='/control')
    
    @app.route('/')
    def index():
        admin=False
        if ('userid' in session and 'identifier' in session and
            session['identifier'] == app.config['ADMINID']):
            admin=True
        return render_template('index.html', session=session, isadmin=admin)

    return app
