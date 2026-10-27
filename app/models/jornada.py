from datetime import time

from sqlalchemy import ForeignKey, Integer, SmallInteger, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


class Jornada(db.Model):
    __tablename__ = "jornada"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profissional_id: Mapped[int] = mapped_column(ForeignKey("profissional.id", ondelete="CASCADE"))
    dia_semana: Mapped[int] = mapped_column(SmallInteger)  # 0 = segunda, igual a date.weekday()
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fim: Mapped[time] = mapped_column(Time)

    profissional = relationship("Profissional", back_populates="jornadas")

    @property
    def dia_nome(self):
        return DIAS_SEMANA[self.dia_semana]

    def __repr__(self):
        return f"<Jornada {self.dia_nome} {self.hora_inicio}-{self.hora_fim}>"
