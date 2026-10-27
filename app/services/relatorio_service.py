from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Agendamento, StatusAgendamento
from app.services import regras
from app.services.tempo import FUSO, agora as agora_atual


def metricas_painel(data_ini, data_fim, profissional_id=None):
    """RF08: métricas do período [data_ini, data_fim] (datas inclusivas)."""
    inicio = datetime.combine(data_ini, time.min, tzinfo=FUSO)
    fim = datetime.combine(data_fim + timedelta(days=1), time.min, tzinfo=FUSO)
    consulta = (
        select(Agendamento)
        .options(selectinload(Agendamento.servico))
        .where(Agendamento.inicio >= inicio, Agendamento.inicio < fim)
    )
    if profissional_id:
        consulta = consulta.where(Agendamento.profissional_id == profissional_id)

    metricas = regras.calcular_metricas(db.session.scalars(consulta).all())
    metricas["periodo"] = {"ini": data_ini.isoformat(), "fim": data_fim.isoformat()}
    return metricas


def proximos_agendamentos(limite=10, profissional_id=None):
    consulta = (
        select(Agendamento)
        .where(Agendamento.status == StatusAgendamento.AGENDADO, Agendamento.inicio >= agora_atual())
        .order_by(Agendamento.inicio)
        .limit(limite)
    )
    if profissional_id:
        consulta = consulta.where(Agendamento.profissional_id == profissional_id)
    return db.session.scalars(consulta).all()
