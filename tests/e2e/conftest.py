"""Sobe a aplicação de verdade (com CSRF ativo) em uma thread para os testes de navegador."""

import socket
import threading

import pytest
from werkzeug.serving import make_server

from app import create_app
from app.comandos import executar_schema, popular_demo
from app.config import TestConfig
from app.extensions import db


class E2EConfig(TestConfig):
    WTF_CSRF_ENABLED = True


def porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def servidor():
    app = create_app(E2EConfig)
    with app.app_context():
        try:
            executar_schema(reset=True)
        except Exception as erro:  # noqa: BLE001
            pytest.skip(f"PostgreSQL de teste indisponível: {erro}")
        popular_demo()
        db.session.remove()

    porta = porta_livre()
    http = make_server("127.0.0.1", porta, app, threaded=True)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{porta}"
    http.shutdown()


@pytest.fixture
def entrar(page, servidor):
    def _entrar(email, senha):
        page.goto(f"{servidor}/login")
        page.fill("#email", email)
        page.fill("#senha", senha)
        page.click("form button[type=submit]")
        page.wait_for_load_state()

    return _entrar
