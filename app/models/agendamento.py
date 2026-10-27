from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class StatusAgendamento:
    AGENDADO = "AGENDADO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"
    FALTOU = "FALTOU"

    ROTULOS = {
        AGENDADO: "Agendado",
        CANCELADO: "Cancelado",
        REALIZADO: "Realizado",
        FALTOU: "Faltou",
    }


class Agendamento(db.Model):
    __tablename__ = "agendamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    profissional_id: Mapped[int] = mapped_column(ForeignKey("profissional.id"))
    servico_id: Mapped[int] = mapped_column(ForeignKey("servico.id"))
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fim: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(10), default=StatusAgendamento.AGENDADO)
    preco_cobrado: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    observacao: Mapped[str | None] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    cliente = relationship("Usuario")
    profissional = relationship("Profissional")
    servico = relationship("Servico")

    @property
    def status_rotulo(self):
        return StatusAgendamento.ROTULOS.get(self.status, self.status)

    @property
    def ativo(self):
        return self.status == StatusAgendamento.AGENDADO

    def __repr__(self):
        return f"<Agendamento {self.id} {self.inicio} {self.status}>"
