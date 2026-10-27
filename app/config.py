import os

from dotenv import load_dotenv

load_dotenv()


def normalizar_url_banco(url):
    """Neon/Render entregam 'postgres://' ou 'postgresql://'; o SQLAlchemy precisa do driver psycopg."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-troque-esta-chave")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/meagendai")
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    FUSO_HORARIO = "America/Sao_Paulo"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(
        os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/meagendai_test")
    )
