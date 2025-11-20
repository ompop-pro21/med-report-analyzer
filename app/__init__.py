from flask import Flask
from config import Config
from .extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.main import main_bp
    from app.analysis import analysis_bp
    from app.drugs import drugs_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(drugs_bp, url_prefix='/drugs')

    @app.errorhandler(413)
    def request_entity_too_large(error):
        from flask import flash, redirect, url_for
        flash('File too large. Maximum size is 16MB.', 'error')
        return redirect(url_for('analysis.upload'))

    return app