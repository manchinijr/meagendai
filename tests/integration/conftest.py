from datetime import time, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import create_app
from app.comandos import executar_schema
from app.config import TestConfig
from app.extensions import db
from app.models import Jornada, Perfil, Profissional, Servico, Usuario
from app.services.tempo import agora, combinar

TABELAS = "agendamento, jornada, profissional_servico, profissional, servico, usuario, configuracao"


@pytest.fixture(scope="session")
def app():
    aplicacao = create_app(TestConfig)
    with aplicacao.app_context():
        try:
            executar_schema(reset=True)
        except OperationalError as erro:
            pytest.skip(f"PostgreSQL de teste indisponível ({TestConfig.SQLALCHEMY_DATABASE_URI}): {erro.orig}")
        yield aplicacao
        db.session.remove()


@pytest.fixture(autouse=True)
def banco_limpo(app):
    with app.app_context():
        yield
        db.session.rollback()
        db.session.execute(text(f"TRUNCATE {TABELAS} RESTART IDENTITY CASCADE"))
        db.session.commit()
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


def criar_usuario(nome, email, perfil, senha="Senha123"):
    usuario = Usuario(nome=nome, email=email, perfil=perfil)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


@pytest.fixture
def cliente():
    return criar_usuario("Cliente Teste", "cliente@teste.com", Perfil.CLIENTE)


@pytest.fixture
def outro_cliente():
    return criar_usuario("Outro Cliente", "outro@teste.com", Perfil.CLIENTE)


@pytest.fixture
def admin():
    return criar_usuario("Admin Teste", "admin@teste.com", Perfil.ADMIN)


@pytest.fixture
def corte():
    servico = Servico(nome="Corte", duracao_min=30, preco=Decimal("45.00"))
    db.session.add(servico)
    db.session.commit()
    return servico


@pytest.fixture
def escova():
    servico = Servico(nome="Escova", duracao_min=45, preco=Decimal("60.00"))
    db.session.add(servico)
    db.session.commit()
    return servico


@pytest.fixture
def barbeiro(corte):
    """Profissional que faz 'Corte' de segunda a sábado, 9h–12h e 13h–18h."""
    usuario = Usuario(nome="Carlos Barbeiro", email="carlos@teste.com", perfil=Perfil.PROFISSIONAL)
    usuario.definir_senha("Senha123")
    profissional = Profissional(usuario=usuario, servicos=[corte])
    for dia in range(6):
        profissional.jornadas.append(Jornada(dia_semana=dia, hora_inicio=time(9), hora_fim=time(12)))
        profissional.jornadas.append(Jornada(dia_semana=dia, hora_inicio=time(13), hora_fim=time(18)))
    db.session.add(profissional)
    db.session.commit()
    return profissional


@pytest.fixture
def dia_util():
    """Próxima segunda-feira com pelo menos 7 dias de distância (sempre no futuro)."""
    hoje = agora().date() + timedelta(days=7)
    return hoje + timedelta(days=(7 - hoje.weekday()) % 7)


@pytest.fixture
def as_10h(dia_util):
    return combinar(dia_util, time(10))


def logar(client, email, senha="Senha123"):
    return client.post("/login", data={"email": email, "senha": senha})
