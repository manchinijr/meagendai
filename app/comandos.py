"""Comandos de linha de comando: flask init-db, flask seed-demo, flask criar-admin."""

import random
from datetime import time, timedelta
from decimal import Decimal
from pathlib import Path

import click
from sqlalchemy import text

from app.extensions import db
from app.models import Agendamento, Jornada, Perfil, Profissional, Servico, StatusAgendamento, Usuario
from app.services.tempo import agora, combinar

SCHEMA = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


def executar_schema(reset=False):
    with db.engine.begin() as conexao:
        if reset:
            conexao.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conexao.exec_driver_sql(SCHEMA.read_text(encoding="utf-8"))


def criar_usuario(nome, email, senha, perfil, telefone=None):
    usuario = Usuario(nome=nome, email=email, perfil=perfil, telefone=telefone)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    return usuario


def popular_demo(semente=42):
    """Dados de demonstração (barbearia) usados nos vídeos e pelos testadores."""
    rnd = random.Random(semente)
    criar_usuario("Administrador MeAgendaí", "admin@meagendai.com", "Admin@123", Perfil.ADMIN)
    cliente = criar_usuario("Cliente Demonstração", "cliente@meagendai.com", "Cliente@123", Perfil.CLIENTE, "(11) 98888-7777")
    clientes_extras = [
        criar_usuario(nome, f"cliente{i}@exemplo.com", "Cliente@123", Perfil.CLIENTE)
        for i, nome in enumerate(["Bruno Alves", "Juliana Costa", "Marcos Pereira", "Fernanda Rocha"], start=1)
    ]

    corte = Servico(nome="Corte masculino", descricao="Corte na tesoura ou máquina", duracao_min=30, preco=Decimal("45.00"))
    barba = Servico(nome="Barba", descricao="Barba com toalha quente", duracao_min=20, preco=Decimal("30.00"))
    combo = Servico(nome="Corte + barba", descricao="Combo completo", duracao_min=50, preco=Decimal("70.00"))
    escova = Servico(nome="Escova", descricao="Lavagem e escova", duracao_min=45, preco=Decimal("60.00"))
    db.session.add_all([corte, barba, combo, escova])

    carlos = Profissional(
        usuario=criar_usuario("Carlos Souza", "carlos@meagendai.com", "Prof@1234", Perfil.PROFISSIONAL),
        especialidade="Barbeiro",
        servicos=[corte, barba, combo],
    )
    ana = Profissional(
        usuario=criar_usuario("Ana Lima", "ana@meagendai.com", "Prof@1234", Perfil.PROFISSIONAL),
        especialidade="Cabeleireira",
        servicos=[corte, escova],
    )
    for profissional in (carlos, ana):
        for dia in range(5):  # segunda a sexta
            profissional.jornadas.append(Jornada(dia_semana=dia, hora_inicio=time(9), hora_fim=time(12)))
            profissional.jornadas.append(Jornada(dia_semana=dia, hora_inicio=time(13), hora_fim=time(18)))
        profissional.jornadas.append(Jornada(dia_semana=5, hora_inicio=time(9), hora_fim=time(13)))
    db.session.add_all([carlos, ana])
    db.session.flush()

    # Histórico dos últimos 30 dias para o painel ter dados.
    hoje = agora().date()
    todos_clientes = [cliente, *clientes_extras]
    for dias_atras in range(30, 0, -1):
        dia = hoje - timedelta(days=dias_atras)
        if dia.weekday() == 6:
            continue
        for profissional in (carlos, ana):
            ocupado_ate = combinar(dia, time(9))
            for _ in range(rnd.randint(1, 4)):
                servico = rnd.choice(profissional.servicos)
                inicio = ocupado_ate + timedelta(minutes=rnd.choice([0, 30, 60]))
                fim = inicio + timedelta(minutes=servico.duracao_min)
                if fim.time() > time(12) and inicio.time() < time(13):
                    break
                status = rnd.choices(
                    [StatusAgendamento.REALIZADO, StatusAgendamento.FALTOU, StatusAgendamento.CANCELADO],
                    weights=[80, 10, 10],
                )[0]
                db.session.add(
                    Agendamento(
                        cliente_id=rnd.choice(todos_clientes).id,
                        profissional_id=profissional.id,
                        servico_id=servico.id,
                        inicio=inicio,
                        fim=fim,
                        status=status,
                        preco_cobrado=servico.preco,
                    )
                )
                ocupado_ate = fim
    db.session.commit()


def registrar(app):
    @app.cli.command("init-db")
    @click.option("--reset", is_flag=True, help="Apaga TODAS as tabelas antes de recriar.")
    def init_db(reset):
        """Cria as tabelas a partir de database/schema.sql."""
        if reset:
            click.confirm("Isso apaga todos os dados do banco. Continuar?", abort=True)
        executar_schema(reset=reset)
        click.echo("Banco criado.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Insere os dados de demonstração (admin, profissionais, serviços e histórico)."""
        if db.session.query(Usuario).count():
            raise click.ClickException("O banco já tem dados. Use 'flask init-db --reset' antes.")
        popular_demo()
        click.echo("Dados de demonstração inseridos.")

    @app.cli.command("criar-admin")
    @click.option("--nome", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option("--senha")
    def criar_admin(nome, email, senha):
        """Cria um usuário administrador."""
        criar_usuario(nome, email.strip().lower(), senha, Perfil.ADMIN)
        db.session.commit()
        click.echo("Administrador criado.")
