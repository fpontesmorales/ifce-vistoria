from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.usuario import Usuario
from app.forms.auth import LoginForm

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirecionar_por_perfil(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        usuario = db.session.scalar(
            db.select(Usuario).where(Usuario.username == form.username.data.strip())
        )
        if usuario is None or not usuario.check_senha(form.senha.data):
            flash("Usuário ou senha inválidos.", "danger")
            return render_template("auth/login.html", form=form)

        if not usuario.ativo:
            flash("Conta inativa. Contate a coordenação.", "warning")
            return render_template("auth/login.html", form=form)

        login_user(usuario, remember=form.lembrar.data)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("auth._rota_painel"))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/")
@login_required
def _rota_painel():
    return _redirecionar_por_perfil(current_user)


def _redirecionar_por_perfil(usuario):
    if usuario.is_coordenacao:
        return redirect(url_for("admin.painel"))
    return redirect(url_for("colaborador.painel"))
