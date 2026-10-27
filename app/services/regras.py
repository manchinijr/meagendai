"""Regras de negócio puras (sem banco e sem Flask), testadas em tests/unit.

Intervalos de horário são semiabertos: [inicio, fim).
"""

from datetime import timedelta
from decimal import Decimal

from app.services.tempo import combinar, local


def sobrepoe(inicio_a, fim_a, inicio_b, fim_b):
    return inicio_a < fim_b and inicio_b < fim_a


def cabe_na_jornada(jornadas, inicio, fim):
    """RN02/RN05: o atendimento inteiro precisa estar dentro de um único período da jornada."""
    data = inicio.date()
    for jornada in jornadas:
        if jornada.dia_semana != data.weekday():
            continue
        if combinar(data, jornada.hora_inicio) <= inicio and fim <= combinar(data, jornada.hora_fim):
            return True
    return False


def gerar_horarios_livres(jornadas, ocupados, data, duracao_min, agora, passo_min=15):
    """RN01 + RN02 + RN05: horários de início possíveis em uma data.

    jornadas: objetos com dia_semana, hora_inicio e hora_fim
    ocupados: lista de (inicio, fim) de agendamentos não cancelados
    """
    duracao = timedelta(minutes=duracao_min)
    passo = timedelta(minutes=passo_min)
    livres = []
    for jornada in jornadas:
        if jornada.dia_semana != data.weekday():
            continue
        candidato = combinar(data, jornada.hora_inicio)
        limite = combinar(data, jornada.hora_fim)
        while candidato + duracao <= limite:
            fim = candidato + duracao
            if candidato > agora and not any(sobrepoe(candidato, fim, i, f) for i, f in ocupados):
                livres.append(candidato)
            candidato += passo
    return sorted(livres)


def pode_cancelar(inicio, agora, antecedencia_horas):
    """RN03: cancelar/remarcar só com pelo menos N horas de antecedência (o limite exato é permitido)."""
    return inicio - agora >= timedelta(hours=antecedencia_horas)


def cliente_bloqueado(faltas, limite_faltas):
    """RN04: atingir o limite de faltas bloqueia novos agendamentos online."""
    return faltas >= limite_faltas


def calcular_metricas(agendamentos):
    """RF08: métricas do painel a partir de itens com status, preco_cobrado e inicio."""
    por_status = {"AGENDADO": 0, "CANCELADO": 0, "REALIZADO": 0, "FALTOU": 0}
    previsto = Decimal("0")
    realizado = Decimal("0")
    por_dia = {}
    por_servico = {}

    for ag in agendamentos:
        por_status[ag.status] = por_status.get(ag.status, 0) + 1
        if ag.status == "AGENDADO":
            previsto += ag.preco_cobrado
        elif ag.status == "REALIZADO":
            realizado += ag.preco_cobrado
        if ag.status != "CANCELADO":
            dia = local(ag.inicio).date().isoformat()
            por_dia[dia] = por_dia.get(dia, 0) + 1
            nome = ag.servico.nome
            por_servico[nome] = por_servico.get(nome, 0) + 1

    concluidos = por_status["REALIZADO"] + por_status["FALTOU"]
    taxa_faltas = round(por_status["FALTOU"] * 100 / concluidos, 1) if concluidos else 0.0
    total = sum(por_status.values()) - por_status["CANCELADO"]

    return {
        "total": total,
        "por_status": por_status,
        "taxa_faltas": taxa_faltas,
        "faturamento_previsto": float(previsto),
        "faturamento_realizado": float(realizado),
        "por_dia": dict(sorted(por_dia.items())),
        "top_servicos": sorted(por_servico.items(), key=lambda item: (-item[1], item[0]))[:5],
    }
