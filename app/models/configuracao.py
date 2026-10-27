from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Configuracao(db.Model):
    __tablename__ = "configuracao"

    chave: Mapped[str] = mapped_column(String(40), primary_key=True)
    valor: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(255))
