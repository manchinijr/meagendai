from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import current_user

from app.controllers import perfil_requerido
from app.controllers.cliente import ler_data
from app.extensions import db
from app.models import Agendamento, Perfil
from app.services import disponibilidade_service, relatorio_service
from app.services.tempo import FUSO, agora

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/horarios")
@perfil_requerido(Perfil.CLIENTE)
def horarios():
    servico_id = request.args.get("servico", type=int)
    profissional_id = request.args.get("profissional", type=int)
    if not servico_id or not profissional_id:
        return jsonify(erro="Informe o serviço e o profissional."), 400
    data = ler_data(request.args.get("data"))
    ignorar = db.session.get(Agendamento, request.args.get("ignorar", type=int) or 0)
    livres = disponibilidade_service.horarios_livres(
        servico_id,
        profissional_id,
        data,
        ignorar_agendamento_id=ignorar.id if ignorar and ignorar.cliente_id == current_user.id else None,
    )
    return jsonify(
        data=data.isoformat(),
        horarios=[{"inicio": h.isoformat(), "rotulo": h.astimezone(FUSO).strftime("%H:%M")} for h in livres],
    )


@bp.route("/painel")
@perfil_requerido(Perfil.ADMIN)
def painel():
    hoje = agora().date()
    try:
        ini = date.fromisoformat(request.args.get("ini", ""))
        fim = date.fromisoformat(request.args.get("fim", ""))
    except ValueError:
        ini, fim = hoje.replace(day=1), hoje
    if fim < ini:
        return jsonify(erro="A data final deve ser igual ou posterior à inicial."), 400
    if (fim - ini).days > 366:
        return jsonify(erro="Escolha um período de até 1 ano."), 400
    return jsonify(relatorio_service.metricas_painel(ini, fim, request.args.get("profissional", type=int)))
