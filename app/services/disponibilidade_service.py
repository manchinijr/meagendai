from datetime import datetime, time, timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import Agendamento, Profissional, Servico, StatusAgendamento
from app.services import config_service, regras
from app.services.tempo import FUSO, agora as agora_atual


def agendamentos_ocupando(profissional_id, data, ignorar_id=None):
    inicio_dia = datetime.combine(data, time.min, tzinfo=FUSO)
    fim_dia = inicio_dia + timedelta(days=1)
    consulta = select(Agendamento.id, Agendamento.inicio, Agendamento.fim).where(
        Agendamento.profissional_id == profissional_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        Agendamento.inicio < fim_dia,
        Agendamento.fim > inicio_dia,
    )
    return [(i, f) for ag_id, i, f in db.session.execute(consulta) if ag_id != ignorar_id]


def horarios_livres(servico_id, profissional_id, data, agora=None, ignorar_agendamento_id=None):
    servico = db.session.get(Servico, servico_id)
    profissional = db.session.get(Profissional, profissional_id)
    if not servico or not profissional or not servico.ativo or not profissional.ativo:
        return []
    if not profissional.realiza(servico):
        return []

    return regras.gerar_horarios_livres(
        jornadas=profissional.jornadas,
        ocupados=agendamentos_ocupando(profissional_id, data, ignorar_agendamento_id),
        data=data,
        duracao_min=servico.duracao_min,
        agora=agora or agora_atual(),
        passo_min=config_service.obter_int("PASSO_SLOT_MIN"),
    )
