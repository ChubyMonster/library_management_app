from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .blueprints.users import users_bp
    from .blueprints.books import books_bp
    from .blueprints.loans import loans_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(loans_bp, url_prefix="/api/loans")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
