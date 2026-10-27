import logging

from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401  registra os models no SQLAlchemy
    from app.controllers import admin, api, auth, cliente, erros, profissional

    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)
    app.register_blueprint(profissional.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)
    erros.registrar(app)

    from app import comandos, filtros

    comandos.registrar(app)
    filtros.registrar(app)

    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)

    return app
