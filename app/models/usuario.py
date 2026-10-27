from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class Perfil:
    ADMIN = "ADMIN"
    PROFISSIONAL = "PROFISSIONAL"
    CLIENTE = "CLIENTE"


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(20))
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(12))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    faltas_zeradas_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profissional = relationship("Profissional", back_populates="usuario", uselist=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_active(self):
        return self.ativo

    @property
    def primeiro_nome(self):
        return self.nome.split()[0]

    def __repr__(self):
        return f"<Usuario {self.email} {self.perfil}>"


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))
