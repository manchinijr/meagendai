from datetime import date, datetime, time, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.controllers import perfil_requerido
from app.extensions import db
from app.forms import AcaoForm, ConfiguracaoForm, JornadaForm, ProfissionalForm, ServicoForm
from app.models import Agendamento, Jornada, Perfil, Profissional, Servico, StatusAgendamento, Usuario
from app.services import agendamento_service, cadastro_service, config_service, relatorio_service
from app.services.erros import RegraNegocioError
from app.services.tempo import FUSO, agora

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@perfil_requerido(Perfil.ADMIN)
def somente_admin():
    """Todas as rotas deste Blueprint exigem perfil ADMIN."""


def obter_ou_404(modelo, ident):
    objeto = db.session.get(modelo, ident)
    if objeto is None:
        abort(404)
    return objeto


def profissionais_ordenados():
    return db.session.scalars(select(Profissional).join(Profissional.usuario).order_by(Usuario.nome)).all()


# ---------- Painel (RF08) ----------

@bp.route("")
def painel():
    hoje = agora().date()
    return render_template(
        "admin/painel.html",
        ini_padrao=hoje.replace(day=1),
        fim_padrao=hoje,
        profissionais=profissionais_ordenados(),
        proximos=relatorio_service.proximos_agendamentos(),
    )


# ---------- Serviços (RF02) ----------

@bp.route("/servicos")
def servicos():
    lista = db.session.scalars(select(Servico).order_by(Servico.ativo.desc(), Servico.nome)).all()
    return render_template("admin/servicos.html", servicos=lista)


@bp.route("/servicos/novo", methods=["GET", "POST"])
@bp.route("/servicos/<int:servico_id>", methods=["GET", "POST"])
def servico_form(servico_id=None):
    servico = obter_ou_404(Servico, servico_id) if servico_id else None
    form = ServicoForm(obj=servico)
    if form.validate_on_submit():
        try:
            cadastro_service.salvar_servico(form.data, servico)
        except RegraNegocioError as erro:
            form.nome.errors.append(erro.mensagem)
        else:
            flash("Serviço salvo.", "success")
            return redirect(url_for("admin.servicos"))
    return render_template("admin/servico_form.html", form=form, servico=servico)


# ---------- Profissionais e jornada (RF03) ----------

@bp.route("/profissionais")
def profissionais():
    return render_template("admin/profissionais.html", profissionais=profissionais_ordenados())


@bp.route("/profissionais/novo", methods=["GET", "POST"])
@bp.route("/profissionais/<int:profissional_id>", methods=["GET", "POST"])
def profissional_form(profissional_id=None):
    profissional = obter_ou_404(Profissional, profissional_id) if profissional_id else None
    form = ProfissionalForm()
    form.servicos.choices = [
        (s.id, s.nome) for s in db.session.scalars(select(Servico).order_by(Servico.nome))
    ]
    if request.method == "GET" and profissional:
        form.nome.data = profissional.usuario.nome
        form.email.data = profissional.usuario.email
        form.telefone.data = profissional.usuario.telefone
        form.especialidade.data = profissional.especialidade
        form.ativo.data = profissional.ativo
        form.servicos.data = [s.id for s in profissional.servicos]

    if form.validate_on_submit():
        if profissional is None and not form.senha.data:
            form.senha.errors.append("Defina uma senha de acesso para o novo profissional.")
        else:
            try:
                profissional = cadastro_service.salvar_profissional(form.data, profissional)
            except RegraNegocioError as erro:
                form.email.errors.append(erro.mensagem)
            else:
                flash("Profissional salvo.", "success")
                return redirect(url_for("admin.jornada", profissional_id=profissional.id))
    return render_template("admin/profissional_form.html", form=form, profissional=profissional)


@bp.route("/profissionais/<int:profissional_id>/jornada", methods=["GET", "POST"])
def jornada(profissional_id):
    profissional = obter_ou_404(Profissional, profissional_id)
    form = JornadaForm()
    if form.validate_on_submit():
        try:
            cadastro_service.adicionar_jornada(
                profissional, form.dia_semana.data, form.hora_inicio.data, form.hora_fim.data
            )
        except RegraNegocioError as erro:
            flash(erro.mensagem, "danger")
        else:
            flash("Período adicionado à jornada.", "success")
        return redirect(url_for("admin.jornada", profissional_id=profissional.id))
    return render_template("admin/jornada.html", profissional=profissional, form=form, acao=AcaoForm())


@bp.route("/jornadas/<int:jornada_id>/remover", methods=["POST"])
def remover_jornada(jornada_id):
    item = obter_ou_404(Jornada, jornada_id)
    profissional_id = item.profissional_id
    if AcaoForm().validate_on_submit():
        cadastro_service.remover_jornada(item)
        flash("Período removido.", "success")
    return redirect(url_for("admin.jornada", profissional_id=profissional_id))


# ---------- Clientes (RN04) ----------

@bp.route("/clientes")
def clientes():
    lista = db.session.scalars(
        select(Usuario).where(Usuario.perfil == Perfil.CLIENTE).order_by(Usuario.nome)
    ).all()
    linhas = [(c, agendamento_service.faltas_do_cliente(c)) for c in lista]
    return render_template(
        "admin/clientes.html",
        linhas=linhas,
        limite=config_service.obter_int("LIMITE_FALTAS"),
        form=AcaoForm(),
    )


@bp.route("/clientes/<int:cliente_id>/zerar-faltas", methods=["POST"])
def zerar_faltas(cliente_id):
    cliente = obter_ou_404(Usuario, cliente_id)
    if cliente.perfil != Perfil.CLIENTE:
        abort(404)
    if AcaoForm().validate_on_submit():
        agendamento_service.zerar_faltas(cliente)
        flash(f"Faltas de {cliente.nome} zeradas. O agendamento online foi liberado.", "success")
    return redirect(url_for("admin.clientes"))


# ---------- Agendamentos ----------

@bp.route("/agendamentos")
def agendamentos():
    hoje = agora().date()
    try:
        data = date.fromisoformat(request.args.get("data", ""))
    except ValueError:
        data = hoje
    status = request.args.get("status") or None
    inicio = datetime.combine(data, time.min, tzinfo=FUSO)
    consulta = (
        select(Agendamento)
        .where(Agendamento.inicio >= inicio, Agendamento.inicio < inicio + timedelta(days=1))
        .order_by(Agendamento.inicio)
    )
    if status in StatusAgendamento.ROTULOS:
        consulta = consulta.where(Agendamento.status == status)
    return render_template(
        "admin/agendamentos.html",
        agendamentos=db.session.scalars(consulta).all(),
        data=data,
        status=status,
        rotulos=StatusAgendamento.ROTULOS,
        agora=agora(),
        form=AcaoForm(),
    )


@bp.route("/agendamentos/<int:agendamento_id>/cancelar", methods=["POST"])
def cancelar_agendamento(agendamento_id):
    agendamento = obter_ou_404(Agendamento, agendamento_id)
    if AcaoForm().validate_on_submit():
        try:
            agendamento_service.cancelar(agendamento, current_user)
        except RegraNegocioError as erro:
            flash(erro.mensagem, "danger")
        else:
            flash("Agendamento cancelado.", "success")
    data = agendamento.inicio.astimezone(FUSO).date().isoformat()
    return redirect(url_for("admin.agendamentos", data=data))


# ---------- Configurações (RF09) ----------

@bp.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    form = ConfiguracaoForm(data=config_service.todas())
    if form.validate_on_submit():
        config_service.atualizar({chave: getattr(form, chave).data for chave in config_service.PADROES})
        flash("Configurações salvas.", "success")
        return redirect(url_for("admin.configuracoes"))
    return render_template("admin/configuracoes.html", form=form)

