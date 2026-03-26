from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required
from app.extensions import db
from app.models.vistoria import Vistoria
from app.models.ocorrencia import Ocorrencia
from app.forms.ocorrencia import OcorrenciaForm
from app.utils import requer_colaborador, get_colaborador_ou_404

bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")


# ─── Nova ocorrência (vinculada a uma vistoria) ────────────────────────────────

@bp.route("/nova/<int:vistoria_id>", methods=["GET", "POST"])
@login_required
@requer_colaborador
def nova(vistoria_id):
    colaborador = get_colaborador_ou_404()

    # Garante que a vistoria existe E pertence a este colaborador
    vistoria = db.session.scalar(
        db.select(Vistoria).where(
            Vistoria.id == vistoria_id,
            Vistoria.colaborador_id == colaborador.id,
        )
    )
    if vistoria is None:
        abort(404)

    form = OcorrenciaForm()

    if form.validate_on_submit():
        ocorrencia = Ocorrencia(
            vistoria_id=vistoria.id,
            categoria=form.categoria.data,
            descricao=form.descricao.data,
            prioridade=form.prioridade.data,
            risco=form.risco.data,
            material_sugerido=form.material_sugerido.data or None,
            observacoes=form.observacoes.data or None,
            status="registrada",
        )
        db.session.add(ocorrencia)
        db.session.commit()

        flash("Ocorrência registrada com sucesso.", "success")
        return redirect(url_for("vistorias.detalhe", vistoria_id=vistoria.id))

    return render_template(
        "ocorrencias/nova.html",
        form=form,
        vistoria=vistoria,
        colaborador=colaborador,
    )


# ─── Detalhe de uma ocorrência ─────────────────────────────────────────────────

@bp.route("/<int:ocorrencia_id>")
@login_required
@requer_colaborador
def detalhe(ocorrencia_id):
    colaborador = get_colaborador_ou_404()

    ocorrencia = db.session.scalar(
        db.select(Ocorrencia)
        .join(Vistoria, Ocorrencia.vistoria_id == Vistoria.id)
        .where(
            Ocorrencia.id == ocorrencia_id,
            Vistoria.colaborador_id == colaborador.id,
        )
    )
    if ocorrencia is None:
        abort(404)

    return render_template(
        "ocorrencias/detalhe.html",
        ocorrencia=ocorrencia,
        vistoria=ocorrencia.vistoria,
        colaborador=colaborador,
    )
