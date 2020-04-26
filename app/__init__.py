from app.config import Config
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from app.extensions import cache, mongo, scheduler
from dotenv import load_dotenv

def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""

        # If a HTTPException, pull the `code` attribute; default to 500
        error_code        = getattr(error, 'code', 500)
        error_description = getattr(error, 'name', '')
        error_message     = getattr(error, 'description', '')
        return make_response(jsonify(
            {
                'error'  :error_code,
                'message':error_message
            }), error_code
        )

    for errcode in [400, 401, 403, 404, 405, 500]:
        app.errorhandler(errcode)(render_error)

def create_app(config_class=Config):
    
    load_dotenv() # Load all env variables for the app

    app   = Flask(__name__)
    CORS(app)
    app.secret_key = ".*nobodysguessingthis__"
    app.config.from_object(config_class)
    
    mongo.init_app(app, Config.MONGO_URI)

    cache.init_app(app, config=Config.CACHE_CONFIG)

    scheduler.init_app(app)
    scheduler.start()

    from app.data import data_bp
    app.register_blueprint(data_bp, cli_group=None)
    register_errorhandlers(app)

    return app
