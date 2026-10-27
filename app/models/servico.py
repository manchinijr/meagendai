from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Servico(db.Model):
    __tablename__ = "servico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(255))
    duracao_min: Mapped[int] = mapped_column(SmallInteger)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    profissionais = db.relationship(
        "Profissional", secondary="profissional_servico", back_populates="servicos"
    )

    def __repr__(self):
        return f"<Servico {self.nome}>"
