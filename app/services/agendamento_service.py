from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Agendamento, Perfil, Profissional, Servico, StatusAgendamento
from app.services import config_service, regras
from app.services.disponibilidade_service import agendamentos_ocupando
from app.services.erros import (
    CancelamentoForaDoPrazoError,
    ClienteBloqueadoError,
    ForaDaJornadaError,
    HorarioIndisponivelError,
    HorarioNoPassadoError,
    PermissaoNegadaError,
    ServicoNaoRealizadoError,
    StatusInvalidoError,
)
from app.services.tempo import agora as agora_atual

SQLSTATE_EXCLUSION_VIOLATION = "23P01"


def faltas_do_cliente(cliente):
    consulta = select(func.count(Agendamento.id)).where(
        Agendamento.cliente_id == cliente.id,
        Agendamento.status == StatusAgendamento.FALTOU,
    )
    if cliente.faltas_zeradas_em:
        consulta = consulta.where(Agendamento.inicio > cliente.faltas_zeradas_em)
    return db.session.scalar(consulta)


def esta_bloqueado(cliente):
    return regras.cliente_bloqueado(faltas_do_cliente(cliente), config_service.obter_int("LIMITE_FALTAS"))


def zerar_faltas(cliente, agora=None):
    cliente.faltas_zeradas_em = agora or agora_atual()
    db.session.commit()


def _validar_novo_horario(servico, profissional, inicio, agora, ignorar_id=None):
    """RN01, RN02 e RN06. Devolve o horário de término."""
    if not servico or not profissional or not servico.ativo or not profissional.ativo:
        raise ServicoNaoRealizadoError()
    if not profissional.realiza(servico):
        raise ServicoNaoRealizadoError()

    fim = inicio + timedelta(minutes=servico.duracao_min)
    if inicio <= agora:
        raise HorarioNoPassadoError()
    if not regras.cabe_na_jornada(profissional.jornadas, inicio, fim):
        raise ForaDaJornadaError()
    ocupados = agendamentos_ocupando(profissional.id, inicio.date(), ignorar_id)
    if any(regras.sobrepoe(inicio, fim, i, f) for i, f in ocupados):
        raise HorarioIndisponivelError()
    return fim


def _salvar(agendamento):
    """Converte a violação da constraint EXCLUDE (corrida entre dois clientes) em erro de domínio."""
    try:
        db.session.flush()
    except IntegrityError as erro:
        db.session.rollback()
        if getattr(erro.orig, "sqlstate", None) == SQLSTATE_EXCLUSION_VIOLATION:
            raise HorarioIndisponivelError() from erro
        raise
    db.session.commit()
    return agendamento


def criar_agendamento(cliente, servico_id, profissional_id, inicio, agora=None, observacao=None):
    agora = agora or agora_atual()
    if esta_bloqueado(cliente):
        raise ClienteBloqueadoError()

    servico = db.session.get(Servico, servico_id)
    profissional = db.session.get(Profissional, profissional_id)
    fim = _validar_novo_horario(servico, profissional, inicio, agora)

    agendamento = Agendamento(
        cliente_id=cliente.id,
        profissional_id=profissional.id,
        servico_id=servico.id,
        inicio=inicio,
        fim=fim,
        status=StatusAgendamento.AGENDADO,
        preco_cobrado=servico.preco,
        observacao=(observacao or "").strip() or None,
    )
    db.session.add(agendamento)
    return _salvar(agendamento)


def _checar_alteracao(agendamento, solicitante, agora):
    if solicitante.perfil != Perfil.ADMIN and agendamento.cliente_id != solicitante.id:
        raise PermissaoNegadaError()
    if agendamento.status != StatusAgendamento.AGENDADO:
        raise StatusInvalidoError()
    if solicitante.perfil == Perfil.ADMIN:
        return
    horas = config_service.obter_int("ANTECEDENCIA_CANCEL_H")
    if not regras.pode_cancelar(agendamento.inicio, agora, horas):
        raise CancelamentoForaDoPrazoError(horas)


def cancelar(agendamento, solicitante, agora=None):
    _checar_alteracao(agendamento, solicitante, agora or agora_atual())
    agendamento.status = StatusAgendamento.CANCELADO
    db.session.commit()
    return agendamento


def remarcar(agendamento, novo_inicio, solicitante, agora=None):
    """Cancela o antigo e cria o novo na mesma transação; se algo falhar, nada muda."""
    agora = agora or agora_atual()
    _checar_alteracao(agendamento, solicitante, agora)

    servico = agendamento.servico
    profissional = agendamento.profissional
    fim = _validar_novo_horario(servico, profissional, novo_inicio, agora, ignorar_id=agendamento.id)

    agendamento.status = StatusAgendamento.CANCELADO
    db.session.flush()  # libera o horário antigo antes de inserir o novo (constraint EXCLUDE)

    novo = Agendamento(
        cliente_id=agendamento.cliente_id,
        profissional_id=profissional.id,
        servico_id=servico.id,
        inicio=novo_inicio,
        fim=fim,
        status=StatusAgendamento.AGENDADO,
        preco_cobrado=servico.preco,
        observacao=agendamento.observacao,
    )
    db.session.add(novo)
    return _salvar(novo)


def marcar_status(agendamento, novo_status, solicitante, agora=None):
    """RF07: o profissional registra se o atendimento foi realizado ou se o cliente faltou."""
    agora = agora or agora_atual()
    if novo_status not in (StatusAgendamento.REALIZADO, StatusAgendamento.FALTOU):
        raise StatusInvalidoError()
    eh_dono = (
        solicitante.perfil == Perfil.PROFISSIONAL
        and solicitante.profissional is not None
        and solicitante.profissional.id == agendamento.profissional_id
    )
    if not (eh_dono or solicitante.perfil == Perfil.ADMIN):
        raise PermissaoNegadaError()
    if agendamento.status != StatusAgendamento.AGENDADO:
        raise StatusInvalidoError()
    if agendamento.inicio > agora:
        raise StatusInvalidoError("Só é possível registrar o atendimento depois do horário de início.")
    agendamento.status = novo_status
    db.session.commit()
    return agendamento
