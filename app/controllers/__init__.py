from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def perfil_requerido(*perfis):
    """Restringe a rota aos perfis informados (403 para os demais)."""

    def decorador(view):
        @wraps(view)
        @login_required
        def envolvida(*args, **kwargs):
            if current_user.perfil not in perfis:
                abort(403)
            return view(*args, **kwargs)

        return envolvida

    return decorador
