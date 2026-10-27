"""Testes de integração da camada de serviço com o PostgreSQL."""

from datetime import time, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Agendamento, StatusAgendamento
from app.services import agendamento_service as svc
from app.services import config_service, disponibilidade_service
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
from app.services.tempo import combinar


def test_cria_agendamento_com_preco_e_fim_calculados(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    assert ag.id is not None
    assert ag.status == StatusAgendamento.AGENDADO
    assert ag.fim == as_10h + timedelta(minutes=30)
    assert ag.preco_cobrado == corte.preco


def test_rn01_nao_permite_horario_sobreposto(cliente, outro_cliente, barbeiro, corte, as_10h):
    svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    with pytest.raises(HorarioIndisponivelError):
        svc.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h + timedelta(minutes=15))


def test_rn01_horario_encostado_e_permitido(cliente, outro_cliente, barbeiro, corte, as_10h):
    svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    seguinte = svc.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h + timedelta(minutes=30))
    assert seguinte.id is not None


def test_rn01_constraint_do_banco_impede_sobreposicao(cliente, barbeiro, corte, as_10h):
    """Segunda camada de proteção: mesmo ignorando o serviço, o PostgreSQL recusa a sobreposição."""
    for _ in range(2):
        db.session.add(
            Agendamento(
                cliente_id=cliente.id, profissional_id=barbeiro.id, servico_id=corte.id,
                inicio=as_10h, fim=as_10h + timedelta(minutes=30), preco_cobrado=corte.preco,
            )
        )
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_rn02_nao_agenda_no_passado(cliente, barbeiro, corte, as_10h):
    with pytest.raises(HorarioNoPassadoError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h, agora=as_10h + timedelta(minutes=1))


def test_rn02_nao_agenda_fora_da_jornada(cliente, barbeiro, corte, dia_util):
    with pytest.raises(ForaDaJornadaError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, combinar(dia_util, time(12, 15)))


def test_rn02_nao_agenda_no_domingo(cliente, barbeiro, corte, dia_util):
    domingo = dia_util + timedelta(days=6)
    with pytest.raises(ForaDaJornadaError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, combinar(domingo, time(10)))


def test_rn02_profissional_precisa_realizar_o_servico(cliente, barbeiro, escova, as_10h):
    with pytest.raises(ServicoNaoRealizadoError):
        svc.criar_agendamento(cliente, escova.id, barbeiro.id, as_10h)


def test_rn06_servico_inativo_nao_pode_ser_agendado(cliente, barbeiro, corte, as_10h):
    corte.ativo = False
    db.session.commit()
    with pytest.raises(ServicoNaoRealizadoError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)


def registrar_faltas(cliente, barbeiro, corte, dia, quantidade):
    for i in range(quantidade):
        inicio = combinar(dia - timedelta(days=14), time(9 + i))
        db.session.add(
            Agendamento(
                cliente_id=cliente.id, profissional_id=barbeiro.id, servico_id=corte.id, inicio=inicio,
                fim=inicio + timedelta(minutes=30), status=StatusAgendamento.FALTOU, preco_cobrado=corte.preco,
            )
        )
    db.session.commit()


def test_rn04_cliente_com_faltas_no_limite_fica_bloqueado(cliente, barbeiro, corte, dia_util, as_10h):
    registrar_faltas(cliente, barbeiro, corte, dia_util, 3)
    assert svc.faltas_do_cliente(cliente) == 3
    with pytest.raises(ClienteBloqueadoError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)


def test_rn04_abaixo_do_limite_ainda_agenda(cliente, barbeiro, corte, dia_util, as_10h):
    registrar_faltas(cliente, barbeiro, corte, dia_util, 2)
    assert svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h).id


def test_rn04_zerar_faltas_libera_o_cliente(cliente, barbeiro, corte, dia_util, as_10h):
    registrar_faltas(cliente, barbeiro, corte, dia_util, 3)
    svc.zerar_faltas(cliente)
    assert svc.faltas_do_cliente(cliente) == 0
    assert svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h).id


def test_rn04_limite_configuravel(cliente, barbeiro, corte, dia_util, as_10h):
    registrar_faltas(cliente, barbeiro, corte, dia_util, 1)
    config_service.atualizar({"LIMITE_FALTAS": 1})
    with pytest.raises(ClienteBloqueadoError):
        svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)


def test_rn03_cancela_com_antecedencia(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    svc.cancelar(ag, cliente, agora=as_10h - timedelta(hours=2))
    assert ag.status == StatusAgendamento.CANCELADO


def test_rn03_bloqueia_cancelamento_em_cima_da_hora(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    with pytest.raises(CancelamentoForaDoPrazoError, match="2 h"):
        svc.cancelar(ag, cliente, agora=as_10h - timedelta(hours=1, minutes=59))
    assert ag.status == StatusAgendamento.AGENDADO


def test_rn03_admin_pode_cancelar_a_qualquer_momento(cliente, admin, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    svc.cancelar(ag, admin, agora=as_10h - timedelta(minutes=5))
    assert ag.status == StatusAgendamento.CANCELADO


def test_cliente_nao_cancela_agendamento_de_outro(cliente, outro_cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    with pytest.raises(PermissaoNegadaError):
        svc.cancelar(ag, outro_cliente)


def test_horario_cancelado_volta_a_ficar_livre(cliente, outro_cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    svc.cancelar(ag, cliente)
    assert svc.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h).id


def test_remarcar_cancela_o_antigo_e_cria_o_novo(cliente, barbeiro, corte, as_10h):
    antigo = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    novo = svc.remarcar(antigo, as_10h + timedelta(hours=4), cliente)
    assert antigo.status == StatusAgendamento.CANCELADO
    assert novo.status == StatusAgendamento.AGENDADO
    assert novo.inicio == as_10h + timedelta(hours=4)


def test_remarcar_para_horario_sobreposto_ao_proprio_funciona(cliente, barbeiro, corte, as_10h):
    antigo = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    novo = svc.remarcar(antigo, as_10h + timedelta(minutes=15), cliente)
    assert novo.inicio == as_10h + timedelta(minutes=15)


def test_remarcar_para_horario_ocupado_nao_altera_nada(cliente, outro_cliente, barbeiro, corte, as_10h):
    antigo = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    svc.criar_agendamento(outro_cliente, corte.id, barbeiro.id, as_10h + timedelta(hours=1))
    with pytest.raises(HorarioIndisponivelError):
        svc.remarcar(antigo, as_10h + timedelta(hours=1), cliente)
    db.session.refresh(antigo)
    assert antigo.status == StatusAgendamento.AGENDADO


def test_rf07_profissional_marca_realizado_depois_do_inicio(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    svc.marcar_status(ag, StatusAgendamento.REALIZADO, barbeiro.usuario, agora=as_10h + timedelta(minutes=40))
    assert ag.status == StatusAgendamento.REALIZADO


def test_rf07_nao_marca_status_antes_do_horario(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    with pytest.raises(StatusInvalidoError):
        svc.marcar_status(ag, StatusAgendamento.FALTOU, barbeiro.usuario, agora=as_10h - timedelta(minutes=1))


def test_rf07_cliente_nao_marca_status(cliente, barbeiro, corte, as_10h):
    ag = svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    with pytest.raises(PermissaoNegadaError):
        svc.marcar_status(ag, StatusAgendamento.REALIZADO, cliente, agora=as_10h + timedelta(hours=1))


def test_rf04_horarios_livres_desconta_agendamentos(cliente, barbeiro, corte, dia_util, as_10h):
    antes = disponibilidade_service.horarios_livres(corte.id, barbeiro.id, dia_util)
    svc.criar_agendamento(cliente, corte.id, barbeiro.id, as_10h)
    depois = disponibilidade_service.horarios_livres(corte.id, barbeiro.id, dia_util)
    assert as_10h in antes
    assert as_10h not in depois
    assert as_10h + timedelta(minutes=30) in depois
