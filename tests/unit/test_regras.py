"""Testes unitários das regras de negócio puras (sem banco de dados)."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services import regras
from app.services.tempo import FUSO

SEGUNDA = date(2030, 3, 4)  # uma segunda-feira


def jornada(dia, inicio, fim):
    return SimpleNamespace(dia_semana=dia, hora_inicio=inicio, hora_fim=fim)


def em(hora, minuto=0, dia=SEGUNDA):
    return datetime.combine(dia, time(hora, minuto), tzinfo=FUSO)


MANHA = jornada(0, time(9), time(12))
TARDE = jornada(0, time(13), time(18))
ANTES_DE_TUDO = em(0)


class TestSobreposicao:
    def test_intervalos_encostados_nao_se_sobrepoem(self):
        assert not regras.sobrepoe(em(9), em(10), em(10), em(11))

    def test_intervalos_que_se_cruzam_se_sobrepoem(self):
        assert regras.sobrepoe(em(9), em(10), em(9, 30), em(10, 30))

    def test_intervalo_contido_em_outro_se_sobrepoe(self):
        assert regras.sobrepoe(em(9), em(12), em(10), em(10, 15))


class TestHorariosLivres:
    def test_rn05_gera_horarios_com_passo_de_15_minutos(self):
        livres = regras.gerar_horarios_livres([MANHA], [], SEGUNDA, 30, ANTES_DE_TUDO, 15)
        assert livres[0] == em(9)
        assert livres[1] == em(9, 15)
        assert livres[-1] == em(11, 30)
        assert len(livres) == 11

    def test_rn05_servico_precisa_caber_inteiro_na_jornada(self):
        livres = regras.gerar_horarios_livres([MANHA], [], SEGUNDA, 45, ANTES_DE_TUDO, 15)
        assert livres[-1] == em(11, 15)
        assert em(11, 30) not in livres

    def test_rn01_exclui_horarios_que_colidem_com_agendamentos(self):
        ocupados = [(em(10), em(10, 30))]
        livres = regras.gerar_horarios_livres([MANHA], ocupados, SEGUNDA, 30, ANTES_DE_TUDO, 15)
        assert em(9, 30) in livres  # termina exatamente quando o outro começa
        assert em(9, 45) not in livres
        assert em(10) not in livres
        assert em(10, 15) not in livres
        assert em(10, 30) in livres

    def test_rn02_nao_oferece_horarios_no_passado(self):
        livres = regras.gerar_horarios_livres([MANHA], [], SEGUNDA, 30, em(10, 5), 15)
        assert livres[0] == em(10, 15)

    def test_rn02_dia_sem_jornada_nao_tem_horarios(self):
        terca = SEGUNDA + timedelta(days=1)
        assert regras.gerar_horarios_livres([MANHA], [], terca, 30, ANTES_DE_TUDO, 15) == []

    def test_intervalo_de_almoco_nao_gera_horarios(self):
        livres = regras.gerar_horarios_livres([MANHA, TARDE], [], SEGUNDA, 60, ANTES_DE_TUDO, 30)
        assert em(11) in livres
        assert em(11, 30) not in livres
        assert em(12) not in livres
        assert em(13) in livres

    def test_resultado_vem_ordenado_mesmo_com_jornadas_fora_de_ordem(self):
        livres = regras.gerar_horarios_livres([TARDE, MANHA], [], SEGUNDA, 60, ANTES_DE_TUDO, 60)
        assert livres == sorted(livres)


class TestCabeNaJornada:
    def test_dentro_da_jornada(self):
        assert regras.cabe_na_jornada([MANHA], em(9), em(9, 30))

    def test_rn02_atravessando_o_almoco_nao_cabe(self):
        assert not regras.cabe_na_jornada([MANHA, TARDE], em(11, 45), em(12, 15))

    def test_rn02_em_dia_sem_jornada_nao_cabe(self):
        terca = SEGUNDA + timedelta(days=1)
        assert not regras.cabe_na_jornada([MANHA], em(9, dia=terca), em(10, dia=terca))


class TestCancelamento:
    def test_rn03_exatamente_no_limite_pode_cancelar(self):
        assert regras.pode_cancelar(em(14), em(12), 2)

    def test_rn03_um_minuto_depois_do_limite_nao_pode(self):
        assert not regras.pode_cancelar(em(14), em(12, 1), 2)

    def test_rn03_antecedencia_zero_permite_ate_o_horario(self):
        assert regras.pode_cancelar(em(14), em(14), 0)


class TestBloqueioPorFaltas:
    @pytest.mark.parametrize("faltas, bloqueado", [(0, False), (2, False), (3, True), (5, True)])
    def test_rn04_bloqueia_ao_atingir_o_limite(self, faltas, bloqueado):
        assert regras.cliente_bloqueado(faltas, 3) is bloqueado


def agendamento(status, preco, inicio, servico="Corte"):
    return SimpleNamespace(status=status, preco_cobrado=Decimal(preco), inicio=inicio, servico=SimpleNamespace(nome=servico))


class TestMetricas:
    def test_rf08_sem_agendamentos_nao_divide_por_zero(self):
        m = regras.calcular_metricas([])
        assert m["total"] == 0
        assert m["taxa_faltas"] == 0.0
        assert m["faturamento_realizado"] == 0.0

    def test_rf08_calcula_faturamento_e_taxa_de_faltas(self):
        dados = [
            agendamento("REALIZADO", "45.00", em(9)),
            agendamento("REALIZADO", "30.00", em(10), "Barba"),
            agendamento("REALIZADO", "45.00", em(11)),
            agendamento("FALTOU", "45.00", em(13)),
            agendamento("AGENDADO", "70.00", em(14), "Combo"),
            agendamento("CANCELADO", "99.00", em(15)),
        ]
        m = regras.calcular_metricas(dados)
        assert m["total"] == 5  # cancelados não contam
        assert m["faturamento_realizado"] == 120.0
        assert m["faturamento_previsto"] == 70.0
        assert m["taxa_faltas"] == 25.0  # 1 falta em 4 atendimentos concluídos
        assert m["por_dia"] == {SEGUNDA.isoformat(): 5}
        assert m["top_servicos"][0] == ("Corte", 3)

    def test_rf08_agrupa_por_dia_no_fuso_local(self):
        # 23h30 em São Paulo ainda é o mesmo dia, mesmo sendo o dia seguinte em UTC
        m = regras.calcular_metricas([agendamento("REALIZADO", "10.00", em(23, 30))])
        assert list(m["por_dia"]) == [SEGUNDA.isoformat()]
