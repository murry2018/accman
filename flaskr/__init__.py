from flask import Flask, g, render_template, session

def create_app(config_filename):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        ADMIN_IDENTIFIER='admin'
    )

    app.config.from_envvar('FLASK_SETTINGS', silent=True)
    
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
        
    @app.route('/')
    def index():
        return render_template('index.html', session=session)

    return app
