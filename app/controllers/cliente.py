from datetime import date, datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.controllers import perfil_requerido
from app.extensions import db
from app.forms import AcaoForm
from app.models import Agendamento, Perfil, Profissional, Servico, StatusAgendamento
from app.services import agendamento_service, config_service, disponibilidade_service
from app.services.erros import RegraNegocioError
from app.services.tempo import FUSO, agora

bp = Blueprint("cliente", __name__)

DIAS_A_FRENTE = 60


def ler_data(texto):
    """Data do filtro (?data=AAAA-MM-DD). Valores inválidos ou fora da janela viram 'hoje'."""
    hoje = agora().date()
    try:
        escolhida = date.fromisoformat(texto) if texto else hoje
    except ValueError:
        return hoje
    if escolhida < hoje or escolhida > hoje + timedelta(days=DIAS_A_FRENTE):
        return hoje
    return escolhida


def ler_inicio(texto):
    try:
        inicio = datetime.fromisoformat(texto)
    except (TypeError, ValueError):
        return None
    return inicio if inicio.tzinfo else inicio.replace(tzinfo=FUSO)


def servicos_ativos():
    return db.session.scalars(select(Servico).where(Servico.ativo).order_by(Servico.nome)).all()


def obter_ou_404(modelo, ident):
    objeto = db.session.get(modelo, ident)
    if objeto is None:
        abort(404)
    return objeto


def agendamento_do_cliente(agendamento_id):
    agendamento = obter_ou_404(Agendamento, agendamento_id)
    if agendamento.cliente_id != current_user.id:
        abort(403)
    return agendamento


@bp.route("/")
def index():
    return render_template("cliente/index.html", servicos=servicos_ativos())


@bp.route("/health")
def health():
    return {"status": "ok"}


@bp.route("/agendar")
@perfil_requerido(Perfil.CLIENTE)
def agendar():
    return render_template(
        "cliente/agendar_servico.html",
        servicos=servicos_ativos(),
        bloqueado=agendamento_service.esta_bloqueado(current_user),
    )


@bp.route("/agendar/<int:servico_id>")
@perfil_requerido(Perfil.CLIENTE)
def escolher_profissional(servico_id):
    servico = obter_ou_404(Servico, servico_id)
    if not servico.ativo:
        abort(404)
    profissionais = [p for p in servico.profissionais if p.ativo]
    return render_template("cliente/agendar_profissional.html", servico=servico, profissionais=profissionais)


@bp.route("/agendar/<int:servico_id>/<int:profissional_id>")
@perfil_requerido(Perfil.CLIENTE)
def escolher_horario(servico_id, profissional_id):
    servico = obter_ou_404(Servico, servico_id)
    profissional = obter_ou_404(Profissional, profissional_id)
    if not servico.ativo or not profissional.ativo or not profissional.realiza(servico):
        abort(404)
    data = ler_data(request.args.get("data"))
    return render_template(
        "cliente/agendar_horario.html",
        servico=servico,
        profissional=profissional,
        data=data,
        hoje=agora().date(),
        data_max=agora().date() + timedelta(days=DIAS_A_FRENTE),
        horarios=disponibilidade_service.horarios_livres(servico.id, profissional.id, data),
        acao=url_for("cliente.criar_agendamento"),
        remarcando=None,
        form=AcaoForm(),
    )


@bp.route("/agendamentos", methods=["POST"])
@perfil_requerido(Perfil.CLIENTE)
def criar_agendamento():
    form = AcaoForm()
    servico_id = request.form.get("servico_id", type=int)
    profissional_id = request.form.get("profissional_id", type=int)
    inicio = ler_inicio(request.form.get("inicio"))
    if not form.validate_on_submit() or not servico_id or not profissional_id:
        abort(400)
    if inicio is None:
        flash("Escolha um horário para continuar.", "warning")
        return redirect(url_for("cliente.escolher_horario", servico_id=servico_id, profissional_id=profissional_id))

    try:
        agendamento = agendamento_service.criar_agendamento(
            current_user, servico_id, profissional_id, inicio, observacao=request.form.get("observacao")
        )
    except RegraNegocioError as erro:
        flash(erro.mensagem, "danger")
        return redirect(
            url_for(
                "cliente.escolher_horario",
                servico_id=servico_id,
                profissional_id=profissional_id,
                data=inicio.date().isoformat(),
            )
        )

    inicio_local = agendamento.inicio.astimezone(FUSO)
    flash(
        f"Agendamento confirmado para {inicio_local:%d/%m/%Y} às {inicio_local:%H:%M} "
        f"com {agendamento.profissional.nome}.",
        "success",
    )
    return redirect(url_for("cliente.meus_agendamentos"))


@bp.route("/meus-agendamentos")
@perfil_requerido(Perfil.CLIENTE)
def meus_agendamentos():
    momento = agora()
    todos = db.session.scalars(
        select(Agendamento).where(Agendamento.cliente_id == current_user.id).order_by(Agendamento.inicio.desc())
    ).all()
    proximos = sorted(
        (a for a in todos if a.status == StatusAgendamento.AGENDADO and a.inicio >= momento),
        key=lambda a: a.inicio,
    )
    historico = [a for a in todos if a not in proximos]
    return render_template(
        "cliente/meus_agendamentos.html",
        proximos=proximos,
        historico=historico,
        antecedencia=config_service.obter_int("ANTECEDENCIA_CANCEL_H"),
        bloqueado=agendamento_service.esta_bloqueado(current_user),
        form=AcaoForm(),
    )


@bp.route("/agendamentos/<int:agendamento_id>/cancelar", methods=["POST"])
@perfil_requerido(Perfil.CLIENTE)
def cancelar(agendamento_id):
    agendamento = agendamento_do_cliente(agendamento_id)
    if not AcaoForm().validate_on_submit():
        abort(400)
    try:
        agendamento_service.cancelar(agendamento, current_user)
    except RegraNegocioError as erro:
        flash(erro.mensagem, "danger")
    else:
        flash("Agendamento cancelado.", "success")
    return redirect(url_for("cliente.meus_agendamentos"))


@bp.route("/agendamentos/<int:agendamento_id>/remarcar", methods=["GET", "POST"])
@perfil_requerido(Perfil.CLIENTE)
def remarcar(agendamento_id):
    agendamento = agendamento_do_cliente(agendamento_id)
    if agendamento.status != StatusAgendamento.AGENDADO:
        flash("Este agendamento não pode mais ser remarcado.", "warning")
        return redirect(url_for("cliente.meus_agendamentos"))

    if request.method == "POST":
        if not AcaoForm().validate_on_submit():
            abort(400)
        novo_inicio = ler_inicio(request.form.get("inicio"))
        if novo_inicio is None:
            flash("Escolha um novo horário.", "warning")
            return redirect(url_for("cliente.remarcar", agendamento_id=agendamento.id))
        try:
            novo = agendamento_service.remarcar(agendamento, novo_inicio, current_user)
        except RegraNegocioError as erro:
            flash(erro.mensagem, "danger")
            return redirect(
                url_for("cliente.remarcar", agendamento_id=agendamento.id, data=novo_inicio.date().isoformat())
            )
        inicio_local = novo.inicio.astimezone(FUSO)
        flash(f"Agendamento remarcado para {inicio_local:%d/%m/%Y} às {inicio_local:%H:%M}.", "success")
        return redirect(url_for("cliente.meus_agendamentos"))

    data = ler_data(request.args.get("data") or agendamento.inicio.astimezone(FUSO).date().isoformat())
    return render_template(
        "cliente/agendar_horario.html",
        servico=agendamento.servico,
        profissional=agendamento.profissional,
        data=data,
        hoje=agora().date(),
        data_max=agora().date() + timedelta(days=DIAS_A_FRENTE),
        horarios=disponibilidade_service.horarios_livres(
            agendamento.servico_id, agendamento.profissional_id, data, ignorar_agendamento_id=agendamento.id
        ),
        acao=url_for("cliente.remarcar", agendamento_id=agendamento.id),
        remarcando=agendamento,
        form=AcaoForm(),
    )
