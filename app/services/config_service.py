from app.extensions import db
from app.models import Configuracao

PADROES = {
    "ANTECEDENCIA_CANCEL_H": ("2", "Horas mínimas de antecedência para cancelar/remarcar"),
    "LIMITE_FALTAS": ("3", "Faltas que bloqueiam novos agendamentos online"),
    "PASSO_SLOT_MIN": ("15", "Intervalo, em minutos, entre os horários oferecidos"),
}


def obter_int(chave):
    registro = db.session.get(Configuracao, chave)
    valor = registro.valor if registro else PADROES[chave][0]
    return int(valor)


def todas():
    return {chave: obter_int(chave) for chave in PADROES}


def atualizar(valores):
    for chave, valor in valores.items():
        if chave not in PADROES:
            raise KeyError(chave)
        if int(valor) < 0:
            raise ValueError("O valor não pode ser negativo.")
        registro = db.session.get(Configuracao, chave)
        if registro is None:
            registro = Configuracao(chave=chave, descricao=PADROES[chave][1])
            db.session.add(registro)
        registro.valor = str(int(valor))
    db.session.commit()
