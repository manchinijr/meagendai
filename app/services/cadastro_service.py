from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Jornada, Perfil, Profissional, Servico, Usuario
from app.services import regras
from app.services.erros import JornadaSobrepostaError, RegistroDuplicadoError


def _commit_ou_duplicado(mensagem):
    try:
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise RegistroDuplicadoError(mensagem) from erro


def email_em_uso(email, ignorar_id=None):
    consulta = select(Usuario.id).where(func.lower(Usuario.email) == email.strip().lower())
    encontrado = db.session.scalar(consulta)
    return encontrado is not None and encontrado != ignorar_id


def cadastrar_cliente(nome, email, senha, telefone=None):
    if email_em_uso(email):
        raise RegistroDuplicadoError("Este e-mail já possui cadastro. Deseja entrar?")
    usuario = Usuario(
        nome=nome.strip(),
        email=email.strip().lower(),
        telefone=(telefone or "").strip() or None,
        perfil=Perfil.CLIENTE,
    )
    usuario.definir_senha(senha)
    db.session.add(usuario)
    _commit_ou_duplicado("Este e-mail já possui cadastro. Deseja entrar?")
    return usuario


def salvar_servico(dados, servico=None):
    servico = servico or Servico()
    servico.nome = dados["nome"].strip()
    servico.descricao = (dados.get("descricao") or "").strip() or None
    servico.duracao_min = dados["duracao_min"]
    servico.preco = dados["preco"]
    servico.ativo = dados.get("ativo", True)
    db.session.add(servico)
    _commit_ou_duplicado("Já existe um serviço com esse nome.")
    return servico


def salvar_profissional(dados, profissional=None):
    """Cria ou atualiza o profissional e o usuário de acesso dele."""
    if profissional is None:
        if email_em_uso(dados["email"]):
            raise RegistroDuplicadoError("Este e-mail já está em uso.")
        usuario = Usuario(perfil=Perfil.PROFISSIONAL)
        profissional = Profissional(usuario=usuario)
    else:
        usuario = profissional.usuario
        if email_em_uso(dados["email"], ignorar_id=usuario.id):
            raise RegistroDuplicadoError("Este e-mail já está em uso.")

    usuario.nome = dados["nome"].strip()
    usuario.email = dados["email"].strip().lower()
    usuario.telefone = (dados.get("telefone") or "").strip() or None
    if dados.get("senha"):
        usuario.definir_senha(dados["senha"])
    profissional.especialidade = (dados.get("especialidade") or "").strip() or None
    profissional.ativo = dados.get("ativo", True)
    usuario.ativo = profissional.ativo
    profissional.servicos = [db.session.get(Servico, sid) for sid in dados.get("servicos", [])]

    db.session.add(profissional)
    _commit_ou_duplicado("Este e-mail já está em uso.")
    return profissional


def adicionar_jornada(profissional, dia_semana, hora_inicio, hora_fim):
    if hora_fim <= hora_inicio:
        raise JornadaSobrepostaError("O horário final deve ser depois do inicial.")
    for existente in profissional.jornadas:
        if existente.dia_semana == dia_semana and regras.sobrepoe(
            hora_inicio, hora_fim, existente.hora_inicio, existente.hora_fim
        ):
            raise JornadaSobrepostaError()
    jornada = Jornada(dia_semana=dia_semana, hora_inicio=hora_inicio, hora_fim=hora_fim)
    profissional.jornadas.append(jornada)
    _commit_ou_duplicado(JornadaSobrepostaError.mensagem)
    return jornada


def remover_jornada(jornada):
    db.session.delete(jornada)
    db.session.commit()
