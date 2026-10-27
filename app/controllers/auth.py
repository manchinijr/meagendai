from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, select

from app.extensions import db
from app.forms import AcaoForm, CadastroForm, LoginForm
from app.models import Perfil, Usuario
from app.services import cadastro_service
from app.services.erros import RegistroDuplicadoError

bp = Blueprint("auth", __name__)


def pagina_inicial(usuario):
    if usuario.perfil == Perfil.ADMIN:
        return url_for("admin.painel")
    if usuario.perfil == Perfil.PROFISSIONAL:
        return url_for("profissional.agenda")
    return url_for("cliente.meus_agendamentos")


def destino_seguro(proximo):
    """Evita redirecionamento para outro site (open redirect)."""
    if proximo and not urlsplit(proximo).netloc and proximo.startswith("/"):
        return proximo
    return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(pagina_inicial(current_user))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        usuario = db.session.scalar(select(Usuario).where(func.lower(Usuario.email) == email))
        if usuario and usuario.ativo and usuario.checar_senha(form.senha.data):
            login_user(usuario, remember=form.lembrar.data)
            flash(f"Olá, {usuario.primeiro_nome}!", "success")
            return redirect(destino_seguro(request.args.get("next")) or pagina_inicial(usuario))
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(pagina_inicial(current_user))

    form = CadastroForm()
    if form.validate_on_submit():
        try:
            usuario = cadastro_service.cadastrar_cliente(
                form.nome.data, form.email.data, form.senha.data, form.telefone.data
            )
        except RegistroDuplicadoError as erro:
            form.email.errors.append(erro.mensagem)
        else:
            login_user(usuario)
            flash("Conta criada com sucesso! Agora é só escolher o serviço.", "success")
            return redirect(url_for("cliente.agendar"))
    return render_template("auth/cadastro.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    if AcaoForm().validate_on_submit():
        logout_user()
        flash("Você saiu da sua conta.", "info")
    return redirect(url_for("cliente.index"))
