from datetime import datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def agora():
    return datetime.now(FUSO)


def combinar(data, hora):
    """Junta uma data e um horário no fuso do estabelecimento."""
    return datetime.combine(data, hora, tzinfo=FUSO)


def local(momento):
    return momento.astimezone(FUSO)
