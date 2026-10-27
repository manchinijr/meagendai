from datetime import date, datetime, time, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.controllers import perfil_requerido
from app.controllers.auth import destino_seguro
from app.extensions import db
from app.forms import AcaoForm
from app.models import Agendamento, Perfil
from app.services import agendamento_service
from app.services.erros import RegraNegocioError
from app.services.tempo import FUSO, agora

bp = Blueprint("profissional", __name__, url_prefix="/agenda")


def periodo(data, visao):
    if visao == "semana":
        inicio = data - timedelta(days=data.weekday())
        return inicio, inicio + timedelta(days=7)
    return data, data + timedelta(days=1)


@bp.route("")
@perfil_requerido(Perfil.PROFISSIONAL)
def agenda():
    profissional = current_user.profissional
    if profissional is None:
        abort(403)
    try:
        data = date.fromisoformat(request.args.get("data", ""))
    except ValueError:
        data = agora().date()
    visao = "semana" if request.args.get("visao") == "semana" else "dia"
    ini, fim = periodo(data, visao)

    agendamentos = db.session.scalars(
        select(Agendamento)
        .where(
            Agendamento.profissional_id == profissional.id,
            Agendamento.inicio >= datetime.combine(ini, time.min, tzinfo=FUSO),
            Agendamento.inicio < datetime.combine(fim, time.min, tzinfo=FUSO),
        )
        .order_by(Agendamento.inicio)
    ).all()

    por_dia = {}
    for ag in agendamentos:
        por_dia.setdefault(ag.inicio.astimezone(FUSO).date(), []).append(ag)

    passo = timedelta(days=7 if visao == "semana" else 1)
    return render_template(
        "profissional/agenda.html",
        data=data,
        visao=visao,
        dias=[ini + timedelta(days=i) for i in range((fim - ini).days)],
        por_dia=por_dia,
        anterior=data - passo,
        seguinte=data + passo,
        agora=agora(),
        form=AcaoForm(),
    )


@bp.route("/<int:agendamento_id>/status", methods=["POST"])
@perfil_requerido(Perfil.PROFISSIONAL, Perfil.ADMIN)
def marcar_status(agendamento_id):
    agendamento = db.session.get(Agendamento, agendamento_id)
    if agendamento is None:
        abort(404)
    if not AcaoForm().validate_on_submit():
        abort(400)
    try:
        agendamento_service.marcar_status(agendamento, request.form.get("status"), current_user)
    except RegraNegocioError as erro:
        flash(erro.mensagem, "danger")
    else:
        flash(f"Atendimento marcado como {agendamento.status_rotulo.lower()}.", "success")
    return redirect(destino_seguro(request.form.get("voltar")) or url_for("profissional.agenda"))
