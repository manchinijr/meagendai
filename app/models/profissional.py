from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

profissional_servico = Table(
    "profissional_servico",
    db.metadata,
    Column("profissional_id", ForeignKey("profissional.id", ondelete="CASCADE"), primary_key=True),
    Column("servico_id", ForeignKey("servico.id", ondelete="CASCADE"), primary_key=True),
)


class Profissional(db.Model):
    __tablename__ = "profissional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), unique=True)
    especialidade: Mapped[str | None] = mapped_column(String(80))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="profissional")
    servicos = relationship("Servico", secondary=profissional_servico, back_populates="profissionais")
    jornadas = relationship(
        "Jornada",
        back_populates="profissional",
        cascade="all, delete-orphan",
        order_by="(Jornada.dia_semana, Jornada.hora_inicio)",
    )

    @property
    def nome(self):
        return self.usuario.nome

    def realiza(self, servico):
        return any(s.id == servico.id for s in self.servicos)

    def __repr__(self):
        return f"<Profissional {self.usuario_id}>"
