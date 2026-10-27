import logging

from flask import jsonify, render_template, request
from flask_wtf.csrf import CSRFError

from app.extensions import db

log = logging.getLogger(__name__)

MENSAGENS = {
    400: ("Requisição inválida", "Os dados enviados não puderam ser processados. Recarregue a página e tente de novo."),
    403: ("Acesso negado", "Você não tem permissão para acessar esta página."),
    404: ("Página não encontrada", "O endereço acessado não existe ou foi removido."),
    500: ("Erro interno", "Algo deu errado do nosso lado. Tente novamente em instantes."),
}


def responder(codigo):
    titulo, mensagem = MENSAGENS[codigo]
    if request.path.startswith("/api/"):
        return jsonify(erro=mensagem), codigo
    return render_template("erros/erro.html", codigo=codigo, titulo=titulo, mensagem=mensagem), codigo


def registrar(app):
    for codigo in (400, 403, 404):
        app.register_error_handler(codigo, lambda e, c=codigo: responder(c))

    @app.errorhandler(CSRFError)
    def csrf_expirado(_erro):
        titulo, _ = MENSAGENS[400]
        mensagem = "Sua sessão expirou. Recarregue a página e tente novamente."
        return render_template("erros/erro.html", codigo=400, titulo=titulo, mensagem=mensagem), 400

    @app.errorhandler(500)
    def erro_interno(erro):
        db.session.rollback()
        log.exception("Erro interno: %s", erro)
        return responder(500)
