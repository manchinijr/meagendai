from datetime import date, datetime

from flask_login import current_user

from app.forms import AcaoForm
from app.models import Perfil
from app.models.jornada import DIAS_SEMANA
from app.services.tempo import FUSO


def data_br(valor):
    if isinstance(valor, datetime):
        valor = valor.astimezone(FUSO)
    return valor.strftime("%d/%m/%Y")


def hora(valor):
    if isinstance(valor, datetime):
        valor = valor.astimezone(FUSO)
    return valor.strftime("%H:%M")


def dia_semana(valor):
    if isinstance(valor, datetime):
        valor = valor.astimezone(FUSO).date()
    return DIAS_SEMANA[valor.weekday()] if isinstance(valor, date) else DIAS_SEMANA[valor]


def moeda(valor):
    texto = f"{float(valor or 0):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def registrar(app):
    app.add_template_filter(data_br)
    app.add_template_filter(hora)
    app.add_template_filter(dia_semana)
    app.add_template_filter(moeda)

    @app.context_processor
    def globais():
        return {"Perfil": Perfil, "form_logout": AcaoForm(), "usuario": current_user}
