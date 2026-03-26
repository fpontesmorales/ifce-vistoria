from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user
from app.extensions import db


def requer_coordenacao(f):
    """Decorator que exige perfil coordenacao ou admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_coordenacao:
            flash("Acesso restrito à coordenação.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def requer_colaborador(f):
    """Decorator que exige perfil colaborador."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_colaborador:
            flash("Acesso restrito a colaboradores.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_colaborador_ou_404():
    """Retorna o Colaborador vinculado ao usuário logado ou aborta com 403."""
    from app.models.colaborador import Colaborador
    colaborador = db.session.scalar(
        db.select(Colaborador).where(Colaborador.usuario_id == current_user.id)
    )
    if colaborador is None:
        abort(403)
    return colaborador
